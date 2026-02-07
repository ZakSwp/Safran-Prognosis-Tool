import pandas as pd
import numpy as np

df = pd.read_csv("C:/Users/mheme/Downloads/accel_physics.csv")
# 2. Determine sampling parameters
# Calculate average time difference between samples
dt = df['Time_s'].diff().mean()
start_time = df['Time_s'].iloc[0]

# 3. Data Extension (Mirroring Strategy)
# We need 4500 samples. The original is ~904.
target_length = 4500
input_length = len(df)
needed_cycles = (target_length // input_length) + 1

# List to store the data chunks
data_chunks = []

for i in range(needed_cycles):
    if i % 2 == 0:
        # Forward pass
        chunk = df[['Ax_ms2', 'Ay_ms2', 'Az_ms2']].copy()
    else:
        # Backward pass (Mirroring) to ensure continuity at boundaries
        chunk = df[['Ax_ms2', 'Ay_ms2', 'Az_ms2']].iloc[::-1].copy()
    
    data_chunks.append(chunk)

# Concatenate all chunks and trim to exactly 4500
extended_df = pd.concat(data_chunks).reset_index(drop=True)
extended_df = extended_df.iloc[:target_length].copy()

# 4. Add Synthetic Noise
# Add small Gaussian noise to prevent exact repetition of values
# Scale is based on a small fraction of the signal's standard deviation
noise_scale = 0.05  # Adjust this for more/less variation
extended_df['Ax_ms2'] += np.random.normal(0, noise_scale, target_length)
extended_df['Ay_ms2'] += np.random.normal(0, noise_scale, target_length)
extended_df['Az_ms2'] += np.random.normal(0, noise_scale, target_length)

# 5. Regenerate Time Column
# Create a strictly increasing time axis starting from the original start time
new_time_axis = [start_time + i * dt for i in range(target_length)]
extended_df.insert(0, 'Time_s', new_time_axis)

# 6. Output
# Round to 3 decimal places to match original file style
extended_df = extended_df.round(3)

# Save to a new CSV file
output_filename = "C:/Users/mheme/Downloads/accel_physics_aug.csv"
extended_df.to_csv(output_filename, index=False)

print(f"Generated {len(extended_df)} samples.")
print(f"File saved as: {output_filename}")
print("First 5 rows of generated data:")
print(extended_df.head())