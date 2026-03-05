# expiration-reminder

Este servicio lee una Google Sheet y envía recordatorios diarios por Telegram cuando hay vencimientos de servicios próximos o del día.

---

## Variables de entorno (`.env`)

Copiá el archivo `.env` y completá los valores:

| Variable | Descripción |
|---|---|
| `TELEGRAM_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | ID del chat donde se envían los mensajes |
| `GOOGLE_SHEETS_CREDS_PATH` | Ruta al archivo JSON de credenciales de Google |
| `GOOGLE_SHEETS_ID` | ID de la Google Sheet |
| `FORCE_LOCALE` | Locale del sistema (ej: `es_AR.UTF-8`). Opcional. |
| `SOON_TIMESPAN` | Días de anticipación para alertas "próximas" (default: `2`) |
| `RUN_TIME` | Horario de ejecución diaria en formato `HH:MM` (default: `08:00`) |

---

## Deploy en Oracle Linux (VM de Oracle Cloud)

### Requisitos previos

- VM con Oracle Linux 8 o 9
- Acceso SSH con usuario `opc` (o similar con `sudo`)
- Archivo de credenciales JSON de Google (`*.json`)

---

### 1. Copiar el proyecto a la VM

Desde tu máquina local, copiá todos los archivos del proyecto a la VM:

```bash
scp -r . opc@<IP_VM>:~/expiration-reminder
```

> Reemplazá `<IP_VM>` con la IP pública de tu VM de Oracle.

---

### 2. Conectarse a la VM

```bash
ssh opc@<IP_VM>
cd ~/expiration-reminder
```

---

### 3. Instalar Python 3

En Oracle Linux, Python 3 se instala con `dnf`:

```bash
sudo dnf install -y python3 python3-pip
```

Verificá la instalación:

```bash
python3 --version
```

---

### 4. Crear el entorno virtual e instalar dependencias

```bash
# Crear el virtualenv en la carpeta del proyecto
python3 -m venv venv

# Activar el virtualenv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Desactivar el virtualenv (opcional, el deploy.sh lo maneja por su cuenta)
deactivate
```

---

### 5. Configurar las variables de entorno

Editá el archivo `.env` con tus valores reales:

```bash
nano .env
```

Ajustá en particular `RUN_TIME` con el horario en que querés que se ejecute diariamente (formato 24h):

```
RUN_TIME=08:00
```

---

### 6. Ejecutar el script de deploy

El script `deploy.sh` se encarga de copiar la app a `/opt/expiration-reminder`, instalar las dependencias en un virtualenv propio y registrar el cron job automáticamente:

```bash
chmod +x deploy.sh
./deploy.sh
```

Para instalar en un directorio personalizado:

```bash
./deploy.sh /ruta/personalizada
```

Al finalizar, el script muestra un resumen con el directorio de instalación, el horario configurado y la ruta del log.

---

### Ejecución manual

Para correr el script manualmente (sin esperar al cron):

```bash
sudo /opt/expiration-reminder/run.sh
```

---

### Cambiar el horario de ejecución

1. Editá `RUN_TIME` en el `.env` de la VM:

```bash
nano /opt/expiration-reminder/.env
```

2. Volvé a correr `deploy.sh` para actualizar el cron:

```bash
cd ~/expiration-reminder
./deploy.sh
```

---

### Logs

Los logs de cada ejecución se guardan en:

```
/opt/expiration-reminder/app.log
```

Para seguirlos en tiempo real:

```bash
tail -f /opt/expiration-reminder/app.log
```
