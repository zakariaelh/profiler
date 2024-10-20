import subprocess
import argparse
import decorator_adder

parser = argparse.ArgumentParser(description='Profile Runner Arguments.')

parser.add_argument('--file_paths_to_profile', action="store", dest='file_paths_to_profile', default='')
parser.add_argument('--entry_point', action="store", dest='entry_point', default='')

args = parser.parse_args()

for file_path_to_profile in str.split(args.file_paths_to_profile, ','):
    decorator_adder.add_decorator(file_path_to_profile, 'profile')

profile_path = 'latency_profile.lprof'
profile_path_txt = 'latency_profile.txt'
# TODO: Suppress STDOUT from first subprocess.
subprocess.run(f'kernprof -l -o {profile_path} {args.entry_point}')
subprocess.run(f'python -m line_profiler -rtmz {profile_path}', stdout=open(profile_path_txt, 'w'))
