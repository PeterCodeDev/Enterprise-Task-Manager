from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, func
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
    nombre = Column(String(100), nullable=True)
    bio = Column(String(500), nullable=True)
    avatar_color = Column(String(7), default="#4361ee", nullable=False)
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
    estado = Column(String(20), default="pendiente", nullable=False)
    recurrencia = Column(String(20), nullable=True)
    tiempo_acumulado = Column(Integer, default=0, nullable=False, server_default="0")
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


class AttachmentModel(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    task = relationship("TaskModel", back_populates="attachments")


TaskModel.attachments = relationship("AttachmentModel", back_populates="task", cascade="all, delete-orphan", order_by="AttachmentModel.id")


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    texto = Column(String(2000), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    task = relationship("TaskModel", back_populates="comments")


TaskModel.comments = relationship("CommentModel", back_populates="task", cascade="all, delete-orphan", order_by="CommentModel.id")


class ActivityLogModel(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    accion = Column(String(50), nullable=False)
    detalle = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    task = relationship("TaskModel", back_populates="activity_logs")


TaskModel.activity_logs = relationship("ActivityLogModel", back_populates="task", cascade="all, delete-orphan", order_by="ActivityLogModel.created_at.desc()")


class ApiTokenModel(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    token_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("UserModel", back_populates="api_tokens")


UserModel.api_tokens = relationship("ApiTokenModel", back_populates="user", cascade="all, delete-orphan")
