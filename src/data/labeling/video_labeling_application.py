"""
A small command line tool to make the labeling videos easier.
Possible labels are: amateur (1), edited (2), professional (3)
Whereas edit videos might include snippets of amateur footage with voice overlay, e.g. news reports,
and professional does not include any amateur footage (e.g. music videos, movie trailers)

TODO What percentage is already covered by amateur, news, trailer, music,


TODO print introduction or something
TODO also print total number of videos already labeled

TODO maybe use moviepy: my_clip.preview(fps=15, audio=False) # don't generate/play the audio.


Modified from https://pythonprogramminglanguage.com/pyqt5-video-widget/
"""

import sys
from random import shuffle

import psycopg2
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel,
                             QSizePolicy, QSlider, QStyle, QVBoxLayout)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton

from src.data.videos import video as video_helper

video_classes = {
    1: "Yes",
    2: "No",
}


class VideoLabelingApplication(QMainWindow):
    def __init__(self, parent=None):
        super(VideoLabelingApplication, self).__init__(parent)
        self.setWindowTitle("Video Labeling Application")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        video_widget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.set_position)

        info_label = QLabel()
        info_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        info_label.setText("Is this footage showing the event and is recorded by a handheld device?")

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.playButton)
        control_layout.addWidget(self.positionSlider)

        class_button_layout = QHBoxLayout()
        class_button_layout.setContentsMargins(0, 0, 0, 0)
        for key in video_classes:
            # The ampersand creates a shortcut for that button (Alt + <key>)
            button = QPushButton("%s (%s)" % (video_classes[key], str(key)))

            button.clicked.connect(self.classified_as(key))
            class_button_layout.addWidget(button)

        skip_button = QPushButton("Skip")
        skip_button.clicked.connect(self.next_video)
        class_button_layout.addWidget(skip_button)

        layout = QVBoxLayout()
        layout.addWidget(video_widget)
        layout.addLayout(control_layout)
        layout.addWidget(info_label)
        layout.addLayout(class_button_layout)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(video_widget)
        self.mediaPlayer.stateChanged.connect(self.media_state_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.error.connect(self.handle_error)

        # Get the videos that are supposed to be labeled
        self.conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
        self.c = self.conn.cursor()

        # Create a cursor for every video that hasn't been labeled yet.
        self.c.execute("""SELECT videos.id, videos.platform FROM videos
                                  LEFT JOIN labeled_videos  ON (labeled_videos.id, labeled_videos.platform) = (videos.id, videos.platform)
                                  WHERE labeled_videos.relevant IS NULL AND videos.crawling_status='Success' AND videos.platform='facebook'""")
        videos = self.c.fetchall()
        shuffle(videos)
        self.videos = iter(videos)

        self.next_video()

        self.session_count = 0

    def next_video(self):
        self.current_video = next(self.videos)
        video_id, platform = self.current_video
        video_path = video_helper.get_path(platform) + "/" + video_id + ".mp4"
        print(video_path)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.mediaPlayer.play()

    def classified_as(self, label):
        def on_click():
            self.session_count += 1
            print("%d Classified as %d" % (self.session_count, label))
            video_id, platform = self.current_video
            self.c.execute("INSERT INTO labeled_videos (platform, id, relevant) VALUES (%s, %s, %s)",
                           [platform, video_id, label])
            self.conn.commit()
            self.next_video()

        return on_click

    def exit(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def media_state_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.positionSlider.setValue(position)

    def duration_changed(self, duration):
        self.positionSlider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def handle_error(self):
        print(self.mediaPlayer.errorString())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoLabelingApplication()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())
