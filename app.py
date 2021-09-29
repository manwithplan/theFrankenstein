from thePlayer.databaseMain import databaseMain



if __name__ == "__main__":
    data = databaseMain()

    print(data.df_snippets[0])
    print(data.df_full[0])