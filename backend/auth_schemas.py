from pydantic import BaseModel, EmailStr

# --- Signup schema ---
class UserCreate(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    password: str

# --- Signin schema ---
class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: str
    full_name: str
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
