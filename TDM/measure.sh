#!/bin/bash

set -e
HOST=nonos-4

DIR=$(dirname $0)
NAME=$1

if [ -z "$NAME" ]; then
    NAME=in
fi

Fs=48000
T=60
FMT=S32_LE
DEV="CARD=sndrpigooglevoi,DEV=0"
CH=2

Tr=$((T - 5))

TMPWAV=/tmp/tone.wav
TMPIN=/tmp/in.wav

sox -n -r $Fs -b 32 -c $CH $DIR/tone.wav synth $T sine 996.826 vol -3dB
rsync $DIR/tone.wav $HOST:$TMPWAV

ssh $HOST "aplay -D hw:$DEV -r $Fs -f $FMT -c $CH $TMPWAV" &
ssh $HOST "arecord -D hw:$DEV -r $Fs -f $FMT -c $CH -d $Tr $TMPIN"

rsync $HOST:$TMPIN $DIR/$NAME.wav

uv run --script measure_tdm.py $DIR/$NAME.wav