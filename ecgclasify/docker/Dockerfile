FROM python:3.7.3

MAINTAINER Abd. Jahiduddin <abd.jahiduddin@gmail.com>

WORKDIR /ecgclasify

COPY requirements.txt /ecgclasify
RUN pip install --no-cache-dir -r requirements.txt

COPY . /ecgclasify

CMD [ "python3", "app.py" ]


