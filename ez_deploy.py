import argparse
import functools
import json
import os
import sys
import subprocess
import virtualenv


def get_python_bin(home):
    if not home:
        return
    home_dir, lib_dir, inc_dir, bin_dir = virtualenv.path_locations(home, dry_run=True)
    python_bin = os.path.join(bin_dir, 'python')
    if virtualenv.IS_WIN:
        python_bin += '.exe'
    return python_bin


def install(path, name, program, arguments=None, **kwargs):
    if not name:
        print_error('Service not specified')
        sys.exit(1)
    if not program:
        print_error('Program not specified')
        sys.exit(1)
    print(f'Installing {name}...')
    if virtualenv.IS_WIN:
        if not path:
            print_error('Invalid home path')
            sys.exit(1)
        home_dir, lib_dir, inc_dir, bin_dir = virtualenv.path_locations(path, dry_run=True)
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
        pass
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
def uninstall(service):
    print(f'Uninstall {service}...')
    if virtualenv.IS_WIN:
        subprocess.check_call(f'SC delete {service}')
        with open(os.devnull, 'w') as f:
            subprocess.call(f'net stop {service}', stdout=f, stderr=f)
    else:
        subprocess.check_call(f'systemctl stop {service}')
        subprocess.check_call(f'systemctl disable {service}')
        subprocess.check_call(f'rm /etc/systemd/system/{service}')
        subprocess.check_call(f'systemctl daemon-reload')
        subprocess.check_call(f'systemctl reset-failed')
    return True


@check_arg('Service not specified')
def start(service):
    print(f'Starting {service}...')
    if virtualenv.IS_WIN:
        subprocess.check_call(f'net start {service}')
    else:
        subprocess.check_call(f'systemctl start {service}')
    return True


@check_arg('Service not specified')
def stop(service):
    print(f'Stopping {service}...')
    if virtualenv.IS_WIN:
        subprocess.check_call(f'net stop {service}')
    else:
        subprocess.check_call(f'systemctl stop {service}')
    return True


def deploy(path, requirements=None, package_dir=None):
    print(f'Using environment \'{path}\'')
    home_dir, lib_dir, inc_dir, bin_dir = virtualenv.path_locations(path, True)
    pip_bin = os.path.join(bin_dir, 'pip')
    if virtualenv.IS_WIN:
        pip_bin += '.exe'
    if not requirements and os.path.exists('requirements.txt'):
        requirements = 'requirements.txt'
    if requirements:
        print(f'Using requirements file: {requirements}')
        args = [pip_bin, 'install', '-r', requirements]
        if package_dir:
            args.extend(['--no-index', '--find-links', package_dir])
        subprocess.check_call(args, shell=True)
    return True


@check_arg('Environment path not specified')
def env(path):
    if not os.path.exists(path):
        print(f'Creating virtual environment \'{path}\'...')
        virtualenv.create_environment(path)
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
    parser.add_argument('--service-program', dest='service_program', help='service bin path')
    parser.add_argument('--service-arguments', nargs='+', dest='service_arguments', help='service arguments')
    parser.add_argument('--service-start', dest='service_start', help='service start mode <auto|manual>')
    windows_group = parser.add_argument_group('Options for Windows', 'Service options for Windows')
    windows_group.add_argument('--service-display', dest='service_display', help='service display name')
    windows_group.add_argument('--service-description', dest='service_description', help='service description')
    windows_group.add_argument('--service-depend', dest='service_depend', help='service dependencies')
    windows_group.add_argument('--service-obj', dest='service_obj', help='service login account')
    windows_group.add_argument('--service-password', dest='service_password', help='service login password')
    options = parser.parse_args()
    virtualenv.logger.consumers = [(virtualenv.logger.LEVELS[2], sys.stdout)]
    config = {}
    if os.path.exists(options.config):
        with open(options.config, encoding='utf8') as f:
            config = json.load(f)
    for name, value in options.__dict__.items():
        if value is None:
            continue
        pk, sep, sk = name.partition('_')
        if sk:
            config[pk][sk] = value
        else:
            config[pk] = value
    service = config.get('service', {})
    action_map = {
        'env': {'func': env, 'args': (config.get('env'),)},
        'deploy': {'func': deploy, 'args': (config.get('env'), config.get('requirements'), config.get('dir')),
                   'depends': ['env']},
        'start': {'func': start, 'args': (config.get('service', {}).get('name'),)},
        'stop': {'func': stop, 'args': (config.get('service', {}).get('name'),)},
        'install': {'func': install, 'args': (config.get('env'),),
                    'kwargs': {'name': service.get('name'), 'program': service.get('program'), **service},
                    'depends': ['deploy']},
        'uninstall': {'func': uninstall, 'args': (config.get('service', {}).get('name'),)},
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
