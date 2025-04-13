"""
This module converts database schema into Pydantic models for validation and generation
"""

from typing import Dict, List, Any, Optional, Union, Type 
from pydantic import BaseModel, Field, create_model
from datetime import datetime, date
import sqlalchemy as sa
import re
import logging

logger = logging.getLogger(__name__)

# from sqlalchemy to pydantic
# Type mapping from SQLAlchemy to Python/Pydantic types
TYPE_MAPPING = {
    # String types
    'VARCHAR': (str, ...),
    'CHAR': (str, ...),
    'TEXT': (str, ...),
    'String': (str, ...),
    # Numeric types
    'INTEGER': (int, ...),
    'BIGINT': (int, ...),
    'SMALLINT': (int, ...),
    'Int': (int, ...),
    'NUMERIC': (float, ...),
    'DECIMAL': (float, ...),
    'FLOAT': (float, ...),
    'REAL': (float, ...),
    'Float': (float, ...),
    # Boolean type
    'BOOLEAN': (bool, ...),
    'Boolean': (bool, ...),
    # Date and time types
    'DATETIME': (datetime, ...),
    'TIMESTAMP': (datetime, ...),
    'DATE': (date, ...),
    'TIME': (str, ...),
    # JSON and JSONB
    'JSON': (Dict[str, Any], ...),
    'JSONB': (Dict[str, Any], ...)
}


class SchemaModelGenerator : 

    def __init__(self, schema_info : Dict):
        self.schema_info = schema_info 
        self.models = {}
        self.model_classes = {}

    def generateModels(self) -> Dict[str, Type[BaseModel]] : 

        for table, table_info in self.schema_info["tables"].items():
            self._generate_model_for_table(table, table_info)
        
        # Process relationships after all base models are created
        self._process_relationships()
        
        return self.model_classes
    
    def _generate_model_for_table(self, table, table_info) : 

        # convert camel_case to CamelCase 
        model = ''.join(word.capitalize() for word in table.split('_'))

        fields = {}

        for column in table_info["columns"] :
            field_info = self._create_field_for_column(column)
            fields[column["name"]] = field_info
        
        self.models[table] = {
            "name": model,
            "fields": fields
        }

        model_class = create_model(
            model,
            __base__=BaseModel,
            **fields
        )
        
        model_class.__doc__ = f"Generated model for table {table}"
        

        self.model_classes[table] = model_class

    def _create_field_for_column(self, column: Dict) -> tuple:
 
        column_type = column["type"]
        nullable = column.get("nullable", True)
        is_primary = column.get("is_primary_key", False)
        
        # Convert something like "VARCHAR(50)" to "VARCHAR"
        base_type = re.match(r'([A-Za-z]+)', column_type).group(1).upper()
        field_type, default_value = TYPE_MAPPING.get(base_type, (str, ...))
        
        if nullable and not is_primary:
            field_type = Optional[field_type]
            default_value = None
        
        field_kwargs = {}
        if "max_length" in column and field_type in (str, Optional[str]):
            field_kwargs["max_length"] = column["max_length"]
        
        # Handle enum types
        if "enum_values" in column:
            field_kwargs["enum_values"] = column["enum_values"]
        
        # Create a description for the field to guide AI generation
        description = f"Column {column['name']} of type {column_type}"
        if "is_primary_key" in column and column["is_primary_key"]:
            description += " (Primary Key)"
        if "is_unique" in column and column["is_unique"]:
            description += " (Unique)"
        
        field_obj = Field(default=default_value, description=description, **field_kwargs)
        
        return (field_type, field_obj)
    
    def _process_relationships(self) -> None:
    
        for relationship in self.schema_info.get("relationships", []):
            source_table = relationship["source_table"]
            target_table = relationship["target_table"]
            
           
            if source_table in self.model_classes and target_table in self.model_classes:
                source_model = self.model_classes[source_table]
                target_model = self.model_classes[target_table]
                
                source_cols = ", ".join(relationship["source_columns"])
                target_cols = ", ".join(relationship["target_columns"])
                
                rel_doc = f"\nForeign Key: {source_cols} references {target_table}({target_cols})"
                
                if source_model.__doc__:
                    source_model.__doc__ += rel_doc
                else:
                    source_model.__doc__ = rel_doc

    def get_model_json_schema(self, table_name: str) -> Dict:
        
        if table_name not in self.model_classes:
            raise ValueError(f"No model found for table {table_name}")
        
        model_class = self.model_classes[table_name]
        print(model_class.model_fields)
        return  model_class.schema()