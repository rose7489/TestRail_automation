#!/usr/bin/env python3
"""
Generate TestRail test cases from PR code changes using Google Gemini

This script:
1. Extracts code changes from a PR using git diff
2. Sends the code changes to Google Gemini to generate test cases
3. Parses the response to extract test cases
4. Creates the test cases in TestRail
"""

import requests
import json
import os
import argparse
import re
import sys
import datetime
import shutil
import time
import base64
from pathlib import Path


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


def generate_test_cases(code_diff, api_key, model="gemini-2.0-flash", log_dir=None, max_retries=3, retry_delay=5):
    """
    Send code changes to Google Gemini to generate test cases
    
    Args:
        code_diff: String containing the git diff output
        api_key: API key for Google Gemini
        model: Gemini model to use
        log_dir: Directory to store log files
        max_retries: Maximum number of retries on rate limit errors
        retry_delay: Delay between retries in seconds
        
    Returns:
        JSON response from Gemini
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
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
    
    EXTREMELY IMPORTANT INSTRUCTIONS FOR JSON FORMATTING:
    1. Return ONLY valid JSON that strictly follows the schema above
    2. Include multiple test cases in the "test_cases" array if needed
    3. Make sure each test case has all required fields: title, preconditions, steps, expected_results, and priority
    4. Do not include any explanatory text outside the JSON structure
    5. Ensure the JSON is properly formatted and valid
    6. Double-check that all arrays and objects are properly closed with ] and }} respectively
    7. Verify that all property names and string values are enclosed in double quotes
    8. Ensure there are no trailing commas in arrays or objects
    9. Make sure all JSON syntax is 100% correct and can be parsed by standard JSON parsers
    10. The response should be a single, complete, valid JSON object
    
    Example of properly formatted JSON:
    ```json
    {{
      "test_cases": [
        {{
          "title": "Verify addition functionality",
          "preconditions": "Calculator app is open",
          "steps": "1. Enter 5\\n2. Press + button\\n3. Enter 7\\n4. Press = button",
          "expected_results": "The result 12 is displayed",
          "priority": "High"
        }},
        {{
          "title": "Verify subtraction functionality",
          "preconditions": "Calculator app is open",
          "steps": "1. Enter 10\\n2. Press - button\\n3. Enter 3\\n4. Press = button",
          "expected_results": "The result 7 is displayed",
          "priority": "High"
        }}
      ]
    }}
    ```
    
    Remember: Your response must be ONLY the JSON object, nothing else.
    """
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,  # Very low temperature for more consistent JSON output
            "maxOutputTokens": 1024
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
    
    # Log the prompt being sent to Gemini
    prompt_log_file = os.path.join(log_dir, f"gemini_prompt_{timestamp}.txt")
    with open(prompt_log_file, 'w') as f:
        f.write(prompt)
    print(f"\n--- Logging Gemini Prompt ---")
    print(f"Prompt saved to: {prompt_log_file}")
    print(f"Absolute path: {os.path.abspath(prompt_log_file)}")
    print(f"Prompt (first 200 chars):\n{prompt[:200]}...")
    
    # Implement retry logic for rate limiting
    retry_count = 0
    while retry_count <= max_retries:
        try:
            print(f"\nSending request to Gemini API (attempt {retry_count + 1}/{max_retries + 1})...")
            response = requests.post(url, headers=headers, json=data)
            
            # Check for rate limiting
            if response.status_code == 429:
                retry_count += 1
                if retry_count <= max_retries:
                    retry_seconds = retry_delay * retry_count
                    print(f"Rate limit exceeded. Retrying in {retry_seconds} seconds...")
                    time.sleep(retry_seconds)
                    continue
                else:
                    print("Maximum retry attempts reached. Exiting.")
                    response.raise_for_status()
            else:
                # For non-rate limit errors, just raise the exception
                response.raise_for_status()
            
            # Get the response JSON
            response_json = response.json()
            
            # Log the raw response
            print("\n--- Gemini API Response ---")
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                generated_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
                print(f"Generated text (first 500 chars):\n{generated_text[:500]}...")
                
                # Save the full response to a file for debugging
                response_log_file = os.path.join(log_dir, f"gemini_response_{timestamp}.json")
                
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
            print(f"Error calling Gemini API: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
                
                # If it's not a rate limit error or we've exhausted retries, exit
                if e.response.status_code != 429 or retry_count >= max_retries:
                    sys.exit(1)
                
                # For rate limit errors, retry with exponential backoff
                retry_count += 1
                retry_seconds = retry_delay * retry_count
                print(f"Rate limit exceeded. Retrying in {retry_seconds} seconds...")
                time.sleep(retry_seconds)
            else:
                # For other errors without response, exit
                sys.exit(1)


def fix_json_string(json_str):
    """
    Attempt to fix common JSON formatting issues
    
    Args:
        json_str: JSON string that might have formatting issues
        
    Returns:
        Fixed JSON string
    """
    # Replace single quotes with double quotes
    json_str = re.sub(r"(?<![\\])\'", "\"", json_str)
    
    # Fix trailing commas in arrays and objects
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*\]", "]", json_str)
    
    # Fix missing quotes around property names
    json_str = re.sub(r"([{,]\s*)(\w+)(\s*:)", r'\1"\2"\3', json_str)
    
    # Fix unclosed arrays by adding missing closing brackets
    open_brackets = json_str.count("[")
    close_brackets = json_str.count("]")
    if open_brackets > close_brackets:
        json_str += "]" * (open_brackets - close_brackets)
    
    # Fix unclosed objects by adding missing closing braces
    open_braces = json_str.count("{")
    close_braces = json_str.count("}")
    if open_braces > close_braces:
        json_str += "}" * (open_braces - close_braces)
    
    return json_str


