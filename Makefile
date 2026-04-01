.PHONY: build clean start test-unit test-unit-v

build:
	docker compose build

run:
	docker compose up

clean:
	docker compose rm -fv && docker compose down -v --remove-orphans

test-unit:
	python -m unittest discover -s ./tests/unit/lib

test-unit-v:
	python -m unittest discover -v -s ./tests/unit/lib