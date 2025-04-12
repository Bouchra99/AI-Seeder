import os 

from dotenv import load_dotenv
from schema_parser import SchemaParser 

load_dotenv()
connectionString  = os.getenv("DB_CONNECTION_STRING")

db = SchemaParser(connectionString)
print(db.connected())

schema = db.parse_schema()

db.save_schema_to_file("schema.json")