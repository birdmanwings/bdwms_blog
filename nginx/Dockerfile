FROM nginx:1.13.12

RUN rm /etc/nginx/conf.d/default.conf
COPY bdwms_blog.conf /etc/nginx/conf.d/bdwms_blog.conf
COPY cert /etc/nginx/