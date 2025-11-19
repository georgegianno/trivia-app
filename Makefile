# Build in python 3.11.10

VENV = virtualenv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python
ROOT_DIR = project
MANAGE = $(PYTHON) manage.py
TEST_PORT = 5000

PGPASSFILE := $(CURDIR)/.pgpass
export PGPASSFILE

DB_HOST := localhost
DB_PORT := 5432
DB_NAME := trivia_db
DB_USER := trivia_db_owner
DB_BACKUP := trivia_db.psql

virtualenv:
	$(shell which python3) -m venv $(VENV)
	@echo 'Virtualenv is ready at $(VENV)'
	$(PIP) install --upgrade pip

install_requirements:
	$(PIP) install -r requirements.txt
	@echo 'Requirements installed'

# Db management commands

# Creates db using sql file
create_db:
	sudo su postgres -c 'psql -f $(ROOT_DIR)/create_db.sql'

# Drops db using sql file
drop_db:
	sudo su postgres -c 'psql -f $(ROOT_DIR)/drop_db.sql'
	@echo 'Database dropped'

# Backup the current db. Overrides the same file every time it is called.
backup_db:
	sudo chmod 600 $(PGPASSFILE)
	PGPASSFILE=$(PGPASSFILE) pg_dump -h $(DB_HOST) -U $(DB_USER) -p $(DB_PORT) -d $(DB_NAME) -f $(DB_BACKUP)
	@echo 'Database saved in file: ./$(DB_BACKUP)'

# Recreates the db, without migrations
truncate_db:
	make drop_db
	make create_db
	@echo 'Database trivia_db recreated'

# Recreates db and migrates the tables
recreate_db:
	make truncate_db
	make migrate
	make run

# Restores db in the latest saved state
restore_db:
	make truncate_db
	PGPASSFILE=$(PGPASSFILE) psql -h $(DB_HOST) -U $(DB_USER) -p $(DB_PORT) -d $(DB_NAME) -f $(DB_BACKUP)
	make migrate
	make run

collectstatic:
	$(MANAGE) collectstatic --noinput --clear

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

run:
	$(MANAGE) runserver $(TEST_PORT)

import_data:
	$(MANAGE) import_data

# Creates the unexisting file 'settings_local.py', which is called in 'settings.py', for local use. The file 'settings_local_fallback.py'
# does not exist, and works as an intermediary file to create the local copy. 
sync_local:
	cd project && \
	if [ ! -e settings_local.py ]; then \
		ln -s settings_local_fallback.py settings_local.py; \
	fi


# Builds the whole application from scratch.
build_app: 
	make virtualenv
	make install_requirements 
	make create_db 
	@echo 'Database trivia_db created'
	make migrate
	make collectstatic
	@echo 'Build complete!'
	make sync_local
	make import_data
	make run

test:
	sudo su postgres -c 'psql -f $(ROOT_DIR)/create_db_test.sql'
	$(MANAGE) test
