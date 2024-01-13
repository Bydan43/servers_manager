FROM python:3.10.13-slim-bullseye

ARG WORKDIR="/servers_mananger"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV BASE_URL=""
ENV DATABASE_URL=""

RUN set -eux \
    ;\
    pip install --upgrade pip \
    && apt-get update \
    && apt-get install -y \
               build-essential \
    ;\
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /

RUN set -eux; \
    pip install --no-cache-dir -r /requirements.txt \
    && mkdir -p ${WORKDIR}/app

COPY app/ $WORKDIR/app
COPY run.py $WORKDIR/run.py
COPY run.sh $WORKDIR/run.sh

RUN chmod +x $WORKDIR/run.sh

VOLUME $WORKDIR

WORKDIR $WORKDIR

EXPOSE 5000

ENTRYPOINT ["/servers_mananger/run.sh"]

