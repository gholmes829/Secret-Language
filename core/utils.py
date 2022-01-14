"""

"""

import subprocess

def read_file(f_path: str) -> str:
    with open(f_path, 'r') as f:
        return f.read()


def write_to_file(f_path: str, content: str) -> str:
    with open(f_path, 'w') as f:
        f.write(content)
    

def run_in_shell(cmd: str, cwd = None):
    try:
        return subprocess.run(
            cmd,
            cwd = cwd,
            shell=True,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT
        ).stdout.decode(encoding='utf-8')
    except Exception as err:
        print(f'FATAL: received error when running cmd in shell "{err}".', flush=True)