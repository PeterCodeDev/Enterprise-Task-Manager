# Enterprise Task Manager 🚀

Este proyecto es un **MVP (Producto Mínimo Viable) Full-Stack** diseñado bajo estándares profesionales de la industria. No es solo una aplicación funcional, sino una demostración práctica de arquitectura contenerizada, automatización de infraestructura (DevOps) y buenas prácticas en el ciclo de vida del desarrollo de software.

La aplicación consta de un ecosistema de microservicios independientes que se comunican de forma eficiente, configurados para replicar un entorno de producción real.

---

## 🛠️ Arquitectura y Tecnologías

El proyecto está completamente modularizado y automatizado utilizando el siguiente stack tecnológico:

* **Frontend:** Angular 20+ estructurado de forma modular, utilizando `HttpClient` para el consumo de APIs y optimizado en producción mediante un servidor **Nginx**.
* **Backend:** API REST robusta y asíncrona construida con **Python (FastAPI)**, utilizando **SQLAlchemy** como ORM y validación de datos estricta con **Pydantic**.
* **Base de Datos:** **PostgreSQL 15** para la persistencia de datos relacionales en un entorno aislado.
* **Contenerización:** **Docker** para el aislamiento de entornos individuales y **Docker Compose** para la orquestación y conectividad de la red local.
* **CI/CD (Automatización):** Flujo de trabajo automatizado en la nube mediante **GitHub Actions**, encargado de compilar, empaquetar y subir las imágenes optimizadas a **Docker Hub** tras cada actualización.

---

## 🚀 Características Clave del Proyecto

* **Arquitectura Multi-contenedor:** Todo el sistema se levanta localmente con un único comando (`docker-compose up --build`), garantizando el principio de *"funciona en mi máquina y en la tuya"*.
* **Producción Ready:** El frontend de Angular se compila en una imagen multi-etapa (*Multi-stage build*) para reducir su peso y se sirve a través de un proxy inverso con **Nginx**.
* **Seguridad e Inyección de Dependencias:** Gestión de credenciales críticas (base de datos y tokens de Docker Hub) protegidas mediante **GitHub Secrets** y variables de entorno.
* **Pipeline de Despliegue Continuo:** Automatización total del empaquetado de imágenes sin intervención humana.
