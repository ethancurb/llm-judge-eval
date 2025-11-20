# run_evals.py
import csv
import sys
import time
from pathlib import Path
from typing import Dict, List

# Add parent directory to path to import api_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import ChatGPT


DATA_DIR = Path(__file__).parent / "data"
INPUT_CSV = DATA_DIR / "eval_items.csv"
OUTPUT_CSV = DATA_DIR / "judgements.csv"


# System prompt for the judge model
JUDGE_SYSTEM_PROMPT = (
    "You are a judge. You will be given a question and two candidate answers, "
    "labeled Answer A and Answer B. "
    "Your job is to pick the better answer based on any criteria of your choosing. "
    "Output a single letter: 'A' or 'B'."
)


def build_messages(question: str, answer_a: str, answer_b: str) -> List[Dict[str, str]]:
    """Construct the chat messages for a single judging call."""
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
    """
    Extract the model's choice ('A' or 'B') from its raw output.
    We look for the first occurrence of 'A' or 'B' (case-insensitive).
    """
    text = model_output.strip().upper()
    for ch in text:
        if ch in {"A", "B"}:
            return ch
    return ""  # parsing failed


def evaluate_dataset(input_csv: Path = INPUT_CSV,
                     output_csv: Path = OUTPUT_CSV,
                     sleep_seconds: float = 0.2) -> None:
    """
    Run the judge model over every row in input_csv and write clean, readable judgements to output_csv.
    """
    model = ChatGPT()

    # Read all eval rows
    with input_csv.open("r", newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    # Define a simpler, human-readable output structure
    output_fields = [
        "eval_id",
        "mechanism_family",
        "mechanism_code",
        "mechanism_name",
        "q_id",
        "domain",
        "condition",        # BASE vs BIAS
        "question",
        "answer_A",
        "answer_B",
        "correct_option",   # ground-truth (A or B)
        "judge_choice",     # model's selection
        "is_correct",       # True/False/""
        "raw_response",     # full explanation from the model
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
                # Stable seed for deterministic judging
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

            # Write clean row to output CSV
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
