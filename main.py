import pdfplumber
import os
import re

from dotenv import load_dotenv
load_dotenv() 


def get_tables_and_text_from_file(file_path: str) -> tuple[dict, dict]:
    tables_found = {}
    extracted_text = {}

    # Open PDF file
    with pdfplumber.open(file_path) as pdf:
        # Loop through pages
        for page_num, page in enumerate(pdf.pages, 1):
            tables_found[page_num] = page.extract_tables()
            extracted_text[page_num] = page.extract_text()

    return tables_found, extracted_text


def filter_transaction_tables(tables_found: dict) -> dict:
    transaction_tables = {}

    target_headers = [
        "Fecha\nde la\noperación",
        "Fecha\nde cargo",
        "Descripción del movimiento",
        "Monto"
    ]

    for page_num, tables in tables_found.items():
        matched_tables = []
        for table in tables:
            # Check if first row matches the target headers
            if table[0] == target_headers:
                matched_tables.append(table)
        if len(matched_tables) > 0:
            transaction_tables[page_num] = matched_tables
    
    return transaction_tables


def fill_missing_values_on_tables(tables: dict, raw_text: dict) -> dict:
    cleaned_tables = {}

    for page_num, tables_on_page in tables.items():
        cleaned_page_tables = []

        # Loop through tables
        for table_num, table in enumerate(tables_on_page, 1):
            cleaned_table = [table[0]]
            for table_row in table[1:]:
                if None in table_row or "" in table_row:
                    print(f"Page {page_num}, table {table_num} has a missing value:")
                    print(f"Original row: {[cell for cell in table_row]}")
                    cleaned_row = fill_row_with_missing_values(table_row, raw_text[page_num])
                    print(f"Cleaned row: {[cell for cell in cleaned_row]}\n")
                else:
                    cleaned_row = table_row
                cleaned_table.append(cleaned_row)

            cleaned_page_tables.append(cleaned_table)

        cleaned_tables[page_num] = cleaned_page_tables
    
    return cleaned_tables


def fill_row_with_missing_values(row, extracted_text):
    # Create a partial representation of the row by joining all known values as a single string
    # Missing values are replaced with empty strings
    partial_row = " ".join([str(cell) if cell else "" for cell in row]).strip()
    
    # Iterate through each line in the extracted text to find a match with the partial row
    for line in extracted_text.splitlines():
        if partial_row in line:
            
            # Find all date matches in the line using the format "dd-mmm-yyyy"
            date_matches = re.findall(r"\d{2}-[a-zA-Z]{3}-\d{4}", line)

            # Find the first monetary value in the line, which may include "+" or "-" and proper formatting
            monto_match = re.search(r"[\+\-]?\s*\$[\d,]+\.\d{2}", line)
            
            # If the first column (row[0]) is missing, fill it with the first date found
            if row[0] is None and len(date_matches) > 0:
                row[0] = date_matches[0]

            # If the second column (row[1]) is missing, fill it with the second date found (if it exists)
            if row[1] is None and len(date_matches) > 1:
                row[1] = date_matches[1]
            
            # If the last column (row[-1]) is missing, fill it with the monetary value found
            if row[-1] is None and monto_match:
                row[-1] = monto_match.group().strip()
            
            # Return the updated row with missing values filled
            return row  
    
    # If no match is found, return the row as is.
    return row  


def print_tables(tables_found: dict) -> None:
    for page_num, tables in tables_found.items():
        print(f"Page {page_num}: {len(tables)} tables found: ")

        for table_num, table in enumerate(tables, 1):
            print(f"\tTable {table_num} has {len(table)} rows:")
            print(f"\t{table[0]}\n")

        print("\n")


def main():
    file_path = os.getenv("FILE_PATH")
    
    # Extract raw tables and text
    raw_tables, raw_text = get_tables_and_text_from_file(file_path)

    # Filter relevant tables
    tables = filter_transaction_tables(raw_tables)

    # Clean missing (None) values
    tables = fill_missing_values_on_tables(tables, raw_text)

    # Print tables
    #print_tables(tables)


if __name__ == "__main__":
    main()