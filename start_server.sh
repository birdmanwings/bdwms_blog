#!/bin/sh
# 升级数据库
flask initdb

# 启动服务，使用exec以防止另起进程
exec gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
