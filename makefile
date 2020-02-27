.PHONY: all run

all: run

run:
	python3 src/sock.py PORT=${PORT}