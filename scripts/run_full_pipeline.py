"""
Complete Pipeline Runner
Executes the entire feature prioritization and A/B testing workflow
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import *
from prioritization import RICEFramework, create_sample_features
from ab_test_simulator import ABTestSimulator
from visualization import Visualizer
import pandas as pd


def main():
    """
    Run complete pipeline
    """
    print("=" * 80)
    print(" FEATURE PRIORITIZATION FRAMEWORK - COMPLETE PIPELINE")
    print("=" * 80)
    print()
    
    # Step 1: Feature Prioritization
    print("STEP 1: FEATURE PRIORITIZATION")
    print("-" * 80)
    
    features_df = create_sample_features()
    print(f"✅ Created {len(features_df)} feature ideas\n")
    
    rice = RICEFramework(features_df)
    results = rice.prioritize_features()
    
    report = rice.generate_summary_report()
    print(report)
    
    # Save RICE results
    features_df.to_csv(RAW_DATA_DIR / 'feature_ideas.csv', index=False)
    results.to_csv(PROCESSED_DATA_DIR / 'rice_scores.csv', index=False)
    print(f"💾 RICE scores saved\n")
    
    # Step 2: A/B Test Simulation
    print("\nSTEP 2: A/B TEST SIMULATION")
    print("-" * 80)
    
    top_feature = results.iloc[0]
    simulator = ABTestSimulator(
        feature_name=top_feature['feature_name'],
        expected_lift=18,
        test_duration_days=14
    )
    
    ab_data = simulator.run_simulation(
        n_users_per_variant=10000,
        baseline_conversion_rate=0.12
    )
    
    ab_results = simulator.analyze_results(ab_data)
    ab_report = simulator.generate_report(ab_results)
    print(ab_report)
    
    # Save A/B test results
    ab_data.to_csv(SYNTHETIC_DATA_DIR / 'user_behavior.csv', index=False)
    pd.DataFrame([ab_results]).to_csv(PROCESSED_DATA_DIR / 'ab_test_results.csv', index=False)
    print(f"💾 A/B test data saved\n")
    
    # Step 3: Generate Visualizations
    print("\nSTEP 3: GENERATING VISUALIZATIONS")
    print("-" * 80)
    
    viz = Visualizer()
    
    print("Creating RICE visualizations...")
    viz.plot_rice_scores(results, top_n=10)
    viz.plot_rice_breakdown(results, top_feature['feature_name'])
    viz.plot_category_distribution(results)
    viz.plot_effort_vs_impact(results)
    
    print("\nCreating A/B test visualizations...")
    viz.plot_ab_test_funnel(ab_data)
    viz.plot_ab_test_results(ab_data)
    
    print("\nCreating executive dashboard...")
    viz.create_executive_dashboard(results, ab_results)
    
    # Step 4: Generate Final Report
    print("\nSTEP 4: GENERATING FINAL REPORT")
    print("-" * 80)
    
    final_report = generate_final_report(results, ab_results, top_feature)
    
    report_path = REPORTS_DIR / 'final_prioritization_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:  # <--- Added encoding='utf-8'
        f.write(final_report)
    
    print(f"💾 Final report saved to: {report_path}\n")
    
    # Summary
    print("\n" + "=" * 80)
    print(" PIPELINE EXECUTION COMPLETE!")
    print("=" * 80)
    print(f"\n📁 All outputs saved to: {OUTPUT_DIR}")
    print(f"   - Figures: {FIGURES_DIR}")
    print(f"   - Reports: {REPORTS_DIR}")
    print(f"   - Data: {PROCESSED_DATA_DIR}")
    print("\n✅ Project execution successful!\n")


def generate_final_report(rice_results: pd.DataFrame, 
                         ab_results: dict,
                         top_feature: pd.Series) -> str:
    """
    Generate comprehensive final report
    """
    report = "=" * 80 + "\n"
    report += "FEATURE PRIORITIZATION & A/B TEST - FINAL REPORT\n"
    report += "=" * 80 + "\n\n"
    
    report += "PROJECT OVERVIEW:\n"
    report += "-" * 80 + "\n"
    report += f"Business Context: Food Delivery Platform\n"
    report += f"Monthly Active Users: {MONTHLY_ACTIVE_USERS:,}\n"
    report += f"Average Order Value: ₹{AVERAGE_ORDER_VALUE}\n"
    report += f"Features Evaluated: {len(rice_results)}\n"
    report += f"Date: {pd.Timestamp.now().strftime('%B %d, %Y')}\n\n"
    
    report += "EXECUTIVE SUMMARY:\n"
    report += "-" * 80 + "\n"
    report += f"Top Recommended Feature: {top_feature['feature_name']}\n"
    report += f"RICE Score: {top_feature['rice_score']:.0f}\n"
    report += f"Expected Impact: {top_feature['impact_level']}\n"
    report += f"Implementation Effort: {top_feature['effort_months']} person-months\n"
    report += f"Confidence Level: {top_feature['confidence_level']}\n\n"
    
    if ab_results['is_significant']:
        report += f"A/B Test Validation: ✅ SUCCESSFUL\n"
        report += f"  - Conversion Lift: {ab_results['relative_lift_pct']:.2f}%\n"
        report += f"  - Statistical Significance: p < {AB_TEST_CONFIG['significance_level']}\n"
        report += f"  - Projected Annual Revenue: ₹{abs(ab_results['revenue_lift'] * 365 / ab_results['test_duration_days'] / 1000000):.2f}M\n\n"
    
    report += "TOP 3 PRIORITIZED FEATURES:\n"
    report += "-" * 80 + "\n"
    for i, (_, feature) in enumerate(rice_results.head(3).iterrows(), 1):
        report += f"{i}. {feature['feature_name']}\n"
        report += f"   RICE Score: {feature['rice_score']:.0f}\n"
        report += f"   Category: {feature['category']}\n"
        report += f"   Reach: {feature['reach_percentage']:.0f}% of users\n"
        report += f"   Description: {feature['description']}\n\n"
    
    report += "RECOMMENDATION:\n"
    report += "-" * 80 + "\n"
    report += f"SHIP '{top_feature['feature_name']}' immediately based on:\n"
    report += f"  1. Highest RICE score among all features\n"
    report += f"  2. Validated through statistically significant A/B test\n"
    report += f"  3. Clear positive impact on business metrics\n"
    report += f"  4. Reasonable implementation effort\n\n"
    
    report += "NEXT STEPS:\n"
    report += "-" * 80 + "\n"
    report += f"  1. Allocate {top_feature['effort_months']} person-months for development\n"
    report += f"  2. Begin technical design and PRD finalization\n"
    report += f"  3. Plan phased rollout with monitoring dashboard\n"
    report += f"  4. Prepare features #2 and #3 for Q2 roadmap\n\n"
    
    report += "=" * 80 + "\n"
    
    return report


if __name__ == "__main__":
    main()
