# 852 Series Search Link Project

## Overview

This project supports better discovery of series' individual volumes in Primo. Series records contain the following public note in the 852 field: "See individual titles in series for full information." The goal of this project was to replace that note with a clickable link that performs a Series search in Primo, allowing users to retrieve all associated volume records directly from the series record.

## Project Goals

1. Identify series records that contain the holdings note:

> 852 $z See individual titles in series for full information

2. Generate Series search URLs for each series
3. Validate the titles used to generate the Series search for each URL by using the python Playwright library to perform the searches and write the results count to a csv to be compared against the expected number of volumes for each series
4. Once the URLs are confirmed, generate HTML links for use in the 852
5. Use the Alma holdings API to bulk update the 852 field with the HTML Series search URL for each series

## Workflow

### Phase 1: Generate and Validate Series Search Links

Using a spreadsheet containing:

- Series Title
- MMS ID
- Holdings ID
- Summary Holdings

Series search URLs were generated in Excel using a SUBSTITUTE() formula that inserts the series title into a Primo Series search URL template and replaces spaces with URL-encoded values (%20).

the validation script then:

- Executes the search using Playwright.
- Retrieves the number of matching results and writes it to a csv.
- Flags records requiring review.

Validation categories include:

- 0 results (possible title mismatch, the Series search uses the 830 field and the uniform title might not match)
- Very large result sets (>500 results)

### Phase 2: Updating the Holdings Record via the Alma Holdings API 

After validation of the titles used to generate the URLs, in the Sandbox:

1. Retrieve holdings records via Alma API.
2. Create a local backup of the original holdings XML.
3. Insert or update the HTML link in the 852 field.
4. Save a before/after change log.
5. Update holdings records in Alma Sandbox.
6. Verify successful updates before doing bigger batches and moving to production.

## Technologies Used

- Python
- pandas
- Playwright
- Alma APIs
- Excel

## Status

In progress: 852 fields have been updated with the series search in the Sandbox.

