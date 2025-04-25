import csv
import os
import re

PHONEBOOK_FILE = "phonebook_data.csv"

def ensure_file():
    if not os.path.exists(PHONEBOOK_FILE):
        with open(PHONEBOOK_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'phone'])

def find_records_by_pattern(pattern):
    results = []
    with open(PHONEBOOK_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (pattern.lower() in row['name'].lower() or 
                pattern in row['phone']):
                results.append(row)
    return results

def upsert_user(name, phone):
    updated = False
    rows = []
    with open(PHONEBOOK_FILE, newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['name'].lower() == name.lower():
                row['phone'] = phone
                updated = True
            rows.append(row)
    if not updated:
        rows.append({'name': name, 'phone': phone})
    with open(PHONEBOOK_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return "Updated" if updated else "Inserted"

def validate_phone(phone):
    return re.match(r'^\+?\d{7,15}$', phone) is not None

def bulk_insert_users(user_list):
    invalid_entries = []
    valid_entries = []
    for name, phone in user_list:
        if not validate_phone(phone):
            invalid_entries.append({'name': name, 'phone': phone, 'error': 'Invalid phone format'})
        else:
            valid_entries.append({'name': name, 'phone': phone})
    if valid_entries:
        with open(PHONEBOOK_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'phone'])
            if os.stat(PHONEBOOK_FILE).st_size == 0:
                writer.writeheader()
            writer.writerows(valid_entries)
    return invalid_entries

def get_paginated_records(limit=10, offset=0):
    with open(PHONEBOOK_FILE, newline='') as f:
        reader = csv.DictReader(f)
        records = list(reader)
        return records[offset:offset+limit]

def delete_by_username_or_phone(value):
    deleted_count = 0
    rows = []
    with open(PHONEBOOK_FILE, newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['name'].lower() == value.lower() or row['phone'] == value:
                deleted_count += 1
            else:
                rows.append(row)
    if deleted_count > 0:
        with open(PHONEBOOK_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    return deleted_count

def show_phonebook():
    print("\n1. Show all\n2. Filter by pattern\n3. Paginated view")
    choice = input("Choose option: ")
    if choice == "1":
        with open(PHONEBOOK_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(f"{row['name']}: {row['phone']}")
    elif choice == "2":
        pattern = input("Enter search pattern: ")
        results = find_records_by_pattern(pattern)
        for row in results:
            print(f"{row['name']}: {row['phone']}")
    elif choice == "3":
        limit = int(input("Records per page: "))
        offset = 0
        while True:
            records = get_paginated_records(limit, offset)
            if not records:
                print("No more records.")
                break
            for row in records:
                print(f"{row['name']}: {row['phone']}")
            print(f"\nPage {offset//limit + 1}")
            nav = input("Next (n), Previous (p), Quit (q): ").lower()
            if nav == 'n':
                offset += limit
            elif nav == 'p' and offset >= limit:
                offset -= limit
            elif nav == 'q':
                break

def main():
    ensure_file()
    while True:
        print("\n1. View Phonebook\n2. Add/Update Entry\n3. Bulk Import\n4. Delete Entry\n5. Exit")
        choice = input("Choose option: ")
        if choice == "1":
            show_phonebook()
        elif choice == "2":
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            result = upsert_user(name, phone)
            print(f"Record {result} successfully!")
        elif choice == "3":
            print("Enter name and phone pairs (leave name blank to finish):")
            user_list = []
            while True:
                name = input("Name: ")
                if not name:
                    break
                phone = input("Phone: ")
                user_list.append((name, phone))
            invalid = bulk_insert_users(user_list)
            if invalid:
                print("\nInvalid entries:")
                for entry in invalid:
                    print(f"{entry['name']}: {entry['phone']} - {entry['error']}")
            print(f"\nSuccessfully processed {len(user_list) - len(invalid)} entries")
        elif choice == "4":
            value = input("Enter name or phone to delete: ")
            count = delete_by_username_or_phone(value)
            print(f"Deleted {count} records")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")

main()
