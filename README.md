# DockerBasedDevelopmentSetupTemplate
This is a Docker based development setup for php back end and angular front end, this include redis server for session management and mysql server as well

## Pre requisites
1. Docker installation
2. Python installation (tested with python3)
3. Python docker installation (pip install docker)

## How to 
1. Simply clone the repo
2. Modify the config.ini with relevant properties
3. Run `setup.py` with command `python setup.py`
4. Run `startup.py` with command `python startup.py`

Then you can point to http://localhost/{your_php_app_name} to access the back end php site
http://localhost/{your_angular_app_name} to access your angular application

## Customize
You would only need to change config.ini file as it has all the required configurations.

_**Note**_ - first time you run `startup.py` it won't work properly, because angular takes some time to build the
distribution, so php server startup before distribution folder is created(hence mount won't work properly)
so, simply restart the php server and it will work. (subsequent `startup.py` calls will work properly as angular distribution folder is not getting deleted)
