# Configuración con AWS SSO

Esta guía explica cómo usar AWS SSO con el sistema de Translation QA.

## ¿Qué es AWS SSO?

AWS SSO (Single Sign-On) permite autenticarse usando credenciales corporativas en lugar de access keys estáticos. Es más seguro y las credenciales se renuevan automáticamente.

## Pre-requisitos

1. AWS CLI instalado y configurado
2. Acceso a AWS SSO configurado por tu organización
3. Docker y Docker Compose

## Configuración Paso a Paso

### 1. Verificar tu perfil de AWS SSO

Revisa tu archivo `~/.aws/config`:

```bash
cat ~/.aws/config
```

Deberías ver algo como:

```ini
[profile sso-ro-data-dev]
sso_start_url = https://your-company.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = ReadOnlyRole
region = us-east-1
output = json
```

### 2. Login con AWS SSO

```bash
aws sso login --profile sso-ro-data-dev
```

Esto abrirá tu navegador para autenticarte. Una vez autenticado, verás:

```
Successfully logged into Start URL: https://your-company.awsapps.com/start
```

### 3. Verificar acceso al bucket

Prueba que tengas acceso al bucket:

```bash
aws s3 ls s3://pangea-data-dev-bedrock-datasets/llm-output/ --profile sso-ro-data-dev
```

Deberías ver el contenido del bucket.

### 4. Configurar el Backend

Edita `backend/.env`:

```bash
# Cambiar a S3
STORAGE_BACKEND=s3

# Configurar el perfil de AWS SSO
AWS_PROFILE=sso-ro-data-dev
AWS_S3_BUCKET=pangea-data-dev-bedrock-datasets
AWS_REGION=us-east-1

# Dejar vacíos los access keys
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

### 5. Montar las credenciales en Docker

Para que el contenedor Docker pueda usar tus credenciales de SSO, necesitas montar el directorio `~/.aws`:

Edita `docker-compose.yml` y agrega el volumen al servicio `backend`:

```yaml
backend:
  build: ./backend
  volumes:
    - ./backend:/app
    - ~/.aws:/root/.aws:ro  # Monta credenciales AWS (read-only)
  environment:
    - PYTHONUNBUFFERED=1
  depends_on:
    - postgres
    - minio
  ports:
    - "8000:8000"
```

**Nota**: `:ro` significa read-only para mayor seguridad.

### 6. Reiniciar el backend

```bash
docker compose down
docker compose up -d
```

### 7. Verificar que funciona

```bash
docker compose exec backend python -c "from app.s3_service import s3_service; print('OK')"
```

Deberías ver:

```
Using AWS S3 backend with profile 'sso-ro-data-dev': s3://pangea-data-dev-bedrock-datasets/
OK
```

## Renovación de Credenciales

Las credenciales de AWS SSO expiran después de un tiempo (usualmente 8-12 horas). Cuando expiren:

1. Ejecuta nuevamente:
   ```bash
   aws sso login --profile sso-ro-data-dev
   ```

2. Reinicia el backend:
   ```bash
   docker compose restart backend
   ```

## Verificar Estado de las Credenciales

Para verificar si tus credenciales están activas:

```bash
aws sts get-caller-identity --profile sso-ro-data-dev
```

Si ves un error, necesitas hacer login nuevamente.

## Troubleshooting

### Error: "Unable to locate credentials"

**Causa**: Docker no tiene acceso a tus credenciales AWS.

**Solución**: Verifica que agregaste el volumen `~/.aws` en `docker-compose.yml`:

```yaml
volumes:
  - ~/.aws:/root/.aws:ro
