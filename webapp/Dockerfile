FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq
RUN apt-get install -y -qq software-properties-common build-essential
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get install -y -qq  python3.7 python3.7-dev default-libmysqlclient-dev libssl-dev
RUN apt-get install -y -qq curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#ModuleNotFoundError: No module named 'distutils.util' 
#https://github.com/pypa/get-pip/issues/43
RUN apt-get install -y -qq python3-distutils
RUN python3.7 get-pip.py

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
ADD app/ /app


CMD ["python3.7","execute.py"]
