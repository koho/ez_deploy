import argparse
import configparser
import functools
import json
import os
import sys
import subprocess
import venv

IS_WIN = sys.platform == "win32"


def install(name, program, arguments=None, path=None, convert_path=False, **kwargs):
    if not name:
        print_error('Service name not specified')
        sys.exit(1)
    print(f'Installing {name}...')
    if IS_WIN:
        if not program or not path:
            print_error('Service program or home path not specified')
            sys.exit(1)
        bin_dir = os.path.join(path, 'Scripts')
        wrapper_path = os.path.join(bin_dir, 'srvwrapper.exe')
        activate_path = os.path.join(bin_dir, 'activate.bat')
        if not os.path.exists(wrapper_path) or not os.path.exists(activate_path):
            print_error('Invalid wrapper path or activate path')
            sys.exit(1)
        args = [activate_path, '&', wrapper_path, name, program]
        if arguments:
            args.extend(['--arguments', ' '.join(arguments)])
        for extra in ['display', 'description', 'start', 'depend', 'obj', 'password']:
            if kwargs.get(extra):
                args.extend([f'--{extra}', kwargs[extra]])
        subprocess.check_call(args, shell=True)
    else:
        if not os.path.isfile(name):
            print_error(f'Service file \'{name}\' not found')
            sys.exit(1)
        service_name = os.path.basename(name)
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(name)
        if convert_path and 'Service' in parser:
            for p in ['ExecStartPre', 'ExecStartPost', 'ExecStart', 'ExecReload',
                      'ExecStop', 'ExecStopPost', 'WorkingDirectory']:
                if parser['Service'].get(p):
                    parser['Service'][p] = parser['Service'][p].replace('./', os.getcwd() + '/')
        with open(f'/etc/systemd/system/{service_name}', 'w') as f:
            parser.write(f)
        if kwargs.get('start') == 'auto':
            os.system(f'systemctl enable {service_name}')
    return True


