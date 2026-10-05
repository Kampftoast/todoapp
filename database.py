from sqlalchemy import create_engine, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime, timezone
from pwdlib import PasswordHash 

engine = create_engine("sqlite+pysqlite:///data.db")

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str]= mapped_column(String, nullable=False)
    description: Mapped[str|None] = mapped_column(String)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

Base.metadata.create_all(engine)    

#----------------
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

#-----------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize only default users
def init_users():
    db = SessionLocal()
    password_hasher = PasswordHash.recommended()
    try:
        for username in ["userA", "userB"]:
            user = db.query(User).filter(User.username == username).first()
            if user is None:
                db.add(User(
                    username=username,
                    password_hash= password_hasher.hash(username)
                    ))
                db.commit()
    finally:
        db.close()