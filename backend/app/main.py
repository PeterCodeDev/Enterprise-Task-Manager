import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.logging_config import logger
from app.database import get_db
from app.models import UserModel, TaskModel, CategoryModel
from app.schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    TaskCreate, TaskUpdate, TaskResponse,
    CategoryCreate, CategoryResponse,
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


app = FastAPI(title="Enterprise Task Manager API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)"
    )
    return response


app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# ============================================================
# Auth
# ============================================================

@app.post("/api/auth/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing:
        raise ConflictException(detail="Email already registered")
    
    db_user = UserModel(
        email=user.email,
        password_hash=get_password_hash(user.password)
    )
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


# ============================================================
# Categories
# ============================================================

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


# ============================================================
# Tasks
# ============================================================

def _get_categories(db: Session, category_ids: List[int]) -> List[CategoryModel]:
    if not category_ids:
        return []
    return db.query(CategoryModel).filter(CategoryModel.id.in_(category_ids)).all()


@app.get("/api/tasks", response_model=List[TaskResponse])
def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    completada: Optional[bool] = Query(None, description="Filter by completion"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(TaskModel).filter(TaskModel.user_id == current_user.id)
    
    if completada is not None:
        query = query.filter(TaskModel.completada == completada)
    
    if category_id is not None:
        query = query.filter(TaskModel.categories.any(CategoryModel.id == category_id))
    
    offset = (page - 1) * page_size
    return (
        query
        .order_by(TaskModel.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )


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
        user_id=current_user.id,
    )
    db_task.categories = _get_categories(db, task.category_ids)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    logger.info(f"Task created: {db_task.titulo}")
    return db_task


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id)
        .first()
    )
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
    db_task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id)
        .first()
    )
    if not db_task:
        raise NotFoundException(detail="Tarea no encontrada")
    db_task.titulo = task.titulo
    db_task.descripcion = task.descripcion
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
    db_task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id)
        .first()
    )
    if not db_task:
        raise NotFoundException(detail="Tarea no encontrada")
    db_task.completada = not db_task.completada
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == current_user.id)
        .first()
    )
    if not db_task:
        raise NotFoundException(detail="Tarea no encontrada")
    db.delete(db_task)
    db.commit()


# ============================================================
# Health
# ============================================================

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
