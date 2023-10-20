import cv2
import os
import pandas as pd


subject = 's29_ChiHoai'
name = '3'
# name = None

root_dir = '../dataset/video'
csv_files = []
mp4_files = []

if name in ['1', '2', '3']:
    csv_files.append(f'{root_dir}/{subject}_{name}.csv')
    mp4_files.append(f'{root_dir}/{subject}_{name}.mp4')
else:
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                csv_files.append(os.path.join(dirpath, filename))
            elif filename.endswith('.mp4'):
                mp4_files.append(os.path.join(dirpath, filename))

# Write text
font = cv2.FONT_HERSHEY_SIMPLEX
org = (250, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

print(mp4_files)

for video, annot in zip(mp4_files, csv_files):
    print(video)
    df = pd.read_csv(annot).to_records()
    label_ls = df['label']
    start_ls = df['start']
    stop_ls = df['stop']

    cap = cv2.VideoCapture(video)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in range(length):
        ret, frame = cap.read()

        for start, stop, label in zip(start_ls, stop_ls, label_ls):
            if start < i < stop:
                break
            label = None

        cv2.putText(frame, str(i), (50, 50), font,
                    fontScale, color, thickness, cv2.LINE_AA)
        cv2.putText(frame, label, (450, 300), font,
                    fontScale, color, thickness, cv2.LINE_AA)
        frame = cv2.resize(frame, (960, 540))
        cv2.imshow('frame', frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
