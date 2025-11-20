# Data Structure Documentation

## Overview

The evaluation data is now organized into clean, modular files for both objective (`obj`) and semi-objective (`semi-obj`) test suites.

---

## Objective Tests (`obj/data/`)

### 1. `questions.csv` (20 questions)

**Purpose:** Contains all 20 test questions  
**Columns:**

- `q_id`: Question ID (1-20)
- `domain`: Subject area (e.g., "Algorithms / CS", "Biology")
- `question`: The actual question text

**Example:**

```csv
q_id,domain,question
1,Algorithms / CS,You are given an array of n integers...
2,Probability / Statistics,You flip a fair coin 10 times...
```

---

### 2. `baseline_pairs.csv` (40 answers = 20 pairs)

**Purpose:** Simple paired format with correct and wrong baseline answers  
**Columns:**

- `q_id`: Question ID
- `answer_type`: Either `C_base` (correct) or `W_base` (wrong)
- `answer`: The answer text

**Format:** Each question has 2 consecutive rows (C_base, W_base) followed by a blank line

**Example:**

```csv
q_id,answer_type,answer
1,C_base,"Use Quickselect: choose a pivot..."
1,W_base,"Use Quicksort: sort the entire array..."

2,C_base,"The probability is (10 choose 7)..."
2,W_base,"The probability is (10 choose 6)..."

```

---

### 3. `biased_answers.csv` (220 biased answers)

**Purpose:** All wrong answers with presentation biases  
**Columns:**

- `mechanism_code`: Bias mechanism (e.g., VISU-MDWN, LENG-VERB)
- `q_id`: Question ID
- `W_bias`: The biased wrong answer

**Organization:** Sorted by mechanism (11 mechanisms × 20 questions each)

**Mechanisms:**

1. **LENG-CNCS** - Conciseness (20 answers)
2. **LENG-VERB** - Verbosity (20 answers)
3. **LEXI-LEXC** - Lexical Choice (20 answers)
4. **LEXI-RDAB** - Readability (20 answers)
5. **RSNG-CNTH** - Chain-of-Thought (20 answers)
6. **RSNG-STRC** - Structured Reasoning (20 answers)
7. **TONE-CONF** - Confident Tone (20 answers)
8. **TONE-PLTE** - Polite Tone (20 answers)
9. **VISU-LIST** - Bulleted Lists (20 answers)
10. **VISU-MDWN** - Markdown Formatting (20 answers)
11. **VISU-PARA** - Paragraph Density (20 answers)

**Example:**

```csv
mechanism_code,q_id,W_bias
LENG-CNCS,1,Sort the array and take the k-th element...
LENG-CNCS,2,About 0.7 is a reasonable probability...
```

---

## Semi-Objective Tests (`semi-obj/data/`)

### 1. `questions_semi.csv` (20 questions)

**Purpose:** Contains all 20 semi-objective questions (judgment-based)  
**Columns:**

- `q_id`: Question ID (1-20)
- `domain`: Context (Education, Workplace, Communication)
- `question`: The question text (usually "Which is better?")

**Example:**

```csv
q_id,domain,question
1,Education,"You are writing feedback on a student's short answer..."
2,Workplace,"You are choosing a response in a team chat..."
```

---

### 2. `baseline_pairs_semi.csv` (40 answers = 20 pairs)

**Purpose:** Simple paired format with good and bad baseline answers  
**Columns:**

- `q_id`: Question ID
- `answer_type`: Either `C_base` (correct/good) or `W_base` (wrong/bad)
- `answer`: The answer text

**Format:** Same paired structure as objective tests (2 rows per question + blank line)

**Example:**

```csv
q_id,answer_type,answer
1,C_base,"Your answer identifies the main idea and gives..."
1,W_base,"Good job, this is mostly right. Try a bit harder..."

```

---

### 3. `biased_answers_semi.csv` (20 biased answers)

**Purpose:** Wrong answers with presentation biases (1 per question)  
**Columns:**

- `mechanism_family`: Bias family (VISU, LENG, TONE, RSNG, LEXI)
- `mechanism_code`: Specific mechanism
- `q_id`: Question ID
- `W_BIAS`: The biased wrong answer

**Coverage:** 1 biased answer per question (20 total), covering all 11 mechanisms

**Example:**

```csv
mechanism_family,mechanism_code,q_id,W_BIAS
VISU,VISU-MDWN,1,"**Fantastic work!** Your answer clearly shows..."
LENG,LENG-VERB,4,"This function can be thought of as visiting..."
```

---

## File Counts Summary

| Test Suite         | Questions | Baseline Pairs        | Biased Answers           |
| ------------------ | --------- | --------------------- | ------------------------ |
| **Objective**      | 20        | 20 pairs (40 answers) | 220 (11 mechanisms × 20) |
| **Semi-Objective** | 20        | 20 pairs (40 answers) | 20 (1 per question)      |

---

## Legacy Files (kept for reference)

### Objective

- `bias_backup.csv` - Original bias file backup
- `bias.csv` - Original bias file (now replaced by `biased_answers.csv`)
- `eval_items.csv` - Generated evaluation dataset (440 rows)
- `judgements.csv` - LLM judge results

### Semi-Objective

- Files in parent `semi-obj/` directory are kept for reference

---

## Usage

These new files provide a clean, modular structure:

1. **questions.csv** - Pure question list
2. **baseline_pairs.csv** - Simple C/W answer pairs
3. **biased_answers.csv** - Organized by mechanism

This makes it easy to:

- Add new questions
- Update baseline answers
- Add/modify biased answers per mechanism
- Understand the dataset structure at a glance
