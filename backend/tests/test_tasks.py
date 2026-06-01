from app.models import UserModel, TaskModel


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "password_hash" not in data
    assert "password" not in data


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "password123"
    })
    response = client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "password456"
    })
    assert response.status_code == 409


def test_register_short_password(client):
    response = client.post("/api/auth/register", json={
        "email": "short@example.com",
        "password": "123"
    })
    assert response.status_code == 422


def test_login_success(client):
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    response = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "password": "password123"
    })
    response = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/api/auth/login", json={
        "email": "noone@example.com",
        "password": "password123"
    })
    assert response.status_code == 401


def test_tasks_without_auth(client):
    response = client.get("/api/tasks")
    assert response.status_code == 401


def test_list_tasks_empty(client, auth_headers):
    response = client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client, auth_headers):
    task_data = {
        "titulo": "Tarea de prueba",
        "descripcion": "Descripción de prueba"
    }
    response = client.post("/api/tasks", json=task_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Tarea de prueba"
    assert data["descripcion"] == "Descripción de prueba"
    assert data["completada"] is False
    assert "id" in data
    assert "user_id" in data


def test_create_task_without_description(client, auth_headers):
    task_data = {"titulo": "Tarea sin descripción"}
    response = client.post("/api/tasks", json=task_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Tarea sin descripción"
    assert data["descripcion"] is None


def test_list_tasks_after_create(client, auth_headers):
    client.post("/api/tasks", json={"titulo": "Tarea 1"}, headers=auth_headers)
    client.post("/api/tasks", json={"titulo": "Tarea 2"}, headers=auth_headers)
    response = client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2


def test_get_task_by_id(client, auth_headers):
    create_response = client.post(
        "/api/tasks",
        json={"titulo": "Tarea específica"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["titulo"] == "Tarea específica"


def test_get_task_not_found(client, auth_headers):
    response = client.get("/api/tasks/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_task(client, auth_headers):
    create_response = client.post(
        "/api/tasks",
        json={"titulo": "Original"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]
    update_data = {
        "titulo": "Actualizada",
        "descripcion": "Nueva descripción"
    }
    response = client.put(
        f"/api/tasks/{task_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Actualizada"
    assert data["descripcion"] == "Nueva descripción"


def test_update_task_not_found(client, auth_headers):
    response = client.put(
        "/api/tasks/999",
        json={"titulo": "Test"},
        headers=auth_headers
    )
    assert response.status_code == 404


def test_toggle_task(client, auth_headers):
    create_response = client.post(
        "/api/tasks",
        json={"titulo": "Toggle test"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]
    response = client.patch(f"/api/tasks/{task_id}/toggle", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["completada"] is True
    response = client.patch(f"/api/tasks/{task_id}/toggle", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["completada"] is False


def test_toggle_task_not_found(client, auth_headers):
    response = client.patch("/api/tasks/999/toggle", headers=auth_headers)
    assert response.status_code == 404


def test_delete_task(client, auth_headers):
    create_response = client.post(
        "/api/tasks",
        json={"titulo": "A eliminar"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]
    response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_task_not_found(client, auth_headers):
    response = client.delete("/api/tasks/999", headers=auth_headers)
    assert response.status_code == 404


def test_create_task_empty_title_fails(client, auth_headers):
    response = client.post(
        "/api/tasks",
        json={"titulo": ""},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_user_cannot_see_other_users_tasks(client, auth_headers, db_session):
    client.post("/api/tasks", json={"titulo": "Mi tarea"}, headers=auth_headers)

    other_user = UserModel(
        email="other@example.com",
        password_hash="hashed"
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    other_task = TaskModel(
        titulo="Tarea de otro usuario",
        user_id=other_user.id
    )
    db_session.add(other_task)
    db_session.commit()

    response = client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["titulo"] == "Mi tarea"
