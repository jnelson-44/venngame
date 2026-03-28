.PHONY: build clean start 

build:
	docker compose build

run:
	docker compose up

clean:
	docker compose rm -fv && docker compose down -v --remove-orphans
