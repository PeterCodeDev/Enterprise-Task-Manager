from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.database import Base

task_category = Table(
    "task_categories",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("TaskModel", back_populates="user", cascade="all, delete-orphan")


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), default="#4361ee")

    tasks = relationship("TaskModel", secondary=task_category, back_populates="categories")


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    completada = Column(Boolean, default=False)
    prioridad = Column(String(10), default="media", nullable=False)
    fecha_vencimiento = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("UserModel", back_populates="tasks")
    categories = relationship("CategoryModel", secondary=task_category, back_populates="tasks")
class SubtaskModel(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    texto = Column(String(500), nullable=False)
    completada = Column(Boolean, default=False)

    task = relationship("TaskModel", back_populates="subtasks")


TaskModel.subtasks = relationship("SubtaskModel", back_populates="task", cascade="all, delete-orphan", order_by="SubtaskModel.id")
