"""
Production settings: рассчитаны на деплой на VPS в РФ
(Timeweb Cloud / Beget / Reg.ru / Selectel) с nginx + gunicorn,
PostgreSQL локально на сервере и Yandex Object Storage для media.

Все секреты подтягиваются из переменных окружения (.env на сервере или
напрямую в systemd unit). Никаких хардкоженных ключей в коде.
"""
from datetime import timedelta

import dj_database_url

from .base import *  # noqa: F403


# ===== Hosts =====
# Явно перечисляем хосты через DJANGO_ALLOWED_HOSTS="example.com,www.example.com".
# На Render дополнительно автоматически подхватываем RENDER_EXTERNAL_HOSTNAME
# (Render выставляет её сам, чтобы не пришлось хардкодить домен .onrender.com).
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()
]




# debug_toolbar НЕ подключать в prod
INSTALLED_APPS = [a for a in INSTALLED_APPS if a != 'debug_toolbar']  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]  # noqa: F405



# ===== Database =====
# PostgreSQL локально на VPS. В .env:
#   DATABASE_URL=postgres://vgbox:password@localhost:5432/vgbox
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', ''),
        conn_max_age=600,
    )
}


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
