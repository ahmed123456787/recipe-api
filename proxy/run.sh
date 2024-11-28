#!/bin/sh


set -e 
envsubst < etc/nginx/defualt.conf.tpl > /etc/nginx/conf.d/defualt.conf
nginx -g "deamon off;"