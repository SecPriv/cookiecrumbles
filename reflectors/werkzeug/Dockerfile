FROM python:3.10-alpine
RUN pip install --no-cache-dir --upgrade werkzeug==2.2.2
COPY . /usr/src/reflector
WORKDIR /usr/src/reflector
CMD [ "python", "./app.py" ]