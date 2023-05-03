# syntax=docker/dockerfile:1

FROM python:alpine
WORKDIR /app

RUN apk update
RUN apk add g++ sqlite

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY main.py .
COPY src/*.py ./src/
COPY src/bot/*.py ./src/bot/
COPY src/db/*.py ./src/db/
COPY src/db/*.sql ./src/db/
COPY src/game/*.py ./src/game/
COPY src/game/*.cpp ./src/game/

RUN mkdir bin
RUN g++ src/game/solver.cpp -o bin/solver.so -std=c++20 -O2 -shared -fPIC
RUN mkdir data
RUN sqlite3 data/db.sqlite3 < src/db/init_db.sql

CMD ["python3", "main.py"]
