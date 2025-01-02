#!/bin/bash

QRUN_DIR=~/.local/quickrun
QRUN_LOCAL=$QRUN_DIR/local
BASEIMG_LIST=${QRUN_DIR}/images.conf
QRUN_IMSET=$QRUN_DIR/imset

PROJECT_ROOT=$(pwd)
PROJECT_QUICKRUN=$PROJECT_ROOT/.quickrun

# initialize .quickrun
if [ $1 = 'init' ]; then
  # if there's .quickrun, ask initialize again or exit
  if [ -f .quickrun ]; then
    echo "This directory has .quickrun file."
    echo "Initialize again? (y/n)"
    read ANS
    if [ $ANS != "y" ]; then
      exit 1
    fi
    if [ -f $PROJECT_QUICKRUN ]; then
      rm $PROJECT_QUICKRUN
    fi
    echo "========================================================"
  fi
  # register excluding .quickrun file to .gitignore
  if [[ -f .gitignore ]] && [[ $(cat .gitignore | egrep .quickrun | wc -l) -eq 0 ]]; then
    echo "# exclude .quickrun file" >> .gitignore
    echo ".quickrun" >> .gitignore
  fi

  # make qrun directory
  if [ ! -d $QRUN_LOCAL ]; then
    mkdir -p $QRUN_LOCAL
  fi

  #
  SEF=$(pwd | rev | cut -d/ -f1 | rev)
  # if [ -f $QRUN_LOCAL/$SEF ]; then
  #   echo "the settings file of this project has already been created!"
  #   exit 1
  # fi
  SEFFL=$QRUN_LOCAL/$SEF
  echo "DIR=$(pwd)" >> $SEFFL

  # select base image
  echo "Select Base Image..."
  cat $BASEIMG_LIST -n
  read IMG_N
  if [[ ! "$IMG_N" =~ ^[0-9]+$ ]]; then
    echo "aaa"
    exit 1
  fi

  BSIMG=$(cat $BASEIMG_LIST | head -n $IMG_N | tail -n 1)
  BSIMG_N=$(echo $BSIMG)

  echo '{' >> $PROJECT_QUICKRUN
  echo '  "image": {' >> $PROJECT_QUICKRUN

  # echo '    "pcman": "apt",' >> $PROJECT_QUICKRUN
  # select tag of image
  cat -n $QRUN_IMSET/$BSIMG_N/tags.conf
  read TAG_N
  echo "TAG_N: ${TAG_N}"
  if [[ ! $TAG_N =~ ^[0-9]+$ ]]; then
    exit 1
  fi
  TAG=$(cat $QRUN_IMSET/$BSIMG_N/tags.conf | head -n $TAG_N | tail -n 1)
  echo "    \"image\": \"$BSIMG_N:$TAG\"," >> $PROJECT_QUICKRUN

  # set workspace directory
  echo "input workspace directory (default /app) :"
  read WSDIR
  if [ -z $WSDIR ]; then
    WSDIR="/app"
  fi
  echo "    \"workspace\": \"$WSDIR\"," >> $PROJECT_QUICKRUN

  # pcman install
  echo "input install package, for example 'nkf' (if quit, input EMPTY value): "
  echo "    \"install\": [" >> $PROJECT_QUICKRUN
  read PCKG
  while [ ! $PCKG = "" ]; do
    echo "      \"$PCKG\"," >> $PROJECT_QUICKRUN
    read PCKG
  done
  truncate -s -2 $PROJECT_QUICKRUN
  echo -e "\n    ]," >> $PROJECT_QUICKRUN

  # set env
  echo "input environment path split '=', for example 'KEY=VALUE' (if quit, input EMPTY value): "
  echo "    \"environment\": [" >> $PROJECT_QUICKRUN
  read ENV
  while [ ! $ENV = "" ]; do
    echo "      \"$ENV\"," >> $PROJECT_QUICKRUN
    read ENV
  done
  truncate -s -2 $PROJECT_QUICKRUN
  echo -e "\n    ]," >> $PROJECT_QUICKRUN

  # set extra env ex. mysql username and password
  if [ -f $QRUN_IMSET/$BSIMG_N/envex.conf ]; then
    while read ENV; do
      echo $ENV
    done
  fi

  # set aws key if need
  # set entrypoint
  echo "input entrypoint file (default ./entrypoint.sh) :"
  read ETFILE
  if [ -z $ETFILE ]; then
    ETFILE="./entrypoint.sh"
  fi
  echo "    \"entrypoint\": \"$ETFILE\"," >> $PROJECT_QUICKRUN



elif [ $1 == 'build' ]; then
  echo "BUILD"
elif [ $1 == 'run' ]; then
  echo "RUN"
else
  echo "Unknown commands: "
  echo "Usage: qrun [init|build|run]"
fi
