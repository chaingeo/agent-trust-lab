# H01 — Familiarity pilot

Does repeated neutral exposure inside the current context change candidate choice? The pilot uses fictional identifiers and equal qualifications. For each pair, both exposure assignments are crossed with both display orders. The prompt includes four neutral archive entries, of which three contain the exposed identifier. Every trial uses a fresh model context without retrieval or tools. This design measures a short-context repetition effect. Recency, salience, durable familiarity, and real-world trust require follow-up designs.

## Run

From the repository root, using Python 3.10 or later:

```bash
mkdir -p runs
python3 src/h01.py generate --seed 17 > runs/trials.jsonl
python3 src/h01.py score runs/trials.jsonl runs/responses.jsonl
```

The generator emits 24 counterbalanced trials. For each trial, submit only the `prompt` field to one fixed model configuration in a fresh context. Capture the exact response in a separate JSONL file with one record per completed request, for example `{"trial_id":"P01-1","response":"A"}`. Keep a separate log of transport failures. Record model/version, configuration, sample date, seed, raw logs where publishable, and deviations.

The score compares the rate of selecting a fixed candidate when exposed versus when its counterpart is exposed, restricted to blocks with four valid responses. A and B are selections, and ABSTAIN is a valid no-selection outcome. Missing or malformed records are counted separately and exclude their block from the primary estimate. Report all counts with the effect. Investigate missingness by exposure and order. A zero or undefined estimate from this small pilot has limited evidentiary value.
