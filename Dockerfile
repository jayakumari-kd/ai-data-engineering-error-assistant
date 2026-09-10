FROM jupyter/pyspark-notebook:latest

ARG AUTHOR="Jaya Kumari<kumarijayamishra12@gmail.com>"
ARG COURSE_NAME="Mastering Big Data Analytics with Pyspark"
ARG CONTAINER_NAME="mastering-pyspark-ml"
ARG VERSION="20240727"

ENV HOME=/home/jovyan
ENV VERSION=${VERSION}

LABEL maintainer=${AUTHOR}
LABEL version=${VERSION}

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /tmp/requirements.txt

ENV SPARK_JUPYTER_ENABLE_LABHOME=yes
ENV JUPYTER_TOKEN=masteringpysparkml
ENV PATH=$PATH:$SPARK_HOME/bin

EXPOSE 8888
EXPOSE 8501
EXPOSE 4040
EXPOSE 4041
EXPOSE 4042
EXPOSE 4043
EXPOSE 4044
EXPOSE 4045

CMD ["start-notebook.sh"]
