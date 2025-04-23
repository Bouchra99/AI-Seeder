# from pydantic import BaseModel , Field 
# from openai import OpenAI
# import instructor 
# import datetime as dt 
# from typing import List 
# print("constructing the model ..")
# class DataModel(BaseModel) : 
#     name: str = Field(..., description="The title of the movie")
#     year: dt.date = Field(..., description="The release date of the movie")
#     director: str = Field(..., description="The director of the movie")
#     genre: List[str] = Field(..., description="A list of genres associated with the movie")

# client = instructor.from_openai(
#     OpenAI(
#         base_url="http://localhost:11434/v1", 
#         api_key="ollama", 

#     ), 
#     mode = instructor.Mode.JSON
# )

# response = client.messages.create(
#     model = "orca-mini:latest",
#     messages= [{
#         'role' : 'user', 
#         'content' : 'generate 1 movie following the provided model'
#     }], 
#     response_model= DataModel
# )
# print("generating ... ")
# print(response)
from pydantic import BaseModel, Field 
from openai import OpenAI
import instructor 
import datetime as dt 
from typing import List 
print("creating the model")
class DataModel(BaseModel):
    name: str = Field(..., description="The title of the movie")
    year: dt.date = Field(..., description="The release date of the movie")
    director: str = Field(..., description="The director of the movie")
    genre: List[str] = Field(..., description="A list of genres associated with the movie")

client = instructor.patch(OpenAI(
    base_url="http://localhost:11434/v1", 
    api_key="ollama",
))

print("generating the response")
response = client.chat.completions.create(
    # model="orca-mini:latest",
    model="qwen2.5:1.5b",

    messages=[{
        'role': 'user', 
        'content': 'Generate a movie following the provided model. Make sure to format the date as YYYY-MM-DD.'
    }], 
    response_model=DataModel
)

print(response)