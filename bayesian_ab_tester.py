#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer
--------------------------
A tool for analyzing A/B test results using Bayesian methods and calculating
required sample sizes to achieve desired precision.

Usage:
1. Edit the configuration section with your test data
2. Run the script: python bayesian_ab_tester.py
"""

import numpy as np
import math
import os
import argparse
from typing import Dict, Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# ============================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================
# A/B Test Data
GROUP_A_SUCCESSES = 54
GROUP_A_TOTAL = 92
GROUP_B_SUCCESSES = 66
GROUP_B_TOTAL = 93

# Target Precision (Width of 95% Credible Interval)
TARGET_WIDTH = 8.0       # Desired width of interval in percentage points (e.g., 5.0%)

# Simulation Parameters
N_SIMULATIONS = 100_000  # Number of Monte Carlo simulations
ALPHA_PRIOR = 1          # Alpha parameter for Beta prior
BETA_PRIOR = 1           # Beta parameter for Beta prior

# Visualization
GENERATE_PLOTS = True    # Set to False to disable plot generation


# ============================================================
# CORE FUNCTIONS
# ============================================================

def run_simulation(a_successes: int, a_total: int, 
                  b_successes: int, b_total: int,
                  n_simulations: int = 100_000, 
                  alpha_prior: float = 1, 
                  beta_prior: float = 1) -> Dict:
    """
    Run Bayesian A/B test simulation and return results.
    
    Args:
        a_successes: Number of successes in group A
        a_total: Total number of trials in group A
        b_successes: Number of successes in group B
        b_total: Total number of trials in group B
        n_simulations: Number of Monte Carlo simulations
        alpha_prior: Alpha parameter for Beta prior
        beta_prior: Beta parameter for Beta prior
        
    Returns:
        Dictionary with simulation results
    """
    # Posterior parameters (Beta distribution)
    a_alpha = a_successes + alpha_prior
    a_beta = a_total - a_successes + beta_prior

    b_alpha = b_successes + alpha_prior
    b_beta = b_total - b_successes + beta_prior

    # Simulate posterior distributions
    a_samples = np.random.beta(a_alpha, a_beta, n_simulations)
    b_samples = np.random.beta(b_alpha, b_beta, n_simulations)

    # Absolute difference
    absolute_diff = b_samples - a_samples
    abs_mean = np.mean(absolute_diff) * 100
    abs_ci = np.percentile(absolute_diff * 100, [2.5, 97.5])
    
    # Relative uplift
    relative_uplift = (b_samples - a_samples) / a_samples
    mean_uplift = np.mean(relative_uplift) * 100
    ci = np.percentile(relative_uplift * 100, [2.5, 97.5])
    ci_width = ci[1] - ci[0]
    
    # Probability B is better
    prob_b_better = np.mean(b_samples > a_samples)
    
    # Expected loss calculations (opportunity cost)
    expected_loss = np.mean(np.maximum(a_samples - b_samples, 0))
    
    return {
        'a_conversion': a_successes / a_total,
        'b_conversion': b_successes / b_total,
        'mean_uplift': mean_uplift,
        'ci_lower': ci[0],
        'ci_upper': ci[1],
        'ci_width': ci_width,
        'abs_mean': abs_mean,
        'abs_ci_lower': abs_ci[0],
        'abs_ci_upper': abs_ci[1],
        'prob_b_better': prob_b_better,
        'expected_loss': expected_loss,
        'a_samples': a_samples,
        'b_samples': b_samples,
        'relative_uplift': relative_uplift
    }


def calculate_additional_sample_size(a_successes: int, a_total: int, 
                               b_successes: int, b_total: int, 
                               target_width: float = 5.0) -> Dict:
    """
    Estimate additional sample size needed to achieve target CI width.
    
    Args:
        a_successes: Number of successes in group A
        a_total: Total number of trials in group A
        b_successes: Number of successes in group B
        b_total: Total number of trials in group B
        target_width: Target width of credible interval in percentage points
        
    Returns:
        Dictionary with sample size estimates
    """
    # Current conversion rates
    a_rate = a_successes / a_total
    b_rate = b_successes / b_total
    
    # Run initial simulation to get current width
    initial_results = run_simulation(a_successes, a_total, b_successes, b_total)
    current_width = initial_results['ci_width']
    
    if current_width <= target_width:
        return {
            'additional_samples_needed_a': 0,
            'additional_samples_needed_b': 0,
            'total_samples_a': a_total,
            'total_samples_b': b_total,
            'estimated_final_width': current_width
        }
    
    # Calculate scaling factor (inverse square relationship between width and sample size)
    scaling_factor = (current_width / target_width) ** 2
    
    # Estimate additional samples needed
    additional_a = math.ceil((scaling_factor - 1) * a_total)
    additional_b = math.ceil((scaling_factor - 1) * b_total)
    
    # Function to test a specific sample size
    def test_width(additional_a, additional_b):
        # Calculate new successes based on current rates
        new_a_successes = round(a_rate * additional_a)
        new_b_successes = round(b_rate * additional_b)
        
        # Run simulation with combined samples
        test_results = run_simulation(
            a_successes + new_a_successes,
            a_total + additional_a,
            b_successes + new_b_successes,
            b_total + additional_b,
            50000  # Smaller simulation for faster iteration
        )
        
        return test_results['ci_width']
    
    # Binary search to refine the estimate
    low_factor = 0.7  # Start at 70% of the initial estimate
    high_factor = 1.3  # Go up to 130% of the initial estimate
    
    best_additional_a = additional_a
    best_additional_b = additional_b
    best_width = test_width(additional_a, additional_b)
    
    # If our initial estimate is too small
    if best_width > target_width:
        high_factor = 2.0  # Try up to double
    
    # Binary search for the optimal sample size
    for _ in range(5):  # Limited iterations for performance
        mid_factor = (low_factor + high_factor) / 2
        mid_additional_a = math.ceil(mid_factor * additional_a)
        mid_additional_b = math.ceil(mid_factor * additional_b)
        
        width = test_width(mid_additional_a, mid_additional_b)
        
        if width < best_width and abs(width - target_width) < abs(best_width - target_width):
            best_width = width
            best_additional_a = mid_additional_a
            best_additional_b = mid_additional_b
        
        if width > target_width:
            low_factor = mid_factor
        else:
            high_factor = mid_factor
    
    # Ensure we're rounding to sensible numbers
    best_additional_a = math.ceil(best_additional_a / 10) * 10
    best_additional_b = math.ceil(best_additional_b / 10) * 10
    
    return {
        'additional_samples_needed_a': best_additional_a,
        'additional_samples_needed_b': best_additional_b,
        'total_samples_a': a_total + best_additional_a,
        'total_samples_b': b_total + best_additional_b,
        'estimated_final_width': best_width
    }


# ============================================================
# VISUALIZATION FUNCTIONS
# ============================================================

def create_posterior_distribution_plot(results: Dict) -> Figure:
    """
    Create a plot of the posterior distributions for A and B.
    
    Args:
        results: Dictionary with simulation results
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot histograms
    ax.hist(results['a_samples'], bins=50, alpha=0.5, label=f'Group A: {results["a_conversion"]:.2%}')
    ax.hist(results['b_samples'], bins=50, alpha=0.5, label=f'Group B: {results["b_conversion"]:.2%}')
    
    # Add vertical lines for means
    ax.axvline(np.mean(results['a_samples']), color='blue', linestyle='--', alpha=0.7)
    ax.axvline(np.mean(results['b_samples']), color='orange', linestyle='--', alpha=0.7)
    
    ax.set_title('Posterior Distributions of Conversion Rates')
    ax.set_xlabel('Conversion Rate')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_uplift_distribution_plot(results: Dict) -> Figure:
    """
    Create a plot of the uplift distribution with CI.
    
    Args:
        results: Dictionary with simulation results
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot uplift histogram
    uplift_pct = results['relative_uplift'] * 100
    ax.hist(uplift_pct, bins=50, alpha=0.6, color='green')
    
    # Add vertical lines for mean and CI
    ax.axvline(results['mean_uplift'], color='green', linestyle='-', linewidth=2, label=f'Mean: {results["mean_uplift"]:.2f}%')
    ax.axvline(results['ci_lower'], color='red', linestyle='--', linewidth=2, label=f'95% CI: [{results["ci_lower"]:.2f}%, {results["ci_upper"]:.2f}%]')
    ax.axvline(results['ci_upper'], color='red', linestyle='--', linewidth=2)
    
    # Add zero line
    ax.axvline(0, color='black', linestyle='-', alpha=0.3)
    
    # Add shaded area for CI
    ax.axvspan(results['ci_lower'], results['ci_upper'], alpha=0.2, color='red')
    
    title = f'Relative Uplift Distribution (Width: {results["ci_width"]:.2f}%)'
    ax.set_title(title)
    ax.set_xlabel('Relative Uplift (%)')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_interval_width_comparison_plot(results: Dict, sample_estimate: Dict, target_width: float) -> Figure:
    """
    Create a plot comparing the current interval width and estimated width after collecting more samples.
    
    Args:
        results: Dictionary with simulation results
        sample_estimate: Dictionary with sample size estimation results
        target_width: Target width of credible interval
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    widths = [results['ci_width'], sample_estimate['estimated_final_width'], target_width]
    labels = ['Current Width', 'Estimated Width\nAfter Additional Samples', 'Target Width']
    colors = ['blue', 'green', 'red']
    
    # Create the bar chart
    bars = ax.bar(labels, widths, color=colors, alpha=0.7)
    
    # Add text labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.2f}%', ha='center', va='bottom')
    
    ax.set_title('Credible Interval Width Comparison')
    ax.set_ylabel('Width (%)')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

