import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status, Query, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, case
import os
import shutil
import json
import secrets
import hashlib
import uuid
from datetime import datetime as dt, timedelta

from app.settings import settings
from app.logging_config import logger
from app.database import get_db
from app.models import UserModel, TaskModel, CategoryModel, SubtaskModel, AttachmentModel, CommentModel, ActivityLogModel, ApiTokenModel
from app.schemas import (
    UserCreate, UserResponse, UserLogin, Token, UserUpdate,
    TaskCreate, TaskUpdate, TaskResponse,
    CategoryCreate, CategoryResponse,
    PasswordChange,
    SubtaskCreate, SubtaskResponse,
    AttachmentResponse,
    CommentCreate, CommentResponse,
    ActivityLogResponse,
    ApiTokenResponse, ApiTokenCreate,
)
from app.security import get_password_hash, verify_password, create_access_token
from app.auth import get_current_user
from app.exceptions import (
    AppException, ConflictException, NotFoundException,
    app_exception_handler, validation_exception_handler, general_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")


app = FastAPI(title="Enterprise Task Manager API", version="2.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)")
    return response


app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.post("/api/auth/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing:
        raise ConflictException(detail="Email already registered")
    db_user = UserModel(email=user.email, password_hash=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User registered: {db_user.email}")
    return db_user


@app.post("/api/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(db_user.id)})
    logger.info(f"User logged in: {db_user.email}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.put("/api/auth/password", status_code=204)
def change_password(
    data: PasswordChange,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña actual incorrecta")
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    logger.info(f"Password changed for: {current_user.email}")


@app.get("/api/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(CategoryModel).order_by(CategoryModel.nombre).all()


@app.post("/api/categories", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(CategoryModel).filter(CategoryModel.nombre == category.nombre).first()
    if existing:
        raise ConflictException(detail="Category already exists")
    db_cat = CategoryModel(nombre=category.nombre, color=category.color)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@app.delete("/api/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not db_cat:
        raise NotFoundException(detail="Category not found")
    db.delete(db_cat)
    db.commit()


def _get_categories(db: Session, category_ids: List[int]) -> List[CategoryModel]:
    if not category_ids:
        return []
    return db.query(CategoryModel).filter(CategoryModel.id.in_(category_ids)).all()


@app.get("/api/tasks", response_model=List[TaskResponse])
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    completada: Optional[bool] = Query(None),
    category_id: Optional[int] = Query(None),
    vencidas: Optional[bool] = Query(None),
    prioridad: Optional[str] = Query(None, description="Filtrar: alta, media, baja"),
    search: Optional[str] = Query(None, description="Buscar por título o descripción"),
    sort_by: Optional[str] = Query("id", description="Campo: id, titulo, fecha_vencimiento"),
    sort_order: Optional[str] = Query("desc", description="Orden: asc, desc"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(TaskModel).filter(TaskModel.user_id == current_user.id)
    if completada is not None:
        query = query.filter(TaskModel.completada == completada)
    if category_id is not None:
        query = query.filter(TaskModel.categories.any(CategoryModel.id == category_id))
    if vencidas:
        from datetime import datetime as dt
        query = query.filter(
            TaskModel.fecha_vencimiento.isnot(None),
            TaskModel.fecha_vencimiento < dt.utcnow(),
            TaskModel.completada == False,
        )
    if prioridad:
        query = query.filter(TaskModel.prioridad == prioridad)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            TaskModel.titulo.ilike(search_term) | TaskModel.descripcion.ilike(search_term)
        )
    sort_column = {
        "id": TaskModel.id,
        "titulo": TaskModel.titulo,
        "fecha_vencimiento": TaskModel.fecha_vencimiento,
        "prioridad": case(
            (TaskModel.prioridad == "alta", 1),
            (TaskModel.prioridad == "media", 2),
            (TaskModel.prioridad == "baja", 3),
            else_=4,
        ),
    }.get(sort_by, TaskModel.id)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()


@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = TaskModel(
        titulo=task.titulo,
        descripcion=task.descripcion,
        completada=False,
        prioridad=task.prioridad,
        estado=task.estado,
        recurrencia=task.recurrencia,
        fecha_vencimiento=task.fecha_vencimiento,
        user_id=current_user.id,
    )
    db_task.categories = _get_categories(db, task.category_ids)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    _log_activity(db, db_task.id, "actualizada", f"Tarea actualizada")
    return db_task


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.user_id == current_user.id
    ).first()
    if not task:
        raise NotFoundException(detail="Tarea no encontrada")
    return task


@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.user_id == current_user.id
    ).first()
    if not db_task:
        raise NotFoundException(detail="Tarea no encontrada")
    db_task.titulo = task.titulo
    db_task.descripcion = task.descripcion
    db_task.prioridad = task.prioridad
    db_task.estado = task.estado
    db_task.recurrencia = task.recurrencia
    db_task.fecha_vencimiento = task.fecha_vencimiento
    db_task.categories = _get_categories(db, task.category_ids)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.patch("/api/tasks/{task_id}/toggle", response_model=TaskResponse)
def toggle_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.user_id == current_user.id
    ).first()
    if not db_task:
        raise NotFoundException(detail="Tarea no encontrada")
    db_task.completada = not db_task.completada
    db_task.estado = "completada" if db_task.completada else "pendiente"
    if db_task.completada and db_task.recurrencia and db_task.fecha_vencimiento:
        new_task = TaskModel(
            titulo=db_task.titulo,
            descripcion=db_task.descripcion,
            prioridad=db_task.prioridad,
            estado="pendiente",
            recurrencia=db_task.recurrencia,
            completada=False,
            user_id=current_user.id,
        )
        delta = {"diaria": timedelta(days=1), "semanal": timedelta(days=7), "mensual": timedelta(days=30)}
        new_task.fecha_vencimiento = db_task.fecha_vencimiento + delta.get(db_task.recurrencia, timedelta(days=7))
        new_task.categories = db_task.categories
        db.add(new_task)
    db.commit()
    db.refresh(db_task)
    _log_activity(db, db_task.id, "toggle", f"Estado: {db_task.estado}")
    return db_task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.user_id == current_user.id
    ).first()
    if not db_task:
        raise NotFoundException(detail="Tarea no encontrada")
    db.delete(db_task)
    db.commit()


@app.get("/api/tasks/export")
def export_tasks(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = db.query(TaskModel).filter(TaskModel.user_id == current_user.id).order_by(TaskModel.id.desc()).all()
    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Título", "Descripción", "Completada", "Prioridad", "Vencimiento", "Categorías"])
    for t in tasks:
        cats = ", ".join(c.nombre for c in t.categories)
        writer.writerow([t.id, t.titulo, t.descripcion or "", "Sí" if t.completada else "No", t.prioridad,
                         t.fecha_vencimiento.isoformat() if t.fecha_vencimiento else "", cats])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=tareas.csv"})


@app.post("/api/tasks/{task_id}/subtasks", response_model=SubtaskResponse, status_code=201)
def create_subtask(
    task_id: int,
    subtask: SubtaskCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if not task:
        raise NotFoundException(detail="Tarea no encontrada")
    db_sub = SubtaskModel(task_id=task_id, texto=subtask.texto)
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


@app.patch("/api/subtasks/{subtask_id}/toggle", response_model=SubtaskResponse)
def toggle_subtask(
    subtask_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = db.query(SubtaskModel).join(TaskModel).filter(
        SubtaskModel.id == subtask_id, TaskModel.user_id == current_user.id
    ).first()
    if not sub:
        raise NotFoundException(detail="Subtarea no encontrada")
    sub.completada = not sub.completada
    db.commit()
    db.refresh(sub)
    return sub


@app.delete("/api/subtasks/{subtask_id}", status_code=204)
def delete_subtask(
    subtask_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = db.query(SubtaskModel).join(TaskModel).filter(
        SubtaskModel.id == subtask_id, TaskModel.user_id == current_user.id
    ).first()
    if not sub:
        raise NotFoundException(detail="Subtarea no encontrada")
    db.delete(sub)
    db.commit()


@app.get("/api/tasks/{task_id}/comments", response_model=List[CommentResponse])
def list_comments(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if not task:
        raise NotFoundException(detail="Tarea no encontrada")
    return task.comments


@app.post("/api/tasks/{task_id}/comments", response_model=CommentResponse, status_code=201)
def create_comment(
    task_id: int,
    comment: CommentCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if not task:
        raise NotFoundException(detail="Tarea no encontrada")
    db_comment = CommentModel(task_id=task_id, texto=comment.texto)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@app.delete("/api/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(CommentModel).join(TaskModel).filter(
        CommentModel.id == comment_id, TaskModel.user_id == current_user.id
    ).first()
    if not comment:
        raise NotFoundException(detail="Comentario no encontrado")
    db.delete(comment)
    db.commit()


@app.get("/api/backup/export")
def backup_export(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = db.query(TaskModel).filter(TaskModel.user_id == current_user.id).all()
    data = {
        "version": 1,
        "categories": [{"nombre": c.nombre, "color": c.color} for c in
                       db.query(CategoryModel).order_by(CategoryModel.nombre).all()],
        "tasks": [{
            "titulo": t.titulo, "descripcion": t.descripcion, "completada": t.completada,
            "prioridad": t.prioridad, "estado": t.estado, "recurrencia": t.recurrencia,
            "fecha_vencimiento": t.fecha_vencimiento.isoformat() if t.fecha_vencimiento else None,
            "categories": [c.nombre for c in t.categories],
            "subtasks": [{"texto": s.texto, "completada": s.completada} for s in t.subtasks],
        } for t in tasks],
    }
    return data


@app.post("/api/backup/import", status_code=201)
async def backup_import(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = await file.read()
    data = json.loads(content)
    count = 0
    cats_map = {c.nombre: c for c in db.query(CategoryModel).all()}
    for tdata in data.get("tasks", []):
        task = TaskModel(
            titulo=tdata["titulo"], descripcion=tdata.get("descripcion"),
            prioridad=tdata.get("prioridad", "media"), estado=tdata.get("estado", "pendiente"),
            recurrencia=tdata.get("recurrencia"), completada=tdata.get("completada", False),
            user_id=current_user.id,
        )
        if tdata.get("fecha_vencimiento"):
            task.fecha_vencimiento = dt.fromisoformat(tdata["fecha_vencimiento"])
        for cat_name in tdata.get("categories", []):
            if cat_name in cats_map:
                task.categories.append(cats_map[cat_name])
        for sdata in tdata.get("subtasks", []):
            task.subtasks.append(SubtaskModel(texto=sdata["texto"], completada=sdata.get("completada", False)))
        db.add(task)
        count += 1
    db.commit()
    return {"imported": count}


UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/uploads")
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except PermissionError:
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _log_activity(db: Session, task_id: int, accion: str, detalle: str = None):
    db.add(ActivityLogModel(task_id=task_id, accion=accion, detalle=detalle))


@app.patch("/api/tasks/{task_id}/public-link")
def generate_public_link(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id).first()
    if not task:
        raise NotFoundException(detail="Tarea no encontrada")
    if not task.public_uuid:
        task.public_uuid = str(uuid.uuid4())
        db.commit()
    return {"public_uuid": task.public_uuid}


@app.get("/api/public/tasks/{public_uuid}", response_model=TaskResponse)
def get_public_task(public_uuid: str, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.public_uuid == public_uuid).first()
    if not task:
        raise NotFoundException(detail="Tarea no encontrada")
    return task


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "database": db_status}
