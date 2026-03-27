# LLM Judge Evaluation Analysis Results

**Generated**: March 27, 2026  
**Total Evaluations**: 500 (440 objective + 60 semi-objective)  
**Overall Accuracy**: 95.2%

---

## Executive Summary

This analysis evaluates how LLM judges (GPT-4.1-nano) perform when assessing answers under baseline and biased conditions across 11 bias mechanisms, 20 questions per mechanism, and multiple domains.

### Key Findings

- **Overall Accuracy**: 95.2% across all 500 evaluations
- **Baseline Accuracy**: 94.6% (227/240 correct)
- **Biased Accuracy**: 95.8% (249/260 correct)
- **Bias Impact**: +1.2% (surprisingly, the model performs slightly *better* under biased conditions)

### Trial Definitions

Per the experimental design:
- **Full Trial** = 440 evaluations (220 questions × 11 mechanisms across 2 question sets)
- **Per-Set Trial** = 220 evaluations (20 questions × 11 mechanisms per question type)

Your current data:
- **Objective set**: 440 evaluations (complete)
- **Semi-objective set**: 60 evaluations (40 judgments + 20 bias tests)
- **Total**: 500 evaluations across both sets

---

## Results Files

### Tables (`analysis_results/tables/`)

1. **00_overall_summary.csv**
   - Overall accuracy, total evaluations, correct count
   - Summary statistics for the entire trial

2. **01_by_condition.csv**
   - Breakdown by condition: BASE (neutral) vs BIAS (biased)
   - Shows if judge performed differently under biased conditions

3. **02_by_mechanism.csv**
   - Accuracy for each of the 11 bias mechanisms
   - Identifies which mechanisms most affect judge behavior
   - Includes mechanism family grouping

4. **03_by_domain.csv**
   - Accuracy broken down by domain (e.g., Education, Workplace, Communication)
   - Shows if certain domains are more susceptible to bias

5. **04_by_question_type.csv**
   - Objective vs Semi-objective question type performance
   - Compares judge performance across question types

6. **05_bias_impact.csv**
   - Bias impact = Biased Accuracy - Baseline Accuracy
   - Sorted by impact (negative = judge more fooled by bias)
   - Shows which mechanisms most successfully bias the judge

7. **06_trial_analysis.csv**
   - Trial-level summary (Full Trial + Per-Set breakdowns)
   - Validates trial definitions and evaluation counts

### Visualizations (`analysis_results/plots/`)

1. **01_baseline_vs_biased.png**
   - Bar chart comparing baseline vs biased accuracy
   - Shows overall effect of bias on judge performance

2. **02_accuracy_by_mechanism.png**
   - Horizontal bar chart of accuracy for each bias mechanism
   - Ranked by performance
   - Includes sample sizes (n) for each mechanism

3. **03_accuracy_by_domain.png**
   - Bar chart of accuracy by domain
   - Shows which domains the judge handles best/worst

4. **04_accuracy_by_question_type.png**
   - Bar chart comparing objective vs semi-objective performance
   - Shows if question type affects judge robustness

5. **05_bias_impact_heatmap.png**
   - Heatmap showing bias impact across mechanism × domain combinations
   - Red = more negative impact (judge more fooled), Green = less impact
   - Identifies particularly vulnerable combinations

---

## Interpretation Guide

### Accuracy Metrics

- **Accuracy %**: (Correct / Total) × 100
- **Bias Impact**: Biased Accuracy - Baseline Accuracy
  - Negative values = bias successfully fools judge
  - Positive values = judge resists bias or performs better
  - Values close to 0 = bias has minimal effect

### What the Numbers Mean

- **95.2% overall**: The judge correctly selected the better answer in 476 of 500 cases
- **+1.2% bias impact**: Counterintuitively, the judge performed slightly better when answers were biased
  - This may indicate the biases are complementary to judge preferences
  - Or that baseline answers are inherently trickier to compare

### Mechanism Analysis

Mechanisms are ranked by bias impact:
- **Most impactful** (most negative): TONE-PLTE (-8.0%), RSNG-STRC (-3.8%)
- **Least impactful** (closest to 0): LENG-VERB (+0.4%), VISU-LIST (+0.4%)

Lower impact suggests these mechanisms less effectively bias GPT-4.1-nano's judgment.

---

## Recommendations for Thesis/Research

### For Reporting

1. **Start with trial-level statistics** (Table 6) to establish experimental scope
2. **Show bias impact as primary finding** (Table 5) - most interesting for readers
3. **Use heatmap** (Plot 5) to show where bias is most effective
4. **Include accuracy breakdowns by mechanism** (Plot 2) for detailed analysis

### Questions to Address

- Why does the model perform *better* under bias overall? 
- Are the baseline answers actually harder to compare?
- Which mechanisms are most reliably effective at biasing?
- Does domain matter? (Education vs Workplace vs Communication)

### Next Steps

Consider:
- Running additional trials with different models (e.g., GPT-4, Claude)
- Testing with larger question sets
- Analyzing which *types* of bias (TONE, RSNG, LEXI, etc.) are most effective
- Examining the actual answers selected to understand judge reasoning

---

## Technical Details

### Data Sources

- **Objective judgements**: `obj/data/judgements.csv` (440 rows)
- **Semi-objective judgements**: `semi-obj/data/judgements_semi.csv` (40 rows)
- **Semi-objective bias test**: `semi-obj/data/bias_test_results.csv` (20 rows)

### Analysis Script

Run the analysis at any time with:
```bash
python analyze_results.py
```

The script:
- Loads all judgment data
- Computes accuracy metrics at multiple levels
- Generates publication-ready tables and charts
- Exports results to `analysis_results/` directory

### Extending the Analysis

The analysis framework is modular. To add new metrics:

1. Add method to `JudgeEvaluationAnalyzer` class
2. Call from `generate_all_reports()`
3. Export in `export_tables()`
4. Visualize if appropriate

---

## Files Structure

```
llm-judge-eval/
├── analyze_results.py              # Main analysis script (run this!)
├── analysis_results/
│   ├── tables/
│   │   ├── 00_overall_summary.csv
│   │   ├── 01_by_condition.csv
│   │   ├── 02_by_mechanism.csv
│   │   ├── 03_by_domain.csv
│   │   ├── 04_by_question_type.csv
│   │   ├── 05_bias_impact.csv
│   │   └── 06_trial_analysis.csv
│   └── plots/
│       ├── 01_baseline_vs_biased.png
│       ├── 02_accuracy_by_mechanism.png
│       ├── 03_accuracy_by_domain.png
│       ├── 04_accuracy_by_question_type.png
│       └── 05_bias_impact_heatmap.png
├── obj/data/
│   ├── judgements.csv
│   └── ...
└── semi-obj/data/
    ├── judgements_semi.csv
    ├── bias_test_results.csv
    └── ...
```

---

## Questions?

For more detail:
- Tables use standard pandas format (can open in Excel)
- Plots are high-resolution PNGs (300 DPI, suitable for publication)
- All metrics computed with `is_correct` boolean from judge output
- "Correct" determined by comparing `judge_choice` to `correct_option`

---

**Note**: This analysis preserves the critical definition of trial sizes (440 full, 220 per-set) and structures output for research/thesis presentation. All tables include necessary metadata for interpretation.
