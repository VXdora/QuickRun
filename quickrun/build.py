import json
import os

QRUN_LOCATE_DIR = "{:s}/.local/quickrun".format(os.getenv("HOME"))
QRUN_LOCAL = "{:s}/local/".format(QRUN_LOCATE_DIR)

with open('.quickrun', encoding='utf-8') as f:
    data = json.load(f)

DOCKERFILE = []

print(data)
DOCKERFILE.append("FROM {:s}:{:s}".format(data['base'], data['tag']))
DOCKERFILE.append("WORKDIR {:s}".format(data['workspace']))
DOCKERFILE.append('')

if 'required_envs' in data:
    for env in data['required_envs']:
        DOCKERFILE.append('ENV {:s}'.format(env))

if 'environments' in data:
    for env in data['environments']:
        DOCKERFILE.append('ENV {:s}'.format(env))

DOCKERFILE.append('RUN {:s} update -y'.format(data['pkgman']))

if 'installPackages' in data:
    DOCKERFILE.append('RUN {:s} install -y {:s}'.format(data['pkgman'], ' '.join(data['install'])))

DOCKERFILE.append('')

if 'requiredCopyFiles' in data:
    for file in data['requiredCopyFiles']:
        DOCKERFILE.append('COPY {:s} {:s}'.format(file, data['workspace']))

if 'requiredInstallPackages' in data:
    for cmd in data['requiredInstallPackages']:
        DOCKERFILE.append('RUN {:s}'.format(cmd))

DOCKERFILE.append('')
data['entrypoint'] = [f"\"{ep}\"" for ep in data['entrypoint'].split(' ')]
print(data['entrypoint'])
DOCKERFILE.append('ENTRYPOINT [{:s}]'.format(','.join(data['entrypoint'])))

for line in DOCKERFILE:
    print(line)
imgname = os.getcwd().split('/')[-1]
with open('Dockerfile', 'w', encoding='utf-8') as f:
    f.write('\n'.join(DOCKERFILE))
