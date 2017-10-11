#!/bin/sh

# Gets a file with one route each line, shuffles it and truncates it

RATIO=0.1
TMP_FILE="/tmp/bgpd_tmp_file.txt"

if [ "$#" -ne 3 ]; then
    echo "Usage $0 num_nodes input_file output_folder";
    exit 1;
fi

NODES=$1
IN_FILE=$2
OUTPUT_FOLDER=$3

TOTAL=$(cat $IN_FILE | wc -l)
INC=$(printf %.0f $(echo "$TOTAL * $RATIO" | bc -l))
SIZE=$(($TOTAL-$INC))
echo "$SIZE over $TOTAL"

for i in $(seq 1 $NODES); do
    shuf ${IN_FILE} > ${TMP_FILE};
    head -n ${SIZE} ${TMP_FILE} >> ${OUTPUT_FOLDER}/bgpd-${i}.conf
done
