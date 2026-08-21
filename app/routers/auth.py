from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import  Session
from app.database.database import get_db
from app.schemas.user import UserCreate,Userlogin,UserResponse
from app.models.user import User
from app.core.security import hash_password, verify_password,create_access_token,get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import authenticate_user
router = APIRouter(
    prefix= "/auth",
    tags=['Authenticaton']
)

@router.post("/signup")
def signup( user: UserCreate, db : Session = Depends(get_db)):
    hashed_password = hash_password(user.password)

    # checking weather the use already exits or not 
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409,detail="User Already exits.")
    # creating a sqlalchmey ovject 
    new_user = User(
        email = user.email,
        hashed_pass = hashed_password
    )
    # now we can use db.add command
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


@router.post("/login")
def login ( user : Userlogin, db : Session = Depends(get_db)):
    
    existing_user = authenticate_user(db,user.email,user.password)
    if not existing_user:
        raise HTTPException(status_code=401,detail="Invalid email or password")
    data_dict = {'sub': str(existing_user.id)}
    token = create_access_token(data=data_dict)
    return {
        "access_token": token,
        "token_type": "bearer"
    }    

@router.post("/token")
def token (form_data : OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    existing_user = authenticate_user(db,form_data.username,form_data.password)
    if not existing_user:
        raise HTTPException(status_code=401,detail="Invalid email or password")
    data_dict = {'sub': str(existing_user.id)}
    token = create_access_token(data=data_dict)
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me",response_model= UserResponse)
def me ( current_user = Depends(get_current_user)):
    return current_user