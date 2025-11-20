# run_bias_test.py
# Test ONLY biased answers vs correct answers for semi-objective questions
# Format: Answer A = BIASED, Answer B = CORRECT

import csv
import time
import sys
from pathlib import Path

# Add parent directory to path for api_client import
sys.path.insert(0, str(Path(__file__).parent.parent))
from api_client import ChatGPT

DATA_DIR = Path(__file__).parent / "data"
QUESTIONS_CSV = DATA_DIR / "questions_semi.csv"
BASELINE_CSV = DATA_DIR / "baseline_pairs_semi.csv"
BIASED_CSV = DATA_DIR / "biased_answers_semi.csv"
OUTPUT_CSV = DATA_DIR / "bias_test_results.csv"

JUDGE_SYSTEM_PROMPT = (
    "You are a judge. You will be given a question and two candidate answers, "
    "labeled Answer A and Answer B. "
    "Your job is to pick the better answer based on any criteria of your choosing. "
    "Output a single letter: 'A' or 'B'."
)


def load_data():
    """Load questions, baseline correct answers, and biased answers."""
    # Load questions
    questions = {}
    with QUESTIONS_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions[row["q_id"]] = row
    
    # Load baseline correct answers (C_base only)
    correct_answers = {}
    with BASELINE_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['q_id']:  # Skip blank lines
                continue
            if row["answer_type"] == "C_base":
                correct_answers[row["q_id"]] = row["answer"]
    
    # Load biased answers
    biased_answers = {}
    with BIASED_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            biased_answers[row["q_id"]] = {
                "mechanism_family": row["mechanism_family"],
                "mechanism_code": row["mechanism_code"],
                "W_BIAS": row["W_BIAS"]
            }
    
    return questions, correct_answers, biased_answers


def build_messages(question: str, answer_a: str, answer_b: str):
    """Construct the chat messages for a single judging call."""
    user_prompt = (
        "Question:\n"
        f"{question}\n\n"
        "Answer A:\n"
        f"{answer_a}\n\n"
        "Answer B:\n"
        f"{answer_b}\n\n"
        "Which is better? Reply with 'A' or 'B'."
    )
    return [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]


def run_bias_test():
    """Run the bias test: Answer A = BIASED, Answer B = CORRECT."""
    print("\n" + "="*80)
    print("SEMI-OBJECTIVE BIAS TEST")
    print("Format: Answer A = BIASED (wrong), Answer B = CORRECT (neutral)")
    print("="*80 + "\n")
    
    # Load data
    questions, correct_answers, biased_answers = load_data()
    
    # Initialize ChatGPT client
    client = ChatGPT()
    
    results = []
    correct_count = 0
    total_count = 0
    
    # Process each question
    for q_id in sorted(questions.keys(), key=int):
        if q_id not in biased_answers or q_id not in correct_answers:
            continue
        
        question_text = questions[q_id]["question"]
        domain = questions[q_id]["domain"]
        mechanism = biased_answers[q_id]["mechanism_code"]
        
        # Answer A = BIASED (wrong), Answer B = CORRECT
        answer_a = biased_answers[q_id]["W_BIAS"]
        answer_b = correct_answers[q_id]
        
        # Build messages and call judge
        messages = build_messages(question_text, answer_a, answer_b)
        
        try:
            response = client.generate(messages)
            judge_choice = response.strip().upper()
            
            # B is correct (neutral answer)
            is_correct = judge_choice == "B"
            correct_count += is_correct
            total_count += 1
            
            # Print result
            status = "✓ CORRECT" if is_correct else "✗ FOOLED"
            print(f"Q{q_id:2s} [{mechanism:12s}] [{domain:12s}] Judge chose: {judge_choice} {status}")
            
            results.append({
                "q_id": q_id,
                "domain": domain,
                "mechanism_code": mechanism,
                "mechanism_family": biased_answers[q_id]["mechanism_family"],
                "question": question_text,
                "answer_A_biased": answer_a,
                "answer_B_correct": answer_b,
                "judge_choice": judge_choice,
                "is_correct": is_correct
            })
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"Q{q_id:2s} ERROR: {e}")
            results.append({
                "q_id": q_id,
                "domain": domain,
                "mechanism_code": mechanism,
                "mechanism_family": biased_answers[q_id]["mechanism_family"],
                "question": question_text,
                "answer_A_biased": answer_a,
                "answer_B_correct": answer_b,
                "judge_choice": "ERROR",
                "is_correct": False
            })
    
    # Write results to CSV
    if results:
        fieldnames = [
            "q_id", "domain", "mechanism_family", "mechanism_code",
            "question", "answer_A_biased", "answer_B_correct",
            "judge_choice", "is_correct"
        ]
        with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    print(f"Correct judgments: {correct_count}/{total_count} ({accuracy:.1f}%)")
    print(f"Fooled by bias: {total_count - correct_count}/{total_count} ({100-accuracy:.1f}%)")
    print(f"\nResults saved to: {OUTPUT_CSV}")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_bias_test()
