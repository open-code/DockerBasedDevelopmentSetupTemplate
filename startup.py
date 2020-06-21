# This is to startup docker based dev environment
# What this script will do
# 1 - Startup Redis docker container (can skip by commenting the relevant section "Redis Startup")
# 2 - Startup Mysql docker container
# 3 - Startup Angular container (which will have Angular app deployed on port 4200)
# 4 - Startup Php docker container (which will esentially have the full app deployed)


import docker
from configparser import ConfigParser

client = docker.APIClient(base_url='unix://var/run/docker.sock')
#########################  Read Configuration file #########################
config = ConfigParser()
config.read('config.ini')

#########################  Redis Startup #########################
redis_docker_container_name = config.get(
    'docker_containers', 'redis_docker_container_name')

client.start(redis_docker_container_name)

print("LOG::INFO: {} docker container started".format(redis_docker_container_name))
#########################  Mysql Startup #########################
mysql_docker_container_name = config.get(
    'docker_containers', 'mysql_docker_container_name')

client.start(mysql_docker_container_name)
print("LOG::INFO: {} docker container started".format(mysql_docker_container_name))
#########################  Angular Startup #########################
angular_docker_container_name = config.get(
    'docker_containers', 'angular_docker_container_name')

client.start(angular_docker_container_name)
print("LOG::INFO: {} docker container started".format(angular_docker_container_name))
#########################  Php Startup #########################
php_docker_container_name = config.get(
    'docker_containers', 'php_docker_container_name')

client.start(php_docker_container_name)
print("LOG::INFO: {} docker container started".format(php_docker_container_name))