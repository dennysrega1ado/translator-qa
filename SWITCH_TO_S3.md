# Cómo Cambiar a AWS S3

## Pasos Rápidos

### 1. Actualiza el archivo `.env`

Edita `backend/.env` y cambia las siguientes variables:

```bash
# Cambiar de MinIO a S3
STORAGE_BACKEND=s3

# Configurar credenciales AWS (opcionales si usas IAM role)
AWS_S3_BUCKET=pangea-data-dev-bedrock-datasets
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=tu-access-key-aqui
AWS_SECRET_ACCESS_KEY=tu-secret-key-aqui

# Si tus datos están en una subcarpeta, descomenta y configura:
# AWS_S3_PREFIX=subfolder/
```

### 2. Reinicia el backend

```bash
docker compose restart backend
```

### 3. Verifica que esté usando S3

```bash
docker compose exec backend python -c "from app.s3_service import s3_service; print('OK')"
```

Deberías ver:
```
Using AWS S3 backend: s3://pangea-data-dev-bedrock-datasets/
OK
```

## Opciones de Credenciales

### Opción 1: AWS SSO (Recomendado) ⭐

Si usas AWS SSO (Single Sign-On), esta es la opción más segura:

```bash
# 1. Login con SSO
aws sso login --profile sso-ro-data-dev

# 2. Descomentar volumen en docker-compose.yml
# - ~/.aws:/root/.aws:ro

# 3. Configurar en .env
AWS_PROFILE=sso-ro-data-dev
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

**Ver guía completa**: [AWS_SSO_SETUP.md](./AWS_SSO_SETUP.md)

### Opción 2: Access Keys Explícitas
```bash
AWS_PROFILE=
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### Opción 3: AWS Credentials File
Si tienes configurado `~/.aws/credentials`, puedes dejar todo vacío:
```bash
AWS_PROFILE=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

### Opción 4: IAM Role (Para producción en AWS)
Si corres en EC2/ECS/Lambda, no necesitas configurar nada:
```bash
AWS_PROFILE=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

## Estructura Esperada en S3

Tu bucket debe tener esta estructura:

```
s3://pangea-data-dev-bedrock-datasets/
└── llm-output/
    └── 2025/
        └── 10/
            └── latest/
                ├── en/
                │   ├── 52fa10a0f67541a98ce0c2ccba4583fc.json
                │   ├── 52fa10a0f67541a98ce0c2ccba4584ab.json
                │   └── 52fa10a0f67541a98ce0c2ccba458f9c.json
                └── es/
                    ├── 52fa10a0f67541a98ce0c2ccba4583fc.json (con score)
                    ├── 52fa10a0f67541a98ce0c2ccba4584ab.json (con score)
                    └── 52fa10a0f67541a98ce0c2ccba458f9c.json (con score)
```

## Cargar Datos desde Sample Data Local a S3

Si quieres cargar los datos de ejemplo a S3:

```bash
# Asegúrate de que STORAGE_BACKEND=s3 en .env
docker compose exec backend python load_sample_data.py
```

Esto leerá los archivos de `backend/sample_data/llm-output/` y los subirá a S3.

## Verificar Archivos en S3

Desde AWS CLI:
```bash
aws s3 ls s3://pangea-data-dev-bedrock-datasets/llm-output/ --recursive
```

## Volver a MinIO

Para volver a desarrollo local con MinIO:

1. Edita `backend/.env`:
   ```bash
   STORAGE_BACKEND=minio
   ```

2. Reinicia:
   ```bash
   docker compose restart backend
   ```

## Troubleshooting

### Error: "Unable to locate credentials"
- Verifica que `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` estén configurados
- O verifica que `~/.aws/credentials` exista y tenga las credenciales

### Error: "Access Denied"
- Verifica que tu usuario/rol tenga permisos en el bucket
- Necesitas: `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`

### Error: "The specified bucket does not exist"
- Verifica que el nombre del bucket sea correcto
- Verifica la región: algunos buckets solo existen en regiones específicas

### Los datos no aparecen en la aplicación
- Verifica que la estructura de carpetas sea correcta
- Confirma que los archivos `es/*.json` tengan el objeto `score`
- Revisa los logs: `docker compose logs backend --tail=50`

## Permisos IAM Mínimos

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

## Comparación: MinIO vs S3

| Característica | MinIO | AWS S3 |
|---|---|---|
| **Configuración** | Automática | Requiere credenciales |
| **Costo** | Gratis (local) | Paga por uso |
| **Velocidad** | Muy rápido | Depende de latencia |
| **Persistencia** | Volumen Docker | Alta durabilidad |
| **Uso** | Desarrollo | Producción |

## Uso Híbrido (Desarrollo + Producción)

Puedes tener dos archivos de configuración:

**`.env.local`** (MinIO para desarrollo):
```bash
STORAGE_BACKEND=minio
```

**`.env.production`** (S3 para producción):
```bash
STORAGE_BACKEND=s3
AWS_S3_BUCKET=pangea-data-dev-bedrock-datasets
# ... resto de configuración S3
```

Y cambiar según necesites:
```bash
# Desarrollo
cp .env.local .env
docker compose restart backend

# Producción
cp .env.production .env
docker compose restart backend
```
