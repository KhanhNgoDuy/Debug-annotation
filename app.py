import sys
import cv2
from pathlib import Path
import pandas as pd
from PyQt5 import uic
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow


subject = 's1_Jeremy'
index = 1
save_folder = 'New_annotation'

root = Path(f'../dataset/video/{subject}')
video_path = (root / f'{subject}_{index}.mp4').as_posix()
annot_path = (root / f'{subject}_{index}.csv').as_posix()


class Buttons:
    def __init__(self):
        self.labels = None
        self.ids = None
        self.idx = 0

    def noGesturePressed(self):
        self.labels[self.idx] = 'NoGesture'
        # print(self.labels)

    def changePressed(self):
        self.labels[self.idx] = 'Change'
        self.ids[self.idx] = 18
        # print(self.labels)

    def depositPressed(self):
        self.labels[self.idx] = 'DepositPart'
        self.ids[self.idx] = 11
        # print(self.labels)

    def pickPressed(self):
        self.labels[self.idx] = 'PickPart'
        self.ids[self.idx] = 10
        # print(self.labels)

    def identificationPressed(self):
        self.labels[self.idx] = 'Identification'
        self.ids[self.idx] = 17
        # print(self.labels)

    def okPressed(self):
        self.labels[self.idx] = 'Ok'
        self.ids[self.idx] = 13
        # print(self.labels)

    def lookPressed(self):
        self.labels[self.idx] = 'Look'
        self.ids[self.idx] = 9
        # print(self.labels)

    def reportPressed(self):
        self.labels[self.idx] = 'Report'
        self.ids[self.idx] = 12
        # print(self.labels)

    def interactionPressed(self):
        self.labels[self.idx] = 'Interaction'
        self.ids[self.idx] = 8
        # print(self.labels)


class MainWindow(QMainWindow, Buttons):
    def __init__(self, cap, annot):
        super().__init__()
        uic.loadUi("app.ui", self)

        self.cap = cap
        self.annot = annot

        self.columns = list(annot.columns)
        self.ids = list(annot['ID'])
        self.labels = list(annot['label'])
        self.starts = list(annot['start'])
        self.stops = list(annot['stop'])

        self.image = None
        self.idx = 0
        self.frame_idx = self.starts[self.idx]

        self.noGesture.clicked.connect(self.noGesturePressed)
        self.ok.clicked.connect(self.okPressed)
        self.pick.clicked.connect(self.pickPressed)
        self.look.clicked.connect(self.lookPressed)
        self.deposit.clicked.connect(self.depositPressed)
        self.change.clicked.connect(self.changePressed)
        self.report.clicked.connect(self.reportPressed)
        self.identification.clicked.connect(self.identificationPressed)
        self.interaction.clicked.connect(self.interactionPressed)

        self.timer_update = QTimer(self)
        self.timer_update.timeout.connect(self.update)
        self.timer_update.start(100)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_A:
            self.frame_idx -= 1
        elif event.key() == Qt.Key_D:
            self.frame_idx += 1
        elif event.key() == Qt.Key_Left:
            self.idx -= 1
            self.frame_idx = self.starts[self.idx]
        elif event.key() == Qt.Key_Right:
            if self.idx == len(self.labels) - 1:
                self.idx = 0
            else:
                self.idx += 1
            self.frame_idx = self.starts[self.idx]
        elif event.key() == Qt.Key_Return:
            self.starts[self.idx] = self.frame_idx
            print(self.labels)

    def update(self):
        self.set_frame()
        self.scale_frame()
        self.create_annotation()

    def scale_frame(self):
        h, w, ch = self.image.shape
        q_image = QImage(self.image.data, w, h, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        label_width = self.frame.width()
        label_height = self.frame.height()
        scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio)

        self.frame.setPixmap(scaled_pixmap)

    def set_frame(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_idx - 1)
        _, self.image = self.cap.read()
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.image = put_text(
            self.image,
            self.labels[self.idx],
            self.frame_idx
        )

    def create_annotation(self):
        folder = Path(save_folder) / f"{subject}"
        folder.mkdir(parents=True, exist_ok=True)
        file = folder / f"{subject}_{index}.csv"

        # Remove NoGesture instances
        labels = []
        starts = []
        stops = []
        ids = []

        for i in range(len(self.labels)):
            if self.labels[i] != 'NoGesture':
                labels.append(self.labels[i])
                starts.append(self.starts[i])
                stops.append(self.stops[i])
                ids.append(self.ids[i])

        df = pd.DataFrame(
            list(zip(ids, labels, starts, stops)),
            columns=self.columns)
        df.to_csv(file)


def put_text(frame, label, idx):
    idx_color = (255, 0, 0)
    if label.lower() in ['change', 'depositpart', 'identification', 'interaction', 'look', 'ok', 'pickpart', 'report']:
        label_color = (0, 0, 255)
        label_thickness = 2
    else:
        label_color = (255, 0, 0)
        label_thickness = 1
    frame = cv2.resize(frame, dsize=(640, 480))
    frame = cv2.putText(frame, str(idx), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, idx_color, 1, cv2.LINE_AA)
    frame = cv2.putText(frame, label, (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, label_color, label_thickness, cv2.LINE_AA)

    return frame


def load_annotation(path):
    df = pd.read_csv(path)
    df = df.drop(columns=['Unnamed: 0'])
    return df


if __name__ == '__main__':
    cap = cv2.VideoCapture(video_path)
    annot = load_annotation(annot_path)

    # Start app
    app = QApplication(sys.argv)
    window = MainWindow(cap, annot)
    window.show()
    app.exec_()
