#!/bin/bash
# Example script showing how to use generate_testrail_cases.py

# Before running this script, set the following environment variables:
# - REPO_PATH: Path to your git repository
# - BASE_SHA: Base commit SHA (before changes)
# - HEAD_SHA: Head commit SHA (after changes)
# - WATSONX_API_KEY: Your watsonx.ai API key
# - TESTRAIL_URL: URL of your TestRail instance
# - TESTRAIL_USER: TestRail username/email
# - TESTRAIL_API_KEY: TestRail API key
# - PROJECT_ID: TestRail project ID
# - SUITE_ID: TestRail test suite ID

# Check if required environment variables are set
if [ -z "$REPO_PATH" ] || [ -z "$BASE_SHA" ] || [ -z "$HEAD_SHA" ] || \
   [ -z "$WATSONX_API_KEY" ] || [ -z "$TESTRAIL_URL" ] || \
   [ -z "$TESTRAIL_USER" ] || [ -z "$TESTRAIL_API_KEY" ] || \
   [ -z "$PROJECT_ID" ] || [ -z "$SUITE_ID" ]; then
  echo "Error: Required environment variables are not set."
  echo "Please set the following environment variables:"
  echo "  REPO_PATH, BASE_SHA, HEAD_SHA, WATSONX_API_KEY,"
  echo "  TESTRAIL_URL, TESTRAIL_USER, TESTRAIL_API_KEY,"
  echo "  PROJECT_ID, SUITE_ID"
  exit 1
fi

# Run the script
python generate_testrail_cases.py \
  --repo-path "$REPO_PATH" \
  --base-sha "$BASE_SHA" \
  --head-sha "$HEAD_SHA" \
  --watsonx-api-key "$WATSONX_API_KEY" \
  --testrail-url "$TESTRAIL_URL" \
  --testrail-user "$TESTRAIL_USER" \
  --testrail-api-key "$TESTRAIL_API_KEY" \
  --project-id "$PROJECT_ID" \
  --suite-id "$SUITE_ID"

echo ""
echo "Example of getting base and head SHAs for the latest PR using GitHub CLI:"
echo '# Requires GitHub CLI (gh) to be installed and authenticated'
echo 'PR_DATA=$(gh pr view --json baseRefOid,headRefOid)'
echo 'export BASE_SHA=$(echo $PR_DATA | jq -r .baseRefOid)'
echo 'export HEAD_SHA=$(echo $PR_DATA | jq -r .headRefOid)'
echo 'echo "Base SHA: $BASE_SHA"'
echo 'echo "Head SHA: $HEAD_SHA"'

# Made with Bob
