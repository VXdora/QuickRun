import json
import sys
import os
import subprocess

QRUN_FILE = ".quickrun"
QRUN_LOCATE_DIR = "{:s}/.local/quickrun".format(os.getenv("HOME"))
QRUN_LOCAL = "{:s}/local/".format(QRUN_LOCATE_DIR)

qrun_lcl_contents = {}
qrun_prj_contents = {}

# located quickrun/local
class LocalInfo:
    def __init__(self):
        self.data = {}

# located project root
class QRunInfo:
    def __init__(self):
        self.data = {
            'workspace': '/app',
            'entrypoint': './entrypoint.sh',
            'background': 1
        }

    def setBaseImage(self, base: str):
        self.data['base'] = base

    def setBaseImageTag(self, tag: str):
        self.data['tag'] = tag

    def setPkgman(self, pkgman):
        self.data['pkgman'] = pkgman

    def setRequiredCopyFiles(self, copyfiles):
        self.data['requiredCopyFiles'] = copyfiles

    #
    # pipやnpmなどのパッケージマネージャでインストールするコマンド
    # ex. pip install requirements.txt
    #
    def setRequiredInstallPackage(self, install_package):
        self.data['requiredInstallPackages'] = install_package

    def setWorkSpaceDirectory(self, workspace_directory):
        self.data['workspace'] = workspace_directory

    def setExtendInstallPackage(self, install_package):
        self.data['installPackages'] = install_package

    def setEnvValue(self, envs):
        self.data['envs'] = envs

    def setEntryPoint(self, entrypoint):
        self.data['entrypoint'] = entrypoint

    def setOutboundPort(self, ports):
        self.data['ports'] = ports

    def setMountVolume(self, mounts):
        self.data['volumes'] = mounts

    def output(self, prj_root):
        fpath = os.path.join(prj_root, '.quickrun')
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

class App:
    def __init__(self, prj_root):
        self.qrunInfo = QRunInfo()
        self._image = None
        with open(os.path.join(QRUN_LOCATE_DIR, 'images.json'), encoding='utf-8') as f:
            self.image_info = json.load(f)
        self.prj_root = prj_root

    def clear_screen(self):
        subprocess.run(['clear'])

    def select_base_image(self):
        while True:
            self.clear_screen()
            print("select base image...")
            for i, e in enumerate([ image['name'] for image in self.image_info['images']]):
                print("[{:2d}] {:s}".format(i, e))
            print(">> ", end='')
            try:
                n = int(input())
                self._image = self.image_info['images'][n]
                self.qrunInfo.setBaseImage(self._image['base'])
                self.qrunInfo.setPkgman(self._image['pkgman'])
                break
            except Exception as e:
                print(e)
                continue

    def select_base_image_tag(self):
        if self._image is None: raise Exception
        while True:
            self.clear_screen()
            print("select base image tag:")
            for i, e in enumerate([tag for tag in self._image['tag']]):
                print("[{:2d}] {:s}".format(i, e))
            print(">> ", end='')
            try:
                n = int(input())
                self.qrunInfo.setBaseImageTag(self._image['tag'][n])
                break
            except Exception as e:
                print(e)
                continue

    def required_copy_files(self):
        if self._image is None: raise Exception
        if 'copy' in self._image:
            self.clear_screen()
            print("select copy file (default {:s})".format(self._image['copy'].replace('${PRJROOT}', os.getcwd())))
            print(">> ", end='')
            cf = self._image['copy'].replace('${PRJROOT}', os.getcwd()) if (n := input()) == '' else n
            self.qrunInfo.setRequiredCopyFiles([cf])

    def required_install_packages(self):
        if self._image is None: raise Exception
        if 'copy' in self._image:
            self.clear_screen()
            print("input install app package command: (default {:s})".format(self._image['install']))
            print(">> ", end='')
            cf = self._image['install'] if (n := input()) == '' else n
            self.qrunInfo.setRequiredInstallPackage([cf])

    def set_workspace_directory(self):
        self.clear_screen()
        print("input workspace directory (default /app)")
        wd = '/app' if (n := input()) == '' else n
        self.qrunInfo.setWorkSpaceDirectory(wd)

    def set_extend_install_package(self):
        self.clear_screen()
        print("input install package, for example 'nkf' (if quit, input EMPTY value)")
        pkgs = []
        while (pkg := input()) != '':
            pkgs.append(pkg)
        self.qrunInfo.setExtendInstallPackage(pkgs)

    def set_entry_point(self):
        self.clear_screen()
        if self._image is None: raise Exception
        entrypoint = './entrypoint.sh' if not 'entrypoint' in self._image else self._image['entrypoint']
        self.qrunInfo.setEntryPoint(entrypoint)

    def set_required_env_value(self):
        self.clear_screen()
        print("input REQUIRED environment value")
        envs = []
        if os.path.isfile("{:s}/imset/{:s}/exenv.conf".format(QRUN_LOCATE_DIR, qrun_prj_contents["base_image"], encoding="utf-8")):
            with open("{:s}/imset/{:s}/exenv.conf".format(QRUN_LOCATE_DIR, qrun_prj_contents["base_image"], encoding="utf-8")) as f:
                envnames = f.read().splitlines()
            for envname in envnames:
                print(envname, '>>', end='')
                envvalue = input()
                if envvalue == '':
                    continue
                envs.append('{:s}={:s}'.format(envname, envvalue))
            qrun_prj_contents['required_envs'] = envs

    def set_env_value(self):
        self.clear_screen()
        print("input environment value, for example KEY=VALUE (if quit, input EMPTY value)")
        envs = []
        while True:
            env = input()
            if env == '':
                qrun_prj_contents['environments'] = envs
                break
            elif not '=' in env:
                print('Invalid Value!  Can\'t registered')
                continue
            else:
                envs.append(env)

    def set_outbound_port(self):
        self.clear_screen()
        print("input outbound port, for example 13306:3306 (if quit, input EMPTY value)")
        ports = []
        while (port := input()) != '':
            ports.append(port)
        self.qrunInfo.setOutboundPort(ports)

    def set_mount_volume(self):
        self.clear_screen()
        print("input mount directory (default src:app)")
        mount = '{:s}/src:/app'.format(os.getcwd()) if (n := input()) == '' else n
        mounts = [mount]
        self.qrunInfo.setMountVolume(mounts)


    def _quit(self):
        self.qrunInfo.output(self.prj_root)

    def select_option(self):
        while True:
            self.clear_screen()
            print("input extra option:")
            print("[ 1]: Set Workspace Directory")
            print("[ 2]: Environment Value")
            print("[ 3]: Install Extend Package")
            print("[ 5]: Set EntryPoint")
            print("[ 6]: Set AWS Profile")
            print("[ 7]: Set Outbound Port")
            print("[ 8]: Set Mount Directory")
            print("[ 9]: Exit")

            print("select number: ", end='')
            try:
                n = int(input())
            except:
                continue

            if n == 1:
                self.set_workspace_directory()
            elif n == 2:
                set_env_value()
            elif n == 3:
                self.set_extend_install_package()
            elif n == 5:
                set_entry_point()
            elif n == 7:
                self.set_outbound_port()
            elif n == 8:
                set_mount_volume()
            elif n == 9:
                self._quit()
                break

    def run(self):
        self.select_base_image()
        self.select_base_image_tag()
        self.required_copy_files()
        self.required_install_packages()
        self.set_entry_point()
        self.set_outbound_port()
        self.set_mount_volume()
        self.select_option()

