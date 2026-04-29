.PHONY: build clean start test-unit test-unit-v dict-local-import print-db-config

build:
	docker compose build

run:
	docker compose up

clean:
	docker compose rm -fv && docker compose down -v --remove-orphans

test-unit:
	docker run --rm -it -v .:/app venngame-app:latest python -m unittest discover -s ./tests/unit/lib

test-unit-v:
	docker run --rm -it -v .:/app venngame-app:latest python -m unittest discover -v -s ./tests/unit/lib

dict-local-import:
	docker exec -it venngame-app-1 python -m src.scripts.dictionary import ./src/data/dictionary.txt
	docker exec -it venngame-db-1 pg_dump -U root -d primary -t dictionary --data-only > ./container/db/primary/01-dictionary.sql

print-db-config:
	@echo export VENNGAME_DATABASE_URL="postgres://root:passwordCity@localhost:5432/primary"