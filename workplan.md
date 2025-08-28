Integration Options Between Watsonx.ai and TestRail (continued)


import requests
import json
import os
import argparse

# 1. Get code changes from a PR
def get_code_changes(repo_path, base_sha, head_sha):
    import subprocess
    os.chdir(repo_path)
    result = subprocess.run(['git', 'diff', f"{base_sha}..{head_sha}"], capture_output=True, text=True)
    return result.stdout

# 2. Send to watsonx.ai
def generate_test_cases(code_diff, api_key):
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a test engineer tasked with creating TestRail test cases for the following code changes:
    
    {code_diff}
    
    For each significant change, create a test case in JSON format with:
    1. Title
    2. Preconditions
    3. Steps to execute
    4. Expected results
    5. Priority (Critical/High/Medium/Low)
    """
    
    data = {
        "model_id": "ibm/granite-13b-instruct-v2",
        "input": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 1024
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# 3. Parse watsonx.ai response to extract test cases
def parse_test_cases(watsonx_response):
    # This would depend on the exact format of the response
    # For this example, we assume the response contains JSON test cases
    response_text = watsonx_response.get("results", [{}])[0].get("generated_text", "")
    
    # Extract JSON objects from the text (this is simplified)
    import re
    json_pattern = r'\{[^{}]*\}'
    json_matches = re.findall(json_pattern, response_text)
    
    test_cases = []
    for json_str in json_matches:
        try:
            test_case = json.loads(json_str)
            test_cases.append(test_case)
        except json.JSONDecodeError:
            continue
    
    return test_cases

# 4. Create test cases in TestRail
def create_testrail_cases(test_cases, testrail_url, testrail_user, testrail_password, project_id, suite_id):
    session = requests.Session()
    session.auth = (testrail_user, testrail_password)
    session.headers.update({'Content-Type': 'application/json'})
    
    for test_case in test_cases:
        data = {
            "title": test_case["title"],
            "type_id": 1,  # Functional test
            "priority_id": {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}[test_case["priority"]],
            "custom_preconds": test_case["preconditions"],
            "custom_steps": test_case["steps"],
            "custom_expected": test_case["expected_results"]
        }
        
        response = session.post(
            f"{testrail_url}/index.php?/api/v2/add_case/{suite_id}",
            json=data
        )
        
        if response.status_code != 200:
            print(f"Failed to create test case: {response.text}")

# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate TestRail test cases from PR code changes')
    parser.add_argument('--repo-path', required=True, help='Path to the git repository')
    parser.add_argument('--base-sha', required=True, help='Base SHA of the PR (before changes)')
    parser.add_argument('--head-sha', required=True, help='Head SHA of the PR (after changes)')
    parser.add_argument('--watsonx-api-key', required=True, help='API key for watsonx.ai')
    parser.add_argument('--testrail-url', required=True, help='URL of your TestRail instance')
    parser.add_argument('--testrail-user', required=True, help='TestRail username/email')
    parser.add_argument('--testrail-api-key', required=True, help='TestRail API key')
    parser.add_argument('--project-id', type=int, required=True, help='TestRail project ID')
    parser.add_argument('--suite-id', type=int, required=True, help='TestRail test suite ID')
    
    return parser.parse_args()

# Main workflow
def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Execute workflow
    code_diff = get_code_changes(args.repo_path, args.base_sha, args.head_sha)
    watsonx_response = generate_test_cases(code_diff, args.watsonx_api_key)
    test_cases = parse_test_cases(watsonx_response)
    create_testrail_cases(
        test_cases, 
        args.testrail_url, 
        args.testrail_user, 
        args.testrail_api_key, 
        args.project_id, 
        args.suite_id
    )

if __name__ == "__main__":
    main()



3. CI/CD Pipeline Integration


name: Generate TestRail Test Cases

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  generate-test-cases:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests
      
      - name: Generate and upload test cases
        env:
          WATSONX_API_KEY: ${{ secrets.WATSONX_API_KEY }}
          TESTRAIL_URL: ${{ secrets.TESTRAIL_URL }}
          TESTRAIL_USER: ${{ secrets.TESTRAIL_USER }}
          TESTRAIL_API_KEY: ${{ secrets.TESTRAIL_API_KEY }}
          PROJECT_ID: ${{ secrets.TESTRAIL_PROJECT_ID }}
          SUITE_ID: ${{ secrets.TESTRAIL_SUITE_ID }}
        run: |
          python scripts/generate_testrail_cases.py \
            --repo-path $GITHUB_WORKSPACE \
            --base-sha ${{ github.event.pull_request.base.sha }} \
            --head-sha ${{ github.event.pull_request.head.sha }} \
            --watsonx-api-key $WATSONX_API_KEY \
            --testrail-url $TESTRAIL_URL \
            --testrail-user $TESTRAIL_USER \
            --testrail-api-key $TESTRAIL_API_KEY \
            --project-id $PROJECT_ID \
            --suite-id $SUITE_ID
