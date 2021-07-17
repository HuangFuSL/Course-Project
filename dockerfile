FROM python:alpine

WORKDIR /root

RUN mkdir logs && mkdir temp

COPY . .

RUN apk add --no-cache --virtual .build gcc g++ libgcc musl-dev make \
    && pip3 install -r requirements.txt \
    && apk add sqlite nginx \
    && apk del .build gcc g++ libgcc musl-dev make

RUN chmod 777 run.sh

VOLUME ["/root/data"]

EXPOSE 8000

CMD ["/root/run.sh"]
# CMD ["sh"]