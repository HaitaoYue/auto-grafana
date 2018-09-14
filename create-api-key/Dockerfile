FROM ppc64le/python:3.6

COPY requirements.txt /
RUN cd / && pip install -r requirements.txt
COPY init.py /app/
WORKDIR /app
