import pandas as pd
import ast
from collections import Counter
import numpy as np
from typing import List, Set, Dict, Tuple, Optional, Union, Any, TypeVar
import logging

from Settings.Settings import (
    rootURL,
    musicFullDataBaseURL,
    musicSnippetsDataBaseURL,
    musicMoodsDataBaseURL,
    musicSnippetsDataBaseTagsURL,
    shutterSpeed,
)


class databaseMain:
    """
    DatabaseMain module is responsible for looking up pieces of music by similarity
    from the .csv files containing the results of prior Music Information
    Retrieval.

    ...

    Attributes
    ----------
    btn : PyQT obj
        button for togging menu on and off
    homescreen : PyQT obj
        placeholder for the differen sub-menu's of the GUI

    Methods
    -------
    findPieceByMood() :
        Takes in a mood and return a matching piece that can be played from the start.

    findSimilarPiece() :
        Takes in a piece of music and looks up close musical matches.

    gatherMoods() :
        Gathers moods from similar pieces.

    gatherValenceAndArousal() :
        Gathers valence and Arousal values from the DB

    gatherSnippets() :
        Gathers snippets for a given piece of music.

    gatherData() :
        Gather relevant data for a given piece

    matchCounters() :
        RegEx voodoo, yes it was aweful to write

    """

    def __init__(self) -> None:
        # initialize logger
        self.logger: object = logging.getLogger(__name__)
        self.logger.info("database main initialized")

        self.referencePiece: Dict[str, Union[str, int]] = {}

        self.df_snippets: TypeVar("pd.DataFrame") = pd.read_csv(
            musicSnippetsDataBaseTagsURL, index_col=0
        )
        self.df_full: TypeVar("pd.DataFrame") = pd.read_csv(musicFullDataBaseURL)
        self.df_moods: TypeVar("pd.DataFrame") = pd.read_csv(musicMoodsDataBaseURL)

    def findPieceByMood(self, mood: str) -> TypeVar("pd.DataFrame"):
        """
        This function will only be used when starting playback from a point where no music has been played yet.
        It will take in a mood and return a matching piece that can be played from the start.

        :mood: string representing the mood of the piece
        :return: a dataframe containg data about pieces that match the given mood.
        """

        matches: TypeVar("pd.DataFrame") = self.df_snippets
        matches = matches.loc[matches.ThirdKey < 25]
        matches = matches[matches[mood].notna()]

        self.logger.info(f"findPieceByMood called - mood: {mood}")
        self.logger.debug(f"findPieceByMood called - returns: {matches}")

        return matches.sort_values(mood, ascending=False)[:250]

    def findSimilarPiece(
        self,
        referencePiece: str,
        mood: str,
        tempoChange: int = 0,
        valenceChange: int = 0,
        arousalChange: int = 0,
    ) -> TypeVar("pd.DataFrame"):

        """
        method that combines data gathering with analysis and returns a name of a snippet that represents
        the closest match.

        :referencePiece: string that represents the filename as it occurs in the full piece database
        :mood: string representing the mood we are currently looking for
        :tempoChange: float representing the amount you want the tempo to change up or down
        :valenceChange: float representing the amount the next match should change for valence
        :arousalChange: float representing the amount the next match should change for arousal
        :return: a dataframe containing possible matches to the reference piece
        """

        # these weights allocate importance to the fidderent commonalities between the 2 snippets.
        self.weights: List[float] = [1.2, 1, 0.2, 1, 1]

        # first step here is to gather all the relevant data via the 'gatherData' method.
        # Then it runs through each relevant parameter and finds close matches by several
        # sorting processes.

        self.gatherData(referencePiece)

        # first step is to select all the pieces with a similar instrumentation, You store the
        # primary keys to look up the value in the other databases as it is the only common
        # element.
        matches = self.df_full.loc[
            self.df_full["Instrument"] == self.referencePiece["Instrument"]
        ]
        matchesOrchestration = matches["PrimaryKey"].tolist()

        # next line gets all the matching keys from the snippets results.
        matches = self.df_snippets.loc[
            self.df_snippets["PrimaryKeys"].isin(matchesOrchestration)
        ]

        # don't return matches for the same piece
        matches = matches.loc[
            matches["PrimaryKeys"] != self.referencePiece["PrimaryKey"]
        ]

        # use only matches that have valence and arousal values
        matches = matches[matches["Valence"].notna()]

        # then we select all the snippets with the same dominant note (= musical key).
        matches = matches.loc[
            matches["DominantNoteMean"] == self.referencePiece["DominantNoteMean"]
        ]

        # then we match the occurance of notes between the reference piece and the previous matches
        # giving us a number. The higher the number, the more matches. But it doesn't take into account
        # that some pieces simply have more notes than others so a normalization is made:
        self.notesRef: TypeVar("Counter") = Counter(
            ast.literal_eval(self.referencePiece["Notes"])
        )

        matches["commonCount"] = matches["Notes"].apply(
            lambda row: self.matchCounters(row)
        )

        matches["commonCountRatio"] = 1 - (
            matches["commonCount"] / matches["DensityNotes"]
        )

        # calculate the difference for the following analytics : TempoMean , NoisinessMedian
        matches["commonTempo"] = (
            1
            - (matches["TempoMean"] / (self.referencePiece["TempoMean"] + tempoChange))
        ).abs()

        matches["commonNoisiness"] = (
            1 - (matches["NoisinessMedian"] / self.referencePiece["NoisinessMedian"])
        ).abs()

        # calculate similarities between the valence and arousal values
        matches["commonValence"] = (
            1 - (matches["Valence"] / (self.referencePiece["Valence"] + valenceChange))
        ).abs()

        matches["commonArousal"] = (
            1 - (matches["Arousal"] / (self.referencePiece["Arousal"] + arousalChange))
        ).abs()

        # now calculate the sum of all the common data. The lower this number, the closer the match
        matches["commonRatio"] = (
            matches["commonCountRatio"] * self.weights[0]
            + matches["commonTempo"] * self.weights[1]
            + matches["commonNoisiness"] * self.weights[2]
            + matches["commonValence"] * self.weights[3]
            + matches["commonArousal"] * self.weights[4]
        ).abs()

        # the result is a list of the best matches to the reference piece.
        finalMatches: TypeVar("pd.DataFrame") = matches.nsmallest(20, "commonRatio")
        finalMatches = finalMatches.iloc[1:, :]

        # here I will now write some code that gathers the moods of the music in order to give the user/program
        # a choice about what the next piece will be.

        # Make a new dataframe column that can store the value for the requested mood.
        finalMatches["Moods"] = ""

        # make a new list that can store the mood representation values themselves.
        moodValues: List[str, str] = []

        # iterate over rows in the finalmatches and lookup the values in the database.
        for _, row in finalMatches.iterrows():
            key = row["SecondaryKeys"]
            moodVal = self.gatherMoods(key, mood)
            moodValues.append(moodVal)

        # write the moods to the newly created column.
        finalMatches["Moods"] = moodValues

        # perform logging operations
        self.logger.info(
            f"findSimilarPiece called - referencePiece: {referencePiece} and mood: {mood}"
        )
        self.logger.debug(
            f"findSimilarPiece called - tempoChange: {tempoChange}, valenceChange: {valenceChange}, arousalChange: {arousalChange}"
        )
        if len(finalMatches) == 0:
            self.logger.warning(f"no matches found")

        # return the potential matches, sorted from high mood awareness to low.
        return finalMatches.sort_values("Moods", ascending=False)

    def gatherMoods(self, matchByKey: int, mood: str) -> TypeVar("pd.Series"):
        """
        This function takes the n most similar matches as calculated in the function findSimilarPiece and gathers the mood values for it.

        :matchByKey: int representing the SecondaryKeys entry in the database
        :mood: string representing which mood values to look for
        :return: a value representing the mood given for the piece specified by secondary key
        """
        row: TypeVar("pd.Series") = self.df_snippets.loc[
            self.df_snippets["SecondaryKeys"] == matchByKey
        ]

        # perform logging operations
        self.logger.info(
            f"gatherMoods called - matchByKey: {matchByKey} and mood: {mood}"
        )

        return row[mood].values[0]

    def gatherValenceAndArousal(self, matchByKey: int) -> List[float]:
        """
        This function takes the n most similar matches as calculated in the function findSimilarPiece and gathers the mood values for it.

        :matchByKey: int representing the SecondaryKeys entry in the database
        :return: a list containing 2 float values representing Valence and Arousal scores
        """
        row: TypeVar("pd.Series") = self.df_snippets.loc[
            self.df_snippets["SecondaryKeys"] == matchByKey
        ]

        # perform logging operations
        self.logger.info(f"gatherValenceAndArousal called - matchByKey: {matchByKey}")

        return [row["Valence"].values[0], row["Arousal"].values[0]]

    def gatherSnippets(self, match: str) -> List[str]:
        """
        For a given snippet, get all the filenames that come after it in the correct order.

        :match: string representing the filename as found in the snippet database TODO
        :returns: list that contains strings representing filenames of snippets as found in the snippet database
        """

        matchedSnippets: List[str] = []

        # from this list we want to gather all the filenames of the snippets that follow our match and gather them in a list.
        try:
            matchedSecondaryKey: str = match["SecondaryKeys"].item()
        except AttributeError:
            matchedSecondaryKey: str = match["SecondaryKeys"]

        lookupKey: int = int(matchedSecondaryKey[-4:])

        total: int = match["TotalSnippets"].item()

        # get all the snippets following the match we found
        for number in range(lookupKey, total):
            matchSecondaryKey = (
                f"{int(match['PrimaryKeys'].item())}_{str(number).zfill(4)}"
            )
            snippetToWrite = self.df_snippets.loc[
                self.df_snippets["SecondaryKeys"] == matchSecondaryKey
            ]
            matchedSnippets.append(snippetToWrite["FileNames"].item())

        # perform logging operations
        self.logger.info(f"gatherSnippets called - match: {match}")
        if matchedSnippets == 0:
            self.logger.warning(f"gatherSnippets called - no snippets found")

        return matchedSnippets

    def gatherData(self, referencePiece: str) -> None:

        """
        Gathers all relevant columns from the different databases and aggregates them in
        a dictionary 'self.referencePiece'

        :referencePiece: string reference to the filename as it is found in the snippet database
        """

        referenceLocationSnippet: TypeVar("pd.DataFrame") = self.df_snippets.loc[
            self.df_snippets["FileNames"] == referencePiece
        ]
        self.referencePiece: Dict[str, Union[str, int]] = {
            "filename": referencePiece,
            "PrimaryKey": referenceLocationSnippet["PrimaryKeys"].values[0],
            "Duration": referenceLocationSnippet["Duration"].values[0],
            "NoisinessMedian": referenceLocationSnippet["NoisinessMedian"].values[0],
            "TempoMean": referenceLocationSnippet["TempoMean"].values[0],
            "DensityNotes": referenceLocationSnippet["DensityNotes"].values[0],
            "Notes": referenceLocationSnippet["Notes"].values[0],
            "UniqueNotes": referenceLocationSnippet["UniqueNotes"].values[0],
            "DominantNoteMean": referenceLocationSnippet["DominantNoteMean"].values[0],
            "Valence": referenceLocationSnippet["Valence"].values[0],
            "Arousal": referenceLocationSnippet["Arousal"].values[0],
        }

        referenceLocationFull: TypeVar("pd.DataFrame") = self.df_full.loc[
            self.df_full["PrimaryKey"] == self.referencePiece["PrimaryKey"]
        ]

        self.referencePiece["Instrument"] = referenceLocationFull["Instrument"].values[
            0
        ]

        # perform logging operations
        self.logger.info(f"gatherData called - referencePiece: {referencePiece}")
        self.logger.debug(f"gatherData called - data gathered: {self.referencePiece}")

    def matchCounters(self, toMatch: str) -> int:
        """
        This method is used in formatting string entries from the .csv files using pure voodoo.
        Afterwards it actually calculates the amount of matching notes (and thus harmonic context)

        :toMatch: string representation of the notes column in the datbase snippets database TODO
        :return: sum of the commonly present notes TODO
        """
        toCount: List[int] = ast.literal_eval(toMatch)
        toCount = [int(x) for x in toCount]
        toCount = Counter(toCount)

        # perform logging operations
        self.logger.info(f"matchCounters called - toMatch: {toMatch}")
        self.logger.debug(f"matchCounters called - toCount: {toCount}")

        return sum((self.notesRef & toCount).values())
