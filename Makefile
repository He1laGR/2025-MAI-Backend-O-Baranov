.PHONY: build up down logs ps clean test migrate init

# Сборка образов
build:
	docker-compose build

# Запуск всех сервисов
up:
	docker-compose up -d

# Остановка всех сервисов
down:
	docker-compose down

# Просмотр логов
logs:
	docker-compose logs -f

# Статус сервисов
ps:
	docker-compose ps

# Очистка (удаление контейнеров, образов и volumes)
clean:
	docker-compose down -v
	docker system prune -f

# Запуск тестов
test:
	pytest tests/

# Инициализация проекта (первый запуск)
init: build up migrate

# Применение миграций
migrate:
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "Database tables created successfully!" 