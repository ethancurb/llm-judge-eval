# Evaluation Count Verification Report

## ACTUAL EVALUATION COUNTS EXECUTED

### Data Files Analysis

**Output Data Files:**

- `obj/data/judgements.csv`: 1,272 data rows + 1 header = 1,273 total lines
- `semi-obj/data/judgements_semi.csv`: 103 data rows + 1 header = 104 total lines
- `semi-obj/data/bias_test_results.csv`: 28 data rows + 1 header = 29 total lines

### Breakdown by Condition

**Objective Set:**

- Baseline (BASE): 220 evaluations
- Biased (BIAS): 220 evaluations
- **Subtotal: 440 evaluations**

**Semi-Objective Set - Judgements:**

- Baseline (BASE): 20 evaluations
- Biased (BIAS): 20 evaluations
- **Subtotal: 40 evaluations**

**Semi-Objective Set - Bias Test:**

- Biased only: 28 evaluations
- **Subtotal: 28 evaluations**

### ACTUAL TOTAL COUNTS

| Category                              | Count   |
| ------------------------------------- | ------- |
| 1. Baseline Objective                 | 220     |
| 2. Baseline Semi-Objective            | 20      |
| 3. Biased Objective                   | 220     |
| 4. Biased Semi-Objective (judgements) | 20      |
| 5. Biased Semi-Objective (bias test)  | 28      |
| **TOTAL EVALUATIONS**                 | **508** |

---

## COMPARISON: EXPECTED vs ACTUAL

### Your Intended Experiment Structure

```
20 objective questions × 6 repetitions (different answer orders) = 120
20 semi-objective questions × 6 repetitions = 120
Baseline total: 240 evaluations

20 objective questions × 11 mechanisms × 6 repetitions = 1,320
20 semi-objective questions × 11 mechanisms × 6 repetitions = 1,320
Biased total: 2,640 evaluations

TOTAL EXPECTED: 2,880 evaluations
```

### What Actually Happened

```
Baseline: 240 evaluations (220 obj + 20 semi) ✓ CORRECT
Biased: 268 evaluations (220 obj + 20 semi judgements + 28 bias test)
TOTAL ACTUAL: 508 evaluations

SHORTFALL: 2,880 - 508 = 2,372 evaluations (82% incomplete)
```

---

## CRITICAL FINDINGS: ANSWER ORDER VARIATIONS NOT IMPLEMENTED

### What Was Not Done

**The answer order variations were NOT implemented:**

- ❌ No "2 runs with manipulated answer first (position A)"
- ❌ No "2 runs with manipulated answer second (position B)"
- ❌ No "2 runs with randomized order"

**Evidence:**

1. The evaluation scripts only loop through input rows **once** per row
2. No mechanism to create 6 variants per question
3. The code does not re-shuffle or reorder answers
4. Only one seed value used per evaluation (`seed_value = i`)

### What Was Actually Implemented

**Single Pass Through Data:**

```python
for i, row in enumerate(rows, start=1):
    # ...
    raw_response = model.generate(messages, seed=seed_value)
    # Only called ONCE per row
```

The code read input CSV files with pre-generated question-answer pairs and evaluated each exactly ONCE. No repetitions or answer-order variations.

---

## EXPECTED vs ACTUAL EVALUATION STRUCTURE

### Expected (Per Your Spec)

```
Objective: 20 questions × 11 mechanisms × 2 conditions × 6 reps = 2,640
Semi-obj:  20 questions × 11 mechanisms × 2 conditions × 6 reps = 2,640
TOTAL: 5,280 evaluations with full answer-order variability
```

### Actual (What the Code Did)

```
Objective: 220 evaluations (20 q × 11 mech baseline ONLY)
           220 evaluations (20 q × 11 mech biased ONLY)
           = 440 evaluations, no repetitions

Semi-obj: 20 evaluations (baseline)
          20 evaluations (biased from judgements_semi.csv)
          28 evaluations (biased from bias_test_results.csv)
          = 68 evaluations, no repetitions

TOTAL: 508 evaluations with NO answer-order variations
```

---

## WHY THE DISCREPANCY

### Root Cause: Input Data Structure

The code was **controlled by the input CSV files** it received:

1. **obj/data/eval_items.csv** - only had the pre-prepared pairs, not 6 variants per question
2. **semi-obj/data/eval_items_semi.csv** - only had limited pairs
3. The scripts just looped through and evaluated each row once

### The Code Path

```
eval_items.csv (pre-created pairs)
    → run_evals.py reads each row
    → generates one evaluation per row
    → writes to judgements.csv
```

There was **no loop to create the 6 answer-order variations** within the scripts.

---

## What Would Be Needed for Full Experiment

To achieve the intended 2,880 (or 5,280 with your 6x multiplier) evaluations:

1. **Generate 6 variants per question pair** in the input data:
   - Variant 1: [Correct, Biased]
   - Variant 2: [Biased, Correct]
   - Variants 3-4: Same with different random seeds
   - Variants 5-6: Fully randomized order

2. **Modify the evaluation scripts** to handle repetitions:

   ```python
   for question_id in range(1, 21):
       for mechanism_id in range(1, 12):
           for condition in ['BASE', 'BIAS']:
               for rep in range(1, 7):
                   # Generate this variant's answer order
                   # Run evaluation
                   # Log result
   ```

3. **Track answer positions** in output:
   - `position_of_correct`: 'first' or 'second'
   - `position_of_biased`: 'first' or 'second'
   - `order_type`: 'natural', 'reversed', 'random'

---

## Summary

| Aspect                  | Specification  | Actual         | Status                 |
| ----------------------- | -------------- | -------------- | ---------------------- |
| Total Evaluations       | 2,880          | 508            | ❌ 82% incomplete      |
| Baseline Total          | 240            | 240            | ✅ Correct             |
| Biased Total            | 2,640          | 268            | ❌ 90% incomplete      |
| Answer Order Variations | 6 per question | 1 per question | ❌ Not implemented     |
| Baseline Objective      | 120            | 220            | ⚠️ Over-represented    |
| Baseline Semi-Objective | 120            | 20             | ✅ Close               |
| Biased Objective        | 1,320          | 220            | ❌ Severely incomplete |
| Biased Semi-Objective   | 1,320          | 48             | ❌ Severely incomplete |

**Conclusion:** The code executed a **single-pass evaluation** of all question-mechanism pairs without the intended 6x repetitions and answer-order variations. The data you analyzed (95.2% accuracy) is based on 508 evaluations, not the intended 2,880+.
