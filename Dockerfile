FROM continuumio/anaconda3:latest
LABEL maintainer "Data Science Brigade <contato@datasciencebr.com>"

RUN mkdir -p /home/jovyan/toolbox
WORKDIR /home/jovyan/toolbox

COPY serenata_toolbox ./serenata_toolbox
COPY setup.py ./
RUN pip install -e .
