FROM nginx:1.13.12

RUN rm /etc/nginx/conf.d/default.conf
COPY bdwms_blog.conf /etc/nginx/conf.d/bdwms_blog.conf

RUN mkdir /etc/nginx/cert
WORKDIR /etc/nginx/cert
COPY cert/1888125_birdmanwings.com.pem 1888125_birdmanwings.com.pem
COPY cert/1888125_birdmanwings.com.key 1888125_birdmanwings.com.key