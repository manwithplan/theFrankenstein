from thePlayer.databaseMain import databaseMain
from thePlayer.musicMain import musicMain


if __name__ == "__main__":
    
    #music = musicMain()
    #music.main()

    data = databaseMain()
    
    matches = data.findSimilarPiece('Air on the G String (from Orchestral Suite no. 3, BWV 1068).mp3_10.wav')

    for index, row in matches.iterrows():
        print(row)