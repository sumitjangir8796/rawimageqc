import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidgetItem, QHeaderView, QSizePolicy, QProgressBar
from PyQt5.QtCore import Qt, QFile, QTextStream, QThread, pyqtSignal
import pandas as pd
import os
import re
import cv2
import numpy as np

def extract_lat_lon_height_from_pos(pos_file_path):
    with open(pos_file_path, 'r') as pos_file:
        lines = pos_file.readlines()

    data_list = []
    for line in lines[12:]:  # Skip the first 12 lines
        match = re.search(r'^(\d+/\d+/\d+\s+\d+:\d+:\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+', line)
        if match:
            timestamp, lat, lon, height, q = match.groups()
            data_list.append({
                'ImageName': '',
                'Latitude': float(lat),
                'Longitude': float(lon),
                'Altitude': float(height),
                'Q': int(q)
            })

    return data_list

def calculate_sharpness(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    return fm

class GenerateCSVThread(QThread):
    progress_signal = pyqtSignal(int)

    def __init__(self, pos_paths, image_paths):
        super().__init__()
        self.pos_paths = pos_paths
        self.image_paths = image_paths

    def run(self):
        pos_file_paths = self.pos_paths.strip().split("\n")
        image_file_paths = self.image_paths.strip().split("\n")

        data_list = []
        total_files = len(pos_file_paths) * len(image_file_paths)
        completed_files = 0

        for i, pos_path in enumerate(pos_file_paths):
            latitude_longitude_altitude_data = extract_lat_lon_height_from_pos(pos_path)
            if latitude_longitude_altitude_data:
                for data in latitude_longitude_altitude_data:
                    image_name = os.path.basename(image_file_paths[i % len(image_file_paths)])
                    data['ImageName'] = image_name

                    # Calculate sharpness and update data_list
                    image_path = os.path.join(image_file_paths[i % len(image_file_paths)], image_name)
                    sharpness = calculate_sharpness(image_path)
                    data['Sharpness'] = sharpness

                    data_list.append(data)

                    completed_files += 1
                    progress = int((completed_files / total_files) * 100)
                    self.progress_signal.emit(progress)

        if data_list:
            df = pd.DataFrame(data_list)
            df.to_csv('output.csv', index=False, header=True)  # Set index=False to exclude the index column
            self.display_csv()

            # Update labels with count of Q values
            self.q1_count_label.setText(f"Q = 1: {q1_count}")
            self.q2_count_label.setText(f"Q = 2: {q2_count}")
            self.q_other_count_label.setText(f"Q other: {q_other_count}")
        else:
            print("No data to generate CSV.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("POS File to CSV Converter sharpness checker")

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        pos_layout = QHBoxLayout()
        pos_paths_label = QLabel(".pos Files:")
        self.pos_paths = QTextEdit()
        self.pos_paths.setFixedHeight(30)
        pos_paths_btn = QPushButton("Browse POS Files")
        pos_paths_btn.clicked.connect(self.browse_pos_files)
        pos_layout.addWidget(pos_paths_label)
        pos_layout.addWidget(self.pos_paths)
        pos_layout.addWidget(pos_paths_btn)

        image_paths_label = QLabel("Image Files:")
        self.image_paths = QTextEdit()
        image_paths_btn = QPushButton("Browse Image Files")
        image_paths_btn.clicked.connect(self.browse_image_files)

        self.generate_csv_btn = QPushButton("Generate CSV")
        self.generate_csv_btn.clicked.connect(self.generate_csv)

        main_layout.addLayout(pos_layout)

        main_layout.addWidget(image_paths_label)
        main_layout.addWidget(self.image_paths)
        main_layout.addWidget(image_paths_btn)

        main_layout.addWidget(self.generate_csv_btn)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.csv_tree = QTreeWidget()
        self.csv_tree.setHeaderLabels(['Image Name', 'Latitude', 'Longitude', 'Altitude', 'Q', 'Sharpness'])
        self.csv_tree.setColumnCount(6)
        header = self.csv_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        self.csv_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(self.csv_tree)

        # Labels to display count of Q values
        self.q1_count_label = QLabel("Q = 1: 0")
        self.q2_count_label = QLabel("Q = 2: 0")
        self.q_other_count_label = QLabel("Q other: 0")
        main_layout.addWidget(self.q1_count_label)
        main_layout.addWidget(self.q2_count_label)
        main_layout.addWidget(self.q_other_count_label)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
       
        self.q5_count_label = QLabel("Q = 5: 0")  # Add the label for Q = 5
       
        self.good_sharpness_label = QLabel("Good Sharpness: 0 (0.00%)")
        self.bad_sharpness_label = QLabel("Bad Sharpness: 0 (0.00%)")
        main_layout.addWidget(self.q1_count_label)
        main_layout.addWidget(self.q2_count_label)
        main_layout.addWidget(self.q5_count_label)  # Add the label for Q = 5
        main_layout.addWidget(self.q_other_count_label)
        main_layout.addWidget(self.good_sharpness_label)
        main_layout.addWidget(self.bad_sharpness_label)

    def browse_pos_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Browse POS Files", "", "POS files (*.pos)")
        if file_paths:
            self.pos_paths.setPlainText("\n".join(file_paths))

    def browse_image_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Browse Image Files", "", "Image files (*.jpg)")
        if file_paths:
            self.image_paths.setPlainText("\n".join(file_paths))

    def generate_csv(self):
        self.progress_bar.setVisible(True)
        self.generate_csv_btn.setDisabled(True)
        self.generate_csv_btn.setText("Generating...")
        thread = GenerateCSVThread(self.pos_paths.toPlainText(), self.image_paths.toPlainText())
        thread.progress_signal.connect(self.update_progress)
        thread.finished.connect(self.on_generate_finished)
        thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def on_generate_finished(self):
        self.progress_bar.setVisible(False)
        self.generate_csv_btn.setEnabled(True)
        self.generate_csv_btn.setText("Generate CSV")
        self.display_csv()




    def display_csv(self):
        csv_path = 'output.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            data = df.to_dict(orient='records')

            # Calculate count and percentage of good and bad sharpness values
            total_images = len(data)
            good_sharpness_count = sum(1 for record in data if record.get('Sharpness') is not None and record['Sharpness'] > 150)
            bad_sharpness_count = total_images - good_sharpness_count
            good_sharpness_percentage = (good_sharpness_count / total_images) * 100
            bad_sharpness_percentage = 100 - good_sharpness_percentage

            # Update labels with count and percentage of sharpness values
            self.q1_count_label.setText(f"Q = 1: {sum(1 for record in data if record['Q'] == 1)}")
            self.q2_count_label.setText(f"Q = 2: {sum(1 for record in data if record['Q'] == 2)}")
            self.q5_count_label.setText(f"Q = 5: {sum(1 for record in data if record['Q'] == 5)}")  # Count for Q = 5
            self.q_other_count_label.setText(f"Q other: {sum(1 for record in data if record['Q'] not in [1, 2, 5])}")  # Exclude Q = 5 from others
            self.good_sharpness_label.setText(f"Good Sharpness: {good_sharpness_count} ({good_sharpness_percentage:.2f}%)")
            self.bad_sharpness_label.setText(f"Bad Sharpness: {bad_sharpness_count} ({bad_sharpness_percentage:.2f}%)")

            self.csv_tree.clear()

            for record in data:
                item = QTreeWidgetItem([record['ImageName'], str(record['Latitude']), str(record['Longitude']), str(record['Altitude']), str(record['Q']), str(record['Sharpness'])])
                q = record.get('Q')
                sharpness = record.get('Sharpness')

                if q == 1:
                    item.setBackground(4, Qt.green)  # Set background color to green if Q = 1
                else:
                    item.setBackground(4, Qt.yellow)  # Set background color to yellow for other Q values

                if sharpness is not None:
                    if sharpness > 150:
                        item.setBackground(5, Qt.green)  # Set background color to green if sharpness > 150
                    else:
                        item.setBackground(5, Qt.yellow)  # Set background color to yellow if sharpness <= 150

                self.csv_tree.addTopLevelItem(item)

        else:
            print("CSV file 'output.csv' does not exist.")

   
             
    def generate_csv(self):
            self.progress_bar.setVisible(True)
            self.generate_csv_btn.setDisabled(True)
            self.generate_csv_btn.setText("Generating...")
            self.thread = GenerateCSVThread(self.pos_paths.toPlainText(), self.image_paths.toPlainText())
            self.thread.progress_signal.connect(self.update_progress)
            self.thread.finished.connect(self.on_generate_finished)
            self.thread.start()

    def on_generate_finished(self):
        self.progress_bar.setVisible(False)
        self.generate_csv_btn.setEnabled(True)
        self.generate_csv_btn.setText("Generate CSV")
        self.display_csv()

    def closeEvent(self, event):
        if hasattr(self, 'thread') and self.thread.isRunning():
            event.ignore()
            self.thread.finished.connect(self.close)
            self.thread.quit()
            self.thread.wait()
        else:
            event.accept()
class GenerateCSVThread(QThread):
    progress_signal = pyqtSignal(int)

    def __init__(self, pos_paths, image_paths):
        super().__init__()
        self.pos_paths = pos_paths
        self.image_paths = image_paths

    def run(self):
        pos_file_paths = self.pos_paths.strip().split("\n")
        image_file_paths = self.image_paths.strip().split("\n")

        data_list = []
        image_index = 0
        q1_count = 0
        q2_count = 0
        q_other_count = 0

        total_steps = len(pos_file_paths) * len(image_file_paths)
        current_step = 0

        for pos_path in pos_file_paths:
            latitude_longitude_altitude_data = extract_lat_lon_height_from_pos(pos_path)
            if latitude_longitude_altitude_data:
                for data in latitude_longitude_altitude_data:
                    image_path = image_file_paths[image_index % len(image_file_paths)]
                    if os.path.exists(image_path):
                        data['ImageName'] = os.path.basename(image_path)

                        # Calculate sharpness for the image
                        sharpness = calculate_sharpness(image_path)
                        data['Sharpness'] = sharpness

                        data_list.append(data)
                        image_index += 1
                        q = data['Q']
                        if q == 1:
                            q1_count += 1
                        elif q == 2:
                            q2_count += 1
                        else:
                            q_other_count += 1

                    current_step += 1
                    progress = int((current_step / total_steps) * 100)
                    self.progress_signal.emit(progress)

        if data_list:
            df = pd.DataFrame(data_list)
            df.to_csv('output.csv', index=False, header=True)  # Set index=False to exclude the index column
            self.progress_signal.emit(100)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

