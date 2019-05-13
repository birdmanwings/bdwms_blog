#!/bin/sh
# 升级数据库
flask initdb

# 启动服务，使用exec以防止另起进程,注意这里要开放为0.0.0.0，因为这是在容器中，监听nginx的所有转发（动态地址）
exec gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
