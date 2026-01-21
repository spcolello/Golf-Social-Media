from sqlalchemy import UniqueConstraint, create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime, timedelta

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


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
    likes = relationship("Likes", back_populates="post")

class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like_post_user"),)

    post = relationship("Post", back_populates="likes")

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def create_user(db, username, email, password):
    user = User(username=username, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_post(db, user_id, score, course, caption=None):
    post = Post(user_id=user_id, score=score, course=course, caption=caption)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def add_like(db, post_id, user_id):
    like = Likes(post_id=post_id, user_id=user_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


db = SessionLocal()
try:
    create_user(db, "testuser", "test@email.com", "password")
    create_post(db, 1, 65, "Shuttle Meadow", "eagle on 18")
    create_user(db, "sean", "sean@email.com", "password")
    add_like(db, 1, 2)
    u = db.query(User).first()
    two = db.query(User).filter(User.id == 2).first()
    print(u.username, u.email, u.created_at, u.id, u.password, u.posts)
    print(u.posts[0].score, u.posts[0].course, u.posts[0].caption, u.posts[0].created_at, u.posts[0].likes)
finally:
    db.close()

