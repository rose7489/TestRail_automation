# TestRail Automation with watsonx.ai

This project automates the generation of TestRail test cases from code changes in pull requests using IBM's watsonx.ai.

## Overview

When a pull request is opened or updated, this automation:

1. Extracts the code changes from the PR
2. Sends the code changes to watsonx.ai for analysis
3. Generates appropriate test cases based on the code changes
4. Creates these test cases in TestRail automatically

## Requirements

- Python 3.8+
- Git repository with code changes
- watsonx.ai API key
- TestRail instance with API access

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/testrail-automation.git
   cd testrail-automation
   ```

2. Install dependencies:
   ```bash
   pip install requests
   ```

## Usage

### Manual Execution

You can run the script manually to generate test cases for specific code changes:

```bash
python scripts/generate_testrail_cases.py \
  --repo-path /path/to/your/repo \
  --base-sha <base-commit-sha> \
  --head-sha <head-commit-sha> \
  --watsonx-api-key <your-watsonx-api-key> \
  --testrail-url https://yourcompany.testrail.io \
  --testrail-user your.email@example.com \
  --testrail-api-key <your-testrail-api-key> \
  --project-id <testrail-project-id> \
  --suite-id <testrail-suite-id>
```

### GitHub Actions Integration

This project includes a GitHub Actions workflow that automatically generates test cases when a pull request is opened or updated.

To set up the GitHub Actions workflow:

1. Add the following secrets to your GitHub repository:
   - `WATSONX_API_KEY`: Your watsonx.ai API key
   - `TESTRAIL_URL`: URL of your TestRail instance
   - `TESTRAIL_USER`: TestRail username/email
   - `TESTRAIL_API_KEY`: TestRail API key
   - `TESTRAIL_PROJECT_ID`: TestRail project ID
   - `TESTRAIL_SUITE_ID`: TestRail test suite ID

2. The workflow file is already configured in `.github/workflows/generate-testrail-cases.yml`

## How It Works

### 1. Code Change Extraction

The script uses `git diff` to extract code changes between the base and head commits of a pull request.

### 2. Test Case Generation with watsonx.ai

The code changes are sent to watsonx.ai with a prompt that instructs it to generate test cases. The prompt specifies the format and required fields for each test case.

### 3. TestRail Integration

The generated test cases are created in TestRail using the TestRail API. Each test case includes:
- Title
- Preconditions
- Steps to execute
- Expected results
- Priority

## Customization

You can customize the test case generation by modifying the prompt in the `generate_test_cases` function in `scripts/generate_testrail_cases.py`.

## Troubleshooting

If you encounter issues:

1. Check that your watsonx.ai API key is valid
2. Verify your TestRail API credentials
3. Ensure the TestRail project and suite IDs are correct
4. Check that the git repository path is valid and contains the specified commits

## License

[MIT License](LICENSE)
