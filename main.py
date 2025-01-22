import pdfplumber
import re


file_path = """
/Users/seb/Documents/Documents - Sebastian’s MacBook Pro/
Personal/Finanzas/BBVA - Estados de cuenta/BBVA 2025-01.pdf
"""

def extract_missing_values(row, extracted_text):
    """
    Busca valores faltantes en una fila usando el texto extraído manualmente.
    """
    # Combina los valores existentes de la fila en una cadena parcial
    partial_row = " ".join([str(cell) if cell else "" for cell in row]).strip()
    
    # Busca la línea completa en el texto extraído
    for line in extracted_text.splitlines():
        if partial_row in line:
            # Detectar fechas en formato dd-mmm-yyyy
            date_matches = re.findall(r'\d{2}-[a-zA-Z]{3}-\d{4}', line)
            # Detectar montos en formato + $12,345.67
            monto_match = re.search(r'[\+\-]?\s*\$[\d,]+\.\d{2}', line)
            
            # Reemplazar valores faltantes en la fila
            if row[0] is None and len(date_matches) > 0:
                row[0] = date_matches[0]  # Primera fecha encontrada
            if row[1] is None and len(date_matches) > 1:
                row[1] = date_matches[1]  # Segunda fecha encontrada
            if row[-1] is None and monto_match:
                row[-1] = monto_match.group().strip()
            return row  # Devuelve la fila corregida
    return row  # Devuelve la fila original si no encuentra coincidencia



with pdfplumber.open(file_path) as pdf:

    # Loop through pages
    for page_num, page in enumerate(pdf.pages, 1):

        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "explicit_horizontal_lines": page.curves + page.edges
        }

        tables = page.extract_tables(table_settings=table_settings)
        print(f'Page {page_num} tables found: {len(tables)}')


        extracted_text = page.extract_text()

        # Loop through tables
        for table_num, table in enumerate(tables, 1):
            if table[0] == ['Fecha\nde la\noperación', 'Fecha\nde cargo', 'Descripción del movimiento', 'Monto']:
                print(f'Table {table_num}: ')

                for i, row in enumerate(table[1:], 1):  # Excluir el encabezado
                    if None in row:  # Si hay valores faltantes
                        print(f"Row {i} has missing values, extracting manually...")
                        row = extract_missing_values(row, extracted_text)
                        print(f"Row {i} corrected: {row}")
                    else:
                        print(f"Row {i}: {row}")
            else:
                print(f'Table {table_num} skipped: Header does not match.')


        


# tables = tabula.read_pdf(file_path, pages="all", lattice=True, pandas_options={"header": 0}, multiple_tables=True)


# desired_columns = [
#     'Fecha\rde la\roperación',
#     'Fecha\rde cargo',
#     'Descripción del movimiento',
#     'Monto'
# ]

# # Itera sobre las tablas y filtra las que contienen las columnas deseadas
# for table in tables:
#     # Normaliza los nombres de las columnas para evitar problemas con saltos de línea o espacios
#     normalized_columns = [col.strip() for col in table.columns]
#     normalized_desired_columns = [col.strip() for col in desired_columns]
    
#     # Verifica si todas las columnas deseadas están en la tabla actual
#     if all(col in normalized_columns for col in normalized_desired_columns):
#         print(table.head(10))  # Muestra las primeras filas de las tablas coincidentes
