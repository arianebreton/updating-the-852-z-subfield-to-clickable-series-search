import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from lxml import etree

# Setup
load_dotenv()

API_KEY = os.getenv("ALMA_API_KEY")

BASE_URL = os.getenv("ALMA_BASE_URL")

INPUT_FILE = "holding_update_test.xlsx"

PUT_ENABLED = True

# Safety Checks
if not API_KEY:
    raise RuntimeError(
        "ALMA_API_KEY not found in .env"
    )

# Create folders
Path("backups").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# Read spreadsheet
df = pd.read_excel(INPUT_FILE)

# Limit processing to the first 5 data rows for test
# df = df.head(5)

change_log = []

# Process records
for index, row in df.iterrows():

    mms_id = str(row["MMS ID"])
    holding_id = str(row["Holdings ID"])
    new_html = str(row["HTML"])

    print(
        f"\nProcessing MMS {mms_id} "
        f"Holdings {holding_id}"
    )

    endpoint = (
        f"{BASE_URL}/almaws/v1/bibs/"
        f"{mms_id}/holdings/{holding_id}"
    )

    response = requests.get(
        endpoint,
        params={
            "apikey": API_KEY,
            "format": "xml"
        },
        headers={
            "Accept": "application/xml"
        }
    )

    print(
        f"HTTP Status: {response.status_code}"
    )

    if response.status_code != 200:

        print("Skipping.")

        change_log.append({
            "MMS ID": mms_id,
            "Holdings ID": holding_id,
            "PUT Status": response.status_code,
            "Old 852z": "",
            "New 852z": new_html
        })

        continue

    # Save original XML
    original_path = (
        f"backups/"
        f"{mms_id}_{holding_id}_original.xml"
    )

    with open(
        original_path,
        "wb"
    ) as file:

        file.write(
            response.content
        )

    # Parse XML
    root = etree.fromstring(
        response.content
    )

    fields_852 = root.xpath(
        ".//*[local-name()='datafield']"
        "[@tag='852']"
    )

    if len(fields_852) != 1:

        print(
            "Unexpected number of 852 fields."
        )

        continue

    field_852 = fields_852[0]

    old_values = []

    existing_z = field_852.xpath(
        "./*[local-name()='subfield']"
        "[@code='z']"
    )

    for z in existing_z:

        if z.text:
            old_values.append(
                z.text
            )

        field_852.remove(z)

    namespace = etree.QName(
        field_852
    ).namespace

    if namespace:

        new_subfield = etree.Element(
            f"{{{namespace}}}subfield"
        )

    else:

        new_subfield = etree.Element(
            "subfield"
        )

    new_subfield.set(
        "code",
        "z"
    )

    new_subfield.text = new_html

    field_852.append(
        new_subfield
    )

    # Create updated XML
    modified_xml = etree.tostring(
        root,
        pretty_print=True,
        encoding="UTF-8",
        xml_declaration=True
    )

    put_status = "NOT RUN"

    # PUT updated record
    if PUT_ENABLED:

        print(
            "Sending PUT..."
        )

        put_response = requests.put(
            endpoint,
            params={
                "apikey": API_KEY,
                "format": "xml"
            },
            headers={
                "Content-Type": "application/xml",
                "Accept": "application/xml"
            },
            data=modified_xml
        )

        put_status = put_response.status_code

        print(
            f"PUT Status: {put_status}"
        )

    change_log.append({
        "MMS ID": mms_id,
        "Holdings ID": holding_id,
        "PUT Status": put_status,
        "Old 852z": " | ".join(old_values),
        "New 852z": new_html
    })

# Save change log
log_df = pd.DataFrame(
    change_log
)

log_df.to_csv(
    "logs/change_log.csv",
    index=False
)

print(
    "\nDone."
)

print(
"Review logs/change_log.csv for PUT results."
)