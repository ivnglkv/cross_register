dc=docker-compose

migrate:
	$(dc) exec cr-python python manage.py migrate

build:
	$(dc) build cr-python
	$(dc) build

dev: build
	$(dc) up -d cr-postgres
	sleep 5
	$(dc) up -d cr-python
	sleep 5
	$(dc) exec cr-python python manage.py migrate

restore:
	mkdir -p /opt/database/cross_register/
	cp ../cross_register_db.dump /opt/database/cross_register/
	$(dc) exec cr-postgres pg_restore -cv -d cr_db -O -h localhost -U postgres /var/lib/postgresql/data/cross_register_db.dump
