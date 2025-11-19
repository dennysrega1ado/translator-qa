# Storage Backend Configuration

Este proyecto soporta dos backends de almacenamiento: **MinIO** (para desarrollo local) y **AWS S3** (para producción).

## Configuración

### 1. Usando MinIO (Default - Desarrollo Local)

MinIO se ejecuta automáticamente en Docker Compose y no requiere credenciales externas.

En `backend/.env`:
```bash
STORAGE_BACKEND=minio
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=translations
MINIO_SECURE=false
```

### 2. Usando AWS S3 (Producción)

Para usar S3, actualiza las siguientes variables en `backend/.env`:

```bash
# Cambiar el backend a S3
STORAGE_BACKEND=s3

# Configuración de AWS S3
AWS_S3_BUCKET=pangea-data-dev-bedrock-datasets
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=tu-access-key-id
AWS_SECRET_ACCESS_KEY=tu-secret-access-key

# Opcional: Prefijo si los datos están en una subcarpeta
# AWS_S3_PREFIX=some-folder/
```

#### Opciones de Credenciales AWS

Puedes configurar las credenciales de AWS de tres formas:

1. **Variables de entorno** (en `.env`):
   ```bash
   AWS_ACCESS_KEY_ID=tu-access-key
   AWS_SECRET_ACCESS_KEY=tu-secret-key
   ```

2. **AWS Credentials File** (`~/.aws/credentials`):
   ```ini
   [default]
   aws_access_key_id = tu-access-key
   aws_secret_access_key = tu-secret-key
   ```

3. **IAM Role** (cuando se ejecuta en EC2/ECS/Lambda):
   - No requiere configurar credenciales explícitas
   - Deja `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` vacíos

## Estructura de Datos

Ambos backends esperan la misma estructura de archivos:

```
llm-output/
  └── YYYY/              # Año (ej: 2025)
      └── MM/            # Mes (ej: 10)
          └── latest/    # Última versión
              ├── en/    # Archivos en inglés
              │   └── {id}.json
              └── es/    # Archivos en español con scores
                  └── {id}.json
```

### Ejemplo de archivo español (`es/{id}.json`):

```json
{
  "summary": "Resumen traducido...",
  "insight1": {
    "text": "Primer insight..."
  },
  "insight2": {
    "text": "Segundo insight..."
  },
  "insight3": {
    "text": "Tercer insight..."
  },
  "score": {
    "coherence": 9.0,
    "fidelity": 8.7,
    "naturalness": 9.1,
    "overall": 8.9
  }
}
```

## Cambiar entre Backends

### Durante Desarrollo

Simplemente cambia la variable `STORAGE_BACKEND` en `backend/.env`:

```bash
# Para MinIO
STORAGE_BACKEND=minio

# Para AWS S3
STORAGE_BACKEND=s3
```

Luego reinicia el backend:

```bash
docker compose restart backend
```

### Cargar Datos

El script `load_sample_data.py` funciona con ambos backends:

```bash
# Con MinIO (local)
docker compose exec backend python load_sample_data.py

# Con AWS S3 (lee de sample_data local y sube a S3)
docker compose exec backend python load_sample_data.py
```

## Verificar el Backend Activo

Al iniciar el backend, verás un mensaje indicando qué backend está en uso:

```
Using MinIO backend: minio:9000/translations
```

o

```
Using AWS S3 backend: s3://pangea-data-dev-bedrock-datasets/
```

## Troubleshooting

### Error: "Invalid STORAGE_BACKEND"
- Verifica que `STORAGE_BACKEND` sea `minio` o `s3` (minúsculas)

### Error al conectar con MinIO
- Asegúrate de que el servicio MinIO esté corriendo: `docker compose ps`
- Verifica el endpoint: `MINIO_ENDPOINT=minio:9000` (no `localhost`)

### Error al conectar con AWS S3
- Verifica tus credenciales AWS
- Confirma que el bucket existe y tienes permisos
- Verifica la región: `AWS_REGION=us-east-1`

### Permisos necesarios en AWS S3

Tu usuario o rol IAM necesita estos permisos:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::pangea-data-dev-bedrock-datasets",
        "arn:aws:s3:::pangea-data-dev-bedrock-datasets/*"
      ]
    }
  ]
}
```

## Ventajas de cada Backend

### MinIO (Desarrollo)
- ✅ Totalmente local, sin costos
- ✅ No requiere credenciales externas
- ✅ Más rápido para desarrollo
- ✅ Se puede resetear fácilmente

### AWS S3 (Producción)
- ✅ Datos persistentes
- ✅ Escalable
- ✅ Alta disponibilidad
- ✅ Integración con otros servicios AWS
- ✅ Backups automáticos
