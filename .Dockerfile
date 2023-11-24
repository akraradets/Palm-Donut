FROM python:3.10.12-bookworm

ARG DEBIAN_FRONTEND=noninteractive
# Timezone
ENV TZ="Asia/Bangkok"

RUN apt update && apt upgrade -y
# Set timezone
RUN apt install -y tzdata
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone
# Set locales
# https://leimao.github.io/blog/Docker-Locale/
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL en_US.UTF-8 
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en


WORKDIR /root/project

RUN pip3 install --upgrade pip
RUN pip3 install pipenv
# For cv2
RUN apt update && apt install -y ffmpeg libsm6 libxext6
# GDAL
RUN apt install -y gdal-bin libgdal-dev
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
# RUN pipenv install GDAL==3.6.2

COPY ./project/Pipfile ./project/Pipfile.lock /root/project/
RUN pipenv install

RUN apt-get clean && rm -rf /var/lib/apt/lists/*
CMD tail -f /dev/null