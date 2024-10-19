import subprocess
import argparse
import decorator_adder

parser = argparse.ArgumentParser(description='Profile Runner Arguments.')

parser.add_argument('--file_name', action="store", dest='file_name', default='')

args = parser.parse_args()

file_name_to_profile = decorator_adder.add_decorator(args.file_name, 'profile')

subprocess.run(f'kernprof -l -v {file_name_to_profile}', stdout=open(f'{file_name_to_profile}_profile.txt', 'w'))
