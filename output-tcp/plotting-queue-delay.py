import re
import matplotlib.pyplot as plt

def read_trace_file(input_file):
    """Reads the trace file and returns the lines."""
    with open(input_file, 'r') as infile:
        lines = infile.readlines()
    return lines

def match_events(lines):
    """Matches enqueue and dequeue events using regex and returns the times."""
    enqueue_pattern = re.compile(r'^\+ (\d+\.\d+) .*TxQueue/Enqueue')
    dequeue_pattern = re.compile(r'^\- (\d+\.\d+) .*TxQueue/Dequeue')

    enqueue_times = []  # List to store enqueue times
    dequeue_times = []  # List to store dequeue times
    queue_lengths = []  # List to store queue length events (time, length)
    queue_length = 0    # Current queue length

    for line in lines:
        # Check for enqueue events
        enqueue_match = enqueue_pattern.match(line)
        if enqueue_match:
            time = float(enqueue_match.group(1))
            enqueue_times.append(time)
            queue_length += 1
            queue_lengths.append((time, queue_length))
            continue

        # Check for dequeue events
        dequeue_match = dequeue_pattern.match(line)
        if dequeue_match:
            time = float(dequeue_match.group(1))
            dequeue_times.append(time)
            queue_length -= 1
            queue_lengths.append((time, queue_length))
            continue

    return enqueue_times, dequeue_times, queue_lengths

def calculate_queue_delays(enqueue_times, dequeue_times):
    """Calculates queue delays by pairing enqueue and dequeue events."""
    queue_delays = []
    for i in range(min(len(enqueue_times), len(dequeue_times))):
        delay = dequeue_times[i] - enqueue_times[i]
        queue_delays.append((dequeue_times[i], delay))
    return queue_delays

def write_output_file(output_file, queue_lengths, queue_delays):
    """Writes the time, queue length, and queue delay to an output file."""
    with open(output_file, 'w') as outfile:
        outfile.write("# Time\tQueueLength\tQueueDelay\n")
        for i, (time, length) in enumerate(queue_lengths):
            delay = queue_delays[i][1] if i < len(queue_delays) else 0
            outfile.write(f"{time}\t{length}\t{delay}\n")
    print(f"Queue length and delay data written to {output_file}")

def extract_data_from_file(input_file, output_file):
    """Main function to process the file, calculate delays, and write the results."""
    lines = read_trace_file(input_file)
    enqueue_times, dequeue_times, queue_lengths = match_events(lines)
    queue_delays = calculate_queue_delays(enqueue_times, dequeue_times)
    write_output_file(output_file, queue_lengths, queue_delays)
    return queue_lengths, queue_delays

def plot_queue_length_and_delay(queue_lengths, queue_delays, save_path=None):
    """Plots the queue length and delay over time, with an option to save as PNG."""
    # Extract time and queue length
    times_length = [event[0] for event in queue_lengths]
    lengths = [event[1] for event in queue_lengths]

    # Extract time and queue delay
    times_delay = [event[0] for event in queue_delays]
    delays = [event[1] for event in queue_delays]

    # Plot the queue length over time
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(times_length, lengths, label="Queue Length", color="blue", linewidth=2)
    plt.title("Queue Length Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Queue Length (packets)")
    plt.grid(True)
    plt.legend()

    # Plot the queue delay over time
    plt.subplot(2, 1, 2)
    plt.plot(times_delay, delays, label="Queue Delay", color="red", linewidth=2)
    plt.title("Queue Delay Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Queue Delay (seconds)")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    
    # Save plot if save_path is provided
    if save_path:
        plt.savefig(save_path)
        print(f"Plot saved as {save_path}")
    
    plt.show()

# Input and output file paths
input_trace_file = "tcp-example.tr"
output_data_file = "queue_results.txt"
output_plot_file = "queue_results_plot.png"

# Extract data, process, and plot results
queue_lengths, queue_delays = extract_data_from_file(input_trace_file, output_data_file)
plot_queue_length_and_delay(queue_lengths, queue_delays, save_path=output_plot_file)
