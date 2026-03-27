#!/usr/bin/env python3
"""
Comprehensive analysis framework for LLM-as-judge bias evaluation study.

Aggregates results across objective and semi-objective question sets.
Computes accuracy metrics at multiple levels (overall, by condition, by mechanism, etc).
Generates research-friendly tables and visualizations.

KEY DEFINITIONS:
- Full Trial = 440 evaluations (220 per set: 20 questions × 11 mechanisms)
  Across both objective + semi-objective sets
- Per-Set Trial = 220 evaluations (20 questions × 11 mechanisms)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path(__file__).parent
OBJ_DIR = DATA_DIR / "obj" / "data"
SEMI_DIR = DATA_DIR / "semi-obj" / "data"

# Input files
OBJ_JUDGEMENTS_FILE = OBJ_DIR / "judgements.csv"
SEMI_JUDGEMENTS_FILE = SEMI_DIR / "judgements_semi.csv"
SEMI_BIAS_TEST_FILE = SEMI_DIR / "bias_test_results.csv"

# Output files
OUTPUT_DIR = DATA_DIR / "analysis_results"
OUTPUT_DIR.mkdir(exist_ok=True)

TABLES_DIR = OUTPUT_DIR / "tables"
TABLES_DIR.mkdir(exist_ok=True)

PLOTS_DIR = OUTPUT_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)


# ============================================================================
# DATA LOADING
# ============================================================================

def load_objective_data() -> pd.DataFrame:
    """Load and prepare objective judgements."""
    df = pd.read_csv(OBJ_JUDGEMENTS_FILE)
    df['question_type'] = 'objective'
    
    # Ensure is_correct is boolean
    df['is_correct'] = df['is_correct'].astype(bool)
    
    return df


def load_semi_objective_data() -> pd.DataFrame:
    """Load and prepare semi-objective judgements."""
    df = pd.read_csv(SEMI_JUDGEMENTS_FILE)
    df['question_type'] = 'semi_objective'
    
    # Ensure is_correct is boolean
    df['is_correct'] = df['is_correct'].astype(bool)
    
    return df


def load_bias_test_data() -> pd.DataFrame:
    """Load and prepare semi-objective bias test results."""
    df = pd.read_csv(SEMI_BIAS_TEST_FILE)
    df['question_type'] = 'semi_objective'
    df['condition'] = 'BIAS'  # Bias test is always biased condition
    df['is_correct'] = df['is_correct'].astype(bool)
    
    return df


def load_all_data() -> pd.DataFrame:
    """Load and combine all evaluation data."""
    print("Loading data...")
    
    obj = load_objective_data()
    semi = load_semi_objective_data()
    bias = load_bias_test_data()
    
    # Combine
    combined = pd.concat([obj, semi, bias], ignore_index=True)
    
    print(f"  - Objective: {len(obj)} rows")
    print(f"  - Semi-objective judgements: {len(semi)} rows")
    print(f"  - Semi-objective bias test: {len(bias)} rows")
    print(f"  - TOTAL: {len(combined)} rows")
    
    return combined


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

class JudgeEvaluationAnalyzer:
    """Comprehensive analyzer for LLM judge evaluation results."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with combined results dataframe."""
        self.df = df.copy()
        self.results = {}
        
    def analyze_overall(self) -> Dict:
        """Overall accuracy statistics."""
        total = len(self.df)
        correct = self.df['is_correct'].sum()
        accuracy = correct / total if total > 0 else 0
        
        return {
            'Total Evaluations': total,
            'Correct': correct,
            'Accuracy': accuracy,
            'Accuracy %': f"{accuracy*100:.1f}%"
        }
    
    def analyze_by_condition(self) -> pd.DataFrame:
        """Accuracy broken down by condition (BASE vs BIAS)."""
        grouped = self.df.groupby('condition').agg({
            'is_correct': ['sum', 'count', 'mean']
        }).round(3)
        
        grouped.columns = ['Correct', 'Total', 'Accuracy']
        grouped['Accuracy %'] = (grouped['Accuracy'] * 100).round(1).astype(str) + '%'
        grouped['Accuracy'] = grouped['Accuracy'].round(3)
        grouped = grouped.astype({'Correct': int, 'Total': int})
        
        return grouped
    
    def analyze_by_mechanism(self) -> pd.DataFrame:
        """Accuracy by bias mechanism."""
        grouped = self.df.groupby('mechanism_code').agg({
            'is_correct': ['sum', 'count', 'mean'],
            'mechanism_family': 'first'
        }).round(3)
        
        grouped.columns = ['Correct', 'Total', 'Accuracy', 'Family']
        grouped['Accuracy %'] = (grouped['Accuracy'] * 100).round(1).astype(str) + '%'
        grouped['Accuracy'] = grouped['Accuracy'].round(3)
        grouped = grouped.astype({'Correct': int, 'Total': int})
        grouped = grouped[['Family', 'Correct', 'Total', 'Accuracy', 'Accuracy %']]
        
        return grouped.sort_values('Accuracy', ascending=False)
    
    def analyze_by_domain(self) -> pd.DataFrame:
        """Accuracy by domain."""
        grouped = self.df.groupby('domain').agg({
            'is_correct': ['sum', 'count', 'mean']
        }).round(3)
        
        grouped.columns = ['Correct', 'Total', 'Accuracy']
        grouped['Accuracy %'] = (grouped['Accuracy'] * 100).round(1).astype(str) + '%'
        grouped['Accuracy'] = grouped['Accuracy'].round(3)
        grouped = grouped.astype({'Correct': int, 'Total': int})
        
        return grouped.sort_values('Accuracy', ascending=False)
    
    def analyze_by_question_type(self) -> pd.DataFrame:
        """Accuracy by question type (objective vs semi-objective)."""
        grouped = self.df.groupby('question_type').agg({
            'is_correct': ['sum', 'count', 'mean']
        }).round(3)
        
        grouped.columns = ['Correct', 'Total', 'Accuracy']
        grouped['Accuracy %'] = (grouped['Accuracy'] * 100).round(1).astype(str) + '%'
        grouped['Accuracy'] = grouped['Accuracy'].round(3)
        grouped = grouped.astype({'Correct': int, 'Total': int})
        
        return grouped
    
    def analyze_bias_impact(self) -> pd.DataFrame:
        """Calculate bias impact = biased_accuracy - baseline_accuracy."""
        # Filter only data that has both BASE and BIAS conditions
        df_filtered = self.df[self.df['condition'].isin(['BASE', 'BIAS'])].copy()
        
        # Group by mechanism and condition
        grouped = df_filtered.groupby(['mechanism_code', 'condition'])['is_correct'].agg(['sum', 'count']).reset_index()
        grouped['accuracy'] = grouped['sum'] / grouped['count']
        
        # Pivot to get BASE and BIAS side by side
        pivot = grouped.pivot(index='mechanism_code', columns='condition', values='accuracy')
        
        if 'BASE' in pivot.columns and 'BIAS' in pivot.columns:
            pivot['Bias Impact'] = pivot['BIAS'] - pivot['BASE']
        else:
            pivot['Bias Impact'] = np.nan
        
        result = pivot[['BASE', 'BIAS', 'Bias Impact']].copy()
        result.columns = ['Baseline Acc', 'Biased Acc', 'Bias Impact']
        result = result * 100  # Convert to percentages
        result = result.round(1)
        
        return result.sort_values('Bias Impact', ascending=True)
    
    def generate_all_reports(self):
        """Generate all analysis reports."""
        print("\nGenerating analysis reports...")
        
        # Overall
        overall = self.analyze_overall()
        print(f"  ✓ Overall: {overall['Accuracy %']}")
        
        # By condition
        by_condition = self.analyze_by_condition()
        print(f"  ✓ By condition")
        
        # By mechanism
        by_mechanism = self.analyze_by_mechanism()
        print(f"  ✓ By mechanism ({len(by_mechanism)} mechanisms)")
        
        # By domain
        by_domain = self.analyze_by_domain()
        print(f"  ✓ By domain ({len(by_domain)} domains)")
        
        # By question type
        by_question_type = self.analyze_by_question_type()
        print(f"  ✓ By question type")
        
        # Bias impact
        bias_impact = self.analyze_bias_impact()
        print(f"  ✓ Bias impact analysis")
        
        return {
            'overall': overall,
            'by_condition': by_condition,
            'by_mechanism': by_mechanism,
            'by_domain': by_domain,
            'by_question_type': by_question_type,
            'bias_impact': bias_impact
        }


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_baseline_vs_biased(df: pd.DataFrame, save_path: Path):
    """Bar chart comparing baseline vs biased accuracy."""
    grouped = df[df['condition'].isin(['BASE', 'BIAS'])].groupby('condition')['is_correct'].mean() * 100
    
    fig, ax = plt.subplots(figsize=(8, 6))
    grouped.plot(kind='bar', ax=ax, color=['#2ecc71', '#e74c3c'], alpha=0.8)
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_xlabel('Condition', fontsize=12)
    ax.set_title('LLM Judge Accuracy: Baseline vs Biased', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 105])
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    
    # Add value labels
    for i, v in enumerate(grouped):
        ax.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {save_path.name}")
    plt.close()


