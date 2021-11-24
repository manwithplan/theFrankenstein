import time

from thePlayer.databaseMain import databaseMain
from thePlayer.musicMain import musicMain

import ast
import numpy as np


if __name__ == "__main__":

    data = databaseMain()
    matches = data.findSimilarPiece(
        "Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3_10.wav"
    )

    music = musicMain()
    print(music.main("bullshit"))
    music.closeMusicPlayer()

    # for index, row in matches.iterrows():
    #    print(row)

