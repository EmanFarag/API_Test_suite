# API and Webhook Test Assignment Suite

## Objective
Build A small but realistic backend test automation suite that validates API functionality and
webhook delivery.

## Quick setup
1. Clone repo.
2. Install requirements:
   ```bash
   pip install -r requirements.txt

3. set environment variables:
   Create a .env file in the project root:
```
WEBHOOK_URL=<your webhook URL ending with /api>
WEBHOOK_TOKEN=<your webhook token>
```
## Run Tests with HTML report
   ```
  pytest --html=reports/report.html --self-contained-html
   ```
## Framework & library choices

**Project Structure**
```
API_Test_suite/
├── tests/
│ ├── init.py
│ ├── test_api_workflow.py
│ └── test_webhook_validation.py
├── utils/
│ ├── init.py
│ ├── api_client.py
│ └── webhook_utils.py
├── config/
│ └── settings.yml
├── .github/
│ └── workflows/
│ └── ci.yml
├── .env
├── requirements.txt
└── README.md
```
**Libraries used in the framework are:**
   1. pytest -> supports fixtures, parametrization, and reporting.
   2. requests	->	Handles API and webhook calls.
   3. python-dotenv -> Load sensitive data from .env securely.
   4. pytest-html -> Generates readable HTML reports for CI/CD.
   5. PyYAML -> load data from yml files.

## How webhook validation logic handled

   1. Send POST to a unique Webhook.site URL.
   2. Add x-request-time header with current UTC timestamp.
   3. Fetch webhook requests via the Webhook.site API.
   4. Match payload fields with expected test payload.
   5. Validate x-request-time is within 2 minutes of current UTC.

## What trade-offs are made and what to be improved

   1. Fetching webhook requests relies on polling with a fixed retry/delay mechanism; may slightly delay test runs.
   2. Tests assume Webhook.site API structure is adding the latest request at the end of the requests body; if their API changes, parsing logic must be updated.

## One test design decision based on risk
   Fetching x_request_time in headers to make sure that we validate the correct latest request