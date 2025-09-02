# Bayesian A/B Test Calculator

A powerful Bayesian A/B testing calculator that runs directly in your browser with no server required. This tool allows you to perform statistical analysis on A/B tests with progress tracking and sample size estimation.

## Features

- **Bayesian Analysis**: Calculate conversion rates, relative uplift, credible intervals, and probability that variant B is better than control A
- **Sample Size Estimation**: Determine how many additional samples you need to reach your desired confidence level
- **History Tracking**: Save and review past test results
- **Cross-Device Sync**: Sync your test history across devices using Supabase
- **Export to CSV**: Export your test results for further analysis
- **Progress Visualization**: Track test progress over time with interactive charts

## How to Use

1. Enter your A/B test data:
   - Group A (Control): Successes and Total trials
   - Group B (Variant): Successes and Total trials
2. Adjust advanced settings if needed:
   - Simulation Settings: Number of simulations and target confidence interval width
   - Beta Prior Parameters: Alpha and Beta values for the Beta distribution
3. Click "Run Bayesian Analysis" to perform the calculation
4. Review the results including conversion rates, uplift, confidence intervals, and probability
5. Check the sample size recommendation to determine how many more samples you need

## Cross-Device Sync with Supabase

To sync your test history across devices:

1. Create a Supabase account:
   - Go to https://supabase.com/
   - Sign up for a free account
   - Create a new project

2. Set up the database:
   - In your Supabase project, go to the SQL Editor
   - Run the SQL script from [supabase_schema.sql](supabase_schema.sql) to create the necessary tables and policies

3. Get your API credentials:
   - In your Supabase project, go to Project Settings > API
   - Copy your Project URL and Anonymous Key

4. Configure sync in the calculator:
   - Open the "Test History" tab
   - Click "Setup Supabase Sync"
   - Enter your Project URL and Anonymous Key
   - Click "Save Configuration"

5. Sync your data:
   - Click "Sync with Supabase" to sync your local history with Supabase
   - The calculator will automatically sync when you save new results

## Technical Details

The calculator uses Monte Carlo simulation to perform Bayesian analysis with Beta-Binomial conjugate priors. All calculations are performed client-side in your browser using JavaScript.

## Privacy

All data is stored locally in your browser's localStorage. When using Supabase sync, your data is stored in your Supabase project and associated with an anonymous user ID. Only you can access your own test results.