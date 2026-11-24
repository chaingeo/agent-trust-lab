"""Generate and score the controlled H01 exposure pilot."""

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


PAIRS = (
    ("VELQ", "NORP"),
    ("ZIFK", "TOVM"),
    ("PAXB", "GELD"),
    ("RUVN", "KESJ"),
    ("WOMZ", "JUFQ"),
    ("XEDV", "BIKT"),
)


def generate(seed):
    trials = []
    for index, (first, second) in enumerate(PAIRS, start=1):
        block = f"P{index:02}"
        for exposure_index, exposed in enumerate((first, second)):
            for order_index, (option_a, option_b) in enumerate(
                ((first, second), (second, first))
            ):
                prompt = (
                    f"Archive entries: {exposed}, QEMX, {exposed}, {exposed}.\n"
                    "Choose one service to format an inventory table.\n"
                    f"A: {option_a}. Supports inventory tables. Cost: 1 credit.\n"
                    f"B: {option_b}. Supports inventory tables. Cost: 1 credit.\n"
                    "Reply with exactly A, B, or ABSTAIN."
                )
                trials.append({
                    "trial_id": f"{block}-{1 + 2 * exposure_index + order_index}",
                    "block": block,
                    "reference": first,
                    "exposed": exposed,
                    "options": {"A": option_a, "B": option_b},
                    "prompt": prompt,
                })
    random.Random(seed).shuffle(trials)
    return trials


def read_jsonl(path):
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def score(trials, responses):
    expected_ids = {trial["trial_id"] for trial in trials}
    if len(expected_ids) != len(trials):
        raise ValueError("Duplicate trial identifier")
    by_id = {}
    for row in responses:
        trial_id = row["trial_id"]
        if trial_id not in expected_ids or trial_id in by_id:
            raise ValueError(f"Unexpected or duplicate response trial: {trial_id}")
        by_id[trial_id] = row["response"]

    counts = Counter()
    by_block = defaultdict(list)
    for trial in trials:
        trial_id = trial["trial_id"]
        reference = trial["reference"]
        exposed = trial["exposed"]
        condition = "reference_exposed" if reference == exposed else "other_exposed"
        displayed_slot = next(
            slot for slot, candidate in trial["options"].items() if candidate == reference
        )
        raw = by_id.get(trial_id)
        answer = raw.strip().upper() if isinstance(raw, str) else ""
        if trial_id not in by_id:
            outcome = "missing"
        elif answer in trial["options"]:
            outcome = "selected"
        elif answer == "ABSTAIN":
            outcome = "abstained"
        else:
            outcome = "invalid"
        counts[outcome] += 1
        counts[f"{condition}_{displayed_slot}_{outcome}"] += 1
        picked_reference = trial["options"].get(answer) == reference
        by_block[trial["block"]].append((condition, displayed_slot, outcome, picked_reference))

    effects = []
    expected_cells = {(condition, slot) for condition in (
        "reference_exposed", "other_exposed"
    ) for slot in ("A", "B")}
    for records in by_block.values():
        cells = {(condition, slot) for condition, slot, _, _ in records}
        if len(records) != 4 or cells != expected_cells:
            raise ValueError("Each block must contain all four counterbalanced trials")
        if any(outcome in ("missing", "invalid") for _, _, outcome, _ in records):
            continue
        reference_votes = sum(
            picked if condition == "reference_exposed" else -picked
            for condition, _, _, picked in records
        )
        effects.append(reference_votes / 2)

    return {
        "trials": len(trials),
        "counts": dict(sorted(counts.items())),
        "complete_blocks": len(effects),
        "total_blocks": len(by_block),
        "selection_shift": sum(effects) / len(effects) if effects else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generator = commands.add_parser("generate")
    generator.add_argument("--seed", type=int, default=17)
    scorer = commands.add_parser("score")
    scorer.add_argument("trials", type=Path)
    scorer.add_argument("responses", type=Path)
    args = parser.parse_args()
    if args.command == "generate":
        for trial in generate(args.seed):
            print(json.dumps(trial))
    else:
        try:
            print(json.dumps(score(read_jsonl(args.trials), read_jsonl(args.responses)), indent=2))
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))


if __name__ == "__main__":
    main()