def parse_test_cases(gemini_response):
    """
    Parse Gemini response to extract test cases
    
    Args:
        gemini_response: JSON response from Gemini
        
    Returns:
        List of test case dictionaries
    """
    try:
        # Extract the generated text from the response
        response_text = ""
        if "candidates" in gemini_response and len(gemini_response["candidates"]) > 0:
            response_text = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
        
        if not response_text:
            print("Error: Empty response from Gemini")
            sys.exit(1)
        
        # Log the full response text for debugging
        print(f"\nFull response text:\n{response_text}\n")
        
        # Extract JSON from the response text
        # First, try to find JSON between code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print("Found JSON in code block")
        else:
            # If no code blocks, try to extract JSON directly
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print("Found JSON without code block")
            else:
                print("Warning: No JSON found in the response")
                print(f"Response text: {response_text[:500]}...")  # Print first 500 chars
                return []
        
        # Print the extracted JSON string for debugging
        print(f"\nExtracted JSON string:\n{json_str}\n")
        
        try:
            # Try to parse the JSON string directly
            parsed_json = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Initial JSON parsing error: {e}")
            print("Attempting to fix JSON formatting issues...")
            
            # Try to fix common JSON formatting issues
            fixed_json_str = fix_json_string(json_str)
            print(f"\nFixed JSON string:\n{fixed_json_str}\n")
            
            try:
                # Try to parse the fixed JSON string
                parsed_json = json.loads(fixed_json_str)
                print("Successfully parsed JSON after fixing formatting issues")
            except json.JSONDecodeError as e:
                print(f"Error parsing fixed JSON: {e}")
                print("Attempting to create a valid test case structure manually...")
                
                # As a last resort, try to extract test case information manually
                title_match = re.search(r'"title"\s*:\s*"([^"]+)"', json_str)
                precond_match = re.search(r'"preconditions"\s*:\s*"([^"]+)"', json_str)
                steps_match = re.search(r'"steps"\s*:\s*"([^"]+)"', json_str)
                expected_match = re.search(r'"expected_results"\s*:\s*"([^"]+)"', json_str)
                priority_match = re.search(r'"priority"\s*:\s*"([^"]+)"', json_str)
                
                if title_match and precond_match and steps_match and expected_match and priority_match:
                    # Create a test case manually
                    parsed_json = {
                        "test_cases": [{
                            "title": title_match.group(1),
                            "preconditions": precond_match.group(1),
                            "steps": steps_match.group(1),
                            "expected_results": expected_match.group(1),
                            "priority": priority_match.group(1)
                        }]
                    }
                    print("Created test case structure manually")
                else:
                    print("Could not extract test case information manually")
                    return []
        
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
            
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        sys.exit(1)


