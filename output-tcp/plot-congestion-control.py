import matplotlib.pyplot as plt

# Function to read cwnd data from a file
def read_cwnd_data(filename):
    time = []
    cwnd = []
    
    with open(filename, 'r') as file:
        for line in file:
            # Skip empty lines
            line = line.strip()
            if not line:
                continue
                
            try:
                # Unpack three values: timestamp, previous cwnd, current cwnd
                t, prev_cwnd, curr_cwnd = map(float, line.split())
                time.append(t)
                cwnd.append(curr_cwnd)  # Use the current cwnd for plotting
            except ValueError:
                print(f"Skipping line due to unexpected format: {line}")
    
    return time, cwnd

# Function to plot the congestion window evolution and optionally save it as PNG
def plot_cwnd_evolution(time, cwnd, save_path=None):
    plt.figure(figsize=(10, 6))
    plt.plot(time, cwnd, label="CWND", color="blue", linewidth=2)
    plt.title("Congestion Window Evolution", fontsize=16)
    plt.xlabel("Time (seconds)", fontsize=14)
    plt.ylabel("Congestion Window Size (packets)", fontsize=14)
    plt.grid(True)
    plt.legend()
    
    # Save the plot if a path is provided
    if save_path:
        plt.savefig(save_path)
        print(f"Plot saved as {save_path}")
    
    plt.show()

# Main function to execute the reading and plotting
def main():
    filename = 'tcp-example.cwnd'
    output_plot_file = 'cwnd_evolution_plot.png'
    
    time, cwnd = read_cwnd_data(filename)
    
    if time and cwnd:
        plot_cwnd_evolution(time, cwnd, save_path=output_plot_file)
    else:
        print("No valid data to plot.")

# Run the main function
if __name__ == "__main__":
    main()
