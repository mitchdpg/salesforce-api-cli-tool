#!/usr/bin/env python3
"""
Salesforce CLI Tool (OAuth 2.0 Client Credentials)
===================================================
A command-line interface for querying and managing Salesforce records.
Supports CRUD operations on Accounts, Contacts, Leads, and Opportunities.
Authenticates via OAuth 2.0 Client Credentials Flow using an External Client App.
No password or security token required — authentication uses Consumer Key and
Consumer Secret stored in environment variables.

Note: In production, a dedicated API/integration user with limited permissions
should be configured as the "Run As" user in the External Client App, rather
than an admin account.

Usage: python3 salesforce_cli.py
"""

import os
import csv
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
SF_INSTANCE_URL = os.getenv("SF_INSTANCE_URL")
SF_CONSUMER_KEY = os.getenv("SF_CONSUMER_KEY")
SF_CONSUMER_SECRET = os.getenv("SF_CONSUMER_SECRET")

# Supported Salesforce objects
SUPPORTED_OBJECTS = ["Account", "Contact", "Lead", "Opportunity"]


def authenticate() -> dict:
    """Authenticate via OAuth 2.0 Client Credentials Flow and return session info."""
    if not all([SF_INSTANCE_URL, SF_CONSUMER_KEY, SF_CONSUMER_SECRET]):
        print("[ERROR] Missing environment variables.")
        print("Set SF_INSTANCE_URL, SF_CONSUMER_KEY, and SF_CONSUMER_SECRET")
        print("in your .env file. See .env.example for reference.")
        raise SystemExit(1)

    token_url = f"{SF_INSTANCE_URL}/services/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": SF_CONSUMER_KEY,
        "client_secret": SF_CONSUMER_SECRET,
    }

    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        error = response.json()
        print(f"\n[ERROR] Authentication failed: {error.get('error_description', error)}")
        raise SystemExit(1)

    auth = response.json()
    return {
        "access_token": auth["access_token"],
        "instance_url": auth["instance_url"],
    }


def sf_request(session: dict, method: str, endpoint: str, json_data: dict = None) -> dict:
    """Make an authenticated request to the Salesforce REST API."""
    url = f"{session['instance_url']}/services/data/v62.0{endpoint}"
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json",
    }

    response = requests.request(method, url, headers=headers, json=json_data)

    if response.status_code == 204:
        return {}
    if response.status_code >= 400:
        error = response.json()
        if isinstance(error, list):
            error = error[0]
        print(f"\n  [ERROR] {error.get('message', error)}")
        return None

    return response.json()


def query_records(session: dict, sobject: str, limit: int = 10):
    """Query and display records for a given Salesforce object."""
    field_map = {
        "Account": "Id, Name, Industry, Phone, CreatedDate",
        "Contact": "Id, FirstName, LastName, Email, Phone, AccountId",
        "Lead": "Id, FirstName, LastName, Company, Status, Email",
        "Opportunity": "Id, Name, StageName, Amount, CloseDate, AccountId",
    }

    fields = field_map.get(sobject, "Id, Name")
    query = f"SELECT {fields} FROM {sobject} LIMIT {limit}"

    print(f"\n  Executing: {query}")
    result = sf_request(session, "GET", f"/query?q={query.replace(' ', '+')}")

    if not result:
        return []

    records = result.get("records", [])
    if not records:
        print(f"\n  No {sobject} records found.")
        return records

    print(f"\n  Found {result['totalSize']} record(s):\n")
    for record in records:
        print(f"  {'─' * 50}")
        for key, value in record.items():
            if key == "attributes":
                continue
            print(f"    {key}: {value}")

    return records


def create_record(session: dict, sobject: str):
    """Create a new record for a given Salesforce object."""
    field_prompts = {
        "Account": {"Name": "Account name", "Industry": "Industry", "Phone": "Phone"},
        "Contact": {
            "FirstName": "First name",
            "LastName": "Last name",
            "Email": "Email",
            "Phone": "Phone",
        },
        "Lead": {
            "FirstName": "First name",
            "LastName": "Last name",
            "Company": "Company",
            "Email": "Email",
        },
        "Opportunity": {
            "Name": "Opportunity name",
            "StageName": "Stage (e.g. Prospecting)",
            "CloseDate": "Close date (YYYY-MM-DD)",
            "Amount": "Amount",
        },
    }

    prompts = field_prompts.get(sobject, {})
    data = {}

    print(f"\n  Enter details for new {sobject}:")
    for field, prompt in prompts.items():
        value = input(f"    {prompt}: ").strip()
        if value:
            data[field] = value

    if not data:
        print("  No data entered. Aborting.")
        return

    result = sf_request(session, "POST", f"/sobjects/{sobject}", data)
    if result:
        print(f"\n  ✓ {sobject} created successfully!")
        print(f"    Record ID: {result['id']}")


