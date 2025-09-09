import os
import sys

# Добавьте путь к вашему проекту
path = '/home/вашusername/django-quotes-app'
if path not in sys.path:
    sys.path.append(path)

# Настройте переменные окружения
os.environ['DJANGO_SETTINGS_MODULE'] = 'quote_project.settings'

# Импортируйте и настройте Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
