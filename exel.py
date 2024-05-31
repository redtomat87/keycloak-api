import openpyxl

def read_xlsx_file(file_path):
    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb['Request']
        column_names = ["Keycloak", "Keycloak environment", "Action", "Client ID", "Role name", "User login"]
        data_list = []

        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_data = [cell for cell in row if cell is not None]
            if row_data:
                data_list.append(row_data)
                row_dict = {
                    "Keycloak": row[0],
                    "Keycloak environment": row[1],
                    "Action": row[2],
                    "Client ID": row[3],
                    "Role name": row[4],
                    "User login": row[5]
                    }

        return data_list, row_dict
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []

file_path = "./Authorization_Template.xlsx"
list, dict = read_xlsx_file(file_path)
print(dict)
