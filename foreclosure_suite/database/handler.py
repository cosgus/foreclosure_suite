import mysql.connector
import pandas as pd
import yaml
from foreclosure_suite.database import queries

class BaseHandler:
    """
    This handler handles connection and execution of the MySQL statements.
    """

    def __init__(self):

        with open('config.yaml') as config:
            self.connection_data = yaml.safe_load(config)['databases']['mysql']

        self.connection = None
        self.is_connected = False

    def __del__(self):
        if self.is_connected is True:
            self.disconnect()

    def connect(self, connection_data = None):
        if self.is_connected is True:
            return self.connection
        
        self.connection_data = connection_data if connection_data else self.connection_data
        
        connection = mysql.connector.connect(**self.connection_data)
        self.is_connected = True
        self.connection = connection

        return self.connection

    def disconnect(self):
        if self.is_connected is False:
            return
        self.connection.close()
        self.is_connected = False
        return

    def query(self, query: str):
        """
        Receive SQL query and runs it
        :param query: The SQL query to run in MySQL
        :return: returns the records from the current recordset
        """

        connection = self.connection if self.is_connected else self.connect() 

        with connection.cursor(dictionary=True, buffered=True) as cur:
            cur.execute(query)

            result = cur.fetchall()
            response = pd.DataFrame(
                    result,
                    columns=[x[0] for x in cur.description]
                )

            connection.commit()

        return response

    def select_data(self, query, params=None):
        self.cursor.execute(query, params) if params else self.cursor.execute(query)
        result = self.cursor.fetchall()
        if result:
            columns = [col[0] for col in self.cursor.description]
            data = [dict(zip(columns, row)) for row in result]
            return data
        else:
            return []

    def get_tables(self):
        """
        Get a list with all of the tabels in MySQL
        """
        q = "SHOW TABLES;"
        result = self.query(q)
        return result

    def get_columns(self, table_name):
        """
        Show details about the table
        """
        q = f"DESCRIBE {table_name};"
        result = self.query(q)
        return result

def main():

    handler = BaseHandler()
    handler.connect()
    handler.query(queries.create_property_table)


if __name__ == '__main__':
    
    main()