```

Y reinicia:
```bash
docker compose down && docker compose up -d
```

### Error: "The SSO session associated with this profile has expired"

**Causa**: Tus credenciales expiraron.

**Solución**:
```bash
aws sso login --profile sso-ro-data-dev
docker compose restart backend
```

### Error: "profile sso-ro-data-dev not found"

**Causa**: El perfil no existe en `~/.aws/config`

**Solución**: Verifica el nombre exacto del perfil:
```bash
aws configure list-profiles
```

Y actualiza `AWS_PROFILE` en `.env` con el nombre correcto.

### Error: "Access Denied" al acceder S3

**Causa**: Tu rol SSO no tiene permisos en el bucket.

**Solución**: Contacta al administrador de AWS para que te den permisos de lectura en el bucket `pangea-data-dev-bedrock-datasets`.

Permisos necesarios:
- `s3:GetObject`
- `s3:ListBucket`

## Automatización del Login

Para evitar tener que hacer login manualmente cada vez, puedes:

### Opción 1: Script de inicio

Crea un script `start.sh`:

```bash
#!/bin/bash
echo "Logging into AWS SSO..."
aws sso login --profile sso-ro-data-dev

echo "Starting backend..."
docker compose up -d backend

echo "Backend started with AWS SSO credentials"
docker compose logs -f backend
```

Hazlo ejecutable:
```bash
chmod +x start.sh
./start.sh
```

### Opción 2: Configurar auto-refresh

Algunas configuraciones de SSO soportan auto-refresh. Verifica con tu administrador de AWS.

## Comparación: SSO vs Access Keys

| Característica | AWS SSO | Access Keys |
|---|---|---|
| **Seguridad** | ✅ Más seguro | ⚠️ Menos seguro |
| **Expiración** | ✅ Auto-renovable | ❌ Permanentes |
| **Setup inicial** | ⚠️ Más complejo | ✅ Simple |
| **Multi-cuenta** | ✅ Soportado | ❌ Una cuenta |
| **Auditoría** | ✅ Mejor trazabilidad | ⚠️ Limitada |
| **Rotación** | ✅ Automática | ❌ Manual |

## Configuración para Desarrollo en Equipo

Si tu equipo usa diferentes perfiles de SSO, pueden mantener sus propias configuraciones locales:

**`.env.local`** (no commitear):
```bash
STORAGE_BACKEND=s3
AWS_PROFILE=mi-perfil-personal-sso
AWS_S3_BUCKET=pangea-data-dev-bedrock-datasets
AWS_REGION=us-east-1
```

Agregar a `.gitignore`:
```
backend/.env.local
```

Y cada desarrollador copia su configuración:
```bash
cp backend/.env.local backend/.env
```

## Ejemplo Completo de Configuración

### `~/.aws/config`
```ini
[profile sso-ro-data-dev]
sso_start_url = https://your-company.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = DataEngineerReadOnly
region = us-east-1
output = json
```

### `backend/.env`
```bash
STORAGE_BACKEND=s3
AWS_PROFILE=sso-ro-data-dev
AWS_S3_BUCKET=pangea-data-dev-bedrock-datasets
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_PREFIX=
```

### Login y Start
```bash
# 1. Login
aws sso login --profile sso-ro-data-dev

# 2. Verificar
aws s3 ls s3://pangea-data-dev-bedrock-datasets/ --profile sso-ro-data-dev

# 3. Start backend
docker compose up -d backend

# 4. Verificar logs
docker compose logs backend | grep "Using AWS S3"
```

Deberías ver:
```
Using AWS S3 backend with profile 'sso-ro-data-dev': s3://pangea-data-dev-bedrock-datasets/
```

## ✅ Checklist Rápido

- [ ] AWS CLI instalado
- [ ] Profile SSO configurado en `~/.aws/config`
- [ ] `aws sso login --profile sso-ro-data-dev` ejecutado exitosamente
- [ ] Acceso al bucket verificado con `aws s3 ls`
- [ ] Volumen `~/.aws` montado en `docker-compose.yml`
- [ ] `AWS_PROFILE=sso-ro-data-dev` en `backend/.env`
- [ ] `STORAGE_BACKEND=s3` en `backend/.env`
- [ ] Backend reiniciado con `docker compose restart backend`
- [ ] Verificado con logs: `docker compose logs backend | grep "Using AWS S3"`

¡Listo! Ahora tu aplicación está usando AWS SSO para acceder a S3. 🚀