def save_all_plots(results: Dict, sample_estimate: Dict, target_width: float) -> None:
    """
    Create and save all visualization plots.
    
    Args:
        results: Dictionary with simulation results
        sample_estimate: Dictionary with sample size estimation results
        target_width: Target width of credible interval
    """
    import os
    
    # Get the directory of the current script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create plots
    # posterior_fig = create_posterior_distribution_plot(results)
    uplift_fig = create_uplift_distribution_plot(results)
    # width_fig = create_interval_width_comparison_plot(results, sample_estimate, target_width)
    
    # Save plots to the script directory
    posterior_path = os.path.join(script_dir, 'posterior_distributions.png')
    uplift_path = os.path.join(script_dir, 'uplift_distribution.png')
    width_path = os.path.join(script_dir, 'interval_width_comparison.png')
    
    # posterior_fig.savefig(posterior_path)
    uplift_fig.savefig(uplift_path)
    # width_fig.savefig(width_path)
    
    plt.close('all')


# ============================================================
# OUTPUT FORMATTING
# ============================================================

def print_separator():
    """Print a separator line"""
    print("=" * 60)

def print_section_header(title):
    """Print a section header"""
    print_separator()
    print(f" {title} ".center(60, "="))
    print_separator()

def print_simulation_results(results):
    """Print formatted simulation results"""
    print(f"Conversion A: {results['a_conversion']:.2%}")
    print(f"Conversion B: {results['b_conversion']:.2%}")
    print(f"Absolute Difference: {results['abs_mean']:.2f}%")
    print(f"Absolute 95% CI: [{results['abs_ci_lower']:.2f}%, {results['abs_ci_upper']:.2f}%]")
    print(f"Relative Uplift: {results['mean_uplift']:.2f}%")
    print(f"Relative 95% CI: [{results['ci_lower']:.2f}%, {results['ci_upper']:.2f}%]")
    print(f"Interval Width: {results['ci_width']:.2f}%")
    print(f"Probability B > A: {results['prob_b_better']:.2%}")
    print(f"Expected Loss: {results['expected_loss']:.4f}")

