FROM python:slim

RUN apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y build-essential

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /usr/app/src/
