#!/usr/bin/env python3
"""
Generate TestRail test cases from PR code changes using watsonx.ai

This script:
1. Extracts code changes from a PR using git diff
2. Sends the code changes to watsonx.ai to generate test cases
3. Parses the response to extract test cases
4. Creates the test cases in TestRail
"""

import requests
import json
import os
import argparse
import re
import sys


def get_code_changes(repo_path, base_sha, head_sha):
    """
    Get code changes between two git commits
    
    Args:
        repo_path: Path to the git repository
        base_sha: Base SHA of the PR (before changes)
        head_sha: Head SHA of the PR (after changes)
        
    Returns:
        String containing the git diff output
    """
    import subprocess
    
    # Store current directory to restore it later
    original_dir = os.getcwd()
    
    try:
        os.chdir(repo_path)
        result = subprocess.run(['git', 'diff', f"{base_sha}..{head_sha}"], 
                               capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing git diff: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Restore original directory
        os.chdir(original_dir)


def generate_test_cases(code_diff, api_key, project_id="19daaa87-9354-4516-8673-7a119cfa7886", log_dir=None):
    """
    Send code changes to watsonx.ai to generate test cases
    
    Args:
        code_diff: String containing the git diff output
        api_key: API key for watsonx.ai
        project_id: Project ID for watsonx.ai
        log_dir: Directory to store log files
        
    Returns:
        JSON response from watsonx.ai
    """
    url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-31"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a test engineer tasked with creating TestRail test cases for the following code changes:
    
    {code_diff}
    
    For each significant change, create a test case following this exact JSON schema:
    
    ```json
    {{
      "test_cases": [
        {{
          "title": "Test case title",
          "preconditions": "Any preconditions needed for the test",
          "steps": "Step-by-step instructions to execute the test",
          "expected_results": "Expected outcomes after test execution",
          "priority": "Critical|High|Medium|Low"
        }}
      ]
    }}
    ```
    
    Important guidelines:
    1. Return ONLY valid JSON that strictly follows the schema above
    2. Include multiple test cases in the "test_cases" array if needed
    3. Make sure each test case has all required fields: title, preconditions, steps, expected_results, and priority
    4. Do not include any explanatory text outside the JSON structure
    5. Ensure the JSON is properly formatted and valid
    """
    
    data = {
        "model_id": "ibm/granite-13b-instruct-v2",
        "input": prompt,
        "project_id": project_id,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 1024
        }
    }
    
    # Set up log directory
    if log_dir is None:
        # Default: create logs directory in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, "logs")
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    print(f"Using log directory: {os.path.abspath(log_dir)}")
    
    # Create a timestamp using current time for uniqueness
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Log the prompt being sent to watsonx.ai
    prompt_log_file = os.path.join(log_dir, f"watsonx_prompt_{timestamp}.txt")
    with open(prompt_log_file, 'w') as f:
        f.write(prompt)
    print(f"\n--- Logging watsonx.ai Prompt ---")
    print(f"Prompt saved to: {prompt_log_file}")
    print(f"Absolute path: {os.path.abspath(prompt_log_file)}")
    print(f"Prompt (first 200 chars):\n{prompt[:200]}...")
    
    try:
        print("\nSending request to watsonx.ai API...")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Get the response JSON
        response_json = response.json()
        
        # Log the raw response
        print("\n--- watsonx.ai API Response ---")
        if "results" in response_json and len(response_json["results"]) > 0:
            generated_text = response_json["results"][0].get("generated_text", "")
            print(f"Generated text (first 500 chars):\n{generated_text[:500]}...")
            
            # Save the full response to a file for debugging
            response_log_file = os.path.join(log_dir, f"watsonx_response_{timestamp}.json")
            
            # Save the response to the log file
            with open(response_log_file, 'w') as f:
                json.dump(response_json, f, indent=2)
            print(f"Full response saved to: {response_log_file}")
            print(f"Absolute path: {os.path.abspath(response_log_file)}")
        else:
            print("Warning: Unexpected response format")
            print(f"Raw response: {json.dumps(response_json, indent=2)[:500]}...")
        print("-------------------------------\n")
        
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"Error calling watsonx.ai API: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)


def parse_test_cases(watsonx_response):
    """
    Parse watsonx.ai response to extract test cases
    
    Args:
        watsonx_response: JSON response from watsonx.ai
        
    Returns:
        List of test case dictionaries
    """
    try:
        # Extract the generated text from the response
        response_text = watsonx_response.get("results", [{}])[0].get("generated_text", "")
        
        if not response_text:
            print("Error: Empty response from watsonx.ai")
            sys.exit(1)
        
        # Extract JSON from the response text
        # First, try to find JSON between code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no code blocks, try to extract JSON directly
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                print("Warning: No JSON found in the response")
                print(f"Response text: {response_text[:500]}...")  # Print first 500 chars
                return []
        
        try:
            # Parse the JSON string
            parsed_json = json.loads(json_str)
            
            # Extract test cases from the parsed JSON
            if "test_cases" in parsed_json and isinstance(parsed_json["test_cases"], list):
                test_cases = parsed_json["test_cases"]
            else:
                print("Warning: Invalid JSON format - 'test_cases' array not found")
                return []
            
            # Validate each test case
            valid_test_cases = []
            required_fields = ["title", "preconditions", "steps", "expected_results", "priority"]
            
            for test_case in test_cases:
                if all(field in test_case for field in required_fields):
                    valid_test_cases.append(test_case)
                else:
                    missing = [f for f in required_fields if f not in test_case]
                    print(f"Warning: Test case missing required fields: {missing}")
            
            return valid_test_cases
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"JSON string: {json_str[:200]}...")  # Print first 200 chars
            return []
    except Exception as e:
        print(f"Error parsing watsonx.ai response: {e}")
        sys.exit(1)


def create_testrail_cases(test_cases, testrail_url, testrail_user, testrail_api_key, project_id, suite_id):
    """
    Create test cases in TestRail
    
    Args:
        test_cases: List of test case dictionaries
        testrail_url: URL of your TestRail instance
        testrail_user: TestRail username/email
        testrail_api_key: TestRail API key
        project_id: TestRail project ID
        suite_id: TestRail test suite ID
    """
    if not test_cases:
        print("No test cases to create")
        return
    
    session = requests.Session()
    session.auth = (testrail_user, testrail_api_key)
    session.headers.update({'Content-Type': 'application/json'})
    
    # Priority mapping
    priority_map = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
    
    created_count = 0
    failed_count = 0
    
    for test_case in test_cases:
        try:
            # Extract fields from the test case
            title = test_case.get("title", "")
            preconditions = test_case.get("preconditions", "")
            steps = test_case.get("steps", "")
            expected_results = test_case.get("expected_results", "")
            
            # Map priority string to TestRail priority ID
            priority = test_case.get("priority", "Medium")
            priority_id = priority_map.get(priority, 3)  # Default to Medium (3) if not found
            
            # Prepare data for TestRail API
            data = {
                "title": title,
                "type_id": 1,  # Functional test
                "priority_id": priority_id,
                "custom_preconds": preconditions,
                "custom_steps": steps,
                "custom_expected": expected_results
            }
            
            # Add optional fields if present
            if "refs" in test_case:
                data["refs"] = test_case["refs"]
            if "estimate" in test_case:
                data["estimate"] = test_case["estimate"]
            
            # Send request to TestRail API
            response = session.post(
                f"{testrail_url}/index.php?/api/v2/add_case/{suite_id}",
                json=data
            )
            
            if response.status_code == 200:
                created_count += 1
                print(f"Created test case: {title}")
            else:
                failed_count += 1
                print(f"Failed to create test case: {response.text}")
        except Exception as e:
            failed_count += 1
            print(f"Error creating test case: {e}")
    
    print(f"\nSummary: Created {created_count} test cases, Failed: {failed_count}")


def parse_arguments():
    """
    Parse command line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Generate TestRail test cases from PR code changes')
    parser.add_argument('--repo-path', required=True, help='Path to the git repository')
    parser.add_argument('--base-sha', required=True, help='Base SHA of the PR (before changes)')
    parser.add_argument('--head-sha', required=True, help='Head SHA of the PR (after changes)')
    parser.add_argument('--watsonx-api-key', required=True, help='API key for watsonx.ai')
    parser.add_argument('--watsonx-project-id', default="19daaa87-9354-4516-8673-7a119cfa7886",
                        help='Project ID for watsonx.ai (default: 19daaa87-9354-4516-8673-7a119cfa7886)')
    parser.add_argument('--testrail-url', required=True, help='URL of your TestRail instance')
    parser.add_argument('--testrail-user', required=True, help='TestRail username/email')
    parser.add_argument('--testrail-api-key', required=True, help='TestRail API key')
    parser.add_argument('--project-id', type=int, required=True, help='TestRail project ID')
    parser.add_argument('--suite-id', type=int, required=True, help='TestRail test suite ID')
    parser.add_argument('--log-dir', help='Directory to store log files (default: scripts/logs)')
    
    return parser.parse_args()


def main():
    """Main function"""
    # Parse command line arguments
    args = parse_arguments()
    
    print(f"Generating test cases for PR changes between {args.base_sha} and {args.head_sha}")
    
    # Get code changes
    print("Getting code changes...")
    code_diff = get_code_changes(args.repo_path, args.base_sha, args.head_sha)
    
    if not code_diff:
        print("No code changes found")
        sys.exit(0)
    
    print(f"Found {len(code_diff.splitlines())} lines of code changes")
    
    # Generate test cases
    print("Generating test cases using watsonx.ai...")
    watsonx_response = generate_test_cases(
        code_diff,
        args.watsonx_api_key,
        args.watsonx_project_id,
        args.log_dir
    )
    
    # Parse test cases
    print("Parsing test cases from watsonx.ai response...")
    test_cases = parse_test_cases(watsonx_response)
    
    print(f"Found {len(test_cases)} test cases")
    
    # Create test cases in TestRail
    print("Creating test cases in TestRail...")
    create_testrail_cases(
        test_cases, 
        args.testrail_url, 
        args.testrail_user, 
        args.testrail_api_key, 
        args.project_id, 
        args.suite_id
    )
    
    print("Done!")


if __name__ == "__main__":
    main()

# Made with Bob
