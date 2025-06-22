import subprocess
import os

os.chdir('/Users/janoschgrellner/PycharmProjects/lth-rec')

commands = [
    ['git', 'add', '-A'],
    ['git', 'commit', '--no-gpg-sign', '-m', 'Fix deployment configuration and add startup scripts'],
    ['git', 'push', 'origin', 'development']
]

for cmd in commands:
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")

print("\nNow updating Azure startup command...")
azure_cmd = [
    'az', 'webapp', 'config', 'set',
    '--name', 'lthrecommendation',
    '--slot', 'usertest-dev',
    '--resource-group', 'rg-sponsorship',
    '--startup-file', 'cd /home/site/wwwroot && python -m pip install -r requirements.txt && python -m gunicorn --bind 0.0.0.0:8000 --timeout 600 --workers 1 --chdir src app:app'
]
result = subprocess.run(azure_cmd, capture_output=True, text=True)
print(result.stdout)

print("\nRestarting webapp...")
restart_cmd = [
    'az', 'webapp', 'restart',
    '--name', 'lthrecommendation',
    '--slot', 'usertest-dev',
    '--resource-group', 'rg-sponsorship'
]
subprocess.run(restart_cmd)

print("\nDone!")