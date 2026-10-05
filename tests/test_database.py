from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pwdlib import PasswordHash
from database import Base, User

password_hasher = PasswordHash.recommended()

test_engine = create_engine(
    "sqlite://",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
    )

Base.metadata.create_all(bind=test_engine)

def init_users():
    db = TestSessionLocal()
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


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
