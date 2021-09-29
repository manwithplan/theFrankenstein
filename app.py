from thePlayer.databaseMain import databaseMain


if __name__ == "__main__":
    data = databaseMain()

    filename, secondaryKey = data.findSimilarPiece('Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3_10.wav')

    print(filename)
    print(secondaryKey[-4:])

