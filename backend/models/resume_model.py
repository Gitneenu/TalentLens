from pydantic import BaseModel

class Resume(BaseModel):
    filename: str
    content: str