# Setting up Supabase for Bayesian A/B Test Calculator

This guide explains how to set up Supabase for cross-device synchronization of your A/B test results.

## Prerequisites

1. A Supabase account (free tier available at [supabase.com](https://supabase.com/))
2. A Supabase project created

## Setting up the Database

1. In your Supabase project, go to the SQL Editor
2. Run the SQL script from `supabase_schema.sql` to create the necessary tables and policies

## Enabling Anonymous Authentication

1. In your Supabase project, go to Authentication > Settings
2. Find the "Enable Anonymous Sign-ins" option
3. Toggle it to "Enabled"
4. Click "Save"

This step is crucial for the Bayesian A/B Test Calculator to work properly, as it uses anonymous authentication to create a unique user ID for each browser.

## Configuring the Application

1. In your Supabase project, go to Project Settings > API
2. Copy your Project URL and Anonymous Key
3. In the Bayesian A/B Test Calculator:
   - Open the "Test History" tab
   - Click "Setup Supabase Sync"
   - Enter your Project URL and Anonymous Key
   - Click "Save Configuration"

## How It Works

The calculator uses Supabase's anonymous authentication to create a unique user ID for each browser. All test results are stored in the `ab_test_history` table and associated with your user ID.

## Security

- Each user can only access their own test results
- Data is stored securely in your Supabase project
- No sensitive information is stored in the database

## Troubleshooting

If you encounter the error "Anonymous sign-ins are disabled":
1. Follow the "Enabling Anonymous Authentication" steps above
2. Save your Supabase configuration again in the calculator
3. Try syncing again