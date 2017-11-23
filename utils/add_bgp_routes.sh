#!/bin/sh

# Gets a file with one route each line, shuffles it and truncates it

TMP_FILE="/tmp/bgpd_tmp_file.txt"

if [ "$#" -lt 3 ]; then
	echo "Usage $0 num_nodes input_file output_folder [ratio]";
	exit 1;
fi

NODES=$1
IN_FILE=$2
OUTPUT_FOLDER=$3
RATIO=$4
if [ -z $RATIO ]; then
	RATIO=0.1;
fi

TOTAL=$(cat $IN_FILE | wc -l)
INC=$(printf %.0f $(echo "$TOTAL * $RATIO" | bc -l))
SIZE=$(($TOTAL-$INC))
echo "$SIZE over $TOTAL"

for i in $(seq 2 $NODES); do
	shuf ${IN_FILE} > ${TMP_FILE};
	head -n ${SIZE} ${TMP_FILE} >> ${OUTPUT_FOLDER}/bgpd-${i}.conf
done
