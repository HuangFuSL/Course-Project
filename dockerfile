FROM python:alpine

WORKDIR /root
COPY . .

RUN apk add --no-cache --virtual .build gcc g++ libgcc musl-dev make \
    && pip3 install -r requirements.txt \
    && apk add sqlite \
    && apk del .build gcc g++ libgcc musl-dev make

EXPOSE 8000

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0"]