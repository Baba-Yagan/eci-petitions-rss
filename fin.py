import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET

def generate_rss(entries, output_file="petitions.xml"):
    """
    Generate RSS feed from petition entries.
    """
    # Create RSS root element
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    # Channel metadata
    ET.SubElement(channel, "title").text = "EU Petitions - ONGOING"
    ET.SubElement(channel, "description").text = "Latest ongoing EU petitions from the European Citizens' Initiative"
    ET.SubElement(channel, "link").text = "https://register.eci.ec.europa.eu"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Add items for each petition
    for entry in entries:
        item = ET.SubElement(channel, "item")
        
        title = entry.get('title', 'Untitled Petition')
        ET.SubElement(item, "title").text = title
        
        support_link = entry.get('supportLink', '')
        ET.SubElement(item, "link").text = support_link
        ET.SubElement(item, "guid").text = str(entry.get('id', ''))
        
        total_supporters = entry.get('totalSupporters', 0)
        description = f"Total supporters: {total_supporters}"
        if support_link:
            description += f"\nSupport link: {support_link}"
        ET.SubElement(item, "description").text = description
        
        # Use current time as pub date since we don't have creation date
        ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Write RSS to file
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"RSS feed generated: {output_file}")

def process_entries(data, db_file):
    """
    Processes entries from a source, compares them with an existing database,
    generates RSS feed, and updates the database.
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

    # --- 6. Generate RSS feed from all current ongoing entries ---
    generate_rss(all_current_ongoing)
    
    # --- 7. Report the new additions to the user ---
    if new_additions:
        print(f"Found {len(new_additions)} new ONGOING entries.")
        for entry in new_additions:
            title = entry.get('title', 'Untitled')
            supporters = entry.get('totalSupporters', 0)
            print(f"- {title} ({supporters} supporters)")
    else:
        print("No new ONGOING entries found.")

    # --- 8. Save the complete list of current ONGOING entries back to the DB file ---
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
