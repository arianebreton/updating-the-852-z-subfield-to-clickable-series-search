import pandas as pd
import re
from playwright.sync_api import sync_playwright

# Read spreadsheet
df = pd.read_excel("series_test.xlsx")

results = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    for index, row in df.iterrows():

        title = row["Title"]
        url = row["Search URL"]

        print(f"\nProcessing: {title}")

        try:

            page.goto(url)

            page.wait_for_timeout(5000)

            body_text = page.locator("body").inner_text()

            match = re.search(
                r"\d+-\d+\s+of\s+([\d,]+)\s+Results",
                body_text
            )

            if match:
                count = int(
                    match.group(1).replace(",", "")
                )
                print(f"Results found: {count}")

            else:
                count = None
                print("Count not found")

        except Exception as e:

            count = None
            print(f"Error: {e}")

        results.append(count)

    browser.close()

# Add result counts
df["Result Count"] = results

# Flag records that need review
df["Review"] = df["Result Count"].apply(
    lambda x: "REVIEW"
    if pd.isna(x) or x == 0
    else ""
)

# Flag very large series
df["Very Large Series"] = df["Result Count"].apply(
    lambda x: "500+ RESULTS"
    if pd.notna(x) and x > 500
    else ""
)

# Save results
df.to_excel(
    "series_test_results.xlsx",
    index=False
)

print("\nDone!")