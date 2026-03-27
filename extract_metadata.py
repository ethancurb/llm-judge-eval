#!/usr/bin/env python3
"""
Simple script to extract metadata from LLM judge evaluation results for charting/visualization.
Extracts key columns without the long text content (questions/answers/raw responses).
"""

import pandas as pd
import os

def extract_objective_metadata():
    """Extract metadata from objective evaluation results."""
    obj_file = "obj/data/judgements.csv"
    
    if not os.path.exists(obj_file):
        print(f"Warning: {obj_file} not found")
        return None
    
    print(f"Loading objective data from {obj_file}...")
    df = pd.read_csv(obj_file)
    
    # Extract metadata columns (excluding long text fields)
    metadata_columns = [
        'eval_id',
        'mechanism_family',
        'mechanism_code', 
        'mechanism_name',
        'q_id',
        'domain',
        'condition',  # BASE or BIAS
        'correct_option',  # A or B
        'judge_choice',    # A or B
        'is_correct'       # True/False
    ]
    
    metadata_df = df[metadata_columns].copy()
    
    # Add some derived columns for analysis
    metadata_df['test_type'] = 'objective'
    metadata_df['bias_present'] = metadata_df['condition'] == 'BIAS'
    metadata_df['correct_with_bias'] = (metadata_df['condition'] == 'BIAS') & metadata_df['is_correct']
    metadata_df['correct_without_bias'] = (metadata_df['condition'] == 'BASE') & metadata_df['is_correct']
    
    return metadata_df

def extract_semi_objective_metadata():
    """Extract metadata from semi-objective evaluation results."""
    semi_file = "semi-obj/data/bias_test_results.csv"
    
    if not os.path.exists(semi_file):
        print(f"Warning: {semi_file} not found")
        return None
    
    print(f"Loading semi-objective data from {semi_file}...")
    df = pd.read_csv(semi_file)
    
    # Extract metadata columns
    metadata_columns = [
        'q_id',
        'domain',
        'mechanism_family',
        'mechanism_code',
        'judge_choice',  # A or B
        'is_correct'     # True/False
    ]
    
    metadata_df = df[metadata_columns].copy()
    
    # Add columns to match objective format
    metadata_df['eval_id'] = 'q' + metadata_df['q_id'].astype(str) + '_' + metadata_df['mechanism_code'] + '_semi'
    metadata_df['mechanism_name'] = metadata_df['mechanism_code']  # Could be mapped if needed
    metadata_df['condition'] = 'BIAS'  # Semi-objective tests are bias tests
    metadata_df['correct_option'] = 'B'  # In semi-obj, B is always the correct answer
    metadata_df['test_type'] = 'semi-objective'
    metadata_df['bias_present'] = True
    metadata_df['correct_with_bias'] = metadata_df['is_correct']
    metadata_df['correct_without_bias'] = False  # No baseline in semi-obj
    
    return metadata_df

def main():
    """Extract metadata from both test types and combine."""
    
    # Extract from both test types
    obj_metadata = extract_objective_metadata()
    semi_metadata = extract_semi_objective_metadata()
    
    # Combine the datasets
    combined_data = []
    
    if obj_metadata is not None:
        combined_data.append(obj_metadata)
        print(f"Extracted {len(obj_metadata)} objective test records")
    
    if semi_metadata is not None:
        combined_data.append(semi_metadata)
        print(f"Extracted {len(semi_metadata)} semi-objective test records")
    
    if not combined_data:
        print("No data found to extract!")
        return
    
    # Combine all data
    all_metadata = pd.concat(combined_data, ignore_index=True)
    
    # Reorder columns for clarity
    column_order = [
        'eval_id',
        'test_type',
        'q_id', 
        'domain',
        'mechanism_family',
        'mechanism_code',
        'mechanism_name',
        'condition',
        'bias_present',
        'correct_option',
        'judge_choice',
        'is_correct',
        'correct_with_bias',
        'correct_without_bias'
    ]
    
    final_df = all_metadata[column_order]
    
    # Save the extracted metadata
    output_file = "extracted_metadata.csv"
    final_df.to_csv(output_file, index=False)
    
    print(f"\nMetadata extraction complete!")
    print(f"Saved {len(final_df)} total records to: {output_file}")
    
    # Print summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Total records: {len(final_df)}")
    print(f"Objective tests: {len(final_df[final_df['test_type'] == 'objective'])}")
    print(f"Semi-objective tests: {len(final_df[final_df['test_type'] == 'semi-objective'])}")
    print(f"\nBy mechanism family:")
    print(final_df['mechanism_family'].value_counts())
    print(f"\nBy domain:")
    print(final_df['domain'].value_counts())
    print(f"\nCorrect judgements:")
    print(f"- With bias: {final_df['correct_with_bias'].sum()}")
    print(f"- Without bias: {final_df['correct_without_bias'].sum()}")
    print(f"- Overall accuracy: {final_df['is_correct'].mean():.2%}")

if __name__ == "__main__":
    main()