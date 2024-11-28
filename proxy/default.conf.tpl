server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/static 
    } 

    location / {
        wusgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/wusgi_params;
        client_max_body_size    10M;
    }
}