def print_sample_size_results(sample_estimate, target_width):
    """Print formatted sample size estimation results"""
    print(f"Target CI Width: {target_width:.1f}%")
    print(f"Additional Samples Needed for Group A: {sample_estimate['additional_samples_needed_a']}")
    print(f"Additional Samples Needed for Group B: {sample_estimate['additional_samples_needed_b']}")
    print(f"Total Final Sample Size A: {sample_estimate['total_samples_a']}")
    print(f"Total Final Sample Size B: {sample_estimate['total_samples_b']}")
    print(f"Estimated Final CI Width: {sample_estimate['estimated_final_width']:.2f}%")


# ============================================================
# MAIN PROGRAM
# ============================================================

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Bayesian A/B Test Analyzer')
    
    parser.add_argument('--a-successes', type=int, default=GROUP_A_SUCCESSES,
                        help=f'Number of successes in group A (default: {GROUP_A_SUCCESSES})')
    parser.add_argument('--a-total', type=int, default=GROUP_A_TOTAL,
                        help=f'Total trials in group A (default: {GROUP_A_TOTAL})')
    parser.add_argument('--b-successes', type=int, default=GROUP_B_SUCCESSES,
                        help=f'Number of successes in group B (default: {GROUP_B_SUCCESSES})')
    parser.add_argument('--b-total', type=int, default=GROUP_B_TOTAL,
                        help=f'Total trials in group B (default: {GROUP_B_TOTAL})')
    parser.add_argument('--target-width', type=float, default=TARGET_WIDTH,
                        help=f'Target width of credible interval in % (default: {TARGET_WIDTH})')
    parser.add_argument('--simulations', type=int, default=N_SIMULATIONS,
                        help=f'Number of Monte Carlo simulations (default: {N_SIMULATIONS})')
    parser.add_argument('--no-plots', action='store_true',
                        help='Disable plot generation')
    
    return parser.parse_args()

