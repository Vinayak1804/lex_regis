# Production Deployment & Infrastructure Guide
## LEX REGIS: Enterprise Deployment Blueprint

---

## 1. System Prerequisites

- **Operating System:** Ubuntu 22.04 LTS / Debian 12 / Enterprise Linux
- **Python Runtime:** Python 3.13+
- **Database Engine:** PostgreSQL 16+
- **In-Memory Cache & Message Broker:** Redis 7.x+
- **Web Server & Reverse Proxy:** Nginx 1.24+
- **Application Server (ASGI):** Daphne 4.x / Uvicorn + Gunicorn

---

## 2. Step-by-Step Production Deployment

### 2.1 Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/organization/lex_regis.git /var/www/lex_regis
cd /var/www/lex_regis
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements/production.txt
```

### 2.2 Configure Production Environment Variables
Create `/var/www/lex_regis/.env`:
```ini
SECRET_KEY=generate-a-secure-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=app.lexregis.com,api.lexregis.com

# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=lex_regis_prod
DB_USER=lex_user
DB_PASSWORD=strong_database_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Redis & Channels
REDIS_URL=redis://127.0.0.1:6379/0

# Groq Cloud AI Engine
GROQ_API_KEY=gsk_your_production_api_key
GROQ_MODEL=openai/gpt-oss-120b

# Email Configuration
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USER=apikey
EMAIL_PASSWORD=your_sendgrid_key
```

### 2.3 Database Migration & Static Files
```bash
python manage.py migrate --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production
python seed_lawyers.py
```

### 2.4 Systemd Service Configuration (`/etc/systemd/system/daphne.service`)
```ini
[Unit]
Description=Daphne ASGI Server for LEX REGIS
After=network.target redis.service postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/lex_regis
ExecStart=/var/www/lex_regis/.venv/bin/daphne -b 127.0.0.1 -p 8001 config.asgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 2.5 Nginx Reverse Proxy Configuration (`/etc/nginx/sites-available/lex_regis`)
```nginx
upstream daphne_backend {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name app.lexregis.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.lexregis.com;

    ssl_certificate /etc/letsencrypt/live/app.lexregis.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.lexregis.com/privkey.pem;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/lex_regis/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /var/www/lex_regis/media/;
        internal; # Protect sensitive downloads via X-Accel-Redirect
    }

    location /ws/ {
        proxy_pass http://daphne_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://daphne_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---
*End of Deployment Guide — LEX REGIS*
