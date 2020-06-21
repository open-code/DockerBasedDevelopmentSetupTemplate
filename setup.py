# This is a setup script, which will setup the full development and deployment environment in docker
# Pre requisites
# 1 - Docker installation
# 2 - Python installation (tested with python3)
# 3 - Python docker installation (pip install docker)
#
# What this script will do
# 1 - Create a docker network so that docker setup can use that network to communicate between docker containers
# 2 - Create a redis server docker image for php session managment(can exclude this by commenting the relevant section called "Redis Setup") and start it
#     Config of the redis docker will be mounted from local folder (${currentFolder}/docker_configs/redis/redis.conf)
# 3 - Create a Mysql docker image and start it
#     Config of the mysql docker will be mounted from local folder (${currentFolder}/docker_configs/mysql/)
#     For saving data, it will mount a local folder to mysql (${currentFolder}/localData/mysql/)
# 4 - Create php docker image from the docker file and use that to create a container(will refresh the exisiting image)
#     A folder from local machine (${currentFolder}/site) will be mounted as /var/www/html folder in docker container
#     A folder from local machine (${currentFolder}/logs) will be mounted as log folder (/usr/local/log) folder so that container logs will be
#     retained in the local machine
# Folder Structure
# root
#   - localData (docker mounted data storage ex mysql data)
#       - mysql
#   - docker_configs (contains docker mounted config files(ex mysql configs, redis configs etc))
#       - mysql
#       - redis
#           - redis.conf
#   - app   (contains app source codes)
#       - ${php_app_src}
#       - ${angular_app_src}
#   - logs (this will contain relevant logs from running apps via docker mounts)
#
# Note - When pushing this as a project to github, avoid pushing following directories
# 1 - ${currentFolder}/localData/
# 2 - ${currentFolder}/logs
# Note - sometimes, docker network cleanup does not work properly, in that case manually cleanup the docker network
# usefull commands to cleanup docker network (TODO - found why this happens, it's because running setup.py while containers are running - fix it)
# 1 - docker network ls
# 2 - docker network rm <network_id>
# 3 - docker network prune (removes all unused networks)

from pathlib import Path
from configparser import ConfigParser
import docker
import pathlib
import json

# client = docker.from_env()
client = docker.APIClient(base_url='unix://var/run/docker.sock')
current_dir = pathlib.Path().absolute()
current_dir_str = str(current_dir)

######################### Begin Helper Function Definitions #########################


def stop_and_remove_container(container_name):
    try:
        client.stop(container_name)
        client.wait(container_name)
        client.remove_container(container_name)
        print("LOG::WARN: existing container '{}' removed".format(container_name))
    except:
        print("LOG::DEBUG: no existing container with name '{}' exist".format(
            container_name))


def cleanup_and_create_container(name, pull_from_central, docker_volumes, docker_ports, docker_host_config, docker_environment):
    docker_img_name = config.get(
        'docker_imgs', '{}_docker_img_name'.format(name))
    docker_container_name = config.get(
        'docker_containers', '{}_docker_container_name'.format(name))
    docker_img_version = config.get(
        'docker_img_versions', '{}_docker_img_version'.format(name))

    # Pull the redis image if not exist
    if pull_from_central:
        for line in client.pull('{}:{}'.format(name, docker_img_version), stream=True, decode=True):
            print(json.dumps(line, indent=4))

    stop_and_remove_container(docker_container_name)

    docker_networking_config = client.create_networking_config({
        docker_network_name: client.create_endpoint_config()
    })

    # Create the container from the image
    client.create_container("{}:{}".format(docker_img_name, docker_img_version), name=docker_container_name, networking_config=docker_networking_config,
                            volumes=docker_volumes, ports=docker_ports, host_config=docker_host_config, environment=docker_environment)
    print("LOG::INFO: docker container '{}' created".format(
        docker_container_name))

######################### End Helper Function Definitions #########################


print("***********************************************************************************")
print("******************************* Start setup process *******************************")
print("***********************************************************************************")

#########################  Read Configuration file #########################
config = ConfigParser()
config.read('config.ini')

#########################  Docker Network Setup #########################
docker_network_name = config.get('docker_network', 'docker_network_name')
# Remove if network already exist
try:
    client.remove_network(docker_network_name)
    print("LOG::WARN: existing network '{}' removed".format(docker_network_name))
