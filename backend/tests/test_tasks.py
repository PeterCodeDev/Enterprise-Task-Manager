def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks_empty(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client):
    task_data = {
        "titulo": "Tarea de prueba",
        "descripcion": "Descripción de prueba"
    }
    response = client.post("/api/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Tarea de prueba"
    assert data["descripcion"] == "Descripción de prueba"
    assert data["completada"] is False
    assert "id" in data


def test_create_task_without_description(client):
    task_data = {"titulo": "Tarea sin descripción"}
    response = client.post("/api/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Tarea sin descripción"
    assert data["descripcion"] is None


def test_list_tasks_after_create(client):
    client.post("/api/tasks", json={"titulo": "Tarea 1"})
    client.post("/api/tasks", json={"titulo": "Tarea 2"})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2


def test_get_task_by_id(client):
    create_response = client.post("/api/tasks", json={"titulo": "Tarea específica"})
    task_id = create_response.json()["id"]
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["titulo"] == "Tarea específica"


def test_get_task_not_found(client):
    response = client.get("/api/tasks/999")
    assert response.status_code == 404


def test_update_task(client):
    create_response = client.post("/api/tasks", json={"titulo": "Original"})
    task_id = create_response.json()["id"]
    update_data = {
        "titulo": "Actualizada",
        "descripcion": "Nueva descripción"
    }
    response = client.put(f"/api/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Actualizada"
    assert data["descripcion"] == "Nueva descripción"


def test_update_task_not_found(client):
    response = client.put("/api/tasks/999", json={"titulo": "Test"})
    assert response.status_code == 404


def test_toggle_task(client):
    create_response = client.post("/api/tasks", json={"titulo": "Toggle test"})
    task_id = create_response.json()["id"]
    response = client.patch(f"/api/tasks/{task_id}/toggle")
    assert response.status_code == 200
    assert response.json()["completada"] is True
    response = client.patch(f"/api/tasks/{task_id}/toggle")
    assert response.status_code == 200
    assert response.json()["completada"] is False


def test_toggle_task_not_found(client):
    response = client.patch("/api/tasks/999/toggle")
    assert response.status_code == 404


def test_delete_task(client):
    create_response = client.post("/api/tasks", json={"titulo": "A eliminar"})
    task_id = create_response.json()["id"]
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404


def test_create_task_empty_title_fails(client):
    response = client.post("/api/tasks", json={"titulo": ""})
    assert response.status_code == 422
