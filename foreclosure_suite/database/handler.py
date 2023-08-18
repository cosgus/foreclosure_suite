import mysql.connector
import psycopg2
import yaml
import pandas as pd

from foreclosure_suite.database.schema import Postgres

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

        with connection.cursor() as cur:
            cur.execute(query)

            result = cur.fetchall()
            # response = pd.DataFrame(
            #         result,
            #         columns=[x[0] for x in cur.description]
            #     )

            # connection.commit()

        return result

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
        q = """SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'"""
        result = self.query(q)
        return result

    def get_columns(self, table_name):
        """
        Show details about the table
        """
        q = f"DESCRIBE {table_name};"
        result = self.query(q)
        return result
    
    def insert(self,table_name =None , data=None, returning = None):

        if isinstance(data, dict):
            columns = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            if returning:
                query += f" RETURNING {returning}"
            self.cursor.execute(query, tuple(data.values()))
            print(f"        {table_name} data inserted successfully.")
        else:
            print("Invalid data format. Only dictionaries are supported for insertion.")

    
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

    def insert(self,table_name =None , data=None, returning = None):
        try:
            super().insert(table_name, data, returning)
            return True
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            return False

    def drop_all_tables(self):
        tables = self.get_tables()
        for table in tables:
            print(f'dropping {table}')
            self.cursor.execute(f'DROP TABLE {table[0]} CASCADE;')
        self.conn.commit()


    def create_databases(self):

        schema = Postgres()
        self.create_table('property', schema.property_table)
        self.create_table('court_case', schema.court_case)
        self.create_table('auction', schema.auction_table)
        self.create_table('party', schema.party)
        self.create_table('case_party', schema.court_case_party)
        self.create_table('auction_party', schema.auction_party)
        self.create_table('no_folio', schema.no_folio)
        self.create_table('multiple_parcel', schema.multiple_parcel)
    
    def reset(self):
        self.drop_all_tables()
        self.create_databases()

class ForeclosureHandler:

    def __init__(self):
        
        self.handler = PostgresHandler()
        self.aid = None
        self.property_info = None
        self.auction_data = None
        self.docket_count = None
        self.pk = {}

    def set_data(self, data):
        self.aid = data['aid']
        self.auction_data = data['auction_data']
        self.property_info = data['property_info']
        self.docket_count = data['docket_count']

    def handle_data(self, data):

        if self.aid != data['aid']:
            self.set_data(data)
        
        self.pk['property'] = self.handler.insert('property', self.property_info)
    
        case_data = self.create_case_data()
        self.pk['case'] = self.handler.insert('court_case', case_data)

        party_data = self.create_party_data()
        self.pk['party'] = self.handler.insert('party', party_data)

        auction_data = self.create_auction_data()
        self.pk['auction'] = self.handler.insert('auction', auction_data)

        court_case_party = {
            'party_id': self.pk['party'],
            'case_id': self.pk['case']
        }
        self.handler.insert('case_party', court_case_party)

        auction_party = {
            'party_id': self.pk['party'],
            'auction_id': self.pk['auction']
        }
        self.handler.insert('auction_party', auction_party)

    def create_case_data(self):
        case_data = {
            'case_number': self.auction_data['case_number'],
            'docket_count': self.docket_count
        }
        return case_data
    
    def create_party_data(self):
        party_data = {}
        for plaintiff in self.auction_data['plaintiff']:
            party_data.update({
                'party_name': plaintiff,
                'side': 'plaintiff'
                })
        for defendant in self.auction_data['defendant']:
            party_data.update({
                'party_name': defendant,
                'side': 'defendant'
                })
        return party_data
    
    def create_auction_data(self):
        auction_data = self.auction_data.copy()
        auction_data.pop('count_description')
        auction_data.pop('parcel_id')
        auction_data.pop('case_number')
        auction_data.pop('property_address')
        auction_data.pop('assessed_value')
        auction_data.pop('property_appraiser_legal_description')
        auction_data.pop('defendant')
        auction_data.pop('plaintiff')
        
        auction_data.update({'time': self.auction_data['time'][11:16]})
        auction_data.update({'date': self.auction_data['time'][:10]})
        auction_data.update({'property_id':self.pk['property']})
        auction_data.update({'case_id': self.pk['case']})

        return auction_data

if __name__ == '__main__':
    PostgresHandler().reset()