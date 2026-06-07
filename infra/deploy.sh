#!/bin/bash
set -e
# ============================================================
# Enterprise Task Manager - Deploy Script for AWS EC2
# ============================================================
# Uso: chmod +x deploy.sh && ./deploy.sh
# ============================================================

echo "========================================="
echo " Task Manager - Deploy to AWS EC2"
echo "========================================="

# ── Cargar variables de entorno ─────────────────────────────
if [ -f .env.production ]; then
    set -a
    source .env.production
    set +a
    echo "[OK] Variables de entorno cargadas"
else
    echo "[ERROR] No se encuentra .env.production"
    exit 1
fi

# ── Docker login en ECR ─────────────────────────────────────
echo "[*] Autenticando en ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin "$ECR_REGISTRY"

# ── Descargar imágenes ──────────────────────────────────────
echo "[*] Descargando imágenes..."
docker compose -f docker-compose.prod.yml pull

# ── Levantar servicios ──────────────────────────────────────
echo "[*] Levantando servicios..."
docker compose -f docker-compose.prod.yml up -d --remove-orphans

# ── Migraciones y estado ────────────────────────────────────
echo "[*] Esperando backend..."
sleep 5
echo ""
echo "========================================="
echo "  Estado de los servicios:"
echo "========================================="
docker compose -f docker-compose.prod.yml ps
echo ""
echo "[OK] Despliegue completado"
echo "Accede en: http://$(curl -s http://checkip.amazonaws.com)"
