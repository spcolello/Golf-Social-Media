from sqlalchemy import UniqueConstraint, create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from datetime import datetime
from fastapi import FastAPI, Depends

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

@app.post("/user")
def create_user(username, password, email: str = None, db: Session = Depends(get_db)):
    user = User(username=username, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/post")
def create_post(user_id, score, course, caption=None,  db: Session = Depends(get_db)):
    post = Post(user_id=user_id, score=score, course=course, caption=caption)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@app.post("/like")
def add_like(post_id, user_id, db: Session = Depends(get_db)):
    like = Like(post_id=post_id, user_id=user_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