def main():
    """Main function"""
    # Parse command line arguments or use defaults from configuration
    args = parse_arguments()
    
    a_successes = args.a_successes 
    a_total = args.a_total
    b_successes = args.b_successes
    b_total = args.b_total
    target_width = args.target_width
    n_simulations = args.simulations
    generate_plots = GENERATE_PLOTS and not args.no_plots
    
    # Print input data
    print_section_header("INPUT DATA")
    print(f"Group A: {a_successes}/{a_total} ({a_successes / a_total:.2%})")
    print(f"Group B: {b_successes}/{b_total} ({b_successes / b_total:.2%})")
    print(f"Target CI Width: {target_width}%")
    print(f"Number of Simulations: {n_simulations:,}")
    
    # Run simulation
    results = run_simulation(
        a_successes, a_total, 
        b_successes, b_total, 
        n_simulations, ALPHA_PRIOR, BETA_PRIOR
    )
    
    # Print simulation results
    print_section_header("BAYESIAN A/B TEST RESULTS")
    print_simulation_results(results)
    
    # Calculate and print sample size needed
    sample_estimate = calculate_additional_sample_size(
        a_successes, a_total, b_successes, b_total, target_width
    )
    
    print_section_header("SAMPLE SIZE ESTIMATION")
    print_sample_size_results(sample_estimate, target_width)
    
    # Optional: Verify with a full simulation using the recommended total sample sizes
    if sample_estimate['additional_samples_needed_a'] > 0:
        print_section_header("VERIFICATION WITH INCREASED SAMPLE SIZE")
        new_a_successes = round(results['a_conversion'] * sample_estimate['additional_samples_needed_a'])
        new_b_successes = round(results['b_conversion'] * sample_estimate['additional_samples_needed_b'])
        
        verification = run_simulation(
            a_successes + new_a_successes, 
            a_total + sample_estimate['additional_samples_needed_a'],
            b_successes + new_b_successes, 
            b_total + sample_estimate['additional_samples_needed_b'],
            n_simulations
        )
        
        print(f"Verified CI Width: {verification['ci_width']:.2f}%")
        print(f"Verified 95% CI: [{verification['ci_lower']:.2f}%, {verification['ci_upper']:.2f}%]")
        print(f"Verified Probability B > A: {verification['prob_b_better']:.2%}")
    
    # Generate and save plots
    if generate_plots:
        print_section_header("VISUALIZATION")
        print("Generating plots...")
        try:
            save_all_plots(results, sample_estimate, target_width)
            # Get the directory of the current script file for display purposes
            script_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"Plots saved to: {script_dir}")
            # print("- posterior_distributions.png")
            print("- uplift_distribution.png")
            # print("- interval_width_comparison.png")
        except Exception as e:
            print(f"Error generating plots: {e}")
    
    print_separator()

if __name__ == "__main__":
    main()