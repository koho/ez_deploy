# Easy Deployment

Easy deployment tool for Python application. It can manager virtual environment 

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
                    [--service-program SERVICE_PROGRAM]
                    [--service-arguments SERVICE_ARGUMENTS [SERVICE_ARGUMENTS ...]]
                    [--service-start SERVICE_START]
                    [--service-display SERVICE_DISPLAY]
                    [--service-description SERVICE_DESCRIPTION]
                    [--service-depend SERVICE_DEPEND]
                    [--service-obj SERVICE_OBJ]
                    [--service-password SERVICE_PASSWORD]
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
  --service-program SERVICE_PROGRAM
                        service bin path
  --service-arguments SERVICE_ARGUMENTS [SERVICE_ARGUMENTS ...]
                        service arguments
  --service-start SERVICE_START
                        service start mode <auto|manual>

Options for Windows:
  Service options for Windows

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
    "start": "auto"
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