#!/usr/local/bin/python3.11

import json
import sys
import os

QRUN_FILE = ".quickrun"
QRUN_LOCATE_DIR = "{:s}/.local/quickrun".format(os.getenv("HOME"))
QRUN_LOCAL = "{:s}/local/".format(QRUN_LOCATE_DIR)

qrun_lcl_contents = {}
qrun_prj_contents = {}

def select_option():
    while True:
        print("input extra option:")
        print("[1]: Environment Value")
        print("[2]: Install Extend Package")
        print("[3]: Set EntryPoint")
        print("[4]: Set AWS Profile")
        print("[5]: Set Outbound Port")
        print("[9]: Exit")

        try:
            print("select number: ", end='')
            n = int(input())
            if n == 1:
                pass
            elif n == 9:
                break
        except Exception as e:
            continue


def select_base_image():
    print("select base image...")
    with open(f"{QRUN_LOCATE_DIR}/images.conf", encoding="utf-8") as f:
        images = f.read().splitlines()
    while True:
        for i, e in enumerate(images):
            print("[{:2d}] {:s}".format(i, e))
        print(">> ", end='')
        try:
            n = int(input())
            qrun_prj_contents['base_image'] = images[n]
            break
        except Exception as e:
            print(e)
            continue

def select_base_image_tag():
    print("select base image tag")
    path ="{:s}/imset/{:s}/tags.conf".format(QRUN_LOCATE_DIR, qrun_prj_contents['base_image'])
    print(f"{path=}")
    with open("{:s}/imset/{:s}/tags.conf".format(QRUN_LOCATE_DIR, qrun_prj_contents['base_image']), encoding="utf-8") as f:
        tags = f.read().splitlines()
    while True:
        for i, e in enumerate(tags):
            print("[{:2d}] {:s}".format(i, e))
        print(">> ", end='')
        try:
            n = int(input())
            qrun_prj_contents['base_image_tag'] = tags[n]
            break
        except:
            continue


if __name__ == '__main__':
    # exist .quickrun??
    if os.path.isfile(QRUN_FILE):
        print("This directory has .quickrun file.")
        print("Initialize again? (y/n)")
        inp = input()
        if inp != "y":
            sys.exit(1)
        os.remove(QRUN_FILE)

    # register exluding .quickrun file to .gitignore
    if os.path.isfile(".gitignore"):
        with open(".gitignore", encoding="utf-8") as f:
            gg = f.read()
        if len([line for line in gg.splitlines() if '.quickrun' in line]) == 0:
            with open(".gitignore", 'a', encoding='utf-8') as f:
                f.write("# exclude .quickrun file\n")
                f.write(".quickrun\n")

    # create qrun local directory
    print(f"{QRUN_LOCAL=}")
    if not os.path.isdir(QRUN_LOCAL):
        os.mkdir(QRUN_LOCAL)

    select_base_image()
    select_base_image_tag()
    select_option()

    qrun_lcl_contents['project_root'] = os.getcwd()

    # save .quickrun
    with open(".quickrun", "w", encoding="utf-8") as f:
        json.dump(qrun_prj_contents, f, indent=4, ensure_ascii=False)








