# LG UHC Stats (Django)

Un site Django pour enregistrer et afficher les statistiques des joueurs sur le mode **Loup Garou UHC** de Minecraft.

## Fonctionnalités
- Inscription / Connexion / Déconnexion
- Ajout d'une partie (rôle, camp, kills, victoire, pseudos tués en option, notes)
- Profil joueur avec : parties, victoires, kills, **K/D**, **winrate**, répartitions par rôle et camp
- Pages : Accueil (récap), Parties récentes, Classements (Top K/D, Kills, Winrate)
- Admin Django

> Hypothèse: dans UHC, *mort = partie non gagnée*, ce qui permet de calculer K/D = kills / morts.

## Démarrage (local)
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt --proxy http://proxy.bruyeres.cea.fr:3128 djangorestframework-simplejwt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput  # optionnel
python manage.py runserver
```

Accès:
- Site : http://127.0.0.1:8000/
- Admin : http://127.0.0.1:8000/admin/

## Déploiement simple sur VPS (Ubuntu + Nginx + Gunicorn)
### 1) Variables d'environnement
```
export DJANGO_SECRET_KEY='votre-cle-secrete'
export DJANGO_DEBUG=false
export ALLOWED_HOSTS='votre.domaine,IP_PUBLIQUE'
# Optionnel Postgres :
# export POSTGRES_NAME='lguhc'
# export POSTGRES_USER='lguser'
# export POSTGRES_PASSWORD='motdepasse'
# export POSTGRES_HOST='127.0.0.1'
```

### 2) Installation
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip nginx
cd /opt/lguhc_stats
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt gunicorn
python manage.py migrate
python manage.py collectstatic --noinput
```

### 3) Service systemd (Gunicorn)
Créez `/etc/systemd/system/lguhc.service` :
```
[Unit]
Description=Gunicorn LG UHC Stats
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/lguhc_stats
Environment="DJANGO_SECRET_KEY=change-me" "DJANGO_DEBUG=false" "ALLOWED_HOSTS=votre.domaine,IP"
ExecStart=/opt/lguhc_stats/venv/bin/gunicorn lguhc_stats.wsgi:application --bind 127.0.0.1:8001 --workers 3

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now lguhc
```

### 4) Nginx
Créez `/etc/nginx/sites-available/lguhc` :
```
server {
    server_name votre.domaine IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ { alias /opt/lguhc_stats/staticfiles/; }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:8001;
    }
    listen 80;
}
```
```bash
sudo ln -s /etc/nginx/sites-available/lguhc /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 5) HTTPS (recommandé)
Utilisez certbot :
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d votre.domaine
```

## Personnalisation
- Modifiez les rôles/camps dans `games/models.py`
- Ajoutez des champs au profil joueur dans `core/models.py`
- Améliorez les classements dans `games/views.py` (filtres par période, etc.)

Bon jeu ✌️
