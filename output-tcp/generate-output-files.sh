#!/bin/bash

# Define an array of input pcap files and corresponding output text files
declare -A files=(
    ["tcp-example-0-0.pcap"]="tcp-example-0-0_output.txt"
    ["tcp-example-1-0.pcap"]="tcp-example-1-0_output.txt"
    ["tcp-example-2-0.pcap"]="tcp-example-2-0_output.txt"
)

# Loop through each file pair
for pcap_file in "${!files[@]}"; do
    output_file="${files[$pcap_file]}"

    # Run tshark command to extract fields and save to output file
    tshark -r "$pcap_file" -T fields -e frame.time_epoch -e ip.src -e ip.dst -e tcp.port -e tcp.seq -e tcp.len -e tcp.ack > "$output_file"

    echo "Generated $output_file from $pcap_file"
done
