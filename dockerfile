FROM python:alpine

WORKDIR /root


COPY . .

RUN apk add --no-cache --virtual .build gcc g++ libgcc musl-dev make \
    && pip3 install -r requirements.txt \
    && apk add sqlite nginx \
    && apk del .build gcc g++ libgcc musl-dev make

VOLUME ["/root/data"]

EXPOSE 8000

CMD ["/root/run.sh"]
# CMD ["sh"]