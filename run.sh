#!/bin/sh
cd ~
chmod -R 777 .
nginx -c ~/conf/nginx.conf -p /root
uvicorn main:app --host 0.0.0.0 --port 8001