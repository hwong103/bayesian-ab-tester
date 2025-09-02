# Bayesian A/B Test Calculator

A powerful Bayesian A/B testing calculator that runs directly in your browser with no server required. This tool allows you to perform statistical analysis on A/B tests with progress tracking and sample size estimation.

## Features

- **Bayesian Analysis**: Calculate conversion rates, relative uplift, credible intervals, and probability that variant B is better than control A
- **Sample Size Estimation**: Determine how many additional samples you need to reach your desired confidence level
- **History Tracking**: Save and review past test results
- **Cross-Device Sync**: Sync your test history across devices using GitHub Gist
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

## Cross-Device Sync with GitHub Gist

To sync your test history across devices:

1. Create a GitHub Gist:
   - Go to https://gist.github.com/
   - Sign in to your GitHub account
   - Create a new private gist (no need to add any files)
   - Copy the Gist ID from the URL (the long string of characters)

2. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token"
   - Select "Gist" scope
   - Generate the token and copy it

3. Configure sync in the calculator:
   - Open the "Test History" tab
   - Click "Setup Gist Sync"
   - Enter your Gist ID and Personal Access Token
   - Click "Save Configuration"

4. Sync your data:
   - Click "Sync with Gist" to sync your local history with the Gist
   - The calculator will automatically sync when you save new results

## Technical Details

The calculator uses Monte Carlo simulation to perform Bayesian analysis with Beta-Binomial conjugate priors. All calculations are performed client-side in your browser using JavaScript.

## Privacy

All data is stored locally in your browser's localStorage. When using GitHub Gist sync, your data is stored in a private Gist that only you can access.