except:
    print("LOG::DEBUG: no existing network with name '{}' exist".format(
        docker_network_name))

# Create the network
client.create_network(docker_network_name)
print("LOG::INFO: network '{}' created".format(docker_network_name))


#########################  Redis Setup #########################
docker_redis_volumes = [
    '{}/docker_configs/redis/redis.conf'.format(current_dir_str)]

docker_redis_host_config = client.create_host_config(
    binds=['{}/docker_configs/redis/redis.conf:/usr/local/etc/redis/redis.conf'.format(current_dir_str)])

cleanup_and_create_container(
    'redis', True, docker_redis_volumes, None, docker_redis_host_config, None)

print("LOG::INFO: redis setup completed")

#########################  Mysql Setup #########################
Path("localData/mysql/8.0").mkdir(parents=True, exist_ok=True)

docker_mysql_volumes = [
    '{}/localData/mysql/8.0'.format(current_dir_str), '{}/docker_configs/mysql'.format(current_dir_str)]

mysql_docker_ports = [3306]
mysql_docker_host_config = client.create_host_config(
    binds=['{}/localData/mysql/8.0:/var/lib/mysql'.format(
        current_dir_str), '{}/docker_configs/mysql:/etc/mysql/conf.d'.format(current_dir_str)],
    port_bindings={
        3306: 3307
    })

mysql_docker_enviroment = ["MYSQL_ROOT_PASSWORD=root123"]

cleanup_and_create_container(
    'mysql', True, docker_mysql_volumes, mysql_docker_ports, mysql_docker_host_config, mysql_docker_enviroment)


print("LOG::INFO: mysql setup completed")
#########################  Angular Setup #########################
angular_app_src = config.get(
    'app_src_dirs', 'angular_app_src')
angular_docker_img_name = config.get(
    'docker_imgs', 'angular_docker_img_name')
angular_docker_img_version = config.get(
    'docker_img_versions', 'angular_docker_img_version')
angular_docker_build_response = [line for line in client.build(path='app/{}'.format(angular_app_src),
                                                               rm=True, tag='{}:{}'.format(angular_docker_img_name, angular_docker_img_version)
                                                               )]

angular_docker_volumes = [
    '{}/app/{}'.format(current_dir_str, angular_app_src)]

angular_docker_host_config = client.create_host_config(
    binds=['{}/app/{}:/app'.format(
        current_dir_str, angular_app_src)])

cleanup_and_create_container(
    'angular', False, angular_docker_volumes, None, angular_docker_host_config, None)
print("LOG::INFO: angular setup completed")
#########################  PHP Setup #########################
Path("logs/php").mkdir(parents=True, exist_ok=True)

angular_app_name = config.get(
    'app_names', 'angular_app_name')

php_app_name = config.get(
    'app_names', 'php_app_name')
php_app_src = config.get(
    'app_src_dirs', 'php_app_src')

php_docker_img_name = config.get(
    'docker_imgs', 'php_docker_img_name')
php_docker_img_version = config.get(
    'docker_img_versions', 'php_docker_img_version')
php_docker_build_response = [line for line in client.build(path='docker_files/php_localhost',
                                                           rm=True, tag='{}:{}'.format(php_docker_img_name, php_docker_img_version)
                                                           )]

php_docker_volumes = [
    '{}/app/{}'.format(current_dir_str, php_app_src), '{}/app/{}/dist/{}'.format(current_dir_str, angular_app_src, angular_app_src), '{}/logs/php'.format(current_dir_str)]

php_docker_ports = [80]
php_docker_host_config = client.create_host_config(
    binds=['{}/app/{}:/var/www/html/{}'.format(current_dir_str, php_app_src, php_app_name), '{}/app/{}/dist/{}:/var/www/html/{}'.format(
        current_dir_str, angular_app_src, angular_app_src, angular_app_name), '{}/logs/php:/usr/local/log'.format(current_dir_str)],
    port_bindings={
        80: 80
    })

cleanup_and_create_container(
    'php', False, php_docker_volumes, php_docker_ports, php_docker_host_config, None)
print("LOG::INFO: php setup completed")
print("***********************************************************************************")
print("***************************** Finished setup process ******************************")
print("***********************************************************************************")
