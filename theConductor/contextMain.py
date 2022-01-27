class contextMain:
    """
    Keeps track of the current game state and uses a decision making process to return which mood to play next.
    """

    def __init__(self) -> None:
        # variable that sets an activity level for playback
        # 0 - been playing for a long time
        # 1 - in regular range of playback
        # 2 - haven't played much for a long time
        self.activityLevel = 2

        # variable that keeps track of how many ticks the object has received
        self.ticksReceived = 0

        # variable that keeps track of how long since the state has changed.
        self.ticksSinceChange = 0

        # variable that keeps track of the current state
        self.currentState = None

        # variable that keeps track of whether the app is currently playing music
        self.playbackActive = True

        # list of dicts that stores which gamestates have been played before, and how long.
        # {
        #   'state': string representing state,
        #   'duration' : int for how long,
        #   'start': int for when it started,
        #   'end': int for when it stopped,
        #   'PrimaryKey': int representing piece,
        # }
        self.gameStateHistory = []

        # list containing the available moods TODO put them in the settings file as global vars
        self.moods = [
            "Dark",
            "Chill",
            "Epic",
            "Scary",
            "Ethereal",
            "Calm",
            "Sad",
            "Romantic",
        ]
        # list containing the available detection TODO put them in the settings file as global vars
        self.detections = [
            "conflictZone",
            "conflictDogFight",
            "planetaryLanding",
            "docking",
            "travel",
            "canyonRunning",
            "planetaryExploration",
            "slowTravel",
            "Menu",
            "False",
        ]
        #
        # multidimensional list for deciding on a mood taking in old and new game state:
        # It looks like this
        # xx  CZ  CD  PL  DO  TR  CR  PE  ST ME FA
        # CZ
        # CD
        # PL
        # DO
        # TR
        # CR
        # PE
        # ST
        # ME
        # FA
        #
        # Where each spot in the matrix is populated by a dict containing activityLevel and corresponding mood keywords
        # False means don't change,
        # True means stop
        # change is for changes in [tempo, valence, arousal]

        self.decisionMatrix = None
        self.initDecisionMatrix()

    def main(self, gameStateOld, gameStateNew, PrimaryKey=None):
        """
        main method that keeps track of the playback context and makes the decision what mood will be next

        :gameStateOld: string representing former gameState
        :gameStateNew: string representing new gameState
        :PrimaryKey: int representing which piece has been played
        :return: string representing mood to be played next OR None in case no change to playback should be made
        """

        # first things first, store each tick.
        self.ticksReceived += 1

        if gameStateNew == gameStateOld:
            # if there is no change in state, keep track and keep going.
            self.ticksSinceChange += 1

            # the variable above will be compared with threshold values and used to determine activity level
            if (self.ticksSinceChange > 500) & (self.playbackActive == True):
                self.activityLevel = 0
            elif (self.ticksSinceChange < 100) & (self.playbackActive == False):
                self.activityLevel = 2
            else:
                self.activityLevel = 1

            mood = None

        else:
            # else take note of the change in game state and store it.
            self.gameStateHistory.append(
                {
                    "state": gameStateOld,
                    "duration": self.ticksSinceChange,
                    "start": self.ticksReceived - self.ticksSinceChange,
                    "end": self.ticksReceived,
                    "PrimaryKey": PrimaryKey,
                }
            )

            # and store the current game state
            self.currentState = gameStateNew

            # reset the tick counter
            self.ticksSinceChange = 0

            try:
                # look up the next mood
                x = self.detections.index(gameStateNew)
                y = self.detections.index(gameStateOld)
                # the line below gets the mood corresponding to the new gamestate taking in context.
                # from the decision matrix a list is retrieved, with the 3 closest moods that match,
                # for the moment we only use the first one but TODO we can actually build in the logic
                # to try the second element of the list if the first doesn't find any corresponding
                # matches, from the similarity lookup.
                mood = self.decisionMatrix[x][y][self.activityLevel][0]
            except ValueError as e:

                # There is a bad practice here, I am using the string "None" to represent no detection made.
                # When I set the mood that is returned to the new gamestate, the 2 get tangled up, even though
                # they both have a use. This is what I am solving below.
                if gameStateNew == "None":
                    mood = None
                else:
                    mood = gameStateNew

        return mood

    def initDecisionMatrix(self):
        """
        writes all relevant information to the decision matrix
        """

        # create the matrix based on the amount of possible detections
        self.decisionMatrix = [
            [[] for y in range(len(self.detections))]
            for x in range(len(self.detections))
        ]

        # format : old to new gamestate

        # conflictZone to conflictZone :
        self.decisionMatrix[0][0] = {
            0: ["Scary", "Dark", True],
            1: ["Epic", "Dark", "Scary"],
            2: ["Epic", "Dark", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to conflictDogFight :
        self.decisionMatrix[0][1] = {
            0: ["Scary", "Dark", True],
            1: ["Dark", "Scary", "Epic"],
            2: ["Epic", "Dark", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to planetaryLanding :
        self.decisionMatrix[0][2] = {
            0: [True, True, True],
            1: [True, True, True],
            2: ["Sad", "Epic", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to docking :
        self.decisionMatrix[0][3] = {
            0: [True, True, True],
            1: ["Sad", "Calm", "Chill"],
            2: ["Sad", "Romantic", "Epic"],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to travel :
        self.decisionMatrix[0][4] = {
            0: [True, True, True],
            1: ["Sad", "Romantic", "Scary"],
            2: ["Sad", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to canyonRunning :
        self.decisionMatrix[0][5] = {
            0: [True, True, True],
            1: [True, True, True],
            2: ["Dark", False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to planetaryExploration :
        self.decisionMatrix[0][6] = {
            0: [True, True, True],
            1: [True, True, True],
            2: ["Dark", False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to slowTravel :
        self.decisionMatrix[0][7] = {
            0: [True, True, True],
            1: ["Sad", "Dark", "Romantic"],
            2: ["Dark", False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to Menu :
        self.decisionMatrix[0][8] = {
            0: [True, True, True],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictZone to False :
        self.decisionMatrix[0][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to conflictZone :
        self.decisionMatrix[1][0] = {
            0: ["Scary", "Dark", True],
            1: ["Epic", "Dark", "Scary"],
            2: ["Epic", "Scary", "Dark"],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to conflictDogFight :
        self.decisionMatrix[1][1] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to planetaryLanding :
        self.decisionMatrix[1][2] = {
            0: [True, True, True],
            1: [True, True, True],
            2: ["Sad", "Epic", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to docking :
        self.decisionMatrix[1][3] = {
            0: [True, True, True],
            1: ["Calm", "Chill", False],
            2: ["Calm", "Romantic", "Sad"],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to travel :
        self.decisionMatrix[1][4] = {
            0: [True, True, True],
            1: ["Epic", "Romantic", "Sad"],
            2: ["Sad", "Dark", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to canyonRunning :
        self.decisionMatrix[1][5] = {
            0: [True, True, True],
            1: [True, True, True],
            2: ["Dark", False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to planetaryExploration :
        self.decisionMatrix[1][6] = {
            0: [True, True, True],
            1: ["Calm", False, False],
            2: ["Dark", "Scary", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to slowTravel :
        self.decisionMatrix[1][7] = {
            0: [True, True, True],
            1: ["Sad", "Dark", "Scary"],
            2: ["Dark", "Epic", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to Menu :
        self.decisionMatrix[1][8] = {
            0: [True, True, True],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # conflictDogFight to False :
        self.decisionMatrix[1][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to conflictZone :
        self.decisionMatrix[2][0] = {
            0: ["Dark", "Epic", False],
            1: ["Epic", "Scary", "Dark"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to conflictDogFight :
        self.decisionMatrix[2][1] = {
            0: ["Dark", "Epic", False],
            1: ["Epic", "Scary", "Dark"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to planetaryLanding :
        self.decisionMatrix[2][2] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to docking :
        self.decisionMatrix[2][3] = {
            0: ["Calm", "Chill", False],
            1: ["Calm", "Chill", "Ethereal"],
            2: ["Calm", "Chill", "Ethereal"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to travel :
        self.decisionMatrix[2][4] = {
            0: [True, True, True],
            1: ["Romantic", "Ethereal", False],
            2: ["Romantic", "Ethereal", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to canyonRunning :
        self.decisionMatrix[2][5] = {
            0: ["Romantic", "Romantic", False],
            1: ["Romantic", "Romantic", False],
            2: ["Romantic", "Romantic", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to planetaryExploration :
        self.decisionMatrix[2][6] = {
            0: ["Ethereal", "Calm", "Chill"],
            1: ["Ethereal", "Calm", "Chill"],
            2: ["Ethereal", "Calm", "Chill"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to slowTravel :
        self.decisionMatrix[2][7] = {
            0: ["Romantic", "Ethereal", False],
            1: ["Romantic", "Ethereal", "Calm"],
            2: ["Romantic", "Ethereal", "Calm"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to Menu :
        self.decisionMatrix[2][8] = {
            0: [True, True, True],
            1: [True, True, True],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryLanding to False :
        self.decisionMatrix[2][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to conflictZone :
        self.decisionMatrix[3][0] = {
            0: ["Scary", "Dark", False],
            1: ["Scary", "Dark", False],
            2: ["Scary", "Dark", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to conflictDogFight :
        self.decisionMatrix[3][1] = {
            0: ["Scary", "Dark", False],
            1: ["Scary", "Dark", False],
            2: ["Scary", "Dark", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to planetaryLanding :
        self.decisionMatrix[3][2] = {
            0: [True, True, True],
            1: [True, True, True],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to docking :
        self.decisionMatrix[3][3] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to travel :
        self.decisionMatrix[3][4] = {
            0: ["Calm", "Chilled", False],
            1: ["Calm", "Chilled", False],
            2: ["Calm", "Chilled", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to canyonRunning :
        self.decisionMatrix[3][5] = {
            0: [True, True, False],
            1: ["Romantic", False, False],
            2: ["Romantic", False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to planetaryExploration :
        self.decisionMatrix[3][6] = {
            0: [True, True, False],
            1: ["Romantic", "Ethereal", False],
            2: ["Romantic", "Ethereal", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to slowTravel :
        self.decisionMatrix[3][7] = {
            0: [True, True, False],
            1: ["Romantic", "Sad", "Chill"],
            2: ["Romantic", "Sad", "Chill"],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to Menu :
        self.decisionMatrix[3][8] = {
            0: [True, True, True],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # docking to False :
        self.decisionMatrix[3][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to conflictZone :
        self.decisionMatrix[4][0] = {
            0: [True, True, False],
            1: ["Scary", "Epic", "Dark"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to conflictDogFight :
        self.decisionMatrix[4][1] = {
            0: [True, True, False],
            1: ["Scary", "Epic", "Dark"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to planetaryLanding :
        self.decisionMatrix[4][2] = {
            0: [True, True, False],
            1: ["Ethereal", "Calm", "Chill"],
            2: ["Ethereal", "Calm", "Chill"],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to docking :
        self.decisionMatrix[4][3] = {
            0: [True, True, False],
            1: ["Calm", "Chill", "Sad"],
            2: ["Calm", "Chill", "Sad"],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to travel :
        self.decisionMatrix[4][4] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to canyonRunning :
        self.decisionMatrix[4][5] = {
            0: [True, True, False],
            1: ["Romantic", True, False],
            2: ["Ethereal", "Epic", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to planetaryExploration :
        self.decisionMatrix[4][6] = {
            0: [True, True, False],
            1: [True, True, False],
            2: ["Ethereal", "Calm", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to slowTravel :
        self.decisionMatrix[4][7] = {
            0: [True, True, False],
            1: ["Sad", "Romantic", "Calm"],
            2: ["Romantic", "Sad", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to Menu :
        self.decisionMatrix[4][8] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # travel to False :
        self.decisionMatrix[4][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to conflictZone :
        self.decisionMatrix[5][0] = {
            0: [True, True, False],
            1: ["Scary", "Epic", "Dark"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to conflictDogFight :
        self.decisionMatrix[5][1] = {
            0: [True, True, False],
            1: ["Scary", "Epic", "Dark"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to planetaryLanding :
        self.decisionMatrix[5][2] = {
            0: [True, True, False],
            1: [False, False, False],
            2: ["Ethereal", "Ethereal", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to docking :
        self.decisionMatrix[5][3] = {
            0: [True, True, False],
            1: ["Ethereal", "Calm", "Chill"],
            2: ["Ethereal", "Calm", "Chill"],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to travel :
        self.decisionMatrix[5][4] = {
            0: [True, True, False],
            1: ["Calm", "Chill", False],
            2: ["Epic", "Calm", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to canyonRunning :
        self.decisionMatrix[5][5] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to planetaryExploration :
        self.decisionMatrix[5][6] = {
            0: [True, False, False],
            1: ["Ethereal", "Scary", "Dark"],
            2: ["Ethereal", "Scary", "Dark"],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to slowTravel :
        self.decisionMatrix[5][7] = {
            0: [True, True, False],
            1: ["Calm", "Chill", False],
            2: ["Epic", "Calm", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to Menu :
        self.decisionMatrix[5][8] = {
            0: [True, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # canyonRunning to False :
        self.decisionMatrix[5][9] = {
            0: [True, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to conflictZone :
        self.decisionMatrix[6][0] = {
            0: ["Dark", False, False],
            1: ["Dark", "Scary", "Dark"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to conflictDogFight :
        self.decisionMatrix[6][1] = {
            0: ["Dark", False, False],
            1: ["Dark", "Scary", "Dark"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to planetaryLanding :
        self.decisionMatrix[6][2] = {
            0: [True, False, False],
            1: ["Ethereal", "Calm", "Dark"],
            2: ["Ethereal", "Calm", "Dark"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to docking :
        self.decisionMatrix[6][3] = {
            0: [True, False, False],
            1: ["Ethereal", "Calm", "Chill"],
            2: ["Ethereal", "Calm", "Chill"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to travel :
        self.decisionMatrix[6][4] = {
            0: [True, False, False],
            1: ["Romantic", "Sad", "Calm"],
            2: ["Romantic", "Sad", "Calm"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to canyonRunning :
        self.decisionMatrix[6][5] = {
            0: [True, False, False],
            1: ["Ethereal", "Calm", "Romantic"],
            2: ["Ethereal", "Calm", "Romantic"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to planetaryExploration :
        self.decisionMatrix[6][6] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to slowTravel :
        self.decisionMatrix[6][7] = {
            0: [True, False, False],
            1: ["Ethereal", "Calm", "Romantic"],
            2: ["Ethereal", "Calm", "Romantic"],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to Menu :
        self.decisionMatrix[6][8] = {
            0: [True, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # planetaryExploration to False :
        self.decisionMatrix[6][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to conflictZone :
        self.decisionMatrix[7][0] = {
            0: [True, False, False],
            1: ["Epic", "Dark", "Scary"],
            2: ["Epic", "Dark", "Scary"],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to conflictDogFight :
        self.decisionMatrix[7][1] = {
            0: [True, False, False],
            1: ["Dark", "Scary", "Romantic"],
            2: ["Dark", "Scary", "Romantic"],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to planetaryLanding :
        self.decisionMatrix[7][2] = {
            0: [False, False, False],
            1: ["Ethereal", "Calm", "Epic"],
            2: ["Ethereal", "Calm", "Epic"],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to docking :
        self.decisionMatrix[7][3] = {
            0: [True, False, False],
            1: ["Calm", "Romantic", "Chill"],
            2: ["Calm", "Romantic", "Chill"],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to travel :
        self.decisionMatrix[7][4] = {
            0: ["Romantic", "Sad", "Calm"],
            1: ["Romantic", "Sad", "Calm"],
            2: ["Romantic", "Sad", "Calm"],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to canyonRunning :
        self.decisionMatrix[7][5] = {
            0: [True, False, False],
            1: ["Romantic", "Ethereal", False],
            2: ["Romantic", "Ethereal", False],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to planetaryExploration :
        self.decisionMatrix[7][6] = {
            0: ["Calm", "Chill", "Ethereal"],
            1: ["Calm", "Chill", "Ethereal"],
            2: ["Calm", "Chill", "Ethereal"],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to slowTravel :
        self.decisionMatrix[7][7] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to Menu :
        self.decisionMatrix[7][8] = {
            0: [True, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # slowTravel to False :
        self.decisionMatrix[7][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to conflictZone :
        self.decisionMatrix[8][0] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to conflictDogFight :
        self.decisionMatrix[8][1] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to planetaryLanding :
        self.decisionMatrix[8][2] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to docking :
        self.decisionMatrix[8][3] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to travel :
        self.decisionMatrix[8][4] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to canyonRunning :
        self.decisionMatrix[8][5] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to planetaryExploration :
        self.decisionMatrix[8][6] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to slowTravel :
        self.decisionMatrix[8][7] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to Menu :
        self.decisionMatrix[8][8] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # menu to False :
        self.decisionMatrix[8][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to conflictZone :
        self.decisionMatrix[9][0] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to conflictDogFight :
        self.decisionMatrix[9][1] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to planetaryLanding :
        self.decisionMatrix[9][2] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to docking :
        self.decisionMatrix[9][3] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to travel :
        self.decisionMatrix[9][4] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to canyonRunning :
        self.decisionMatrix[9][5] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to planetaryExploration :
        self.decisionMatrix[9][6] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to slowTravel :
        self.decisionMatrix[9][7] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to Menu :
        self.decisionMatrix[9][8] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }

        # False to False :
        self.decisionMatrix[9][9] = {
            0: [False, False, False],
            1: [False, False, False],
            2: [False, False, False],
            "changes": [0.0, 0.0, 0.0],
        }
