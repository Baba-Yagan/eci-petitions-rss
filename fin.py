import json
import os

def process_entries(data, db_file):
    """
    Processes entries from a source, compares them with an existing database,
    prints new additions, and updates the database.
    """
    # --- 1. Load existing entries from our database file ---
    existing_entries = []
    if os.path.exists(db_file):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                existing_entries = json.load(f)
        except json.JSONDecodeError:
            # Handle case where the file is empty or corrupted
            print(f"Warning: Could not decode JSON from '{db_file}'. Starting fresh.")
            existing_entries = []

    # --- 2. Create a set of existing entry IDs for efficient lookups ---
    # We use .get('id') to avoid errors if an entry somehow lacks an 'id'
    existing_ids = {entry.get('id') for entry in existing_entries}

    # --- 3. Prepare to find new and all current ONGOING entries ---
    new_additions = []
    all_current_ongoing = []

    # Check if 'entries' key exists in the source data
    if 'entries' not in data:
        print("No 'entries' found in the source data")
        return

    # --- 4. Iterate through entries from the source file ---
    for entry in data['entries']:
        # We only care about entries with "ONGOING" status
        if entry.get('status') == "ONGOING":
            # Add every ONGOING entry from the source to this list
            all_current_ongoing.append(entry)

            # --- 5. Compare with existing IDs to find new additions ---
            entry_id = entry.get('id')
            if entry_id and entry_id not in existing_ids:
                new_additions.append(entry)

    # --- 6. Report the new additions to the user ---
    if new_additions:
        print("--- New ONGOING Entries Found ---")
        counter=0
        for entry in new_additions:
            message=entry.get('title')
            support_link=entry.get('supportLink')
            total_supporters=entry.get('totalSupporters')
            message+=f"\nlink: {support_link}\ntotal supporters right now:{total_supporters}\n"
            with open(str(counter)+".txt",'w') as f:
                f.write(message)
                counter+=1
            # Pretty-print the new entry's JSON for readability
            # print(json.dumps(entry, indent=2, ensure_ascii=False))
            # print("---------------------------------")
        print(f"Found {len(new_additions)} new additions.")
    else:
        print("No new ONGOING entries found.")

    # --- 7. Save the complete list of current ONGOING entries back to the DB file ---
    # This overwrites the old file, keeping our DB in sync with the latest source
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(all_current_ongoing, f, ensure_ascii=False, indent=4)

    print(f"\nUpdated database saved to '{db_file}' with {len(all_current_ongoing)} total ONGOING entries.")


def main():
    source_json_file = "1000.json"
    database_json_file = "ongoing_entries.json"  # File to store/compare ongoing entries

    try:
        with open(source_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Source file '{source_json_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{source_json_file}'.")
        return

    process_entries(data, database_json_file)

if __name__ == '__main__':
    main()
