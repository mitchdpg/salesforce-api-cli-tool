# Salesforce CLI Tool (Python)

Built a command-line interface to authenticate with Salesforce via REST API and perform CRUD operations on standard objects (Accounts, Contacts, Leads, Opportunities). Includes CSV export functionality. Prompts for password and security token at runtime — no credentials stored in code.

## Overview

This project demonstrates Python automation against the Salesforce REST API using the `simple_salesforce` library. It provides an interactive CLI for querying, creating, updating, and deleting records across standard Salesforce objects, as well as exporting records to CSV.

The goal of this project is not full application development, but practical CRM automation commonly used in admin workflows, data management, and integration testing.

## Security Note

This project prompts for the Salesforce password and security token at runtime using `getpass`.
No secrets, tokens, or org-specific identifiers are stored in the repository.
All examples use placeholder values.

## Configuration & Variables

This project uses environment variables to configure the Salesforce connection.

Required variables:

- `SF_USERNAME` – Salesforce username for authentication
- `SF_INSTANCE_URL` – Salesforce instance URL (for reference only)

The password and security token are prompted at runtime. All configuration values are loaded from a `.env` file or environment variables. See `.env.example` for quick setup.

## What This Project Demonstrates

- Salesforce REST API authentication via username/password flow
- SOQL queries against standard Salesforce objects
- Full CRUD operations (Create, Read, Update, Delete)
- CSV export of Salesforce records
- Interactive CLI with menu-driven navigation
- Use of environment variables for configuration management

## Project Structure

```
salesforce-cli-tool/
├── salesforce_cli.py     # Interactive CLI for Salesforce operations
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Supported Objects & Operations

| Object | Query | Create | Update | Delete | Export |
|--------|-------|--------|--------|--------|--------|
| Account | ✓ | ✓ | ✓ | ✓ | ✓ |
| Contact | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lead | ✓ | ✓ | ✓ | ✓ | ✓ |
| Opportunity | ✓ | ✓ | ✓ | ✓ | ✓ |

## Example Usage

```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your Salesforce username and instance URL

# Install dependencies
pip install -r requirements.txt

# Run the CLI
python3 salesforce_cli.py
```

Example output:

```
============================================================
Salesforce CLI Tool
============================================================

[*] Authenticating to Salesforce...
    ✓ Connected successfully

──────────────────────────────────────────────────────────
  ACTIONS:
    1. Query records
    2. Create record
    3. Update record
    4. Delete record
    5. Export to CSV
    6. Exit

  Select action (1-6): 1

  Available objects:
    1. Account
    2. Contact
    3. Lead
    4. Opportunity

  Select object (1-4): 2
  Record limit (default 10): 5

  Executing: SELECT Id, FirstName, LastName, Email, Phone, AccountId FROM Contact LIMIT 5

  Found 5 record(s):

  ──────────────────────────────────────────────────────
    Id: 003xxxxxxxxxxxxxxx
    FirstName: Jane
    LastName: Doe
    Email: jane.doe@example.com
    Phone: (555) 123-4567
    AccountId: 001xxxxxxxxxxxxxxx
```

## Use Case

This project reflects common real-world CRM automation scenarios, such as:

- Querying and auditing Salesforce data from the command line
- Bulk exporting records to CSV for reporting
- Quick record creation and updates during testing
- Supporting admin workflows and data migration tasks

## Disclaimer

This project is not affiliated with or officially supported by Salesforce.
It was created for learning and demonstration purposes using a Developer Edition environment.
