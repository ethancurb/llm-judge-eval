# dataset_builder.py
import csv
import random
from pathlib import Path

import pandas as pd


# Use Excel for questions and baseline, CSV for new biases
EXCEL_PATH = Path(__file__).parent.parent / "CSCE 477 - Project Taxonomy.xlsx"
BIAS_CSV = Path(__file__).parent / "data" / "biased_answers.csv"
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_CSV = OUTPUT_DIR / "eval_items.csv"


def build_eval_dataset(excel_path: Path = EXCEL_PATH,
                       bias_csv: Path = BIAS_CSV,
                       output_csv: Path = OUTPUT_CSV,
                       seed: int = 42) -> None:
    """
    Build a CSV of evaluation items from Excel (questions + baseline) and biased_answers.csv (new biases).

    Each row is a single judging instance with:
      - question
      - answer_A / answer_B (randomized order)
      - correct_option (A or B) – kept only in CSV, *never* sent to the judge
      - metadata (q_id, mechanism, domain, condition, etc.)
    """
    # Read Excel file for questions, correct answers, and baseline wrong answers
    df_excel = pd.read_excel(excel_path, sheet_name="Biased")
    
    # Read the new bias CSV
    df_bias = pd.read_csv(bias_csv)
    
    # Merge bias data with Excel data on mechanism_code and q_id
    # Create a lookup dictionary for biases
    bias_lookup = {}
    for _, bias_row in df_bias.iterrows():
        key = (str(bias_row['mechanism_code']), int(bias_row['q_id']))
        bias_lookup[key] = str(bias_row['W_bias']).strip()
    
    rng = random.Random(seed)
    rows = []

    for _, row in df_excel.iterrows():
        mechanism_code = str(row["mechanism_code"])
        q_id = int(row["q_id"])
        
        # Get the new bias from the CSV, or fall back to Excel W_BIAS if not found
        key = (mechanism_code, q_id)
        w_bias = bias_lookup.get(key, str(row.get("W_BIAS", row.get("W_BASE", ""))).strip())
        
        # Create BASE condition (C_BASE vs W_BASE)
        base_record = _make_pair(row, condition="BASE", wrong_answer=str(row["W_BASE"]).strip(), rng=rng)
        
        # Create BIAS condition (C_BASE vs new W_BIAS from CSV)
        bias_record = _make_pair(row, condition="BIAS", wrong_answer=w_bias, rng=rng)
        
        rows.extend([base_record, bias_record])

    fieldnames = list(rows[0].keys()) if rows else []

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} eval rows to {output_csv}")
    print(f"  - Using questions and baseline from: {excel_path.name}")
    print(f"  - Using new biases from: {bias_csv.name}")


def _make_pair(row, condition: str, wrong_answer: str, rng: random.Random):
    """
    Given an Excel row and a wrong answer, build a single eval-row dict.
    
    Args:
        row: DataFrame row from Excel with question and metadata
        condition: "BASE" or "BIAS"
        wrong_answer: The wrong answer text (from W_BASE or W_BIAS)
        rng: Random number generator for answer order randomization
    """
    q_id = int(row["q_id"])
    mechanism_family = str(row["mechanism_family"])
    mechanism_code = str(row["mechanism_code"])
    mechanism_name = str(row["mechanism_name"])
    domain = str(row["domain"])
    question = str(row["question"]).strip()
    correct = str(row["C_BASE"]).strip()

    # Unique but human-readable identifier
    eval_id = f"q{q_id:02d}_{mechanism_code}_{condition.lower()}"

    # Randomize which side is correct so the model can't exploit position
    if rng.random() < 0.5:
        answer_a, answer_b = correct, wrong_answer
        correct_option = "A"
    else:
        answer_a, answer_b = wrong_answer, correct
        correct_option = "B"

    return {
        "eval_id": eval_id,
        "q_id": q_id,
        "mechanism_family": mechanism_family,
        "mechanism_code": mechanism_code,
        "mechanism_name": mechanism_name,
        "domain": domain,
        "condition": condition,  # BASE vs BIAS
        "question": question,
        "answer_A": answer_a,
        "answer_B": answer_b,
        # Ground-truth (never shown to judge)
        "correct_option": correct_option,
    }


if __name__ == "__main__":
    build_eval_dataset()
