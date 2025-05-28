import sys
import os

# Добавляем путь к проекту
project_home = '/home/yourusername/festival-schedule'  # Замените yourusername на ваше имя пользователя
if project_home not in sys.path:
   sys.path.append(project_home)

# Импортируем приложение Flask
from festival_schedule_app import app as application