def plot_by_mechanism(df: pd.DataFrame, save_path: Path):
    """Bar chart of accuracy by mechanism."""
    grouped = df.groupby('mechanism_code')['is_correct'].agg(['mean', 'count'])
    grouped['mean'] = grouped['mean'] * 100
    grouped = grouped.sort_values('mean', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    grouped['mean'].plot(kind='barh', ax=ax, color='#3498db', alpha=0.8)
    ax.set_xlabel('Accuracy (%)', fontsize=12)
    ax.set_ylabel('Mechanism', fontsize=12)
    ax.set_title('LLM Judge Accuracy by Bias Mechanism', fontsize=14, fontweight='bold')
    ax.set_xlim([0, 105])
    ax.axvline(x=50, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    
    # Add value labels
    for i, (idx, v) in enumerate(grouped['mean'].items()):
        n = int(grouped.loc[idx, 'count'])
        ax.text(v + 1, i, f'{v:.1f}% (n={n})', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {save_path.name}")
    plt.close()


def plot_by_domain(df: pd.DataFrame, save_path: Path):
    """Bar chart of accuracy by domain."""
    grouped = df.groupby('domain')['is_correct'].agg(['mean', 'count'])
    grouped['mean'] = grouped['mean'] * 100
    grouped = grouped.sort_values('mean', ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    grouped['mean'].plot(kind='bar', ax=ax, color='#9b59b6', alpha=0.8)
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_xlabel('Domain', fontsize=12)
    ax.set_title('LLM Judge Accuracy by Domain', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 105])
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    
    # Add value labels
    for i, (idx, v) in enumerate(grouped['mean'].items()):
        n = int(grouped.loc[idx, 'count'])
        ax.text(i, v + 2, f'{v:.1f}%\n(n={n})', ha='center', fontsize=9)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {save_path.name}")
    plt.close()


def plot_by_question_type(df: pd.DataFrame, save_path: Path):
    """Bar chart of accuracy by question type."""
    grouped = df.groupby('question_type')['is_correct'].agg(['mean', 'count'])
    grouped['mean'] = grouped['mean'] * 100
    
    fig, ax = plt.subplots(figsize=(8, 6))
    grouped['mean'].plot(kind='bar', ax=ax, color=['#e67e22', '#1abc9c'], alpha=0.8)
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_xlabel('Question Type', fontsize=12)
    ax.set_title('LLM Judge Accuracy by Question Type', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 105])
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    
    # Add value labels
    for i, (idx, v) in enumerate(grouped['mean'].items()):
        n = int(grouped.loc[idx, 'count'])
        ax.text(i, v + 2, f'{v:.1f}%\n(n={n})', ha='center', fontsize=9)
    
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {save_path.name}")
    plt.close()


def plot_bias_impact_heatmap(df: pd.DataFrame, save_path: Path):
    """Heatmap of bias impact by mechanism and domain."""
    df_filtered = df[df['condition'].isin(['BASE', 'BIAS'])].copy()
    
    # Compute accuracy by mechanism, domain, and condition
    grouped = df_filtered.groupby(['mechanism_code', 'domain', 'condition'])['is_correct'].mean().unstack(fill_value=0)
    
    if len(grouped) > 0 and 'BASE' in grouped.columns and 'BIAS' in grouped.columns:
        grouped['impact'] = grouped['BIAS'] - grouped['BASE']
        pivot_data = grouped['impact'].unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='RdYlGn_r', center=0, 
                    cbar_kws={'label': 'Bias Impact (Biased - Baseline)'}, ax=ax)
        ax.set_title('Bias Impact by Mechanism and Domain', fontsize=14, fontweight='bold')
        ax.set_xlabel('Domain', fontsize=12)
        ax.set_ylabel('Mechanism', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {save_path.name}")
        plt.close()


def generate_all_visualizations(df: pd.DataFrame):
    """Generate all visualizations."""
    print("\nGenerating visualizations...")
    
    plot_baseline_vs_biased(df, PLOTS_DIR / "01_baseline_vs_biased.png")
    plot_by_mechanism(df, PLOTS_DIR / "02_accuracy_by_mechanism.png")
    plot_by_domain(df, PLOTS_DIR / "03_accuracy_by_domain.png")
    plot_by_question_type(df, PLOTS_DIR / "04_accuracy_by_question_type.png")
    plot_bias_impact_heatmap(df, PLOTS_DIR / "05_bias_impact_heatmap.png")


# ============================================================================
# TABLE EXPORT
# ============================================================================

def export_tables(reports: Dict, analyzer):
    """Export all analysis tables as CSV."""
    print("\nExporting tables...")
    
    # Overall summary
    overall_df = pd.DataFrame([reports['overall']])
    overall_df.to_csv(TABLES_DIR / "00_overall_summary.csv", index=False)
    print(f"  ✓ Saved: 00_overall_summary.csv")
    
    # By condition
    reports['by_condition'].to_csv(TABLES_DIR / "01_by_condition.csv")
    print(f"  ✓ Saved: 01_by_condition.csv")
    
    # By mechanism
    reports['by_mechanism'].to_csv(TABLES_DIR / "02_by_mechanism.csv")
    print(f"  ✓ Saved: 02_by_mechanism.csv")
    
    # By domain
    reports['by_domain'].to_csv(TABLES_DIR / "03_by_domain.csv")
    print(f"  ✓ Saved: 03_by_domain.csv")
    
    # By question type
    reports['by_question_type'].to_csv(TABLES_DIR / "04_by_question_type.csv")
    print(f"  ✓ Saved: 04_by_question_type.csv")
    
    # Bias impact
    reports['bias_impact'].to_csv(TABLES_DIR / "05_bias_impact.csv")
    print(f"  ✓ Saved: 05_bias_impact.csv")
    
    # Trial analysis
    trial_analysis = analyze_trials(analyzer.df)
    trial_analysis.to_csv(TABLES_DIR / "06_trial_analysis.csv")
    print(f"  ✓ Saved: 06_trial_analysis.csv")


# ============================================================================
# TRIAL ANALYSIS
# ============================================================================

def analyze_trials(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze results by trial definition.
    
    Full Trial = 440 evaluations (220 per set × 2 sets)
    Per-Set Trial = 220 evaluations (20 questions × 11 mechanisms)
    """
    
    # Calculate number of complete trials based on data volume
    obj_trials = len(df[df['question_type'] == 'objective']) // 220
    semi_trials = len(df[df['question_type'] == 'semi_objective']) // 220
    
    trial_data = {
        'Trial Type': [
            'Full Trial (Objective + Semi-Objective)',
            'Per-Set Trial (Objective)',
            'Per-Set Trial (Semi-Objective)'
        ],
        'Expected Evaluations': [440, 220, 220],
        'Actual Evaluations': [
            len(df),
            len(df[df['question_type'] == 'objective']),
            len(df[df['question_type'] == 'semi_objective'])
        ]
    }
    
    trial_df = pd.DataFrame(trial_data)
    
    # Calculate accuracy for each
    accuracies = [
        (df['is_correct'].sum() / len(df)) * 100,
        (df[df['question_type'] == 'objective']['is_correct'].sum() / 
         len(df[df['question_type'] == 'objective']) * 100),
        (df[df['question_type'] == 'semi_objective']['is_correct'].sum() / 
         len(df[df['question_type'] == 'semi_objective']) * 100)
    ]
    
    trial_df['Accuracy %'] = [f"{acc:.1f}%" for acc in accuracies]
    trial_df['Correct Evaluations'] = [
        df['is_correct'].sum(),
        df[df['question_type'] == 'objective']['is_correct'].sum(),
        df[df['question_type'] == 'semi_objective']['is_correct'].sum()
    ]
    
    return trial_df


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run complete analysis pipeline."""
    print("\n" + "="*80)
    print("LLM JUDGE EVALUATION ANALYSIS")
    print("="*80)
    
    # Load data
    df = load_all_data()
    
    # Run analysis
    analyzer = JudgeEvaluationAnalyzer(df)
    reports = analyzer.generate_all_reports()
    
    # Export tables
    export_tables(reports, analyzer)
    
    # Generate visualizations
    generate_all_visualizations(df)
    
    # Print summary to console
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print(f"  - Tables: {TABLES_DIR}")
    print(f"  - Plots: {PLOTS_DIR}")
    
    print("\n=== KEY FINDINGS ===")
    print(f"Overall Accuracy: {reports['overall']['Accuracy %']}")
    print(f"\nBy Condition:")
    print(reports['by_condition'][['Correct', 'Total', 'Accuracy %']])
    
    print(f"\nBias Impact (Top 5 Mechanisms):")
    print(reports['bias_impact'].head())
    
    print(f"\nBy Question Type:")
    print(reports['by_question_type'][['Correct', 'Total', 'Accuracy %']])


if __name__ == "__main__":
    main()
