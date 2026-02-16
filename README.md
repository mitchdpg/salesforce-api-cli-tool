# Salesforce API CLI Tool — OAuth 2.0 Client Credentials (Python)

Created a command-line interface to authenticate with Salesforce via OAuth 2.0 Client Credentials Flow and perform CRUD operations on standard objects (Accounts, Contacts, Leads, Opportunities). Includes CSV export functionality. Uses an External Client App with Consumer Key and Consumer Secret — no passwords or security tokens required.

## Overview

This project demonstrates Python automation against the Salesforce REST API using OAuth 2.0 Client Credentials Flow. It provides an interactive CLI for querying, creating, updating, and deleting records across standard Salesforce objects, as well as exporting records to CSV.

Authentication is handled entirely through the External Client App's Consumer Key and Consumer Secret, making this approach suitable for automated and headless workflows where interactive credential prompts are not practical.

The goal of this project is not full application development, but practical CRM automation commonly used in admin workflows, data management, and integration testing.

## Security Note

This project uses environment variables for all credential storage.
No secrets, tokens, or org-specific identifiers are stored in the repository.
All examples use placeholder values.

**Production Note:** In a production environment, a dedicated API/integration user with limited permissions should be configured as the "Run As" user in the External Client App, rather than an admin account.

## Configuration & Variables

This project uses environment variables to configure the Salesforce connection.

Required variables:

- `SF_INSTANCE_URL` – Salesforce instance URL
- `SF_CONSUMER_KEY` – Consumer Key from the External Client App
- `SF_CONSUMER_SECRET` – Consumer Secret from the External Client App

All configuration values are loaded from a `.env` file or environment variables. See `.env.example` for quick setup.

## Salesforce Setup (External Client App)

Before running the script, you need to verify API permissions and create an External Client App in Salesforce.

### 1. Verify API Permissions

1. In Setup, search **Profiles** in the Quick Find box
2. Click on your profile (e.g., **System Administrator**)
3. Confirm **API Enabled** is checked
4. Confirm your user is assigned to this profile (Setup → **Users** → find your user → check the Profile column)

### 2. Verify User Interface API Settings

1. In Setup, search **User Interface** in the Quick Find box
2. Click **User Interface** (under the User Interface section)
3. Scroll down to the **Setup** subsection
4. Note: **Enable SOAP API login()** is NOT required for this project — we use OAuth 2.0

### 3. Create the External Client App

1. In Setup, search **App Manager** in the Quick Find box
2. Click **External Client App Manager** in the left sidebar
3. Click **New External Client App**
4. Fill in the basic details:
   - **External Client App Name:** `CLI Tool`
   - **API Name:** `CLI_Tool` (auto-fills)
   - **Contact Email:** your email
5. Under **API (Enable OAuth Settings)**, check **Enable OAuth**
6. Set **Callback URL** to `http://localhost:8443/callback`
7. Under **OAuth Scopes**, move the following to the Selected side:
   - **Manage user data via APIs (api)**
   - **Full access (full)**
8. Under **Flow Enablement**, check **Enable Client Credentials Flow**
9. Click **Create**

### 4. Configure OAuth Policies

1. After creation, you'll be on the app management page
2. Click the **Policies** tab
3. Click **Edit**
4. Under **OAuth Flows and External Client App Enhancements**, check **Enable Client Credentials Flow**
5. Set the **Run As (Username)** to your Salesforce user (or a dedicated integration user in production)
6. Click **Save**

### 5. Retrieve Consumer Key and Consumer Secret

1. Go to the **Settings** tab on the app management page
2. Copy the **Consumer Key** and **Consumer Secret**
3. Add these values to your `.env` file (see `.env.example`)

**Note:** The External Client App can take a few minutes to become fully active after creation.

## What This Project Demonstrates

- OAuth 2.0 Client Credentials Flow authentication
- Salesforce REST API integration (SOQL queries, CRUD operations)
- External Client App configuration for headless API access
- CSV export of Salesforce records
- Interactive CLI with menu-driven navigation
- Use of environment variables for secure credential management

## Project Structure

```
salesforce-api-cli-tool/
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
# Edit .env with your Salesforce instance URL, Consumer Key, and Consumer Secret

# Install dependencies
pip install -r requirements.txt

# Run the CLI
python3 salesforce_cli.py
```

## Example Output

```
============================================================
Salesforce CLI Tool (OAuth 2.0 Client Credentials)
============================================================

[*] Authenticating to Salesforce via OAuth 2.0...
    ✓ Connected successfully

────────────────────────────────────────────────────────────
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
    Id: 003fj00000TYtEJAA1
    FirstName: Rose
    LastName: Gonzalez
    Email: rose@edge.com
    Phone: (512) 757-6000
    AccountId: 001fj00000WSJrkAAH

  ──────────────────────────────────────────────────────
    Id: 003fj00000TYtEKAA1
    FirstName: Sean
    LastName: Forbes
    Email: sean@edge.com
    Phone: (512) 757-6000
    AccountId: 001fj00000WSJrkAAH
```

## Use Case

This project reflects common real-world CRM automation scenarios, such as:

- Querying and auditing Salesforce data from the command line
- Bulk exporting records to CSV for reporting
- Quick record creation and updates during testing
- Supporting admin workflows and data migration tasks
- Headless API integration for automated pipelines

## Disclaimer

This project is not affiliated with or officially supported by Salesforce.
It was created for learning and demonstration purposes using a Developer Edition environment.
