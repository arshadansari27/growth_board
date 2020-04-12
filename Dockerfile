FROM python:3.8-apline

ENV LANGUAGE=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LC_MESSAGES=en_US.UTF-8

RUN sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

COPY setup.py Makefile config.yml ./
COPY requirements.txt requirements.dev.txt ./
RUN pip install -r requirements.txt
COPY scripts/ ./scripts/
COPY sql/ ./sql/
COPY growth/ ./growth/
RUN pip install -e .