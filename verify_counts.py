#!/usr/bin/env python3
import pandas as pd

# Objective
obj = pd.read_csv('obj/data/eval_items.csv')
print("=== OBJECTIVE INPUT ===")
print(f"Total input rows: {len(obj)}")
print(f"Unique q_ids: {obj['q_id'].nunique()}")
print(f"Unique mechanisms: {obj['mechanism_code'].nunique()}")
print(f"Unique conditions: {obj['condition'].nunique()}")

# Objective output
obj_out = pd.read_csv('obj/data/judgements.csv')
print(f"\nObjective output rows: {len(obj_out)}")
print(f"Unique conditions in output: {obj_out['condition'].nunique()}")
print(f"Breakdown by condition:")
print(obj_out['condition'].value_counts())

# Semi-objective input
semi = pd.read_csv('semi-obj/data/eval_items_semi.csv')
print("\n=== SEMI-OBJECTIVE INPUT ===")
print(f"Total input rows: {len(semi)}")
print(f"Unique q_ids: {semi['q_id'].nunique()}")
print(f"Unique mechanisms: {semi['mechanism_code'].nunique()}")
print(f"Unique conditions: {semi['condition'].nunique()}")

# Semi-objective output
semi_out = pd.read_csv('semi-obj/data/judgements_semi.csv')
print(f"\nSemi-objective output rows: {len(semi_out)}")
print(f"Unique conditions in output: {semi_out['condition'].nunique()}")
print(f"Breakdown by condition:")
print(semi_out['condition'].value_counts())

# Bias test
bias = pd.read_csv('semi-obj/data/bias_test_results.csv')
print(f"\nBias test output rows: {len(bias)}")

print("\n=== ACTUAL EXECUTION SUMMARY ===")
baseline_obj = len(obj_out[obj_out['condition'] == 'BASE'])
baseline_semi = len(semi_out[semi_out['condition'] == 'BASE'])
biased_obj = len(obj_out[obj_out['condition'] == 'BIAS'])
biased_semi = len(semi_out[semi_out['condition'] == 'BIAS'])
bias_test = len(bias)

print(f"1. Baseline objective: {baseline_obj}")
print(f"2. Baseline semi-objective: {baseline_semi}")
print(f"3. Biased objective: {biased_obj}")
print(f"4. Biased semi-objective: {biased_semi}")
print(f"5. Total evaluations: {baseline_obj + baseline_semi + biased_obj + biased_semi + bias_test}")

print("\n=== EXPECTED vs ACTUAL ===")
print(f"Expected total: 2880 (240 baseline + 2640 biased)")
print(f"Actual total: {baseline_obj + baseline_semi + biased_obj + biased_semi + bias_test}")
print(f"Difference: {(baseline_obj + baseline_semi + biased_obj + biased_semi + bias_test) - 2880}")
