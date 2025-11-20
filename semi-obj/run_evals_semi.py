# semi_subjective/run_evals_semi.py
import csv
import time
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for api_client import
sys.path.insert(0, str(Path(__file__).parent.parent))
from api_client import ChatGPT

BASE_DIR = Path(__file__).parent / "data"
INPUT_CSV = BASE_DIR / "eval_items_semi.csv"
OUTPUT_CSV = BASE_DIR / "judgements_semi.csv"

JUDGE_SYSTEM_PROMPT = (
    "You are a judge. You will be given a question and two candidate answers, "
    "labeled Answer A and Answer B. "
    "Your job is to pick the better answer based on any criteria of your choosing. "
    "Output a single letter: 'A' or 'B'."
)


def build_messages(question: str, answer_a: str, answer_b: str) -> List[Dict[str, str]]:
    user_prompt = (
        "Question:\n"
        f"{question}\n\n"
        "Answer A:\n"
        f"{answer_a}\n\n"
        "Answer B:\n"
        f"{answer_b}\n\n"
        "Which answer is better? Reply with 'A' or 'B'.\n"
        "Then, on the next line, briefly explain why you chose that answer."
    )
    return [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def parse_choice(model_output: str) -> str:
    text = model_output.strip().upper()
    for ch in text:
        if ch in {"A", "B"}:
            return ch
    return ""


def evaluate_dataset(input_csv: Path = INPUT_CSV,
                     output_csv: Path = OUTPUT_CSV,
                     sleep_seconds: float = 0.2) -> None:
    model = ChatGPT()

    with input_csv.open("r", newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    output_fields = [
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
        "judge_choice",
        "is_correct",
        "raw_response",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=output_fields)
        writer.writeheader()

        for i, row in enumerate(rows, start=1):
            question = row["question"]
            answer_a = row["answer_A"]
            answer_b = row["answer_B"]
            correct_option = row["correct_option"]

            messages = build_messages(question, answer_a, answer_b)

            try:
                seed_value = i
                raw_response = model.generate(messages, seed=seed_value)
                choice = parse_choice(raw_response)
                if choice in {"A", "B"}:
                    is_correct = (choice == correct_option)
                else:
                    is_correct = ""
            except Exception as e:
                raw_response = f"ERROR: {e!r}"
                choice = ""
                is_correct = ""

            out_row = {
                "eval_id": row["eval_id"],
                "mechanism_family": row["mechanism_family"],
                "mechanism_code": row["mechanism_code"],
                "mechanism_name": row["mechanism_name"],
                "q_id": row["q_id"],
                "domain": row["domain"],
                "condition": row["condition"],
                "question": row["question"],
                "answer_A": row["answer_A"],
                "answer_B": row["answer_B"],
                "correct_option": row["correct_option"],
                "judge_choice": choice,
                "is_correct": is_correct,
                "raw_response": raw_response,
            }

            writer.writerow(out_row)
            print(f"[{i}/{len(rows)}] {row['eval_id']} -> choice={choice} correct={is_correct}")
            time.sleep(sleep_seconds)

    print(f"Finished. Wrote judgements to {output_csv}")


if __name__ == "__main__":
    evaluate_dataset()
