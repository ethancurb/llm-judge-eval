# summarize_results.py
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
JUDGEMENTS_CSV = DATA_DIR / "judgements.csv"


def summarize_results(judgements_csv: Path = JUDGEMENTS_CSV) -> None:
    """
    Print accuracy summaries by mechanism, condition, and overall.
    """
    df = pd.read_csv(judgements_csv)

    # Filter out rows where we failed to get a valid choice
    valid = df[df["is_correct"].isin([True, False, "True", "False"])]
    # Normalize booleans if stored as strings
    valid["is_correct"] = valid["is_correct"].astype(str).map({"True": True, "False": False})

    overall_acc = valid["is_correct"].mean()
    print(f"Overall accuracy: {overall_acc:.3f} ({valid['is_correct'].sum()}/{len(valid)})")

    print("\nAccuracy by mechanism_code:")
    by_mech = valid.groupby("mechanism_code")["is_correct"].mean().sort_values(ascending=False)
    for mech, acc in by_mech.items():
        print(f"  {mech:15s}  {acc:.3f}")

    print("\nAccuracy by mechanism_code and condition:")
    by_mech_cond = valid.groupby(["mechanism_code", "condition"])["is_correct"].mean()
    for (mech, cond), acc in by_mech_cond.items():
        print(f"  {mech:15s}  {cond:5s}  {acc:.3f}")


if __name__ == "__main__":
    summarize_results()
