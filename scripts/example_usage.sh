#!/bin/bash
# Example usage of the generate_testrail_cases.py script with Google Gemini

# Set your API keys and credentials
GEMINI_API_KEY="your-gemini-api-key"
TESTRAIL_URL="https://yourcompany.testrail.io"
TESTRAIL_USER="your-email@example.com"
TESTRAIL_API_KEY="your-testrail-api-key"
TESTRAIL_PROJECT_ID="1"  # Replace with your TestRail project ID
TESTRAIL_SUITE_ID="2"    # Replace with your TestRail suite ID

# Set repository information
REPO_PATH="$(pwd)"  # Current directory, adjust as needed
BASE_SHA="main"     # Base branch or commit SHA
HEAD_SHA="HEAD"     # Current branch or commit SHA

# Run the script
python scripts/generate_testrail_cases.py \
  --repo-path "$REPO_PATH" \
  --base-sha "$BASE_SHA" \
  --head-sha "$HEAD_SHA" \
  --gemini-api-key "$GEMINI_API_KEY" \
  --gemini-model "gemini-2.0-flash" \
  --testrail-url "$TESTRAIL_URL" \
  --testrail-user "$TESTRAIL_USER" \
  --testrail-api-key "$TESTRAIL_API_KEY" \
  --project-id "$TESTRAIL_PROJECT_ID" \
  --suite-id "$TESTRAIL_SUITE_ID" \
  --max-retries 5 \
  --retry-delay 10

# Made with Bob
