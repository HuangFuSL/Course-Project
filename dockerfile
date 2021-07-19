FROM ubuntu:latest

WORKDIR /root
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir logs && mkdir temp

RUN apt update \
    && apt install build-essential gcc g++ musl-dev make python3 python3-pip \
    gfortran sqlite nginx python3-scipy -y -q \
    && pip3 install --no-cache-dir numpy

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN apt remove build-essential gcc g++ musl-dev make gfortran -y -q \
    && apt autoremove -y -q

RUN chmod 777 run.sh

VOLUME ["/root/data"]

EXPOSE 8000

CMD ["/root/run.sh"]
# CMD ["sh"]