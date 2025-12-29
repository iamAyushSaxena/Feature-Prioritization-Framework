# Lab Logbook - Feature Prioritization Framework

## Execution Workflow

### Phase 1: Setup (15 minutes)
1. Create project directory structure
2. Set up Python virtual environment
3. Install all dependencies from requirements.txt
4. Verify installation with test imports

### Phase 2: Feature Brainstorming (30 minutes)
1. Research food delivery app pain points
2. Brainstorm 15+ feature ideas across categories:
   - Customer Retention
   - Order Value Increase
   - User Experience
   - Operational Efficiency
   - Discovery & Exploration
3. Document each feature with description

### Phase 3: RICE Prioritization (45 minutes)
1. For each feature, estimate:
   - **Reach**: % of MAU affected
   - **Impact**: Qualitative score (Massive/High/Medium/Low)
   - **Confidence**: Based on research/precedent (High/Medium/Low)
   - **Effort**: Engineering time in person-months
2. Run `prioritization.py` to calculate RICE scores
3. Review top 3 features
4. Document rationale for estimates

### Phase 4: PRD Creation (2 hours)
1. Select top 3 features from RICE analysis
2. Write complete PRDs including:
   - Problem statement
   - User stories
   - Acceptance criteria
   - Success metrics
   - Technical considerations
   - Launch plan
3. Save in `prds/` directory

### Phase 5: A/B Test Design (1 hour)
1. Select #1 ranked feature for testing
2. Design test parameters:
   - Control vs Treatment groups
   - Sample size calculations
   - Test duration
   - Primary and secondary metrics
   - Guardrail metrics
3. Document test plan

### Phase 6: Simulation & Analysis (1 hour)
1. Run `ab_test_simulator.py`
2. Generate synthetic user behavior data
3. Perform statistical analysis:
   - Chi-square test
   - Z-test for proportions
   - Confidence intervals
   - Power analysis
4. Interpret results

### Phase 7: Visualization (1 hour)
1. Run `visualization.py`
2. Generate all charts:
   - RICE score rankings
   - Effort vs Impact matrix
   - A/B test funnel
   - Conversion trends
   - Executive dashboard
3. Review and annotate key insights

### Phase 8: Reporting (1 hour)
1. Compile final report
2. Write executive summary
3. Document recommendations
4. Prepare presentation deck (optional)

### Phase 9: Documentation (30 minutes)
1. Update README with results
2. Document methodology
3. Add comments to code
4. Create architecture diagram

### Phase 10: Quality Check (30 minutes)
1. Run all tests
2. Verify all outputs generated
3. Check for broken links/paths
4. Final review of documentation

**Total Time: ~9 hours spread over 2-3 days**

## Key Learnings
- RICE framework provides objective prioritization
- Statistical validation prevents false positives
- Data visualization crucial for stakeholder buy-in
- Documentation as important as analysis

## Challenges Faced
1. Estimating confidence levels without real data
2. Balancing detail vs simplicity in PRDs
3. Choosing right sample size for simulation
4. Making visualizations executive-friendly

## Next Steps
- Build interactive Streamlit dashboard
- Add more sophisticated ML models
- Include multi-variant testing
- Create video walkthrough