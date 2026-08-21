from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr = Field(
        description="Enter a valid email address."
    )
    password: str

class Userlogin(BaseModel):
    email: EmailStr 
    password: str

class UserResponse(BaseModel):
    id: int 
    email : EmailStr