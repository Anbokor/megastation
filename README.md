# Megastation

Megastation - это интернет-магазин сотовых телефонов и аксессуаров, разработанный на **Django + DRF** для бэкенда и **Vue 3** для фронтенда.

## 🚀 Функционал
- 📦 **Каталог товаров**: просмотр, фильтрация и сортировка товаров.
- 🛒 **Корзина**: добавление, удаление и оформление заказов.
- 🛍 **Оформление заказов**: создание, отмена и отслеживание статуса заказов.
- 🏪 **Складской учет**: автоматическое управление запасами.
- 👤 **Пользователи и роли**: Администраторы, продавцы, покупатели.
- 🔔 **Уведомления о низком запасе**.
- 📑 **Управление накладными**: создание, аннулирование, изменение статусов.

## 🛠 Технологический стек
- **Backend**: Django, Django REST Framework, PostgreSQL, Celery, Redis
- **Frontend**: Vue 3, Vite, Vue Router, Pinia, Axios
- **Deployment**: Docker, Docker Compose

## 📥 Установка
### 1. Клонирование репозитория
```bash
git clone https://github.com/Anbokor/megastation.git
cd megastation
```

### 2. Установка зависимостей
Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv .venv
source .venv/bin/activate  # Для Linux/macOS
.venv\Scripts\activate    # Для Windows
pip install -r requirements.txt
```

### 3. Настройка базы данных
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Запуск проекта
```bash
python manage.py runserver
```

## 🐳 Запуск в Docker
```bash
docker-compose up --build
```

## 📌 API-документация
Документация API доступна по адресу:
```
http://127.0.0.1:8000/api/docs/
```

## 📬 Контакты
Если у вас есть вопросы или предложения, пишите в Issues репозитория или создавайте Pull Requests.

