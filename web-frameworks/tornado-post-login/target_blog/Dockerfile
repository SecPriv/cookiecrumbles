FROM python:3.7 as base

RUN mkdir -p /usr/src/app

### Clone and checkout the right version
WORKDIR /usr/src/
RUN git clone https://github.com/tornadoweb/tornado.git
WORKDIR /usr/src/tornado
RUN git checkout e72cc5769265abf0a279a293fa9cb383cff84db8

### Copy blog application to /usr/src/app
RUN cp -r demos/blog/* /usr/src/app

WORKDIR /usr/src/app

FROM base AS v6.2.0
RUN pip install --no-cache-dir -r requirements.txt

### Apply the diffs
COPY csrf_app.diff .
RUN patch -p1 -i csrf_app.diff

ENTRYPOINT ["python3", "blog.py"]
