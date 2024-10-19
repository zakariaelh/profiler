import subprocess
import argparse
import decorator_adder
import os

parser = argparse.ArgumentParser(description='Profile Runner Arguments.')

parser.add_argument('--file_path', action="store", dest='file_path', default='')

args = parser.parse_args()

file_path_to_profile = decorator_adder.add_decorator(args.file_path, 'profile')
profile_binary_file_path = os.path.splitext(file_path_to_profile)[0] + '_profile_decorated_profile.binary_prof'
profile_text_file_path = os.path.splitext(file_path_to_profile)[0] + '_profile_decorated_profile.txt'

subprocess.run(f'kernprof -l -v -o {profile_binary_file_path} {file_path_to_profile}', stdout=open(profile_text_file_path, 'w'))
