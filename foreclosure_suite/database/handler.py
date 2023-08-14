import mysql.connector
import psycopg2
import yaml

from foreclosure_suite.database import schema

class DatabaseHandler:

    def __init__(self):
        self.conn = None
        self.is_connected = False
        self.connection_data = None

    def __del__(self):
        if self.is_connected is True:
            self.disconnect()

    def create_table(self, table_name, schema):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});"
        self.cursor.execute(query)
        self.conn.commit()

    def disconnect(self):
        if self.is_connected is False:
            return
        self.conn.close()
        self.is_connected = False
        return
    
    def query(self, query: str):
        """
        Receive SQL query and runs it
        :param query: The SQL query to run in MySQL
        :return: returns the records from the current recordset
        """

        connection = self.conn if self.is_connected else self.connect() 

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
    
    def insert(self,table , data):
        print(f'inserting data into {table} ... ')

class MySQLHandler(DatabaseHandler):
    """
    This handler handles connection and execution of the MySQL statements.
    """
    def __init__(self):

        super().__init__()

        with open('config.yaml') as config:
            self.connection_data = yaml.safe_load(config)['databases']['mysql']

        self.connect()
        self.cursor = self.conn.cursor()

    def connect(self, connection_data = None):
        
        if self.is_connected is True:
            return self.conn 
        
        self.connection_data = connection_data if connection_data else self.connection_data
        
        self.conn = mysql.connector.connect(**self.connection_data)
        self.is_connected = True

        return self.conn

    
class PostgresHandler(DatabaseHandler):

    def __init__(self):

        super().__init__()

        with open('config.yaml') as config:
            self.connection_data = yaml.safe_load(config)['databases']['postgres']

        self.connect()
        self.cursor = self.conn.cursor()

    def connect(self, connection_data = None):
        
        if self.is_connected is True:
            return self.conn 
        
        self.connection_data = connection_data if connection_data else self.connection_data
        
        self.conn = psycopg2.connect(**self.connection_data)
        self.is_connected = True

        return self.conn

def main():

    handler = PostgresHandler()
    handler.create_table('property', schema.property_table)
    handler.create_table('auction', schema.auction_table)
    

if __name__ == '__main__':
    
    main()