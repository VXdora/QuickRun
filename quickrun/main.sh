#!/bin/bash

QRUN_DIR=~/.local/quickrun
QRUN_LOCAL=$QRUN_DIR/local
BASEIMG_LIST=${QRUN_DIR}/images.conf
QRUN_IMSET=$QRUN_DIR/imset

PROJECT_ROOT=$(pwd)
PROJECT_QUICKRUN=$PROJECT_ROOT/.quickrun

QUICKRUN_VER='0.0.1-SNAPSHOT'

# initialize .quickrun
if [ $1 = 'init' ]; then
  python3.11 $QRUN_DIR/init.py
elif [ $1 == 'build' ]; then
  TAG=$(pwd | rev | cut -d/ -f1 | rev)
  docker images | grep $TAG | awk -F' ' '{ print $3 }'

  # 既にDockerfileがある場合は退避
  if [[ -f Dockerfile ]]; then
    mv Dockerfile Dockerfile_bk
  fi

  python3.11 $QRUN_DIR/build.py

  docker build -t ${TAG} .
  rm Dockerfile

  # Dockerfileを戻す
  if [[ -f Dockerfile_bk ]]; then
    mv Dockerfile_bk Dockerfile
  fi

elif [ $1 == 'run' ]; then
  TAG=$(pwd | rev | cut -d/ -f1 | rev)

  # portの設定
  PORTS=$(cat .quickrun | jq '.ports')
  if [[ $PORTS != "null" ]]; then
    _PORTS=$(cat .quickrun | jq -r '"-p " + (.ports | join(" -p "))')
  fi

  # volumeの設定
  VOLUMES=$(cat .quickrun | jq '.volumes')
  if [[ $VOLUMES != "null" ]]; then
    _VOLUMES=$(cat .quickrun | jq -r '"-v " + (.volumes | join(" -v "))')
  fi

  # backgroundの設定
  BG=$(cat .quickrun | jq '.background')
  if [[ $BG == '1' ]]; then
    CMD='-itd'
  else
    CMD='-it'
  fi

  docker run $_PORTS $_VOLUMES $CMD $TAG

elif [ $1 == 'stop' ]; then
  TAG=$(pwd | rev | cut -d/ -f1 | rev)
  docker stop $(docker ps | grep $TAG | awk -F' ' '{ print $1 }')

elif [[ $1 == '--version' ]] || [[ $1 == '-V' ]]; then
  echo "QuickRun Ver.${QUICKRUN_VER} created by VXdora."
else
  echo "Unknown commands: "
  echo "Usage: qrun [init|build|run]"
fi
