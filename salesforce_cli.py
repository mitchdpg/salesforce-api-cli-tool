#!/usr/bin/env python3
"""
Salesforce CLI Tool
===================
A command-line interface for querying and managing Salesforce records.
Supports CRUD operations on Accounts, Contacts, Leads, and Opportunities.
Authenticates via username/password with security token.

Usage: python3 salesforce_cli.py
"""

import os
import getpass
import csv
from datetime import datetime
from simple_salesforce import Salesforce
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
SF_USERNAME = os.getenv("SF_USERNAME")
SF_INSTANCE_URL = os.getenv("SF_INSTANCE_URL")

# Supported Salesforce objects
SUPPORTED_OBJECTS = ["Account", "Contact", "Lead", "Opportunity"]


def authenticate() -> Salesforce:
    """Authenticate to Salesforce and return a session."""
    if not SF_USERNAME:
        print("[ERROR] Missing SF_USERNAME environment variable.")
        print("See .env.example for reference.")
        raise SystemExit(1)

    password = getpass.getpass("Enter Salesforce password: ")
    security_token = getpass.getpass("Enter security token: ")

    sf = Salesforce(
        username=SF_USERNAME,
        password=password,
        security_token=security_token,
    )
    return sf


def query_records(sf: Salesforce, sobject: str, limit: int = 10):
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
    results = sf.query(query)

    records = results.get("records", [])
    if not records:
        print(f"\n  No {sobject} records found.")
        return records

    print(f"\n  Found {results['totalSize']} record(s):\n")
    for record in records:
        print(f"  {'─' * 50}")
        for key, value in record.items():
            if key == "attributes":
                continue
            print(f"    {key}: {value}")

    return records


def create_record(sf: Salesforce, sobject: str):
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

    result = getattr(sf, sobject).create(data)
    print(f"\n  ✓ {sobject} created successfully!")
    print(f"    Record ID: {result['id']}")


def update_record(sf: Salesforce, sobject: str):
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

    getattr(sf, sobject).update(record_id, updates)
    print(f"\n  ✓ {sobject} {record_id} updated successfully!")


def delete_record(sf: Salesforce, sobject: str):
    """Delete a record by ID."""
    record_id = input(f"\n  Enter {sobject} record ID to delete: ").strip()
    if not record_id:
        print("  No ID entered. Aborting.")
        return

    confirm = input(f"  Confirm delete {record_id}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("  Delete cancelled.")
        return

    getattr(sf, sobject).delete(record_id)
    print(f"\n  ✓ {sobject} {record_id} deleted successfully!")


def export_to_csv(sf: Salesforce, sobject: str):
    """Export records to a CSV file."""
    field_map = {
        "Account": "Id, Name, Industry, Phone, CreatedDate",
        "Contact": "Id, FirstName, LastName, Email, Phone",
        "Lead": "Id, FirstName, LastName, Company, Status, Email",
        "Opportunity": "Id, Name, StageName, Amount, CloseDate",
    }

    fields = field_map.get(sobject, "Id, Name")
    query = f"SELECT {fields} FROM {sobject}"
    results = sf.query_all(query)
    records = results.get("records", [])

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
    print("Salesforce CLI Tool")
    print("=" * 60)

    # Authenticate
    print("\n[*] Authenticating to Salesforce...")
    sf = authenticate()
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
            query_records(sf, sobject, int(limit))
        elif choice == "2":
            create_record(sf, sobject)
        elif choice == "3":
            update_record(sf, sobject)
        elif choice == "4":
            delete_record(sf, sobject)
        elif choice == "5":
            export_to_csv(sf, sobject)


if __name__ == "__main__":
    main()
