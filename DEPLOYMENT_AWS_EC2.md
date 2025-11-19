# Despliegue en AWS EC2 - Guía Mínima Esencial

## Arquitectura

```
Internet → EC2 Instance (IP Pública)
           ├── Docker: Nginx (Frontend)
           ├── Docker: FastAPI (Backend)
           ├── Docker: PostgreSQL (Base de datos)
           └── S3 (Almacenamiento de archivos)
```

## Componentes Indispensables

### 1. EC2 Instance
- **Tipo:** `t3.medium` (2 vCPU, 4GB RAM)
- **SO:** Ubuntu 22.04 LTS
- **Almacenamiento:** 30 GB EBS gp3
- **Costo:** ~$30/mes

### 2. PostgreSQL
- En Docker dentro del EC2
- Costo: Incluido en EC2

### 3. S3 Bucket
- Para almacenar archivos de traducción
- Costo: ~$1-2/mes (50GB)

### 4. Elastic IP
- IP pública estática
- Costo: Gratis (si está asociada a EC2 en ejecución)

**Costo Total Estimado:** ~$32-35/mes

---

## Paso 1: Crear Instancia EC2

### 1.1 Desde AWS Console

1. Ir a **EC2 → Launch Instance**
2. Configurar:
   - **Name:** `translator-qa-prod`
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Instance type:** `t3.medium`
   - **Key pair:** Crear o seleccionar tu llave SSH
   - **Network settings:**
     - Allow SSH (22) from: My IP
     - Allow HTTP (80) from: Anywhere
   - **Storage:** 30 GB gp3

3. **Launch Instance**

### 1.2 Asignar Elastic IP

1. **EC2 → Elastic IPs → Allocate Elastic IP address**
2. **Actions → Associate Elastic IP address**
3. Seleccionar tu instancia EC2

---

## Paso 2: Conectar y Configurar EC2

```bash
# Conectar via SSH
ssh -i tu-llave.pem ubuntu@TU-IP-ELASTICA

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Recargar sesión
exit
# Volver a conectar por SSH

# Verificar instalación
docker --version
docker-compose --version
```

---

## Paso 3: Subir Código a EC2

```bash
# Opción A: Desde tu máquina local (recomendado)
scp -i tu-llave.pem -r ./translator-qa ubuntu@TU-IP-ELASTICA:/home/ubuntu/

# Opción B: Clonar desde Git
ssh -i tu-llave.pem ubuntu@TU-IP-ELASTICA
git clone <tu-repositorio-url> translator-qa
```

---

## Paso 4: Configurar IAM Role para S3

### 4.1 Crear IAM Role

1. **IAM → Roles → Create Role**
2. **Trusted entity type:** AWS Service → EC2
3. **Permissions:** Agregar esta política personalizada:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::tu-bucket-translator-qa",
        "arn:aws:s3:::tu-bucket-translator-qa/*"
      ]
    }
  ]
}
```

4. **Role name:** `translator-qa-s3-role`
5. **Create role**

### 4.2 Asignar Role a EC2

1. **EC2 → Seleccionar tu instancia**
2. **Actions → Security → Modify IAM Role**
3. Seleccionar `translator-qa-s3-role`
4. **Update IAM role**

---

## Paso 5: Crear S3 Bucket

```bash
# Desde tu máquina local (con AWS CLI configurado)
aws s3 mb s3://tu-bucket-translator-qa --region us-east-1
```

O desde AWS Console:
1. **S3 → Create bucket**
2. **Bucket name:** `tu-bucket-translator-qa`
3. **Region:** us-east-1
4. **Create bucket**

---

## Paso 6: Configurar Aplicación

```bash
# En el EC2
cd /home/ubuntu/translator-qa

# Crear archivo .env
nano .env
```

### Contenido del archivo `.env`:

```bash
# Base de datos
DATABASE_URL=postgresql://translator_user:TU_PASSWORD_SEGURA@postgres:5432/translator_qa

# Storage S3
STORAGE_BACKEND=s3
AWS_S3_BUCKET=tu-bucket-translator-qa
AWS_REGION=us-east-1
AWS_PROFILE=

# Security - Generar con: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=GENERAR_KEY_SEGURA_AQUI_32_CARACTERES_MINIMO
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Generar SECRET_KEY segura:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Paso 7: Modificar docker-compose.yml

```bash
nano docker-compose.yml
```

### Archivo `docker-compose.yml` para producción:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: translator-qa-db
    environment:
      POSTGRES_USER: translator_user
      POSTGRES_PASSWORD: TU_PASSWORD_SEGURA
      POSTGRES_DB: translator_qa
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U translator_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: translator-qa-backend
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: translator-qa-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## Paso 8: Iniciar Aplicación

```bash
# Construir e iniciar contenedores
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Verificar que todo esté corriendo
docker-compose ps

# Debería mostrar:
# translator-qa-db        running
# translator-qa-backend   running
# translator-qa-frontend  running

# Inicializar base de datos (si es necesario)
docker-compose exec backend python -m app.init_db
```

---

## Paso 9: Verificar Funcionamiento

```bash
# Desde tu navegador:
http://TU-IP-ELASTICA

# Verificar API:
http://TU-IP-ELASTICA/api/docs
```

---

## Comandos de Mantenimiento

### Ver estado de servicios
```bash
docker-compose ps
```

### Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Reiniciar servicios
```bash
# Todos los servicios
docker-compose restart

# Solo un servicio
docker-compose restart backend
```

### Actualizar aplicación
```bash
# Descargar cambios
git pull

# Reconstruir e iniciar
docker-compose up -d --build
```

### Detener aplicación
```bash
docker-compose down
```

### Detener y eliminar volúmenes (¡CUIDADO! Borra datos)
```bash
docker-compose down -v
```

---

## Backup de Base de Datos

### Backup manual
```bash
# Crear directorio para backups
mkdir -p ~/backups

# Hacer backup
docker-compose exec postgres pg_dump -U translator_user translator_qa > ~/backups/backup_$(date +%Y%m%d).sql

# Comprimir backup
gzip ~/backups/backup_$(date +%Y%m%d).sql

# Subir a S3
aws s3 cp ~/backups/backup_$(date +%Y%m%d).sql.gz s3://tu-bucket-translator-qa/backups/
```

### Restaurar backup
```bash
# Descargar desde S3
aws s3 cp s3://tu-bucket-translator-qa/backups/backup_20250119.sql.gz ~/backups/

# Descomprimir
gunzip ~/backups/backup_20250119.sql.gz

# Restaurar
docker-compose exec -T postgres psql -U translator_user translator_qa < ~/backups/backup_20250119.sql
```

### Script de backup automático

```bash
# Crear script
nano ~/backup.sh
```

Contenido:
```bash
#!/bin/bash
BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="translator_qa_backup_$DATE.sql.gz"

mkdir -p $BACKUP_DIR
cd /home/ubuntu/translator-qa

# Backup
docker-compose exec -T postgres pg_dump -U translator_user translator_qa | gzip > "$BACKUP_DIR/$FILENAME"

# Subir a S3
aws s3 cp "$BACKUP_DIR/$FILENAME" s3://tu-bucket-translator-qa/backups/

# Mantener solo últimos 7 backups locales
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completado: $FILENAME"
```

```bash
# Dar permisos de ejecución
chmod +x ~/backup.sh

# Programar backup diario a las 2 AM
crontab -e

# Agregar esta línea:
0 2 * * * /home/ubuntu/backup.sh >> /home/ubuntu/backup.log 2>&1
```

---

## Monitoreo Básico

### Ver uso de recursos
```bash
# CPU, Memoria, Red de contenedores
docker stats

# Espacio en disco
df -h

# Memoria del sistema
free -h

# Procesos
htop  # Instalar con: sudo apt install htop
```

### Ver tamaño de volúmenes Docker
```bash
docker system df -v
```

---

## Troubleshooting

### Contenedor no inicia
```bash
# Ver logs del contenedor
docker-compose logs nombre-servicio

# Ver últimos errores
docker-compose logs --tail=50 backend
```

### Puerto ya en uso
```bash
# Ver qué usa el puerto 80
sudo lsof -i :80

# Matar proceso
sudo kill -9 PID
```

### Sin espacio en disco
```bash
# Limpiar contenedores, imágenes y volúmenes no usados
docker system prune -a

# Ver espacio usado
docker system df
```

### Reiniciar EC2
```bash
sudo reboot

# Después del reinicio, los contenedores se iniciarán automáticamente
# debido a "restart: unless-stopped" en docker-compose.yml
```

### Base de datos corrupta
```bash
# Restaurar desde backup más reciente
# Ver sección "Restaurar backup" arriba
```

---

## Security Group (Firewall)

### Reglas mínimas necesarias:

**Inbound Rules:**
| Type | Port | Source | Description |
|------|------|--------|-------------|
| SSH | 22 | Tu IP | Acceso SSH |
| HTTP | 80 | 0.0.0.0/0 | Acceso web |

**Outbound Rules:**
| Type | Port | Destination | Description |
|------|------|-------------|-------------|
| All traffic | All | 0.0.0.0/0 | Permitir salida |

---

## Checklist de Despliegue

- [ ] EC2 instance creada (t3.medium, Ubuntu 22.04)
- [ ] Elastic IP asociada
- [ ] Security Group configurado (SSH + HTTP)
- [ ] Docker y Docker Compose instalados
- [ ] IAM Role creado y asignado al EC2
- [ ] S3 Bucket creado
- [ ] Código subido al EC2
- [ ] Archivo .env creado con valores correctos
- [ ] docker-compose.yml actualizado para producción
- [ ] Aplicación iniciada con `docker-compose up -d --build`
- [ ] Base de datos inicializada
- [ ] Aplicación accesible desde navegador
- [ ] Script de backup configurado
- [ ] Cron job de backup programado

---

## Costos Mensuales Estimados

| Componente | Costo |
|------------|-------|
| EC2 t3.medium | $30.37 |
| EBS 30GB | $2.40 |
| S3 Storage 50GB | $1.15 |
| Elastic IP | $0 |
| **TOTAL** | **~$34/mes** |

---

## Próximos Pasos Recomendados

Una vez que la aplicación esté funcionando:

1. **Configurar dominio personalizado** (en lugar de usar IP)
2. **Agregar SSL/HTTPS** con Let's Encrypt
3. **Monitoreo con CloudWatch** para alertas
4. **Migrar PostgreSQL a RDS** para mayor confiabilidad
5. **Agregar CloudFront** para mejor rendimiento global
