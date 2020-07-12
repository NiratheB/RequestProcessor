FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /RequestProcessor
ADD requirements.txt /RequestProcessor/

WORKDIR /RequestProcessor


RUN pip install -r requirements.txt
ADD . /RequestProcessor/
