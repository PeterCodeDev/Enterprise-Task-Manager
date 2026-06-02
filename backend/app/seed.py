from datetime import datetime as dt

from app.database import SessionLocal
from app.models import UserModel, CategoryModel, TaskModel
from app.security import get_password_hash


def run():
    db = SessionLocal()
    try:
        # Create demo user
        user = db.query(UserModel).filter(UserModel.email == "demo@demo.com").first()
        if not user:
            user = UserModel(
                email="demo@demo.com",
                password_hash=get_password_hash("demo123")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user: demo@demo.com / demo123")

        # Create categories
        cats_data = [
            ("Trabajo", "#4361ee"),
            ("Personal", "#06d6a0"),
            ("Urgente", "#ef476f"),
            ("Estudio", "#ffd166"),
        ]
        categories = {}
        for nombre, color in cats_data:
            cat = db.query(CategoryModel).filter(CategoryModel.nombre == nombre).first()
            if not cat:
                cat = CategoryModel(nombre=nombre, color=color)
                db.add(cat)
                db.commit()
            categories[nombre] = cat

        # Create demo tasks
        if db.query(TaskModel).filter(TaskModel.user_id == user.id).count() == 0:
            tasks_data = [
                ("Comprar víveres", "Leche, pan, huevos", ["Personal"], None, "baja"),
                ("Preparar presentación Q3", "PowerPoint para el cliente", ["Trabajo", "Urgente"],
                 dt(2026, 6, 10), "alta"),
                ("Estudiar FastAPI", "Capítulo 5: Autenticación", ["Estudio"], None, "media"),
                ("Revisar PR #42", "Refactor del módulo auth", ["Trabajo"],
                 dt(2026, 6, 2), "alta"),
            ]
            for titulo, desc, cats, fecha, prio in tasks_data:
                task = TaskModel(
                    titulo=titulo,
                    descripcion=desc,
                    user_id=user.id,
                    prioridad=prio,
                    fecha_vencimiento=fecha,
                )
                task.categories = [categories[c] for c in cats]
                db.add(task)
            db.commit()
            print("Created 4 demo tasks")

        print("Seed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    run()
