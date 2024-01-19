ARG DEBIAN_RELEASE

FROM debian:bookworm

ENV DEBIAN_FRONTEND noninteractive

RUN apt update

RUN apt -y --no-install-recommends install python-is-python3 python3-pip python3-dotenv python3-jinja2 curl git pkg-config python3-poetry

RUN mkdir /tmp/build

WORKDIR /tmp/build

ADD . /tmp/build

RUN poetry build

RUN pip3 install dist/*.whl --break-system-packages