def check_arg(message):
    def wrapper(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            if any(not v for v in args):
                print_error(message)
                sys.exit(1)
            return func(*args, **kwargs)
        return _wrapper
    return wrapper


def print_error(*args, **kwargs):
    print('ERROR:', *args, file=sys.stderr, **kwargs)


@check_arg('Service not specified')
def uninstall(name):
    print(f'Uninstall {name}...')
    if IS_WIN:
        subprocess.check_call(f'SC delete {name}')
        with open(os.devnull, 'w') as f:
            subprocess.call(f'net stop {name}', stdout=f, stderr=f)
    else:
        os.system(f'systemctl stop {name}')
        os.system(f'systemctl disable {name}')
        os.system(f'rm /etc/systemd/system/{name}')
        os.system(f'systemctl daemon-reload')
        os.system(f'systemctl reset-failed')
    return True


@check_arg('Service not specified')
def start(name):
    print(f'Starting {name}...')
    if IS_WIN:
        subprocess.check_call(f'net start {name}')
    else:
        os.system(f'systemctl start {name}')
    return True


@check_arg('Service not specified')
def stop(name):
    print(f'Stopping {name}...')
    if IS_WIN:
        subprocess.check_call(f'net stop {name}')
    else:
        os.system(f'systemctl stop {name}')
    return True


def deploy(path, requirements=None, package_dir=None):
    print(f'Using environment \'{path}\'')
    if IS_WIN:
        bin_dir = os.path.join(path, 'Scripts')
        pip_bin = 'pip.exe'
    else:
        bin_dir = os.path.join(path, 'bin')
        pip_bin = 'pip'
    pip_path = os.path.join(bin_dir, pip_bin)
    if not requirements and os.path.exists('requirements.txt'):
        requirements = 'requirements.txt'
    if requirements:
        print(f'Using requirements file: {requirements}')
        args = [pip_path, 'install', '-r', requirements]
        if package_dir:
            args.extend(['--no-index', '--find-links', package_dir])
        subprocess.check_call(args, shell=False)
    return True


@check_arg('Environment path not specified')
def env(path):
    if not os.path.exists(path):
        print(f'Creating virtual environment \'{path}\'...')
        if os.name == 'nt':
            use_symlinks = False
        else:
            use_symlinks = True
        venv.create(path, symlinks=use_symlinks, with_pip=True)
    return True


def main():
    parser = argparse.ArgumentParser(description='Easy Deployment Tool', add_help=True)
    parser.add_argument('command', help='Command <env|deploy|install|uninstall|start|stop>')

    parser.add_argument('-c', '--config', dest='config', action='store', default='deployment.json',
                        help='use config file (JSON format, default=deployment.json)')
    parser.add_argument('--env', dest='env', help='virtual environment path')
    parser.add_argument('--requirements', dest='requirements',
                        help='package requirements file (default=requirements.txt)')
    parser.add_argument('--dir', dest='dir', help='package lookup directory')
    parser.add_argument('--service-name', dest='service_name', help='service name')
    parser.add_argument('--service-start', dest='service_start',
                        help='service start mode <auto|manual> (default=manual)')
    windows_group = parser.add_argument_group('Options for Windows', 'Service options for Windows')
    windows_group.add_argument('--service-program', dest='service_program', help='service bin path')
    windows_group.add_argument('--service-arguments', nargs='+', dest='service_arguments', help='service arguments')
    windows_group.add_argument('--service-display', dest='service_display', help='service display name')
    windows_group.add_argument('--service-description', dest='service_description', help='service description')
    windows_group.add_argument('--service-depend', dest='service_depend', help='service dependencies')
    windows_group.add_argument('--service-obj', dest='service_obj', help='service login account')
    windows_group.add_argument('--service-password', dest='service_password', help='service login password')
    linux_group = parser.add_argument_group('Options for Linux', 'Service options for Linux')
    linux_group.add_argument('--service-file', dest='service_file', help='service file to install '
                                                                         '(default=SERVICE_NAME.service)')
    linux_group.add_argument('--service-convert-path', dest='service_convert_path',
                             help='convert service path to absolute path')
    options = parser.parse_args()
    config = {}
    if os.path.exists(options.config):
        with open(options.config, encoding='utf8') as f:
            config = json.load(f)
    for name, value in options.__dict__.items():
        if value is None:
            continue
        pk, sep, sk = name.partition('_')
        if not pk:
            continue
        if sk:
            if pk not in config:
                config[pk] = {}
            config[pk][sk] = value
        else:
            config[pk] = value
    service = config.get('service', {})
    if IS_WIN:
        service_name = service.get('name')
    else:
        if service.get('file'):
            service_name = service['file']
        elif service.get('name'):
            service_name = service['name'] + '.service'
        else:
            service_name = None
    if 'name' in service:
        service.pop('name')
    action_map = {
        'env': {'func': env, 'args': (config.get('env'),)},
        'deploy': {'func': deploy, 'args': (config.get('env'), config.get('requirements'), config.get('dir')),
                   'depends': ['env']},
        'start': {'func': start, 'args': (service_name,)},
        'stop': {'func': stop, 'args': (service_name,)},
        'install': {'func': install, 'args': tuple(),
                    'kwargs': {'name': service_name, 'program': service.get('program'),
                               'path': config.get('env'), **service},
                    'depends': ['deploy']},
        'uninstall': {'func': uninstall, 'args': (service_name,)},
    }
    if options.command in action_map:
        run(options.command, action_map)
    else:
        print_error(f'Unknown command \'{options.command}\'')


def run(command, action_map):
    if command not in action_map:
        return False
    action = action_map[command]
    for dep in action.get('depends', []):
        if not run(dep, action_map):
            return False
    return action['func'](*action['args'], **action.get('kwargs', {}))


if __name__ == '__main__':
    main()
