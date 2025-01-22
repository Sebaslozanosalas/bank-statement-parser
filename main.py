import pdfplumber
import re
import os
from dotenv import load_dotenv
load_dotenv() 

file_path = os.getenv("FILE_PATH")
print(file_path)

def extract_missing_values(row, extracted_text):
    partial_row = " ".join([str(cell) if cell else "" for cell in row]).strip()
    
    for line in extracted_text.splitlines():
        if partial_row in line:
            
            date_matches = re.findall(r"\d{2}-[a-zA-Z]{3}-\d{4}", line)
            monto_match = re.search(r"[\+\-]?\s*\$[\d,]+\.\d{2}", line)
            
            if row[0] is None and len(date_matches) > 0:
                row[0] = date_matches[0]  
            if row[1] is None and len(date_matches) > 1:
                row[1] = date_matches[1]  
            if row[-1] is None and monto_match:
                row[-1] = monto_match.group().strip()
            return row  
    return row  



with pdfplumber.open(file_path) as pdf:

    # Loop through pages
    for page_num, page in enumerate(pdf.pages, 1):

        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "explicit_horizontal_lines": page.curves + page.edges
        }

        tables = page.extract_tables(table_settings=table_settings)
        print(f"Page {page_num} tables found: {len(tables)}")


        extracted_text = page.extract_text()

        # Loop through tables
        for table_num, table in enumerate(tables, 1):
            table_headers = [
                "Fecha\nde la\noperación",
                "Fecha\nde cargo",
                "Descripción del movimiento",
                "Monto"
            ]
            if table[0] == table_headers:
                print(f"Table {table_num}: ")

                for i, row in enumerate(table[1:], 1):  # Exclue headings
                    if None in row:  # If there are missing values
                        print(f"Row {i} has missing values, extracting manually...")
                        row = extract_missing_values(row, extracted_text)
                        print(f"Row {i} corrected: {row}")
                    else:
                        print(f"Row {i}: {row}")
            else:
                print(f"Table {table_num} skipped: Header does not match.")

