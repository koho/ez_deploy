# Easy Deployment

Easy deployment tool for Python application. It can manage virtual environment and create service.

## Install
Download and install the `ez-deploy` package for python.
```
pip install ez-deploy
```
## Usage:
Use the `ez-deploy` command to manage deployment.
```
usage: ez_deploy.py [-h] [-c CONFIG] [--env ENV] [--requirements REQUIREMENTS]
                    [--dir DIR] [--service-name SERVICE_NAME]
                    [--service-start SERVICE_START]
                    [--service-program SERVICE_PROGRAM]
                    [--service-arguments SERVICE_ARGUMENTS [SERVICE_ARGUMENTS ...]]
                    [--service-display SERVICE_DISPLAY]
                    [--service-description SERVICE_DESCRIPTION]
                    [--service-depend SERVICE_DEPEND]
                    [--service-obj SERVICE_OBJ]
                    [--service-password SERVICE_PASSWORD]
                    [--service-file SERVICE_FILE]
                    [--service-convert-path SERVICE_CONVERT_PATH]
                    command

Easy Deployment Tool

positional arguments:
  command               Command <env|deploy|install|uninstall|start|stop>

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        use config file (JSON format, default=deployment.json)
  --env ENV             virtual environment path
  --requirements REQUIREMENTS
                        package requirements file (default=requirements.txt)
  --dir DIR             package lookup directory
  --service-name SERVICE_NAME
                        service name
  --service-start SERVICE_START
                        service start mode <auto|manual> (default=manual)

Options for Windows:
  Service options for Windows

  --service-program SERVICE_PROGRAM
                        service bin path
  --service-arguments SERVICE_ARGUMENTS [SERVICE_ARGUMENTS ...]
                        service arguments
  --service-display SERVICE_DISPLAY
                        service display name
  --service-description SERVICE_DESCRIPTION
                        service description
  --service-depend SERVICE_DEPEND
                        service dependencies
  --service-obj SERVICE_OBJ
                        service login account
  --service-password SERVICE_PASSWORD
                        service login password
  --service-restart     restart service after service failure
  --service-restart-delay SERVICE_RESTART_DELAY
                        restart delay(in seconds) after service failure

Options for Linux:
  Service options for Linux

  --service-file SERVICE_FILE
                        service file to install (default=SERVICE_NAME.service)
  --service-convert-path SERVICE_CONVERT_PATH
                        convert service path to absolute path
```
Also, you can create a `deployment.json` file in a directory and run `ez-deploy` to load it.
```json
{
  "env": "venv",
  "requirements": "requirements.txt",
  "dir": "packages",
  "service": {
    "name": "example",
    "program": "python",
    "arguments": ["main.py"],
    "display": "Example Service",
    "description": "A service",
    "start": "auto",
    "file": "example.service",
    "restart": true,
    "restart_delay": 30
  }
}
```

## Examples
1. Create a virtual environment named `venv`:
```cmd
ez-deploy env --env=venv
```

2. Install packages in the virtual environment:
```cmd
ez-deploy deploy --env=venv --requirements=requirements.txt
```

3. Run a python script as service:
```cmd
ez-deploy install --service-name=python-service --service-program=/usr/bin/python --service-arguments main.py
```