def update_record(session: dict, sobject: str):
    """Update an existing record by ID."""
    record_id = input(f"\n  Enter {sobject} record ID to update: ").strip()
    if not record_id:
        print("  No ID entered. Aborting.")
        return

    print(f"  Enter fields to update (leave blank to skip):")
    updates = {}

    field_options = {
        "Account": ["Name", "Industry", "Phone"],
        "Contact": ["FirstName", "LastName", "Email", "Phone"],
        "Lead": ["FirstName", "LastName", "Company", "Status"],
        "Opportunity": ["Name", "StageName", "Amount", "CloseDate"],
    }

    for field in field_options.get(sobject, []):
        value = input(f"    {field}: ").strip()
        if value:
            updates[field] = value

    if not updates:
        print("  No updates entered. Aborting.")
        return

    result = sf_request(session, "PATCH", f"/sobjects/{sobject}/{record_id}", updates)
    if result is not None:
        print(f"\n  ✓ {sobject} {record_id} updated successfully!")


def delete_record(session: dict, sobject: str):
    """Delete a record by ID."""
    record_id = input(f"\n  Enter {sobject} record ID to delete: ").strip()
    if not record_id:
        print("  No ID entered. Aborting.")
        return

    confirm = input(f"  Confirm delete {record_id}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("  Delete cancelled.")
        return

    result = sf_request(session, "DELETE", f"/sobjects/{sobject}/{record_id}")
    if result is not None:
        print(f"\n  ✓ {sobject} {record_id} deleted successfully!")


def export_to_csv(session: dict, sobject: str):
    """Export records to a CSV file."""
    field_map = {
        "Account": "Id, Name, Industry, Phone, CreatedDate",
        "Contact": "Id, FirstName, LastName, Email, Phone",
        "Lead": "Id, FirstName, LastName, Company, Status, Email",
        "Opportunity": "Id, Name, StageName, Amount, CloseDate",
    }

    fields = field_map.get(sobject, "Id, Name")
    query = f"SELECT {fields} FROM {sobject}"
    result = sf_request(session, "GET", f"/query?q={query.replace(' ', '+')}")

    if not result:
        return

    records = result.get("records", [])
    if not records:
        print(f"\n  No {sobject} records to export.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{sobject}_export_{timestamp}.csv"

    fieldnames = [key for key in records[0].keys() if key != "attributes"]
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = {k: v for k, v in record.items() if k != "attributes"}
            writer.writerow(row)

    print(f"\n  ✓ Exported {len(records)} records to {filename}")


def select_object() -> str:
    """Prompt user to select a Salesforce object."""
    print("\n  Available objects:")
    for i, obj in enumerate(SUPPORTED_OBJECTS, 1):
        print(f"    {i}. {obj}")

    while True:
        choice = input("\n  Select object (1-4): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(SUPPORTED_OBJECTS):
            return SUPPORTED_OBJECTS[int(choice) - 1]
        print("  Invalid selection. Try again.")


def main():
    print("=" * 60)
    print("Salesforce CLI Tool (OAuth 2.0 Client Credentials)")
    print("=" * 60)

    # Authenticate
    print("\n[*] Authenticating to Salesforce via OAuth 2.0...")
    session = authenticate()
    print("    ✓ Connected successfully")

    while True:
        print("\n" + "─" * 60)
        print("  ACTIONS:")
        print("    1. Query records")
        print("    2. Create record")
        print("    3. Update record")
        print("    4. Delete record")
        print("    5. Export to CSV")
        print("    6. Exit")

        choice = input("\n  Select action (1-6): ").strip()

        if choice == "6":
            print("\n  Goodbye!")
            break

        if choice not in ("1", "2", "3", "4", "5"):
            print("  Invalid selection.")
            continue

        sobject = select_object()

        if choice == "1":
            limit = input("  Record limit (default 10): ").strip() or "10"
            query_records(session, sobject, int(limit))
        elif choice == "2":
            create_record(session, sobject)
        elif choice == "3":
            update_record(session, sobject)
        elif choice == "4":
            delete_record(session, sobject)
        elif choice == "5":
            export_to_csv(session, sobject)


if __name__ == "__main__":
    main()
