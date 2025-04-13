import os 

from dotenv import load_dotenv
from schema_parser import SchemaParser 
from schema_models import SchemaModelGenerator
import json 

load_dotenv()
connectionString  = os.getenv("DB_CONNECTION_STRING")

db = SchemaParser(connectionString)
print(db.connected())

schema = db.parse_schema()

model = SchemaModelGenerator(schema)

print(model.generateModels())

# db.save_schema_to_file("schma.json")


with open("model.json", 'w') as f:
    json.dump(model.get_model_json_schema("movie") , f, indent=2)