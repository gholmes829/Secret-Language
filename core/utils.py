"""

"""

import subprocess

def read_file(f_path: str) -> str:
    with open(f_path, 'r') as f:
        return f.read()


def write_to_file(f_path: str, content: str) -> str:
    with open(f_path, 'w') as f:
        f.write(content)
    

def run_in_shell(cmd: str):
    subprocess.run(cmd, shell=True)