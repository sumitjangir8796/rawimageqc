The "POS to CSV Converter" is a Python script that allows you to extract specific data from POS (Positioning) files and image files and then generate a CSV (Comma Separated Values) file for further analysis and visualization. The script utilizes the PyQt5 library to create a user-friendly graphical user interface (GUI) for easy interaction.

Here's how the script works:

User Interface:

The GUI provides two text boxes for browsing and selecting .pos (Positioning) and image files, respectively.
The "Browse POS Files" button allows the user to select one or more .pos files containing positioning data.
The "Browse Image Files" button allows the user to select one or more image files (in JPG format) to associate with the POS data.
Once the files are selected, the user can click the "Generate CSV" button to start the data processing.
Data Processing:

The script reads the selected POS files and extracts latitude, longitude, altitude, and Q values (which represent the quality of the positioning).
The image files are associated with the extracted data based on the user's selection.
The extracted data is then converted into a pandas DataFrame and saved as an output.csv file in the current directory.
CSV Display:

After generating the CSV file, the script displays the extracted data in a QTreeWidget, presenting the image name, latitude, longitude, altitude, and Q values.
The Q values are color-coded to distinguish between different positioning qualities. If Q=1, the background is green, if Q=2, it is yellow, and for other Q values, it is red.
Additionally, the script calculates the sharpness of each image and displays the sharpness value in the CSV view as well. If the sharpness is above 150, the background color of the sharpness column is green.
Sharpness Calculation:

The sharpness of each image is computed using OpenCV's Laplacian method, which measures the clarity and focus of the image.
The Laplacian method calculates the variance of the Laplacian of the image intensity, providing an indication of the rate of intensity change from one pixel to another.
Sharpness values above 150 are considered "good" sharpness, while values below 150 are considered "bad" sharpness.
Count and Percentage:

The script also calculates and displays the count and percentage of images with good and bad sharpness values.
It shows the number of images with Q=1, Q=2, and other Q values in separate labels.
Progress Bar:

To improve user experience, the script includes a progress bar that updates during CSV generation, showing the progress of the file processing.
The "POS to CSV Converter" provides a convenient and efficient way to handle positioning data, associate it with image files, and analyze the sharpness of images for further data exploration and analysis. The user-friendly GUI and visual representation make it easy for users to interact with the script and understand the data at a glance.

Installation Guide:

Install Python:

If you don't have Python installed, download and install the latest version of Python from the official website (https://www.python.org/downloads/).
Make sure to select the option to add Python to PATH during the installation process.
Install Required Packages:

Open a command prompt or terminal.
Install PyQt5 package using pip:
pip install PyQt5

Install pandas package using pip:
pip install pandas

Install OpenCV package using pip:
pip install opencv-python

Download the Script:

Download the "POS to CSV Converter" script (pos_to_sheet.py) from the provided source or repository.
Run the Script:

Open a command prompt or terminal in the directory where the script (pos_to_sheet.py) is located.
Run the script using Python:
python pos_to_sheet.py
GUI Interface:

The script's graphical user interface (GUI) will open.
Use the "Browse POS Files" button to select one or more .pos files containing positioning data.
Use the "Browse Image Files" button to select one or more image files (in JPG format) to associate with the POS data.
Click the "Generate CSV" button to start processing the data and generate the CSV file.
View and Analyze Data:

After generating the CSV file, the extracted data will be displayed in the GUI.
The data will be presented in a tabular format with columns for image name, latitude, longitude, altitude, Q value, and sharpness value.
The background color of the Q value and sharpness columns will indicate the positioning quality and sharpness of each image, respectively.
With these installation steps, you should be able to use the "POS to CSV Converter" script to process POS files, associate them with image files, calculate image sharpness, and analyze the data conveniently through the GUI interface
