import pandas as pd
import ast
from collections import Counter

from Settings.Settings import rootURL, musicFullDataBaseURL, musicSnippetsDataBaseURL, shutterSpeed

class databaseMain():

    """
    DatabaseMain module is responsible for looking up pieces of music by similarity
    from the .csv files containing the results of prior Music Information
    Retrieval.

    """

    def __init__(self):

        self.referencePiece = {}

        self.df_snippets = pd.read_csv(musicSnippetsDataBaseURL)
        self.df_full = pd.read_csv(musicFullDataBaseURL)

    def findSimilarPiece(self, referencePiece):

        """
        method that combines data gathering with analysis and returns a name of a snippet that represents
        the closest match.
        """

        self.weights = [1.2,1,0.2]

        # first step here is to gather all the relevant data via the 'gatherData' method. 
        # Then it runs through each relevant parameter and finds close matches by several 
        # sorting processes.

        self.gatherData(referencePiece)
        
        # first step is to select all the pieces with a similar instrumentation, You store the 
        # primary keys to look up the value in the other databases as it is the only common 
        # element.
        matches = self.df_full.loc[self.df_full['Instrument'] == self.referencePiece['Instrument']]
        matchesOrchestration = matches['PrimaryKey'].tolist()

        # next line gets all the matching keys from the snippets results.
        matches = self.df_snippets.loc[self.df_snippets['PrimaryKeys'].isin(matchesOrchestration)]

        # then we select all the snippets with the same dominant note (= musical key).
        matches = matches.loc[matches['DominantNoteMean'] == self.referencePiece['DominantNoteMean']]

        # then we match the occurance of notes between the reference piece and the previous matches
        # giving us a number. The higher the number, the more matches. But it doesn't take into account 
        # that some pieces simply have more notes than others so a normalization is made:  
        self.notesRef = Counter( ast.literal_eval(self.referencePiece['Notes']) )

        matches['commonCount'] = matches['Notes'].apply(lambda row: self.matchCounters(row))
        matches['commonCountRatio'] = 1 - (matches['commonCount'] / matches['DensityNotes'])

        # calculate the difference for the following analytics : TempoMean , NoisinessMedian
        matches['commonTempo'] = (1 - (matches['TempoMean'] / self.referencePiece['TempoMean'])).abs()
        matches['commonNoisiness'] = (1 - (matches['NoisinessMedian'] / self.referencePiece['NoisinessMedian'])).abs()

        # now calculate the sum of all the common data. The lower this number, the closer the match
        matches['commonRatio'] = (matches['commonCountRatio']*self.weights[0] + matches['commonTempo']*self.weights[1] + matches['commonNoisiness']*self.weights[2]).abs()

        finalMatches = matches.nsmallest(10, 'commonRatio')
        match = finalMatches.iloc[[1]]
        return match['FileNames'].item(), match['SecondaryKeys'].item()

        

    def gatherData(self, referencePiece):

        """
        gatherData gathers all relevant information from the different databases and aggregates them in
        a dictionary 'self.referencePiece'.
        """

        referenceLocationSnippet = self.df_snippets.loc[self.df_snippets['FileNames'] == referencePiece]
        self.referencePiece = {
            'filename':referencePiece,
            'PrimaryKey':referenceLocationSnippet['PrimaryKeys'].values[0],
            'Duration':referenceLocationSnippet['Duration'].values[0],
            'NoisinessMedian':referenceLocationSnippet['NoisinessMedian'].values[0],
            'TempoMean':referenceLocationSnippet['TempoMean'].values[0],
            'DensityNotes':referenceLocationSnippet['DensityNotes'].values[0],
            'Notes':referenceLocationSnippet['Notes'].values[0],
            'UniqueNotes':referenceLocationSnippet['UniqueNotes'].values[0],
            'DominantNoteMean':referenceLocationSnippet['DominantNoteMean'].values[0],
            }

        referenceLocationFull = self.df_full.loc[self.df_full['PrimaryKey'] == self.referencePiece['PrimaryKey']]
        self.referencePiece['Instrument'] = referenceLocationFull['Instrument'].values[0]

        
    def matchCounters(self, toMatch):
            """
            This method is used in formatting string entries from the .csv files using pure voodoo.
            Afterwards it actually calculates the amount of matching notes (and thus harmonic context)
            """
            toCount = ast.literal_eval(toMatch)
            toCount = [ int(x) for x in toCount ]
            toCount = Counter(toCount)
            return sum((self.notesRef & toCount).values())