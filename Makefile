SHELL = /bin/sh
CURRENT_UID := $(shell id -u)

format:
	docker run --rm -v $(CURDIR):/data cytopia/black . -l 120 -t py38
	docker run --rm -v $(CURDIR):/data chelovek/cisort --profile black --line-length 120 .

remove_all:
	(docker stop $$(docker ps -a -q) && \
    docker container rm $$(docker ps -aq) -f && \
	docker rmi -f $$(docker images -aq) && \
	docker volume rm $$(docker volume ls -q --filter dangling=true))