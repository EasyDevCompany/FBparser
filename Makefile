SHELL = /bin/sh
CURRENT_UID := $(shell id -u)


start:
	docker-compose --env-file ./src/.env up -d --build

stop:
	docker stop $$(docker ps -a -q)

format:
	docker run --rm -v $(CURDIR):/data cytopia/black . -l 120 -t py38
	docker run --rm -v $(CURDIR):/data chelovek/cisort --profile black --line-length 120 .

remove_all:
	(docker stop $$(docker ps -a -q) && \
    docker container rm $$(docker ps -aq) -f && \
	docker rmi -f $$(docker images -aq) && \
	docker volume rm $$(docker volume ls -q --filter dangling=true))

remove_except_postgres:
	(docker stop $$(docker ps -a -q) && \
	docker rm $$(docker ps -a -q | grep -v `docker ps -a -q --filter "name=db"`) && \
	docker rmi -f $$(docker images -aq) && \
	docker volume prune)