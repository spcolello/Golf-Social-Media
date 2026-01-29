from sqlalchemy import UniqueConstraint, create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from .auth import create_access_token, decode_access_code


DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

app = FastAPI()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    posts = relationship("Post", back_populates="owner")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    score = Column(Integer, nullable=False)
    course = Column(String, nullable=False)
    caption = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)

    owner = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post")

class Like(Base):
    __tablename__ = "like"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like_post_user"),)

    post = relationship("Post", back_populates="likes")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain, hashed)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_code(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    username: str = payload.get("user_id")

    if username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

# pydantic schemas
class UserCreate(BaseModel):
    username: str
    password: str
    email: str | None = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class LogIn(BaseModel):
    username: str
    password: str

class PostCreate(BaseModel):
    user_id: int
    score: int
    course: str
    caption: str | None = None

class PostOut(BaseModel):
    id: int
    score: int
    course: str
    caption: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class LikeIn(BaseModel):
    user_id: int
    post_id: int

class LikeOut(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True  

@app.post("/user")
def create_user(info: UserCreate, db: Session = Depends(get_db)):
    user = User(username = info.username, email = info.email, password=hash_password(info.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    db.refresh(user)
    return UserOut.from_orm(user)

@app.post("/post")
def create_post(info: PostCreate,  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = Post(user_id=current_user.id, score=info.score, course=info.course, caption=info.caption)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@app.post("/like")
def add_like(info: LikeIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    like = Like(post_id=info.post_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return like

@app.post("/unlike")
def remove_like(info: LikeIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    like = db.query(Like).filter(
        Like.post_id == info.post_id,
        Like.user_id == info.user_id
    )
    db.delete(like)
    db.commit()
    db.refresh(like)
    return {"detail": "like removed"}


@app.post("/login")
def login(info: LogIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == info.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not verify_password(info.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    token = create_access_token({"user_id": info.username})

    return {"access_token": token, "token_type": "bearer"}  

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
if __name__ == "__main__":
    # reset_db.py
    from backend.main import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database schema dropped and recreated.")
