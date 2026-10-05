from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#---
def authenticate_user(username: str, password: str) -> tuple[str, str]:
    return username, password
#---

def test_get_tasks_unauthorized():
    response = client.get("/api/tasks")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_tasks_as_user():
    credentials = authenticate_user("userA", "userA")
    response = client.get("/api/tasks", auth=credentials)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task_as_user():
    credentials = authenticate_user("userA", "userA")
    task_data = {
        "title": "Test Task",
        "description": "This is a test task.",
        "status": False,
        "priority": 1,
    }
    response = client.post("/api/task", json=task_data, auth=credentials)
    assert response.status_code == 200
    task = response.json()
    assert task["title"] == task_data["title"]
    assert task["description"] == task_data["description"]
    assert task["status"] == task_data["status"]
    assert task["priority"] == task_data["priority"]

def test_user_cannot_access_other_users_task():
    credentials_userA = authenticate_user("userA", "userA")
    task_data = {
        "title": "User A Task",
        "description": "Task for user A.",
        "status": False,
        "priority": 1,
    }
    response = client.post("/api/task", json=task_data, auth=credentials_userA)
    assert response.status_code == 200
    task_id = response.json()["id"]


    credentials_userB = authenticate_user("userB", "userB")
    response = client.get(f"/api/task/{task_id}", auth=credentials_userB)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_user_can_update_own_task():
    credentials_userA = authenticate_user("userA", "userA")
    task_data = {
        "title": "User A Task to Update",
        "description": "Task for user A.",
        "status": False,
        "priority": 1,
    }
    response = client.post("/api/task", json=task_data, auth=credentials_userA)
    assert response.status_code == 200
    task_id = response.json()["id"]

    update_data = {
        "title": "Updated Task Title",
        "description": "Updated description.",
        "status": True,
        "priority": 2,
    }
    response = client.put(f"/api/task/{task_id}", json=update_data, auth=credentials_userA)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["title"] == update_data["title"]
    assert updated_task["description"] == update_data["description"]
    assert updated_task["status"] == update_data["status"]
    assert updated_task["priority"] == update_data["priority"]

def test_user_cannot_update_other_users_task():
    credentials_userA = authenticate_user("userA", "userA")
    task_data = {
        "title": "User A Task to Update",
        "description": "Task for user A.",
        "status": False,
        "priority": 1,
    }
    response = client.post("/api/task", json=task_data, auth=credentials_userA)
    assert response.status_code == 200
    task_id = response.json()["id"]

    credentials_userB = authenticate_user("userB", "userB")
    update_data = {
        "title": "Updated Task Title by User B",
        "description": "Updated description by User B.",
        "status": True,
        "priority": 2,
    }
    response = client.put(f"/api/task/{task_id}", json=update_data, auth=credentials_userB)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}  

def test_user_can_delete_own_task():
    credentials_userA = authenticate_user("userA", "userA")
    task_data = {
        "title": "User A Task to Delete",
        "description": "Task for user A.",
        "status": False,
        "priority": 1,
    }
    response = client.post("/api/task", json=task_data, auth=credentials_userA)
    assert response.status_code == 200
    task_id = response.json()["id"]

    response = client.delete(f"/api/task/{task_id}", auth=credentials_userA)
    assert response.status_code == 200
    assert response.json() == {"detail": "Task deleted successfully"}

def test_user_cannot_delete_other_users_task():
    credentials_userA = authenticate_user("userA", "userA")
    task_data = {
        "title": "User A Task to Delete",
        "description": "Task for user A.",
        "status": False,
        "priority": 1,
    }
    response = client.post("/api/task", json=task_data, auth=credentials_userA)
    assert response.status_code == 200
    task_id = response.json()["id"]

    credentials_userB = authenticate_user("userB", "userB")
    response = client.delete(f"/api/task/{task_id}", auth=credentials_userB)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}    

def test_invalid_credentials():
    credentials = authenticate_user("invalidUser", "invalidPassword")
    response = client.get("/api/tasks", auth=credentials)
    assert response.status_code == 401

def test_create_task_starts_open():
    credentials = authenticate_user("userA", "userA")
    task_data = {
        "title": "Open Task",
        "description": "This task should start open.",
        "priority": 1,
    }
    response = client.post("/api/task", json=task_data, auth=credentials)
    assert response.status_code == 200
    task = response.json()
    assert task["status"] is False    