def get_testrail_sections(testrail_url, testrail_user, testrail_api_key, project_id, suite_id):
    """
    Get available sections in TestRail for the given project and suite
    
    Args:
        testrail_url: URL of your TestRail instance
        testrail_user: TestRail username/email
        testrail_api_key: TestRail API key
        project_id: TestRail project ID
        suite_id: TestRail test suite ID
        
    Returns:
        List of section dictionaries
    """
    # Create a session for TestRail API requests
    session = requests.Session()
    
    # Set up authentication headers
    auth_str = f"{testrail_user}:{testrail_api_key}"
    auth_bytes = auth_str.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_b64}'
    })
    
    # Ensure the TestRail URL doesn't end with a slash
    if testrail_url.endswith('/'):
        testrail_url = testrail_url[:-1]
    
    try:
        # Get sections for the project and suite
        sections_url = f"{testrail_url}/index.php?/api/v2/get_sections/{project_id}&suite_id={suite_id}"
        response = session.get(sections_url)
        response.raise_for_status()
        
        sections = response.json()
        print(f"Found {len(sections)} sections in TestRail")
        
        # Print section information for debugging
        for section in sections:
            print(f"Section ID: {section.get('id')}, Name: {section.get('name')}")
        
        return sections
    except requests.exceptions.RequestException as e:
        print(f"Error getting TestRail sections: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return []


def create_default_section(testrail_url, testrail_user, testrail_api_key, project_id, suite_id):
    """
    Create a default section in TestRail if none exists
    
    Args:
        testrail_url: URL of your TestRail instance
        testrail_user: TestRail username/email
        testrail_api_key: TestRail API key
        project_id: TestRail project ID
        suite_id: TestRail test suite ID
        
    Returns:
        Section ID of the created section
    """
    # Create a session for TestRail API requests
    session = requests.Session()
    
    # Set up authentication headers
    auth_str = f"{testrail_user}:{testrail_api_key}"
    auth_bytes = auth_str.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_b64}'
    })
    
    # Ensure the TestRail URL doesn't end with a slash
    if testrail_url.endswith('/'):
        testrail_url = testrail_url[:-1]
    
    try:
        # Create a new section
        section_url = f"{testrail_url}/index.php?/api/v2/add_section/{project_id}"
        data = {
            "name": "generic",  # Use "generic" as the section name
            "suite_id": suite_id,
            "description": "Test cases generated automatically from code changes"
        }
        
        response = session.post(section_url, json=data)
        response.raise_for_status()
        
        section = response.json()
        section_id = section.get('id')
        print(f"Created new section 'generic' with ID: {section_id}")
        
        return section_id
    except requests.exceptions.RequestException as e:
        print(f"Error creating TestRail section: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None


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
    
    # Create a session for TestRail API requests
    session = requests.Session()
    
    # Set up authentication headers
    # TestRail API uses Basic Authentication with username and API key
    auth_str = f"{testrail_user}:{testrail_api_key}"
    auth_bytes = auth_str.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_b64}'
    })
    
    # Print authentication details for debugging (mask the API key)
    masked_api_key = testrail_api_key[:4] + '*' * (len(testrail_api_key) - 8) + testrail_api_key[-4:]
    print(f"Using TestRail authentication - User: {testrail_user}, API Key: {masked_api_key}")
    
    # Priority mapping
    priority_map = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
    
    created_count = 0
    failed_count = 0
    
    # Ensure the TestRail URL doesn't end with a slash
    if testrail_url.endswith('/'):
        testrail_url = testrail_url[:-1]
    
    # Test the authentication with a simple API call
    try:
        print("Testing TestRail API connection...")
        test_url = f"{testrail_url}/index.php?/api/v2/get_projects"
        test_response = session.get(test_url)
        test_response.raise_for_status()
        print("TestRail API connection successful")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to TestRail API: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)
    
    # Get available sections or create a default one
    sections = get_testrail_sections(testrail_url, testrail_user, testrail_api_key, project_id, suite_id)
    
    section_id = None
    # Look for a section named "generic"
    for section in sections:
        if section.get('name') == "generic":
            section_id = section.get('id')
            print(f"Found existing 'generic' section with ID: {section_id}")
            break
    
    # If no "generic" section found, create one
    if not section_id:
        section_id = create_default_section(testrail_url, testrail_user, testrail_api_key, project_id, suite_id)
        if not section_id:
            print("Failed to create a 'generic' section. Cannot add test cases.")
            sys.exit(1)
    
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
                "custom_expected": expected_results,
                "section_id": section_id  # Add section_id to the request
            }
            
            # Add optional fields if present
            if "refs" in test_case:
                data["refs"] = test_case["refs"]
            if "estimate" in test_case:
                data["estimate"] = test_case["estimate"]
            
            # Send request to TestRail API
            api_url = f"{testrail_url}/index.php?/api/v2/add_case/{section_id}"
            print(f"Sending request to TestRail API: {api_url}")
            print(f"Request data: {json.dumps(data, indent=2)}")
            
            response = session.post(api_url, json=data)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            
            created_count += 1
            print(f"Created test case: {title}")
        except requests.exceptions.RequestException as e:
            failed_count += 1
            print(f"Failed to create test case: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
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
    parser.add_argument('--gemini-api-key', required=True, help='API key for Google Gemini')
    parser.add_argument('--gemini-model', default="gemini-2.0-flash",
                        help='Gemini model to use (default: gemini-2.0-flash)')
    parser.add_argument('--testrail-url', required=True, help='URL of your TestRail instance')
    parser.add_argument('--testrail-user', required=True, help='TestRail username/email')
    parser.add_argument('--testrail-api-key', required=True, help='TestRail API key')
    parser.add_argument('--project-id', type=int, required=True, help='TestRail project ID')
    parser.add_argument('--suite-id', type=int, required=True, help='TestRail test suite ID')
    parser.add_argument('--log-dir', help='Directory to store log files (default: scripts/logs)')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum number of retries on rate limit errors')
    parser.add_argument('--retry-delay', type=int, default=5, help='Base delay between retries in seconds')
    
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
    print("Generating test cases using Google Gemini...")
    gemini_response = generate_test_cases(
        code_diff,
        args.gemini_api_key,
        args.gemini_model,
        args.log_dir,
        args.max_retries,
        args.retry_delay
    )
    
    # Parse test cases
    print("Parsing test cases from Gemini response...")
    test_cases = parse_test_cases(gemini_response)
    
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
