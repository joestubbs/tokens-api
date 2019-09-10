# image: tapis/tokens-api
from tapis/flaskbase

ADD requirements.txt /home/tapis/requirements.txt

WORKDIR /home/tapis

# ----API specific code
ENV TAPIS_API tokens

COPY configschema.json /home/tapis/configschema.json
COPY config-local.json /home/tapis/config.json
COPY service /home/tapis/service

RUN chown -R tapis:tapis /home/tapis
USER tapis

