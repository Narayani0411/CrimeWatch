from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from . import auth_schemas, auth_utils

# -----------------------------
# MongoDB Collection
# -----------------------------
USER_COLLECTION = auth_utils.USER_COLLECTION

# -----------------------------
# Router setup
# -----------------------------
router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

# JWT constants (must match values in auth_utils)
SECRET_KEY = auth_utils.SECRET_KEY
ALGORITHM = auth_utils.ALGORITHM


# -----------------------------
# Helper function for current user
# -----------------------------
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extract and validate the user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        # Lookup user in DB
        user = USER_COLLECTION.find_one({"email": email})
        if not user:
            raise credentials_exception

        return {"id": str(user["_id"]), "email": user["email"]}
    except JWTError:
        raise credentials_exception


# -----------------------------
# Signup route
# -----------------------------
@router.post("/signup", response_model=auth_schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: auth_schemas.UserCreate):
    """Handles user registration (Sign Up) using MongoDB."""

    # 1. Check if user already exists
    if USER_COLLECTION.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 2. Hash the password
    hashed_password = auth_utils.get_password_hash(user.password)

    # 3. Create the new user document
    new_user_doc = {
        "email": user.email,
        "hashed_password": hashed_password
    }

    # 4. Insert into MongoDB
    result = USER_COLLECTION.insert_one(new_user_doc)

    # 5. Prepare response
    user_out = {
        "id": str(result.inserted_id),
        "email": user.email
    }

    return user_out


# -----------------------------
# Signin route
# -----------------------------
@router.post("/signin", response_model=auth_schemas.Token)
def login_for_access_token(user_data: auth_schemas.UserCreate):
    """Handles user login (Sign In) and returns a JWT access token."""

    # 1. Find the user
    user_doc = USER_COLLECTION.find_one({"email": user_data.email})

    # 2. Verify existence and password
    if not user_doc or not auth_utils.verify_password(user_data.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create JWT token
    access_token = auth_utils.create_access_token(
        data={"sub": user_doc["email"]}
    )

    # 4. Return the token
    return {"access_token": access_token, "token_type": "bearer"}
