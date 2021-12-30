import pandas as pd
import ast
from collections import Counter

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

    """

    def __init__(self):

        self.referencePiece = {}

        self.df_snippets = pd.read_csv(musicSnippetsDataBaseTagsURL, index_col=0)
        self.df_full = pd.read_csv(musicFullDataBaseURL)
        self.df_moods = pd.read_csv(musicMoodsDataBaseURL)

    def findSimilarPiece(
        self, referencePiece, mood, tempoChange=0, valenceChange=0, arousalChange=0
    ):

        """
        method that combines data gathering with analysis and returns a name of a snippet that represents
        the closest match.

        :referencePiece: string that represents the filename as it occurs in the full piece database
        :mood: string representing the mood we are currently looking for
        :tempoChange: float representing the amount you want the tempo to change up or down
        :valenceChange: float representing the amount the next match should change for valence
        :arousalChange: float representing the amount the next match should change for arousal
        """

        # these weights allocate importance to the fidderent commonalities between the 2 snippets.
        self.weights = [1.2, 1, 0.2, 1, 1]

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
        self.notesRef = Counter(ast.literal_eval(self.referencePiece["Notes"]))

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
        finalMatches = matches.nsmallest(20, "commonRatio")
        finalMatches = finalMatches.iloc[1:, :]

        # here I will now write some code that gathers the moods of the music in order to give the user/program
        # a choice about what the next piece will be.

        # Make a new dataframe column that can store the value for the requested mood.
        finalMatches["Moods"] = ""

        # make a new list that can store the mood representation values themselves.
        moodValues = []

        # iterate over rows in the finalmatches and lookup the values in the database.
        for index, row in finalMatches.iterrows():
            key = row["SecondaryKeys"]
            moodVal = self.gatherMoods(key, mood)
            moodValues.append(moodVal)

        # write the moods to the newly created column.
        finalMatches["Moods"] = moodValues

        # return the potential matches, sorted from high mood awareness to low.
        return finalMatches.sort_values("Moods", ascending=False)

    def gatherMoods(self, matchByKey, mood):
        """
        This function takes the n most similar matches as calculated in the function findSimilarPiece and gathers the mood values for it.

        :matchByKey: int representing the SecondaryKeys entry in the database
        :mood: string representing which mood values to look for
        :return: a value representing the mood given for the piece specified by secondary key
        """
        row = self.df_snippets.loc[self.df_snippets["SecondaryKeys"] == matchByKey]
        return row[mood].values[0]

    def gatherValenceAndArousal(self, matchByKey):
        """
        This function takes the n most similar matches as calculated in the function findSimilarPiece and gathers the mood values for it.

        :matchByKey: int representing the SecondaryKeys entry in the database
        :return: a list containing 2 float values representing Valence and Arousal scores
        """
        row = self.df_snippets.loc[self.df_snippets["SecondaryKeys"] == matchByKey]
        return [row["Valence"].values[0], row["Arousal"].values[0]]

    def gatherSnippets(self, match):
        """
        For a given snippet, get all the filenames that come after it in the correct order.

        :match: string representing the filename as found in the snippet database TODO
        :returns: list that contains strings representing filenames of snippets as found in the snippet database
        """

        matchedSnippets = []

        # from this list we want to gather all the filenames of the snippets that follow our match and gather them in a list.
        try:
            matchedSecondaryKey = match["SecondaryKeys"].item()
        except AttributeError:
            matchedSecondaryKey = match["SecondaryKeys"]

        lookupKey = int(matchedSecondaryKey[-4:])

        total = match["TotalSnippets"].item()

        # get all the snippets following the match we found
        for number in range(lookupKey, total):
            matchSecondaryKey = (
                f"{int(match['PrimaryKeys'].item())}_{str(number).zfill(4)}"
            )
            snippetToWrite = self.df_snippets.loc[
                self.df_snippets["SecondaryKeys"] == matchSecondaryKey
            ]
            matchedSnippets.append(snippetToWrite["FileNames"].item())

        return matchedSnippets

    def gatherData(self, referencePiece):

        """
        Gathers all relevant columns from the different databases and aggregates them in
        a dictionary 'self.referencePiece'

        :referencePiece: string reference to the filename as it is found in the snippet database
        """

        referenceLocationSnippet = self.df_snippets.loc[
            self.df_snippets["FileNames"] == referencePiece
        ]
        self.referencePiece = {
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

        referenceLocationFull = self.df_full.loc[
            self.df_full["PrimaryKey"] == self.referencePiece["PrimaryKey"]
        ]
        self.referencePiece["Instrument"] = referenceLocationFull["Instrument"].values[
            0
        ]

    def matchCounters(self, toMatch):
        """
        This method is used in formatting string entries from the .csv files using pure voodoo.
        Afterwards it actually calculates the amount of matching notes (and thus harmonic context)

        :toMatch: string representation of the notes column in the datbase snippets database TODO
        :return: sum of the commonly present notes TODO
        """
        toCount = ast.literal_eval(toMatch)
        toCount = [int(x) for x in toCount]
        toCount = Counter(toCount)
        return sum((self.notesRef & toCount).values())
