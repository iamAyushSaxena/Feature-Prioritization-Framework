"""
A/B Test Simulator
Generates synthetic user behavior data and simulates A/B test results
"""

from os import name
import pandas as pd
import numpy as np
from typing import Dict, Tuple
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
from config import *


class ABTestSimulator:
    """
    Simulates A/B test for feature validation
    """
    
    def __init__(self, feature_name: str, expected_lift: float, 
                 test_duration_days: int = 14):
        """
        Initialize A/B test simulator
        
        Args:
            feature_name: Name of feature being tested
            expected_lift: Expected improvement percentage (e.g., 18 for 18%)
            test_duration_days: Duration of test in days
        """
        self.feature_name = feature_name
        self.expected_lift = expected_lift / 100  # Convert to decimal
        self.test_duration_days = test_duration_days
        self.control_data = None
        self.treatment_data = None
        
    def calculate_sample_size(self, baseline_rate: float, 
                            mde: float, alpha: float = 0.05, 
                            power: float = 0.8) -> int:
        """
        Calculate required sample size for A/B test
        
        Args:
            baseline_rate: Current conversion rate (e.g., 0.10 for 10%)
            mde: Minimum detectable effect (e.g., 0.05 for 5% relative lift)
            alpha: Significance level (default 0.05 for 95% confidence)
            power: Statistical power (default 0.8)
            
        Returns:
            Required sample size per variant
        """
        # Effect size (Cohen's h)
        p1 = baseline_rate
        p2 = baseline_rate * (1 + mde)
        
        effect_size = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        # Sample size calculation
        n = ((z_alpha + z_beta) / effect_size) ** 2
        
        return int(np.ceil(n))
    
    def generate_user_behavior(self, n_users: int, conversion_rate: float, 
                              is_treatment: bool = False) -> pd.DataFrame:
        """
        Generate synthetic user behavior data
        
        Args:
            n_users: Number of users in variant
            conversion_rate: Base conversion rate
            is_treatment: Whether this is treatment group
            
        Returns:
            DataFrame with user behavior
        """
        # User IDs
        user_ids = [f"user_{i:06d}" for i in range(n_users)]
        
        # Variant assignment
        variant = 'treatment' if is_treatment else 'control'
        
        # Generate conversions based on rate
        conversions = np.random.binomial(1, conversion_rate, n_users)
        
        # Generate order values (only for converted users)
        order_values = np.where(
            conversions == 1,
            np.random.normal(AVERAGE_ORDER_VALUE, AVERAGE_ORDER_VALUE * 0.3, n_users),
            0
        )
        order_values = np.maximum(order_values, 0)  # No negative orders
        
        # Generate session data
        sessions = np.random.poisson(3, n_users)  # Average 3 sessions
        time_on_app = np.random.exponential(5, n_users)  # Average 5 minutes
        
        # Generate timestamps (spread over test duration)
        start_date = pd.Timestamp.now() - pd.Timedelta(days=self.test_duration_days)
        timestamps = [
            start_date + pd.Timedelta(days=np.random.uniform(0, self.test_duration_days))
            for _ in range(n_users)
        ]
        
        df = pd.DataFrame({
            'user_id': user_ids,
            'variant': variant,
            'timestamp': timestamps,
            'converted': conversions,
            'order_value': order_values,
            'sessions': sessions,
            'time_on_app_min': time_on_app
        })
        
        return df
    
    def run_simulation(self, n_users_per_variant: int = 10000, 
                      baseline_conversion_rate: float = 0.12) -> pd.DataFrame:
        """
        Run complete A/B test simulation
        
        Args:
            n_users_per_variant: Number of users per variant
            baseline_conversion_rate: Current conversion rate
            
        Returns:
            Combined DataFrame with control and treatment data
        """
        print(f"\n🧪 Simulating A/B Test for: {self.feature_name}")
        print(f"   Expected Lift: {self.expected_lift*100:.1f}%")
        print(f"   Test Duration: {self.test_duration_days} days")
        print(f"   Users per Variant: {n_users_per_variant:,}\n")
        
        # Calculate treatment conversion rate
        treatment_conversion_rate = baseline_conversion_rate * (1 + self.expected_lift)
        
        # Generate control group data
        print("   Generating control group data...")
        self.control_data = self.generate_user_behavior(
            n_users_per_variant, 
            baseline_conversion_rate, 
            is_treatment=False
        )
        
        # Generate treatment group data
        print("   Generating treatment group data...")
        self.treatment_data = self.generate_user_behavior(
            n_users_per_variant,
            treatment_conversion_rate,
            is_treatment=True
        )
        
        # Combine data
        combined_data = pd.concat([self.control_data, self.treatment_data], 
                                 ignore_index=True)
        
        print("   ✅ Simulation complete!\n")
        
        return combined_data
    
    def analyze_results(self, data: pd.DataFrame) -> Dict:
        """
        Perform statistical analysis on A/B test results
        
        Args:
            data: Combined control and treatment data
            
        Returns:
            Dictionary with analysis results
        """
        control = data[data['variant'] == 'control']
        treatment = data[data['variant'] == 'treatment']
        
        # Conversion metrics
        control_conversions = control['converted'].sum()
        treatment_conversions = treatment['converted'].sum()
        
        control_rate = control['converted'].mean()
        treatment_rate = treatment['converted'].mean()
        
        # Lift calculation
        absolute_lift = treatment_rate - control_rate
        relative_lift = (absolute_lift / control_rate) * 100
        
        # Revenue metrics
        control_revenue = control['order_value'].sum()
        treatment_revenue = treatment['order_value'].sum()
        
        control_arpu = control_revenue / len(control)
        treatment_arpu = treatment_revenue / len(treatment)
        
        # Statistical significance (Chi-square test)
        contingency_table = np.array([
            [control_conversions, len(control) - control_conversions],
            [treatment_conversions, len(treatment) - treatment_conversions]
        ])
        
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Z-test for proportions
        z_stat, z_pvalue = proportions_ztest(
            [treatment_conversions, control_conversions],
            [len(treatment), len(control)]
        )
        
        # Confidence interval for lift
        se = np.sqrt(
            (control_rate * (1 - control_rate) / len(control)) +
            (treatment_rate * (1 - treatment_rate) / len(treatment))
        )
        
        ci_lower = absolute_lift - 1.96 * se
        ci_upper = absolute_lift + 1.96 * se
        
        # Statistical power (post-hoc)
        effect_size = 2 * (np.arcsin(np.sqrt(treatment_rate)) - 
                          np.arcsin(np.sqrt(control_rate)))
        power = stats.norm.cdf(
            abs(effect_size) * np.sqrt(len(control)/2) - 
            stats.norm.ppf(1 - AB_TEST_CONFIG['significance_level']/2)
        )
        
        results = {
            'feature_name': self.feature_name,
            'test_duration_days': self.test_duration_days,
            'control_size': len(control),
            'treatment_size': len(treatment),
            'control_conversions': control_conversions,
            'treatment_conversions': treatment_conversions,
            'control_rate': control_rate,
            'treatment_rate': treatment_rate,
            'absolute_lift': absolute_lift,
            'relative_lift_pct': relative_lift,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'p_value': p_value,
            'z_statistic': z_stat,
            'is_significant': p_value < AB_TEST_CONFIG['significance_level'],
            'statistical_power': power,
            'control_revenue': control_revenue,
            'treatment_revenue': treatment_revenue,
            'control_arpu': control_arpu,
            'treatment_arpu': treatment_arpu,
            'revenue_lift': treatment_revenue - control_revenue,
            'chi_square': chi2
        }
        
        return results
    
    def generate_report(self, analysis_results: Dict) -> str:
        """
        Generate formatted A/B test report
        
        Args:
            analysis_results: Results from analyze_results()
            
        Returns:
            Formatted report string
        """
        r = analysis_results
        
        report = "=" * 80 + "\n"
        report += f"A/B TEST RESULTS: {r['feature_name']}\n"
        report += "=" * 80 + "\n\n"
        
        report += "TEST CONFIGURATION:\n"
        report += f"  Duration: {r['test_duration_days']} days\n"
        report += f"  Control Group: {r['control_size']:,} users\n"
        report += f"  Treatment Group: {r['treatment_size']:,} users\n"
        report += f"  Significance Level: {AB_TEST_CONFIG['significance_level']*100:.0f}%\n\n"
        
        report += "CONVERSION RESULTS:\n"
        report += f"  Control Rate: {r['control_rate']*100:.2f}% ({r['control_conversions']:,} conversions)\n"
        report += f"  Treatment Rate: {r['treatment_rate']*100:.2f}% ({r['treatment_conversions']:,} conversions)\n"
        report += f"  Absolute Lift: {r['absolute_lift']*100:.2f} percentage points\n"
        report += f"  Relative Lift: {r['relative_lift_pct']:.2f}%\n"
        report += f"  95% CI: [{r['ci_lower']*100:.2f}%, {r['ci_upper']*100:.2f}%]\n\n"
        report += "STATISTICAL ANALYSIS:\n"
        report += f"  P-value: {r['p_value']:.6f}\n"
        report += f"  Z-statistic: {r['z_statistic']:.4f}\n"
        report += f"  Chi-square: {r['chi_square']:.4f}\n"
        report += f"  Statistical Power: {r['statistical_power']*100:.1f}%\n"
        
        if r['is_significant']:
            report += f"  ✅ RESULT: STATISTICALLY SIGNIFICANT (p < {AB_TEST_CONFIG['significance_level']})\n\n"
        else:
            report += f"  ❌ RESULT: NOT STATISTICALLY SIGNIFICANT (p >= {AB_TEST_CONFIG['significance_level']})\n\n"
        
        report += "REVENUE IMPACT:\n"
        report += f"  Control Revenue: ₹{r['control_revenue']:,.0f}\n"
        report += f"  Treatment Revenue: ₹{r['treatment_revenue']:,.0f}\n"
        report += f"  Revenue Lift: ₹{r['revenue_lift']:,.0f}\n"
        report += f"  Control ARPU: ₹{r['control_arpu']:.2f}\n"
        report += f"  Treatment ARPU: ₹{r['treatment_arpu']:.2f}\n\n"
        
        # Annualized projection
        daily_users = MONTHLY_ACTIVE_USERS / 30
        test_users = r['treatment_size']
        scale_factor = daily_users / (test_users / r['test_duration_days'])
        
        daily_lift = r['revenue_lift'] / r['test_duration_days']
        monthly_lift = daily_lift * 30 * scale_factor
        annual_lift = monthly_lift * 12
        
        report += "PROJECTED BUSINESS IMPACT (if rolled out to 100%):\n"
        report += f"  Monthly Revenue Lift: ₹{monthly_lift:,.0f}\n"
        report += f"  Annual Revenue Lift: ₹{annual_lift:,.0f}\n\n"
        
        report += "RECOMMENDATION:\n"
        if r['is_significant'] and r['relative_lift_pct'] > 5:
            report += "  ✅ SHIP IT - Feature shows strong, significant positive impact\n"
        elif r['is_significant'] and r['relative_lift_pct'] > 0:
            report += "  ⚠️  CONSIDER SHIPPING - Significant but modest gains\n"
        elif not r['is_significant'] and r['relative_lift_pct'] > 10:
            report += "  🔄 EXTEND TEST - Large lift but not yet significant, needs more data\n"
        else:
            report += "  ❌ DO NOT SHIP - No significant improvement detected\n"
        
        report += "\n" + "=" * 80 + "\n"
        
        return report
    
    if name == "main":
        print("🧪 Running A/B Test Simulation...\n")
        # Simulate for Smart Reorder feature
        simulator = ABTestSimulator(
            feature_name="Smart Reorder",
            expected_lift=18,  # 18% lift
            test_duration_days=14
        )

        # Run simulation
        data = simulator.run_simulation(
            n_users_per_variant=10000,
            baseline_conversion_rate=0.12
        )

        # Analyze results
        results = simulator.analyze_results(data)

        # Generate report
        report = simulator.generate_report(results)
        print(report)

        # Save data
        data.to_csv(SYNTHETIC_DATA_DIR / 'user_behavior.csv', index=False)

        results_df = pd.DataFrame([results])
        results_df.to_csv(PROCESSED_DATA_DIR / 'ab_test_results.csv', index=False)

        print(f"💾 Data saved to {SYNTHETIC_DATA_DIR / 'user_behavior.csv'}")
        print(f"💾 Results saved to {PROCESSED_DATA_DIR / 'ab_test_results.csv'}")