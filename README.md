This tool enriches a CSV file of LinkedIn profile URLs with phone numbers, emails, names, and location using a large JSONL database.

Requirements

Python 3.9 or higher
pandas (pip install pandas)
jsonlines (pip install jsonlines)
Excel or Google Sheets (for editing CSVs)

How it works

The JSONL index file is hashmapped in memory, so even large enrichments take only a few seconds to run.

Usage

Prepare your files:
Place your_data.csv (with LinkedIn profile URLs), pdl_linkedin_index.jsonl, and enrich_phone_numbers.py in the same folder.

Extract LinkedIn IDs:
In Excel or Google Sheets, use this formula to extract the ID from the URL:

=TEXTAFTER(A2, "/in/")

Save your CSV with the new column Linkedin_IDs.

Run the script:
Open a terminal in the folder and run:

python enrich_phone_numbers.py

Follow the prompts to select your files and specify the column name.

Get your results:

The script will create a new file your_data_enriched.csv with added columns for name, location, phone, email, and LinkedIn URL.

