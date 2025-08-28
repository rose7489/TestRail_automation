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


def generate_test_cases(code_diff, api_key):
    """
    Send code changes to watsonx.ai to generate test cases
    
    Args:
        code_diff: String containing the git diff output
        api_key: API key for watsonx.ai
        
    Returns:
        JSON response from watsonx.ai
    """
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
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
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
            
        # Extract JSON objects from the text
        # This is a simplified approach and might need refinement based on actual responses
        json_pattern = r'\{[^{}]*\}'
        json_matches = re.findall(json_pattern, response_text)
        
        if not json_matches:
            print("Warning: No JSON test cases found in the response")
            print(f"Response text: {response_text[:500]}...")  # Print first 500 chars
            return []
        
        test_cases = []
        for json_str in json_matches:
            try:
                test_case = json.loads(json_str)
                # Validate required fields
                required_fields = ["title", "preconditions", "steps", "expected_results", "priority"]
                if all(field in test_case for field in required_fields):
                    test_cases.append(test_case)
                else:
                    missing = [f for f in required_fields if f not in test_case]
                    print(f"Warning: Test case missing required fields: {missing}")
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON: {json_str[:100]}...")
                continue
        
        return test_cases
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
            # Map priority string to TestRail priority ID
            priority = test_case.get("priority", "Medium")
            priority_id = priority_map.get(priority, 3)  # Default to Medium (3) if not found
            
            data = {
                "title": test_case["title"],
                "type_id": 1,  # Functional test
                "priority_id": priority_id,
                "custom_preconds": test_case["preconditions"],
                "custom_steps": test_case["steps"],
                "custom_expected": test_case["expected_results"]
            }
            
            # Add optional fields if present
            if "refs" in test_case:
                data["refs"] = test_case["refs"]
            if "estimate" in test_case:
                data["estimate"] = test_case["estimate"]
            
            response = session.post(
                f"{testrail_url}/index.php?/api/v2/add_case/{suite_id}",
                json=data
            )
            
            if response.status_code == 200:
                created_count += 1
                print(f"Created test case: {test_case['title']}")
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
    parser.add_argument('--testrail-url', required=True, help='URL of your TestRail instance')
    parser.add_argument('--testrail-user', required=True, help='TestRail username/email')
    parser.add_argument('--testrail-api-key', required=True, help='TestRail API key')
    parser.add_argument('--project-id', type=int, required=True, help='TestRail project ID')
    parser.add_argument('--suite-id', type=int, required=True, help='TestRail test suite ID')
    
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
    watsonx_response = generate_test_cases(code_diff, args.watsonx_api_key)
    
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
