#!/bin/sh

PARENT_DIR=$(cd $(dirname $0);cd ..; pwd)

d=$(find $PARENT_DIR/src/ -name "__pycache__" -type d -print)
echo $d

rm -rf $d