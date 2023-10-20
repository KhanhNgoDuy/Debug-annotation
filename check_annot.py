import cv2
import time
import keyboard
import pandas as pd
from pathlib import Path


subject = 's1_Jeremy'
index = 1
root = Path(f'../dataset/video/{subject}')


def main():
    video_path = (root / f'{subject}_{index}.mp4').as_posix()
    annot_path = (root / f'{subject}_{index}.csv').as_posix()

    video = cv2.VideoCapture(video_path)
    annot = load_annotation(annot_path)

    for idx, row in annot.iterrows():
        label, start, stop = row.values
        i = start
        while True:
            if keyboard.is_pressed('a'):
                i -= 1
            if keyboard.is_pressed('d'):
                i += 1
            if keyboard.is_pressed('space'):
                time.sleep(0.1)
                break
            video.set(cv2.CAP_PROP_POS_FRAMES, i - 1)
            res, frame = video.read()
            frame = put_text(frame, label, i)
            cv2.imshow("", frame)
            cv2.waitKey()


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
    df = df.drop(columns=['Unnamed: 0', 'ID'])
    return df


if __name__ == '__main__':
    main()