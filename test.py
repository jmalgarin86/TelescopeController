import matplotlib.pyplot as plt

# Define the file path
file_path = 'log_2024-08-14_00-32-34.txt'

# Initialize empty lists to store the second and third columns
second_column = []
third_column = []

# Open the file and read line by line
with open(file_path, 'r') as file:
    for line in file:
        # Split the line into columns using spaces as a separator
        columns = line.split()

        # Append the second and third columns to their respective lists
        second_column.append(float(columns[1])-525)
        third_column.append(float(columns[2])-333)

# Plot the second column
plt.plot(second_column[0:], linestyle='-', color='b', label='Second Column')

# Plot the third column
plt.plot(third_column[0:], linestyle='-', color='r', label='Third Column')

# Add labels and title
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('Plot of the Second and Third Columns')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()