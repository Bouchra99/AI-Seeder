'''
This module extracts your database schema information 
'''
import sqlalchemy as sa
from sqlalchemy import create_engine, inspect, MetaData
from typing import Dict, List, Optional, Tuple, Any
import logging
import json

class SchemaParser : 
    def __init__(self, connectionString : str):
        self.connectionString = connectionString
        self.engine = None 
        self.inspector = None
        self.metadata  = None 
        self.schema_info= {}
        self.logger = logging.getLogger(__name__)

    def connected(self) -> bool :
        try : 
            self.logger.info("connecting to the database ..")
            self.engine = create_engine(self.connectionString)
            self.inspector = inspect(self.engine)
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            return True
        except Exception as excpt : 
            self.logger.error(f"failed to connect : {str(excpt)}")
            return False 
        
    def parse_schema(self) -> Dict : 
        "extract schenma info"

        if not self.engine or not self.inspector : 
            if not self.connected() : 
                raise ConnectionError("Could not connect to the db")
        
        schema_info = {
            "tables" : {},
            "relationships" :[]
        }

        # get all tables 

        for table in self.inspector.get_table_names() : 
            print(table)
            table_info = self._parse_table(table)
            schema_info["tables"][table] = table_info
        
        self._extract_relationships(schema_info)

        self.schema_info = schema_info

        return schema_info



    def _parse_table(self, table : str) -> Dict : 
        columns = []
        primary_keys = self.inspector.get_pk_constraint(table).get('constrained_columns',[])
        indexes = self.inspector.get_indexes(table)
        uniques = [idx for idx in indexes if idx.get('unique', False)] 

         # Get column information
        for column in self.inspector.get_columns(table):
            col_info = {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column.get("nullable", True),
                "default": str(column.get("default", "None")),
                "is_primary_key": column["name"] in primary_keys,
                "is_unique": any(column["name"] in idx["column_names"] for idx in uniques)
            }

            if hasattr(column["type"], "length") and column["type"].length:
                col_info["max_length"] = column["type"].length
                
          
            if isinstance(column["type"], sa.Enum):
                col_info["enum_values"] = column["type"].enums
                
            columns.append(col_info)
        
        return {
            "columns": columns,
            "primary_keys": primary_keys,
            "unique_constraints": [idx["column_names"] for idx in uniques]
        }

    def _extract_relationships(self, schema_info : Dict ) ->None : 

        for table in self.inspector.get_temp_table_names() : 
            fks = self.inspector.get_multi_foreign_keys(table)

            for fk in fks : 
                relationship  = {
                    "source_table" : table, 
                    "source_column" : fk["constrained_columns"],
                    "target_table": fk["referred_table"], 
                    "target_columns" : fk["referred_columns"], 
                    "name" : fk.get("name",""), 
                }    
                schema_info["relationships"].append(relationship)
    
    def save_schema_to_file(self, filename: str) -> None:
        """
        Save the schema information to a JSON file
        """
        if not self.schema_info:
            self.parse_schema()
            
        with open(filename, 'w') as f:
            json.dump(self.schema_info, f, indent=2)
        
        self.logger.info(f"Schema saved to {filename}")