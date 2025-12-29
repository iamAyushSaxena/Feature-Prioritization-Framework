# Methodology & Theoretical Framework

This document outlines the product management frameworks and statistical methodologies implemented in this project. It serves as the theoretical basis for the code logic found in `src/prioritization.py` and `src/ab_test_simulator.py`.

## 1. RICE Prioritization Framework

The **RICE** framework is used to evaluate and prioritize feature ideas objectively. It combats recency bias and "loudest voice in the room" decision-making by scoring features based on four factors.

### The Formula
$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

### Component Definitions

#### **R**each (Users per Month)
The number of users who will be affected by the feature within a given time period (typically one month).
* **Metric:** Absolute number of users.
* **Calculation:** `Monthly Active Users (MAU) * % of User Base Targeted`
* **Example:** If MAU is 500,000 and a feature targets 20% of users, Reach = 100,000.

#### **I**mpact (Business Value)
A qualitative estimate of how much the feature will increase the target metric (e.g., conversion rate, revenue) for each reached user.
* **Scale:**
    * **3.0 (Massive):** Fundamental game-changer
    * **2.0 (High):** Significant improvement
    * **1.0 (Medium):** Standard optimization
    * **0.5 (Low):** Minor tweak
    * **0.25 (Minimal):** Cosmetic change

#### **C**onfidence (%)
How sure are we about our Reach, Impact, and Effort estimates? This acts as a penalty for uncertainty.
* **Scale:**
    * **100% (High):** Validated by user research, data, or engineering specs.
    * **80% (Medium):** Educated guess based on industry standards.
    * **50% (Low):** "Moonshot" or gut feeling.

#### **E**ffort (Person-Months)
The total amount of time required from all team members (product, design, engineering) to ship the feature.
* **Metric:** Person-months.
* **Scale:** Lower is better (since it's the denominator). 0.5 means 2 weeks of work; 3 means 3 months of work.

---

## 2. A/B Testing & Statistical Analysis

Once the top feature is identified via RICE, we validate its impact using a simulated A/B test (Split Test).

### Hypothesis Design
* **Null Hypothesis ($H_0$):** The new feature has **no effect** or a negative effect on the conversion rate ($p_{treatment} \leq p_{control}$).
* **Alternative Hypothesis ($H_1$):** The new feature **increases** the conversion rate ($p_{treatment} > p_{control}$).

### Test Parameters
* **Control Group:** Users experiencing the current app version.
* **Treatment Group:** Users experiencing the new feature.
* **Split Ratio:** 50/50.

### Statistical Significance Tests
To determine if the observed difference is real or just random noise, we employ two primary tests:

#### 1. Z-Test for Proportions
Used to compare two independent proportions (conversion rates).
* **Formula:**
    $$Z = \frac{(\hat{p}_1 - \hat{p}_2)}{\sqrt{\hat{p}(1-\hat{p})(\frac{1}{n_1} + \frac{1}{n_2})}}$$
    * Where $\hat{p}$ is the pooled proportion.
* **P-Value:** The probability of observing the result assuming $H_0$ is true. If P-value < $\alpha$ (0.05), we reject $H_0$.

#### 2. Chi-Square Test of Independence ($\chi^2$)
Used as a secondary validation to check if "Variant" and "Conversion" are independent variables.

### Metrics & Thresholds
* **Significance Level ($\alpha$):** 0.05 (We are 95% confident that the result is not due to chance).
* **Statistical Power ($1 - \beta$):** 0.80 (We have an 80% chance of detecting an effect if one actually exists).
* **Minimum Detectable Effect (MDE):** The smallest lift we care about detecting (set to 5%).

---

## 3. Synthetic Data Generation (Monte Carlo Simulation)

Since we do not have real users, we generate synthetic data to simulate the A/B test.

* **User Behavior:** We model user actions using probability distributions:
    * **Conversions:** Bernoulli trial (Binomial distribution).
    * **Order Value:** Normal distribution centered around Average Order Value (AOV).
    * **Session Time:** Exponential distribution.
* **Simulation Logic:**
    1.  Assign $N$ users to Control and $N$ users to Treatment.
    2.  For Control, simulate conversions based on baseline rate (e.g., 12%).
    3.  For Treatment, simulate conversions based on `baseline * (1 + expected_lift)`.
    4.  Run statistical tests on the resulting datasets.