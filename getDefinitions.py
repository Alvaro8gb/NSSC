import mysql.connector

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the value of the API_KEY environment variable
HOST = os.getenv('HOST_SQL')
USER = os.getenv('USER_SQL')
PASS = os.getenv('PASS_SQL')
DATABASE = os.getenv('DB_SQL')  # the name of the database you want to connect to


class UMLSSQL:
    def __init__(self, host=HOST, user=USER, password=PASS, database=DATABASE):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def open_connection(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_cui_definition(self, cui: str):
        query = "SELECT definition FROM cui_definitions WHERE CUI='"+cui+"' and source='NCI'"
        rows = self.execute_query(query)
        return rows
    
    def get_label_from_cui(self, cui: str):
        query = "SELECT Label FROM MultiLang WHERE CUI='"+cui+"' and Lang='SPA'"
        rows = self.execute_query(query)
        if len(rows) == 0:
            query = "SELECT Label FROM MultiLang WHERE CUI='"+cui+"' and Lang='ENG'"
            rows = self.execute_query(query)
        return rows
    
    def get_languages(self):
        query = "SELECT DISTINCT(Lang) FROM MultiLang"
        rows = self.execute_query(query)
        return rows

    def show_db(self):
        cursor = self.connection.cursor()

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for t in tables:
            table_name = t[0]
            print(f"Tabla: {table_name}")
            cursor.execute(f"DESCRIBE {table_name}")
            estructura = cursor.fetchall()
            for col in estructura:
                col_name = col[0]
                type_data = col[1]
                print(f"   - Columna: {col_name}, Tipo de dato: {type_data}")


if __name__ == '__main__':

    UMLS_DB = UMLSSQL(HOST, USER, PASS, DATABASE)

    UMLS_DB.open_connection()

    #UMLS_DB.show_db()

    #print(UMLS_DB.get_languages()) Not in local

    CUI = 'C0000257'
    print("Example searching CUI:", CUI)
    print(UMLS_DB.get_cui_definition(CUI))

    UMLS_DB.close_connection()
