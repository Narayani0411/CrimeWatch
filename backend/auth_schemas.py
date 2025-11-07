from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for incoming request data (Signup/Signin)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema for the data we return on a successful API call
class UserOut(BaseModel):
    # Use str for the MongoDB _id
    id: str 
    email: EmailStr

    class Config:
        # Necessary for Pydantic to handle MongoDB's object representation
        from_attributes = True

# Schema for the JWT Token we return
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"