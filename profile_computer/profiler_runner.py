import subprocess
import decorator_adder

def get_latency_profile(file_paths_to_profile, entry_point, sandbox):
    for file_path_to_profile in str.split(file_paths_to_profile, ','):
        decorator_adder.add_decorator(file_path_to_profile, 'profile')
    decorator_adder.add_decorator(entry_point, 'profile')

    profile_path = f'{sandbox}/latency_profile.lprof'
    profile_path_txt = f'{sandbox}/latency_profile.txt'
    # TODO: Suppress STDOUT from first subprocess.
    subprocess.run(f'kernprof -l -o {profile_path} {entry_point}')
    subprocess.run(f'python -m line_profiler -rtmz {profile_path}', stdout=open(profile_path_txt, 'w'))
    with open(profile_path_txt, 'r') as file:
        profile_txt_file_contents = file.read()

    return profile_txt_file_contents