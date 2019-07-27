FROM python:3.7.3

MAINTAINER Abd. Jahiduddin <abd.jahiduddin@gmail.com>

WORKDIR /ecgstorageapi

COPY requirements.txt /ecgstorageapi
RUN pip install --no-cache-dir -r requirements.txt

COPY . /ecgstorageapi

CMD [ "python3", "app.py" ]
