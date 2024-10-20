import subprocess
import decorator_adder
import re 

def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
    return ansi_escape.sub('', text)


def get_latency_profile(file_paths_to_profile, entry_point, sandbox_name):
    for file_path_to_profile in str.split(file_paths_to_profile, ','):
        decorator_adder.add_decorator(file_path_to_profile, 'profile')
    decorator_adder.add_decorator(f'{sandbox_name}/{entry_point}', 'profile')

    python_path = f"venv/bin/python"

    profile_path = f'latency_profile.lprof'
    profile_path_txt = f'latency_profile.txt'
    # TODO: Suppress STDOUT from first subprocess.
    subprocess.run(['ls', '-la'], cwd=sandbox_name)
    subprocess.run(['kernprof', '-l', '-o', profile_path, entry_point], cwd=sandbox_name)
    subprocess.run([python_path, '-m', 'line_profiler', '-rtmz', profile_path], stdout=open(profile_path_txt, 'w'), cwd=sandbox_name)
    with open(profile_path_txt, 'r') as file:
        profile_txt_file_contents = file.read()

    return remove_ansi_escape_sequences(profile_txt_file_contents)