if __name__ == '__main__':
    # exist .quickrun??
    if os.path.isfile(QRUN_FILE):
        print("This directory has .quickrun file.")
        print("Initialize again? (y/n)")
        inp = input()
        if inp != "y":
            sys.exit(1)

    # register exluding .quickrun file to .gitignore
    if os.path.isfile(".gitignore"):
        with open(".gitignore", encoding="utf-8") as f:
            gg = f.read()
        if len([line for line in gg.splitlines() if '.quickrun' in line]) == 0:
            with open(".gitignore", 'a', encoding='utf-8') as f:
                f.write("# exclude .quickrun file\n")
                f.write(".quickrun\n")

    app = App(os.getcwd())
    app.run()
    sys.exit(0)

    # create qrun local directory
    print(f"{QRUN_LOCAL=}")
    if not os.path.isdir(QRUN_LOCAL):
        os.mkdir(QRUN_LOCAL)

    # Initialize .quickrun value
    imgname = os.getcwd().split('/')[-1]
    qrun_prj_contents['imgname'] = imgname
    qrun_prj_contents['workspace'] = '/app'
    qrun_prj_contents['entrypoint'] = ['./entrypoint.sh']

    select_base_image()
    select_base_image_tag()
    set_required_env_value()
    set_install_app_extend_package_cmd()
    select_option()

    qrun_lcl_contents['project_root'] = os.getcwd()
    clear_screen()

    # save .quickrun
    with open(".quickrun", "w", encoding="utf-8") as f:
        json.dump(qrun_prj_contents, f, indent=4, ensure_ascii=False)

    if not os.path.isdir('{:s}/{:s}'.format(QRUN_LOCAL, imgname)):
        os.mkdir('{:s}/{:s}'.format(QRUN_LOCAL, imgname))
    with open('{:s}/{:s}/settings.json'.format(QRUN_LOCAL, imgname), 'w', encoding='utf-8') as f:
        json.dump(qrun_lcl_contents, f, ensure_ascii=False, indent=4)



