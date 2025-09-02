# Test Script for Supabase Integration

This script outlines the steps to test the Supabase integration:

1. Open the Bayesian A/B Test Calculator in a browser
2. Enter test data:
   - Group A: 50 successes, 100 total
   - Group B: 65 successes, 100 total
3. Click "Run Bayesian Analysis"
4. Click "Save Result to History"
5. Verify the result appears in the history table
6. Click "Setup Supabase Sync"
7. Enter your Supabase URL and Anonymous Key
8. Click "Save Configuration"
9. Click "Sync with Supabase"
10. Verify the sync status message
11. Clear browser data and reload the page
12. Re-enter Supabase credentials
13. Click "Sync with Supabase"
14. Verify that your test history is restored from Supabase

Expected behavior:
- Data should sync successfully to Supabase
- Data should be retrieved from Supabase when syncing
- Local storage should be updated with data from Supabase
- All existing functionality should continue to work