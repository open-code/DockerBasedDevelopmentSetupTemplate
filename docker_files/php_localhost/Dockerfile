FROM php:7.3-apache

# run non-interactive. Suppresses prompts and just accepts defaults automatically.
ENV DEBIAN_FRONTEND=noninteractive

# update os
RUN apt-get update; \
    apt-get -yq upgrade; \
    apt-get install -y --no-install-recommends \
    apt-utils \
    nano; \
    apt-get -yq autoremove; \
    apt-get clean; \ 
    rm -rf /var/lib/apt/lists/*

# create required log directories
RUN mkdir /usr/local/log; \
    mkdir /usr/local/log/apache2; \
    mkdir /usr/local/log/php; \
    chmod -R ug+w /usr/local/log

# create PHP.ini file
RUN cp /usr/local/etc/php/php.ini-development /usr/local/etc/php/php.ini

# install MySQLi
RUN docker-php-ext-install mysqli 

# install PDO mysql driver
RUN docker-php-ext-install pdo pdo_mysql

# install xdebug, igbinary 
RUN pecl channel-update pecl.php.net; \
    pecl install xdebug-2.7.2; \
    pecl install igbinary-3.0.1; \
    pecl bundle redis-5.0.2 && cd redis && phpize && ./configure --enable-redis-igbinary && make && make install; \
    docker-php-ext-enable xdebug igbinary redis

# cleanup inis after above commands
RUN rm -rf /usr/local/etc/php/conf.d/docker-php-ext-igbinary.ini; \
    rm -rf /usr/local/etc/php/conf.d/docker-php-ext-redis.ini; \ 
    rm -rf /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini

# create php config in conf.d
RUN { \
        echo 'short_open_tag = Off'; \
        echo 'expose_php = Off'; \    
        echo 'error_reporting = E_ALL & ~E_STRICT'; \
        echo 'display_errors = On'; \
        echo 'error_log = /usr/local/log/php/php_errors.log'; \
        echo 'allow_url_fopen = on'; \
        echo '[xdebug]'; \
        echo 'upload_tmp_dir = /tmp/'; \
        echo 'zend_extension="xdebug.so"'; \
        echo 'xdebug.remote_autostart = 1'; \
        echo 'xdebug.remote_enable = 1'; \
        echo 'xdebug.remote_connect_back = 0'; \
        echo 'xdebug.remote_port = 9001'; \
        echo 'xdebug.remote_host = host.docker.internal'; \
        echo 'xdebug.idekey = VSCODE'; \
        echo '[redis]'; \
        echo 'extension="redis.so"'; \
        echo 'extension="igbinary.so"'; \
        echo 'session.save_handler = "redis"'; \
        echo 'session.save_path = "tcp://redis-localhost:6379?weight=1&timeout=2.5"'; \
    } > /usr/local/etc/php/conf.d/php-config.ini

# set up the apache environment 
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /usr/local/log/apache2

# apache mods
RUN a2enmod rewrite 

# serverName parameter
RUN echo "ServerName localhost" | tee /etc/apache2/conf-available/servername.conf
RUN a2enconf servername

# update the default apache site 
RUN { \
        echo '<VirtualHost *:80>'; \
        echo '    ServerAdmin your_email@example.com'; \
        echo '    DocumentRoot /var/www/html'; \
        echo '    <Directory /var/www/html/>'; \
        echo '        Options Indexes FollowSymLinks MultiViews'; \
        echo '        AllowOverride All'; \
        echo '        Order deny,allow'; \
        echo '        Allow from all'; \
        echo '    </Directory>'; \
        echo '    ErrorLog /usr/local/log/apache2/error.log'; \
        echo '    CustomLog /usr/local/log/apache2/access.log combined' ; \
        echo '</VirtualHost>'; \
    } > /etc/apache2/sites-enabled/000-default.conf

EXPOSE 80
