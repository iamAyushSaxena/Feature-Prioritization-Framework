"""
Statistical Analysis Module
Advanced statistical tests and power analysis for A/B testing
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


class StatisticalAnalyzer:
    """
    Performs various statistical analyses for A/B testing
    """
    
    @staticmethod
    def calculate_sample_size_continuous(baseline_mean: float, 
                                        mde: float,
                                        std_dev: float,
                                        alpha: float = 0.05,
                                        power: float = 0.8) -> int:
        """
        Calculate sample size for continuous metrics (e.g., revenue)
        
        Args:
            baseline_mean: Current average value
            mde: Minimum detectable effect (absolute)
            std_dev: Standard deviation
            alpha: Significance level
            power: Statistical power
            
        Returns:
            Required sample size per variant
        """
        effect_size = mde / std_dev
        
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        
        return int(np.ceil(n))
    
    @staticmethod
    def bayesian_ab_test(control_conversions: int, control_total: int,
                        treatment_conversions: int, treatment_total: int,
                        num_samples: int = 100000) -> Dict:
        """
        Bayesian A/B test using Beta distributions
        
        Args:
            control_conversions: Number of conversions in control
            control_total: Total users in control
            treatment_conversions: Number of conversions in treatment
            treatment_total: Total users in treatment
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary with Bayesian analysis results
        """
        # Prior: uniform Beta(1,1)
        control_alpha = 1 + control_conversions
        control_beta = 1 + control_total - control_conversions
        
        treatment_alpha = 1 + treatment_conversions
        treatment_beta = 1 + treatment_total - treatment_conversions
        
        # Sample from posterior distributions
        control_samples = np.random.beta(control_alpha, control_beta, num_samples)
        treatment_samples = np.random.beta(treatment_alpha, treatment_beta, num_samples)
        
        # Probability that treatment is better
        prob_treatment_better = np.mean(treatment_samples > control_samples)
        
        # Expected lift
        lift_samples = (treatment_samples - control_samples) / control_samples
        expected_lift = np.mean(lift_samples)
        lift_std = np.std(lift_samples)
        
        # Credible interval (95%)
        ci_lower, ci_upper = np.percentile(lift_samples, [2.5, 97.5])
        
        return {
            'prob_treatment_better': prob_treatment_better,
            'expected_lift': expected_lift,
            'lift_std': lift_std,
            'credible_interval_95': (ci_lower, ci_upper),
            'control_posterior_mean': control_alpha / (control_alpha + control_beta),
            'treatment_posterior_mean': treatment_alpha / (treatment_alpha + treatment_beta)
        }
    
    @staticmethod
    def sequential_testing(data: pd.DataFrame, 
                          alpha: float = 0.05,
                          check_frequency: int = 1000) -> pd.DataFrame:
        """
        Sequential analysis to detect significance early
        
        Args:
            data: DataFrame with 'variant' and 'converted' columns
            alpha: Significance level
            check_frequency: How often to check for significance
            
        Returns:
            DataFrame with sequential test results
        """
        control = data[data['variant'] == 'control'].copy()
        treatment = data[data['variant'] == 'treatment'].copy()
        
        results = []
        
        # Check at regular intervals
        for n in range(check_frequency, min(len(control), len(treatment)), check_frequency):
            control_subset = control.iloc[:n]
            treatment_subset = treatment.iloc[:n]
            
            control_conv = control_subset['converted'].sum()
            treatment_conv = treatment_subset['converted'].sum()
            
            # Perform z-test
            z_stat, p_value = stats.proportions_ztest(
                [treatment_conv, control_conv],
                [len(treatment_subset), len(control_subset)]
            )
            
            # Bonferroni correction for multiple testing
            adjusted_alpha = alpha / (len(range(check_frequency, 
                                               min(len(control), len(treatment)), 
                                               check_frequency)))
            
            results.append({
                'sample_size': n,
                'control_rate': control_conv / len(control_subset),
                'treatment_rate': treatment_conv / len(treatment_subset),
                'p_value': p_value,
                'is_significant': p_value < adjusted_alpha,
                'adjusted_alpha': adjusted_alpha
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def meta_analysis(experiments: list) -> Dict:
        """
        Combine results from multiple experiments
        
        Args:
            experiments: List of dicts with experiment results
            
        Returns:
            Combined meta-analysis results
        """
        # Extract effect sizes and standard errors
        effects = []
        variances = []
        
        for exp in experiments:
            effect = exp['relative_lift_pct'] / 100
            se = (exp['ci_upper'] - exp['ci_lower']) / (2 * 1.96)
            
            effects.append(effect)
            variances.append(se ** 2)
        
        effects = np.array(effects)
        variances = np.array(variances)
        
        # Inverse variance weighting
        weights = 1 / variances
        combined_effect = np.sum(weights * effects) / np.sum(weights)
        combined_variance = 1 / np.sum(weights)
        combined_se = np.sqrt(combined_variance)
        
        # Confidence interval
        ci_lower = combined_effect - 1.96 * combined_se
        ci_upper = combined_effect + 1.96 * combined_se
        
        # Heterogeneity (I²)
        Q = np.sum(weights * (effects - combined_effect) ** 2)
        df = len(experiments) - 1
        I_squared = max(0, (Q - df) / Q) if Q > 0 else 0
        
        return {
            'combined_effect': combined_effect * 100,
            'combined_se': combined_se * 100,
            'ci_95': (ci_lower * 100, ci_upper * 100),
            'n_experiments': len(experiments),
            'heterogeneity_i2': I_squared * 100,
            'Q_statistic': Q
        }
    
    @staticmethod
    def calculate_winner_probability(data: pd.DataFrame, 
                                    num_simulations: int = 10000) -> Dict:
        """
        Monte Carlo simulation to calculate probability of each variant winning
        
        Args:
            data: DataFrame with variant and converted columns
            num_simulations: Number of Monte Carlo simulations
            
        Returns:
            Probability estimates for each variant
        """
        variants = data['variant'].unique()
        results = {}
        
        # Get conversion stats for each variant
        variant_stats = {}
        for variant in variants:
            subset = data[data['variant'] == variant]
            conversions = subset['converted'].sum()
            total = len(subset)
            
            variant_stats[variant] = {
                'conversions': conversions,
                'total': total,
                'rate': conversions / total
            }
        
        # Simulate conversion rates
        simulated_rates = {}
        for variant, stats_dict in variant_stats.items():
            # Use Beta distribution (conjugate prior for Binomial)
            alpha = stats_dict['conversions'] + 1
            beta = stats_dict['total'] - stats_dict['conversions'] + 1
            
            simulated_rates[variant] = np.random.beta(alpha, beta, num_simulations)
        
        # Calculate probability of winning
        rates_array = np.array([simulated_rates[v] for v in variants])
        winners = np.argmax(rates_array, axis=0)
        
        for i, variant in enumerate(variants):
            prob_winning = np.mean(winners == i)
            results[variant] = {
                'prob_winning': prob_winning,
                'observed_rate': variant_stats[variant]['rate'],
                'expected_rate': np.mean(simulated_rates[variant])
            }
        
        return results
    
    @staticmethod
    def novelty_effect_analysis(data: pd.DataFrame, 
                                window_days: int = 7) -> pd.DataFrame:
        """
        Analyze if results are affected by novelty effect
        
        Args:
            data: DataFrame with timestamp and converted columns
            window_days: Rolling window size in days
            
        Returns:
            DataFrame with time-based conversion rates
        """
        # Ensure timestamp is datetime
        data = data.copy()
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['date'] = data['timestamp'].dt.date
        
        # Calculate daily conversion rates
        daily_stats = []
        
        for variant in data['variant'].unique():
            variant_data = data[data['variant'] == variant]
            
            for date in sorted(variant_data['date'].unique()):
                day_data = variant_data[variant_data['date'] == date]
                
                daily_stats.append({
                    'date': date,
                    'variant': variant,
                    'conversions': day_data['converted'].sum(),
                    'users': len(day_data),
                    'conversion_rate': day_data['converted'].mean()
                })
        
        daily_df = pd.DataFrame(daily_stats)
        
        # Calculate rolling average
        daily_df = daily_df.sort_values(['variant', 'date'])
        daily_df['rolling_avg'] = daily_df.groupby('variant')['conversion_rate'].transform(
            lambda x: x.rolling(window=window_days, min_periods=1).mean()
        )
        
        # Detect trend
        for variant in daily_df['variant'].unique():
            variant_data = daily_df[daily_df['variant'] == variant].copy()
            
            if len(variant_data) > 1:
                x = np.arange(len(variant_data))
                y = variant_data['conversion_rate'].values
                
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                daily_df.loc[daily_df['variant'] == variant, 'trend_slope'] = slope
                daily_df.loc[daily_df['variant'] == variant, 'trend_p_value'] = p_value
        
        return daily_df


if __name__ == "__main__":
    print("📊 Statistical Analysis Module\n")
    
    # Example: Calculate sample size
    analyzer = StatisticalAnalyzer()
    
    # For conversion rate
    print("Sample Size Calculation (Conversion Rate):")
    n = analyzer.calculate_sample_size_continuous(
        baseline_mean=0.12,
        mde=0.02,  # Want to detect 2 percentage point increase
        std_dev=0.33,  # Binary outcome std dev
        alpha=0.05,
        power=0.8
    )
    print(f"  Required sample size per variant: {n:,}\n")
    
    # For revenue
    print("Sample Size Calculation (Revenue):")
    n_revenue = analyzer.calculate_sample_size_continuous(
        baseline_mean=350,
        mde=20,  # Want to detect ₹20 increase
        std_dev=150,  # Revenue std dev
        alpha=0.05,
        power=0.8
    )
    print(f"  Required sample size per variant: {n_revenue:,}\n")
    
    # Bayesian analysis example
    print("Bayesian A/B Test Analysis:")
    bayesian_result = analyzer.bayesian_ab_test(
        control_conversions=1200,
        control_total=10000,
        treatment_conversions=1416,
        treatment_total=10000
    )
    
    print(f"  Probability Treatment is Better: {bayesian_result['prob_treatment_better']*100:.1f}%")
    print(f"  Expected Lift: {bayesian_result['expected_lift']*100:.2f}%")
    print(f"  95% Credible Interval: [{bayesian_result['credible_interval_95'][0]*100:.1f}%, "
          f"{bayesian_result['credible_interval_95'][1]*100:.1f}%]")