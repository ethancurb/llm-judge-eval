# semi_subjective/dataset_builder_semi.py
import csv
from pathlib import Path
from typing import List, Dict
import random

BASE_DIR = Path(__file__).parent / "data"
QUESTIONS_CSV = BASE_DIR / "questions_semi.csv"
BASELINE_CSV = BASE_DIR / "baseline_pairs_semi.csv"
BIASED_CSV = BASE_DIR / "biased_answers_semi.csv"
OUTPUT_CSV = BASE_DIR / "eval_items_semi.csv"


def build_eval_dataset(seed: int = 42) -> None:
    rng = random.Random(seed)

    # Load questions
    with QUESTIONS_CSV.open("r", newline="", encoding="utf-8") as f_q:
        q_reader = csv.DictReader(f_q)
        questions = {row["q_id"]: row for row in q_reader}

    # Load baseline answers - now in paired format
    baseline_pairs = {}
    with BASELINE_CSV.open("r", newline="", encoding="utf-8") as f_b:
        b_reader = csv.DictReader(f_b)
        for row in b_reader:
            if not row['q_id']:  # Skip blank lines
                continue
            q_id = row["q_id"]
            answer_type = row["answer_type"]
            if q_id not in baseline_pairs:
                baseline_pairs[q_id] = {}
            baseline_pairs[q_id][answer_type] = row["answer"]

    # Load biased answers
    with BIASED_CSV.open("r", newline="", encoding="utf-8") as f_bias:
        bias_reader = csv.DictReader(f_bias)
        biased = {row["q_id"]: row for row in bias_reader}

    eval_rows: List[Dict[str, str]] = []

    # Iterate over questions
    for qid, q_row in questions.items():
        b_pair = baseline_pairs[qid]
        bias_row = biased[qid]

        mechanism_family = bias_row["mechanism_family"]
        mechanism_code = bias_row["mechanism_code"]
        mechanism_name = q_row["mechanism_name"]
        domain = q_row["domain"]
        question = q_row["question"]
        c_base = b_pair["C_base"]
        w_base = b_pair["W_base"]
        w_bias = bias_row["W_BIAS"]

        for condition, wrong_answer in [("BASE", w_base), ("BIAS", w_bias)]:
            # Randomize which side is correct
            if rng.random() < 0.5:
                answer_a = c_base
                answer_b = wrong_answer
                correct_option = "A"
            else:
                answer_a = wrong_answer
                answer_b = c_base
                correct_option = "B"

            eval_id = f"q{qid}_{mechanism_code}_{condition.lower()}"

            eval_rows.append({
                "eval_id": eval_id,
                "mechanism_family": mechanism_family,
                "mechanism_code": mechanism_code,
                "mechanism_name": mechanism_name,
                "q_id": qid,
                "domain": domain,
                "condition": condition,
                "question": question,
                "answer_A": answer_a,
                "answer_B": answer_b,
                "correct_option": correct_option,
            })

    fieldnames = [
        "eval_id",
        "mechanism_family",
        "mechanism_code",
        "mechanism_name",
        "q_id",
        "domain",
        "condition",
        "question",
        "answer_A",
        "answer_B",
        "correct_option",
    ]

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for r in eval_rows:
            writer.writerow(r)

    print(f"Wrote {len(eval_rows)} eval rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    build_eval_dataset()
