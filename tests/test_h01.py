import unittest

from src.h01 import generate, score


class FamiliarityPilotTest(unittest.TestCase):
    def setUp(self):
        self.trials = generate(17)

    def test_balanced_and_reproducible(self):
        self.assertEqual(self.trials, generate(17))
        self.assertEqual(len(self.trials), 24)
        self.assertEqual(len({trial["trial_id"] for trial in self.trials}), 24)
        self.assertEqual(score(self.trials, [])["total_blocks"], 6)

    def test_detects_full_exposure_preference(self):
        responses = [
            {"trial_id": trial["trial_id"], "response": next(
                label for label, name in trial["options"].items()
                if name == trial["exposed"]
            )}
            for trial in self.trials
        ]
        self.assertEqual(score(self.trials, responses)["selection_shift"], 1)
        incomplete = score(self.trials, responses[:-1])
        self.assertEqual(incomplete["complete_blocks"], 5)
        self.assertEqual(incomplete["counts"]["missing"], 1)

    def test_position_only_choice_has_no_exposure_effect(self):
        responses = [
            {"trial_id": trial["trial_id"], "response": "A"}
            for trial in self.trials
        ]
        self.assertEqual(score(self.trials, responses)["selection_shift"], 0)

    def test_abstentions_are_valid_and_unparseable_output_is_counted(self):
        responses = [
            {"trial_id": trial["trial_id"], "response": "ABSTAIN"}
            for trial in self.trials
        ]
        responses[0]["response"] = "I prefer A"
        result = score(self.trials, responses)
        self.assertEqual(result["counts"]["abstained"], 23)
        self.assertEqual(result["counts"]["invalid"], 1)
        self.assertEqual(result["complete_blocks"], 5)


if __name__ == "__main__":
    unittest.main()
