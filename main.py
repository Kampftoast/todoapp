from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic
from database import Base, User,Task, get_db, init_users
from pwdlib import PasswordHash
from pydantic import BaseModel


app = FastAPI()
security = HTTPBasic()

#----

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: int = 0

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: bool | None = None
    priority: int | None = None
#-----
@app.on_event("startup")
def startup():
    init_users()

#----

def authenticate_user(
        credentials = Depends(security),
          db = Depends(get_db)
          ):
    password_hasher = PasswordHash.recommended()
    user = db.query(User).filter(User.username == credentials.username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not password_hasher.verify(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return user



#----
@app.get("/api/tasks")
def get_tasks(
    user = Depends(authenticate_user),
    db = Depends(get_db)
    ):
    tasks = db.query(Task).filter(Task.user_id == user.id).all()
    return tasks


@app.get("/api/task/{task_id}")
def get_task(
    task_id: int,
    user = Depends(authenticate_user),
    db = Depends(get_db)
    ):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user.id
    ).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/api/task")
def create_task(
    task: TaskCreate,
    user = Depends(authenticate_user),
    db = Depends(get_db)
    ):
    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        user_id=user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/api/task/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user = Depends(authenticate_user),
    db = Depends(get_db)
    ):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user.id
    ).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")


    task.title = task_data.title
    task.description = task_data.description
    task.status = task_data.status
    task.priority = task_data.priority

    db.commit()
    db.refresh(task)
    return task

@app.delete("/api/task/{task_id}")
def delete_task(
    task_id: int,
    user = Depends(authenticate_user),
    db = Depends(get_db)
    ):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user.id
    ).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}