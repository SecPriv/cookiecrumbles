FROM python:3.10 as base

WORKDIR /usr/src

COPY . .

FROM base AS v0.6.1
RUN echo "" > /usr/src/vulnerable

RUN pip install -r requirements.txt

CMD python main.py


FROM base AS v0.6.2
RUN echo "" > /usr/src/not_fixed

COPY patches/patch-requirements-0.6.2.txt .

RUN patch -p0 < patch-requirements-0.6.2.txt
RUN pip install -r requirements.txt

CMD python main.py
