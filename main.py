from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List, Annotated
import uvicorn
import shutil
import os
import imghdr
from pymongo import MongoClient

models.Base.metadata.create_all(bind=engine)

# MongoDB setup
MONGO_URL = "mongodb://localhost:27017"
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["user_database"]
mongo_collection = mongo_db["profiles"]

app = FastAPI()

#for cors html
origins = [
    "http://127.0.0.1:5500",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    profile_picture: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def root():
    return {"message": "Welcome to User Registration API"}

@app.post("/register/")
async def register_user(db: db_dependency, full_name: str = Form(...),
                         email: EmailStr = Form(...),
                         password: str = Form(...),
                         phone: str = Form(...), 
                         my_file: UploadFile = File(...) ):
  
    print(f"Received user data: {full_name,email, password, phone}")
    print(f"Received file: {my_file}")

    #PP dir in server
    profile_picture_dir = "profile_pictures"
    if not os.path.exists(profile_picture_dir):
        os.makedirs(profile_picture_dir) 

    #if email or phone already exists    
    user_check = db.query(models.User).filter((models.User.email == email) | (models.User.phone == phone)).first()
    if user_check:
        raise HTTPException(status_code=400, detail="Email or phone already registered")
    
    # if the uploaded file is an image
    if imghdr.what(my_file.file) not in ('jpeg', 'png', 'gif'):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload an image (jpg, png, or gif).")

    try:
        profile_picture_path = f"profile_pictures/{full_name}_{my_file.filename}"
        print(f"Saving file to: {profile_picture_path}")
        with open(profile_picture_path, "wb") as buffer:
            shutil.copyfileobj(my_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"There was an error uploading the file: {str(e)}")
        # return {"message": "There was an error uploading the file"}
    finally:
        my_file.file.close()

    try:
        # Creating user
        db_user = models.User(full_name=full_name, email=email, password=password, phone=phone)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print("your user id: ",db_user.id,)
    
        # # Creatiing profile using postgresdb
        # db_profile = models.Profile(user_id=db_user.id, profile_picture=profile_picture_path)
        # db.add(db_profile)
        # db.commit()
        # db.refresh(db_profile)

        # Creatiing profile using mongodb
        try:
            mongo_collection.insert_one({"user_id": db_user.id, "profile_picture": profile_picture_path})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Profile picture couldn't be uploaded to MongoDB: {str(e)}")
        mongo_client.close()


        return {"message": f"User registered successfully and your user_id is {db_user.id}"}
    except Exception as e:
        db.rollback()  # Rollback if exception occurs
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")
    
@app.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: db_dependency):
    # print(user_id,"id2")
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # db_profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

    #Mongodb
    mongo_user = mongo_collection.find_one({"user_id": user_id})
    if mongo_user:  # if user exists 
        profile_picture = mongo_user.get('profile_picture', None)  # Use get method with default value
    else:
        raise HTTPException(status_code=404, detail="User not found")
    print(mongo_user)


    user_details = UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        email=db_user.email,
        phone=db_user.phone,
        # profile_picture=db_profile.profile_picture if db_profile else None
        profile_picture = profile_picture
    )
    
    mongo_client.close()
    return user_details

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)