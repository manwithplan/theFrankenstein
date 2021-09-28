import pandas as pd

from Settings.Settings import rootURL, musicFullDataBaseURL, musicSnippetsDataBaseURL, shutterSpeed

class databaseMain():

    """
    DatabaseMain module is responsible for looking up pieces of music by similarity
    from the .csv files containing the results of prior Music Information
    Retrieval.

    """

    def __init__(self):

        self.df_snippets = pd.read_csv(musicSnippetsDataBaseURL)
        self.df_full = pd.read_csv(musicFullDataBaseURL)

        

