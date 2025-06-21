import re
import matplotlib.pyplot as plt

# Function to parse enqueue and dequeue events
def parse_event_line(line, enqueue_pattern, dequeue_pattern, queue_length):
    enqueue_match = enqueue_pattern.match(line)
    dequeue_match = dequeue_pattern.match(line)
    
    if enqueue_match:
        time = float(enqueue_match.group(1))
        queue_length += 1
        return time, queue_length
    elif dequeue_match:
        time = float(dequeue_match.group(1))
        queue_length -= 1
        return time, queue_length
    return None, queue_length

# Function to read events from the trace file
def read_trace_file(input_file):
    enqueue_pattern = re.compile(r'^\+ (\d+\.\d+) .*TxQueue/Enqueue')
    dequeue_pattern = re.compile(r'^\- (\d+\.\d+) .*TxQueue/Dequeue')
    queue_length = 0  # Initial queue length
    events = []       # List to store time and queue length

    with open(input_file, 'r') as infile:
        for line in infile:
            time, queue_length = parse_event_line(line, enqueue_pattern, dequeue_pattern, queue_length)
            if time is not None:
                events.append((time, queue_length))
    
    return events

# Function to write parsed events to an output file
def write_output_file(events, output_file):
    with open(output_file, 'w') as outfile:
        outfile.write("# Time\tQueueLength\n")
        for time, length in events:
            outfile.write(f"{time}\t{length}\n")
    print(f"Queue length data written to {output_file}")

# Function to plot queue length over time and save the plot as an image
def plot_queue_length(events, plot_file="queue_length_plot.png"):
    times = [event[0] for event in events]
    queue_lengths = [event[1] for event in events]

    plt.figure(figsize=(10, 6))
    plt.plot(times, queue_lengths, label="Queue Length", color="blue", linewidth=2)
    plt.title("Queue Length Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Queue Length (packets)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_file)  # Save the plot as an image
    plt.show()
    print(f"Plot saved as {plot_file}")

# Main function to orchestrate file processing, saving, and plotting
def main():
    input_trace_file = "tcp-example.tr"
    output_data_file = "queue_length.txt"
    plot_file = "queue_length_plot.png"
    
    events = read_trace_file(input_trace_file)
    write_output_file(events, output_data_file)
    plot_queue_length(events, plot_file)

# Run the main function
if __name__ == "__main__":
    main()
