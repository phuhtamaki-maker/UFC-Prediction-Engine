import unittest
import pandas as pd
from walk_forward import year_by_year


def generated_fights():
    fighters = [f"F{i}" for i in range(30)]
    fights = []
    for year in range(2015, 2022):
        for index in range(42):
            a = fighters[(index * 3 + year) % 30]
            b = fighters[(index * 3 + year + 1) % 30]
            fights.append(dict(fight_id=f"{year}-{index}", event_date=f"{year}-05-{(index % 28) + 1:02d}",
                               f1_name=a, f2_name=b, f1_id=a, f2_id=b,
                               result_f1="W" if index % 2 else "L",
                               result_f2="L" if index % 2 else "W"))
    return pd.DataFrame(fights)


class WalkForwardTests(unittest.TestCase):
    def test_prior_year_only(self):
        result = year_by_year(generated_fights(), 2020, 2021)
        rows = result["years"]
        self.assertTrue(all(row["eligible"] for row in rows))
        self.assertEqual(rows[0]["training_n"], 42 * 4)
        self.assertEqual(rows[0]["calibration_n"], 42)
        self.assertEqual(rows[0]["test_n"], 42)
        self.assertEqual(rows[1]["training_n"], 42 * 5)

    def test_future_labels_do_not_affect_prior_year_result(self):
        data = generated_fights()
        first = year_by_year(data, 2020, 2020)["years"][0]["model"]
        modified = data.copy()
        affected = modified.event_date.str.startswith("2021")
        modified.loc[affected, "result_f1"] = "W"
        modified.loc[affected, "result_f2"] = "L"
        second = year_by_year(modified, 2020, 2020)["years"][0]["model"]
        self.assertEqual(first, second)

    def test_empty_year_reported(self):
        result = year_by_year(generated_fights(), 2024, 2024)
        self.assertFalse(result["years"][0]["eligible"])
        self.assertEqual(result["evaluated_years"], 0)


if __name__ == "__main__":
    unittest.main()
