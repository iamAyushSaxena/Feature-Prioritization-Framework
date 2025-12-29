"""
Visualization Module
Creates charts, dashboards, and visual reports
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from statsmodels.stats.proportion import proportions_ztest
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict
from config import *

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class Visualizer:
    """
    Creates visualizations for feature prioritization and A/B testing
    """
    
    def __init__(self):
        self.colors = COLOR_SCHEME
    
    def plot_rice_scores(self, data: pd.DataFrame, top_n: int = 10) -> None:
        """
        Create horizontal bar chart of RICE scores
        
        Args:
            data: DataFrame with RICE scores
            top_n: Number of top features to show
        """
        top_features = data.nsmallest(top_n, 'rank')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = [self.colors['primary'] if i < 3 else self.colors['secondary'] 
                  for i in range(len(top_features))]
        
        bars = ax.barh(top_features['feature_name'], 
                       top_features['rice_score'],
                       color=colors,
                       edgecolor='black',
                       linewidth=1.5)
        
        # Add value labels
        for i, (idx, row) in enumerate(top_features.iterrows()):
            ax.text(row['rice_score'] + 500, i, f"{row['rice_score']:.0f}",
                   va='center', fontweight='bold')
        
        ax.set_xlabel('RICE Score', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Features by RICE Score', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.invert_yaxis()
        
        # Add grid
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'rice_scores_bar_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Saved: rice_scores_bar_chart.png")
    
    def plot_rice_breakdown(self, data: pd.DataFrame, feature_name: str) -> None:
        """
        Create radar chart showing RICE component breakdown
        
        Args:
            data: DataFrame with RICE scores
            feature_name: Name of feature to visualize
        """
        feature = data[data['feature_name'] == feature_name].iloc[0]
        
        categories = ['Reach\n(Users)', 'Impact\n(Score)', 
                     'Confidence\n(%)', 'Effort\n(Inverse)']
        
        # Normalize values for radar chart
        values = [
            feature['reach_users'] / MONTHLY_ACTIVE_USERS * 100,  # As percentage
            feature['impact_score'] / 3 * 100,  # Scale to 100
            feature['confidence_score'] * 100,
            (1 / feature['effort_months']) * 100 if feature['effort_months'] > 0 else 0
        ]
        
        values += values[:1]  # Close the polygon
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, values, 'o-', linewidth=2, color=self.colors['primary'])
        ax.fill(angles, values, alpha=0.25, color=self.colors['primary'])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(['25', '50', '75', '100'], fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5)
        
        ax.set_title(f'RICE Component Breakdown: {feature_name}',
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / f'rice_breakdown_{feature_name.replace(" ", "_").lower()}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Saved: rice_breakdown_{feature_name.replace(' ', '_').lower()}.png")
    
    def plot_category_distribution(self, data: pd.DataFrame) -> None:
        """
        Visualize feature distribution across categories
        
        Args:
            data: DataFrame with feature categories
        """
        category_counts = data['category'].value_counts()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Bar chart
        colors_list = list(self.colors.values())
        ax1.bar(range(len(category_counts)), category_counts.values,
               color=colors_list[:len(category_counts)],
               edgecolor='black', linewidth=1.5)
        ax1.set_xticks(range(len(category_counts)))
        ax1.set_xticklabels(category_counts.index, rotation=45, ha='right')
        ax1.set_ylabel('Number of Features', fontweight='bold')
        ax1.set_title('Features by Category', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Pie chart
        ax2.pie(category_counts.values, labels=category_counts.index,
               autopct='%1.1f%%', colors=colors_list[:len(category_counts)],
               startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax2.set_title('Category Distribution', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'category_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Saved: category_distribution.png")
    
    def plot_effort_vs_impact(self, data: pd.DataFrame) -> None:
        """
        Create scatter plot of Effort vs Impact (prioritization matrix)
        
        Args:
            data: DataFrame with RICE scores
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create bubble sizes based on reach
        sizes = (data['reach_users'] / data['reach_users'].max() * 1000)
        
        scatter = ax.scatter(data['effort_months'], data['impact_score'],
                           s=sizes, alpha=0.6, c=data['rice_score'],
                           cmap='RdYlGn', edgecolors='black', linewidth=1.5)
        
        # Add labels for top 5 features
        top_5 = data.nsmallest(5, 'rank')
        for _, row in top_5.iterrows():
            ax.annotate(row['feature_name'], 
                       (row['effort_months'], row['impact_score']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        ax.set_xlabel('Effort (Person-Months)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Impact Score', fontsize=12, fontweight='bold')
        ax.set_title('Effort vs Impact Matrix (Bubble size = Reach)',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Add quadrant lines
        ax.axhline(y=data['impact_score'].median(), color='gray', 
                  linestyle='--', alpha=0.5, linewidth=2)
        ax.axvline(x=data['effort_months'].median(), color='gray',
                  linestyle='--', alpha=0.5, linewidth=2)
        
        # Add quadrant labels
        ax.text(0.95, 0.95, 'High Impact\nLow Effort\n(PRIORITIZE)', 
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               horizontalalignment='right', bbox=dict(boxstyle='round', 
               facecolor=self.colors['success'], alpha=0.7))
        
        ax.text(0.05, 0.05, 'Low Impact\nHigh Effort\n(AVOID)',
               transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
               horizontalalignment='left', bbox=dict(boxstyle='round',
               facecolor=self.colors['warning'], alpha=0.7))
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('RICE Score', rotation=270, labelpad=20, fontweight='bold')
        
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'effort_vs_impact_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Saved: effort_vs_impact_matrix.png")
    
    def plot_ab_test_funnel(self, data: pd.DataFrame) -> None:
        """
        Create conversion funnel visualization
        
        Args:
            data: A/B test data with conversions
        """
        control = data[data['variant'] == 'control']
        treatment = data[data['variant'] == 'treatment']
        
        stages = ['Users', 'Sessions', 'Converted']
        
        control_values = [
            len(control),
            control['sessions'].sum(),
            control['converted'].sum()
        ]
        
        treatment_values = [
            len(treatment),
            treatment['sessions'].sum(),
            treatment['converted'].sum()
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Funnel(
            name='Control',
            y=stages,
            x=control_values,
            textinfo="value+percent initial",
            marker=dict(color=self.colors['secondary'])
        ))
        
        fig.add_trace(go.Funnel(
            name='Treatment',
            y=stages,
            x=treatment_values,
            textinfo="value+percent initial",
            marker=dict(color=self.colors['primary'])
        ))
        
        fig.update_layout(
            title='A/B Test Conversion Funnel',
            font=dict(size=12),
            showlegend=True,
            height=600
        )
        
        fig.write_html(FIGURES_DIR / 'ab_test_funnel.html')
        print("✅ Saved: ab_test_funnel.html")
    
    def plot_ab_test_results(self, data: pd.DataFrame) -> None:
            """
            Create comprehensive A/B test results visualization
            
            Args:
                data: A/B test data
            """
            # REMOVED: from scipy import stats as sp_stats  <-- This line caused the error
            
            control = data[data['variant'] == 'control']
            treatment = data[data['variant'] == 'treatment']
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Conversion Rate Comparison', 
                            'Revenue Distribution',
                            'Conversion Over Time',
                            'Statistical Significance'),
                specs=[[{'type': 'bar'}, {'type': 'box'}],
                    [{'type': 'scatter'}, {'type': 'indicator'}]]
            )
            
            # 1. Conversion Rate Comparison
            conv_rates = [control['converted'].mean() * 100, 
                        treatment['converted'].mean() * 100]
            fig.add_trace(
                go.Bar(x=['Control', 'Treatment'], y=conv_rates,
                    marker_color=[self.colors['secondary'], self.colors['primary']],
                    text=[f"{rate:.2f}%" for rate in conv_rates],
                    textposition='outside'),
                row=1, col=1
            )
            
            # 2. Revenue Distribution
            fig.add_trace(
                go.Box(y=control[control['converted']==1]['order_value'],
                    name='Control', marker_color=self.colors['secondary']),
                row=1, col=2
            )
            fig.add_trace(
                go.Box(y=treatment[treatment['converted']==1]['order_value'],
                    name='Treatment', marker_color=self.colors['primary']),
                row=1, col=2
            )
            
            # 3. Conversion Over Time
            data_sorted = data.sort_values('timestamp')
            data_sorted['cumulative_conversions'] = data_sorted.groupby('variant')['converted'].cumsum()
            data_sorted['cumulative_users'] = data_sorted.groupby('variant').cumcount() + 1
            data_sorted['cumulative_rate'] = (data_sorted['cumulative_conversions'] / 
                                            data_sorted['cumulative_users'] * 100)
            
            for variant in ['control', 'treatment']:
                variant_data = data_sorted[data_sorted['variant'] == variant]
                color = self.colors['secondary'] if variant == 'control' else self.colors['primary']
                fig.add_trace(
                    go.Scatter(x=variant_data.index, y=variant_data['cumulative_rate'],
                            name=variant.capitalize(), line=dict(color=color, width=2)),
                    row=2, col=1
                )
            
            # 4. Statistical Significance Indicator
            control_conv = control['converted'].sum()
            treatment_conv = treatment['converted'].sum()
            
            # FIXED LINE BELOW: Using the correct function from statsmodels
            z_stat, p_value = proportions_ztest(
                [treatment_conv, control_conv],
                [len(treatment), len(control)]
            )
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=treatment['converted'].mean() * 100,
                    delta={'reference': control['converted'].mean() * 100,
                        'valueformat': '.2f',
                        'suffix': '%'},
                    title={'text': "Treatment vs Control<br>Conversion Rate"},
                    domain={'x': [0, 1], 'y': [0, 1]}
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                height=900,
                showlegend=True,
                title_text="A/B Test Comprehensive Results Dashboard",
                title_font_size=16
            )
            
            fig.update_xaxes(title_text="Variant", row=1, col=1)
            fig.update_yaxes(title_text="Conversion Rate (%)", row=1, col=1)
            fig.update_yaxes(title_text="Order Value (₹)", row=1, col=2)
            fig.update_xaxes(title_text="User Index", row=2, col=1)
            fig.update_yaxes(title_text="Cumulative Conversion Rate (%)", row=2, col=1)
            
            fig.write_html(FIGURES_DIR / 'ab_test_comprehensive_dashboard.html')
            print("✅ Saved: ab_test_comprehensive_dashboard.html")
    
    def create_executive_dashboard(self, rice_data: pd.DataFrame,
                                   ab_results: Dict) -> None:
        """
        Create comprehensive executive dashboard
        
        Args:
            rice_data: DataFrame with RICE scores
            ab_results: Dictionary with A/B test results
        """
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Top 5 Features by RICE Score',
                          'Expected Annual Revenue Impact',
                          'Effort vs Impact Matrix',
                          'A/B Test Results',
                          'Category-wise Feature Count',
                          'Key Metrics Summary'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'scatter'}, {'type': 'bar'}],
                   [{'type': 'pie'}, {'type': 'table'}]],
            row_heights=[0.3, 0.35, 0.35]
        )
        
        # 1. Top 5 RICE Scores
        top_5 = rice_data.nsmallest(5, 'rank')
        fig.add_trace(
            go.Bar(y=top_5['feature_name'], x=top_5['rice_score'],
                  orientation='h', marker_color=self.colors['primary'],
                  text=top_5['rice_score'].round(0), textposition='outside'),
            row=1, col=1
        )
        
        # 2. Revenue Impact (mock calculation)
        revenue_impact = []
        for _, feature in top_5.iterrows():
            impact = (feature['reach_users'] * feature['impact_score'] * 
                     feature['confidence_score'] * AVERAGE_ORDER_VALUE * 
                     AVERAGE_ORDERS_PER_MONTH * 12 / 1000000)  # In millions
            revenue_impact.append(impact)
        
        fig.add_trace(
            go.Bar(y=top_5['feature_name'], x=revenue_impact,
                  orientation='h', marker_color=self.colors['success'],
                  text=[f"₹{x:.1f}M" for x in revenue_impact],
                  textposition='outside'),
            row=1, col=2
        )
        
        # 3. Effort vs Impact
        fig.add_trace(
            go.Scatter(x=rice_data['effort_months'], y=rice_data['impact_score'],
                      mode='markers', marker=dict(size=10, color=rice_data['rice_score'],
                      colorscale='Viridis', showscale=True),
                      text=rice_data['feature_name'], hoverinfo='text'),
            row=2, col=1
        )
        
        # 4. A/B Test Results
        if ab_results:
            variants = ['Control', 'Treatment']
            rates = [ab_results['control_rate'] * 100, 
                    ab_results['treatment_rate'] * 100]
            colors_ab = [self.colors['secondary'], self.colors['primary']]
            
            fig.add_trace(
                go.Bar(x=variants, y=rates, marker_color=colors_ab,
                      text=[f"{r:.2f}%" for r in rates], textposition='outside'),
                row=2, col=2
            )
        
        # 5. Category Distribution
        category_counts = rice_data['category'].value_counts()
        fig.add_trace(
            go.Pie(labels=category_counts.index, values=category_counts.values,
                  hole=0.3),
            row=3, col=1
        )
        
        # 6. Key Metrics Table
        metrics_data = [
            ['Total Features Evaluated', len(rice_data)],
            ['Top Feature', top_5.iloc[0]['feature_name']],
            ['Highest RICE Score', f"{top_5.iloc[0]['rice_score']:.0f}"],
            ['Expected Annual Revenue (Top 5)', f"₹{sum(revenue_impact):.1f}M"],
            ['A/B Test Significance', 'Yes' if ab_results and ab_results['is_significant'] else 'N/A'],
            ['Recommended Action', 'Ship Top 3 Features']
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'],
                           fill_color=self.colors['primary'],
                           font=dict(color='white', size=12),
                           align='left'),
                cells=dict(values=list(zip(*metrics_data)),
                          fill_color='lavender',
                          align='left',
                          font=dict(size=11))
            ),
            row=3, col=2
        )
        
        fig.update_layout(
            height=1400,
            showlegend=False,
            title_text="Executive Dashboard - Feature Prioritization & A/B Test Results",
            title_font_size=18,
            title_x=0.5
        )
        
        fig.update_xaxes(title_text="RICE Score", row=1, col=1)
        fig.update_xaxes(title_text="Annual Revenue (₹M)", row=1, col=2)
        fig.update_xaxes(title_text="Effort (Months)", row=2, col=1)
        fig.update_yaxes(title_text="Impact Score", row=2, col=1)
        fig.update_xaxes(title_text="Variant", row=2, col=2)
        fig.update_yaxes(title_text="Conversion Rate (%)", row=2, col=2)
        
        # Create dashboards directory if it doesn't exist
        dashboards_dir = OUTPUT_DIR / 'dashboards'
        dashboards_dir.mkdir(parents=True, exist_ok=True)
        
        fig.write_html(dashboards_dir / 'executive_dashboard.html')
        print("✅ Saved: executive_dashboard.html")


if __name__ == "__main__":
    print("📊 Generating Visualizations...\n")
    
    # Load data
    rice_data = pd.read_csv(PROCESSED_DATA_DIR / 'rice_scores.csv')
    ab_data = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_behavior.csv')
    ab_results = pd.read_csv(PROCESSED_DATA_DIR / 'ab_test_results.csv').to_dict('records')[0]
    
    # Create visualizer
    viz = Visualizer()
    
    # Generate all visualizations
    print("Creating RICE score visualizations...")
    viz.plot_rice_scores(rice_data, top_n=10)
    viz.plot_rice_breakdown(rice_data, 'Smart Reorder')
    viz.plot_category_distribution(rice_data)
    viz.plot_effort_vs_impact(rice_data)
    
    print("\nCreating A/B test visualizations...")
    viz.plot_ab_test_funnel(ab_data)
    viz.plot_ab_test_results(ab_data)
    
    print("\nCreating executive dashboard...")
    viz.create_executive_dashboard(rice_data, ab_results)
    
    print("\n✅ All visualizations created successfully!")