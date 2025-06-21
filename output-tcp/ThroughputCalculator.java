import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class ThroughputCalculator {
    public static void main(String[] args) {
        // List of files to process
        String[] filenames = {
            "tcp-example-0-0_output.txt",
            "tcp-example-1-0_output.txt",
            "tcp-example-2-0_output.txt"
        };

        // Variable to accumulate total throughput
        double totalThroughputBps = 0;
        int fileCount = 0;

        // Process each file
        for (String filename : filenames) {
            double throughputBps = calculateThroughput(filename);
            if (throughputBps >= 0) { // If valid throughput is calculated
                totalThroughputBps += throughputBps;
                fileCount++;
            }
        }

        // Calculate and print the average throughput
        if (fileCount > 0) {
            double averageThroughputBps = totalThroughputBps / fileCount;
            double averageThroughputMbps = averageThroughputBps / 1_000_000;
            System.out.printf("Average Throughput: %.2f bps (%.2f Mbps)%n", averageThroughputBps, averageThroughputMbps);
        } else {
            System.out.println("No valid data to calculate average throughput.");
        }
    }

    public static double calculateThroughput(String filename) {
        List<Double> timestamps = new ArrayList<>();
        int totalBytes = 0;
        System.out.println("\n-----------------------------------\n");
        System.out.println("Processing file: " + filename);

        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            String line;

            // Read each line
            while ((line = br.readLine()) != null) {
                String[] parts = line.trim().split("\\s+");

                // Check if we have the expected number of parts in each line
                if (parts.length >= 7) {
                    try {
                        double timestamp = Double.parseDouble(parts[0]);  // frame.time_epoch
                        int tcpLength = Integer.parseInt(parts[5]);       // tcp.len

                        timestamps.add(timestamp);
                        totalBytes += tcpLength;

                    } catch (NumberFormatException e) {
                        System.err.println("Error parsing line: " + line);
                    }
                }
            }

            // Calculate time range
            if (!timestamps.isEmpty()) {
                double timeRange = timestamps.stream().mapToDouble(v -> v).max().orElse(0.0) -
                                   timestamps.stream().mapToDouble(v -> v).min().orElse(0.0);

                // Calculate throughput (bps)
                double throughputBps = (totalBytes * 8) / timeRange;

                // Convert bps to Mbps
                double throughputMbps = throughputBps / 1_000_000;

                // Display results for the current file
                System.out.printf("Total Bytes Received: %d bytes%n", totalBytes);
                System.out.printf("Time Range: %.2f seconds%n", timeRange);
                System.out.printf("Throughput: %.2f bps (%.2f Mbps)%n", throughputBps, throughputMbps);
                System.out.println("\n");
                // Return throughput in bps for averaging
                return throughputBps;
            } else {
                System.out.println("No valid data in file: " + filename);
                return -1;  // Indicating no valid data for throughput calculation
            }

        } catch (IOException e) {
            System.err.println("Error reading the file " + filename + ": " + e.getMessage());
            return -1;  // Indicating error in file reading
        }
    }
}
