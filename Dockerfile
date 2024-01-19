ARG DEBIAN_RELEASE

FROM debian:bookworm

ENV DEBIAN_FRONTEND noninteractive

RUN apt update

RUN apt -y --no-install-recommends install python-is-python3 python3-pip python3-dotenv python3-jinja2 curl git pkg-config build-essential libpython3-dev python3-poetry libaspell-dev libsqlite3-dev

RUN mkdir /home/mcmxi

RUN adduser --home /home/mcmxi mcmxi

ENV HOME /home/mcmxi

RUN mkdir -p /usr/src/mcmxi

WORKDIR /usr/src/mcmxi

ADD . /usr/src/mcmxi

RUN chown -R mcmxi /home/mcmxi

USER mcmxi

VOLUME /home/mcmxi

RUN poetry install

RUN poetry run mcmxi

ENTRYPOINT ["poetry", "run", "mcmxi"]
