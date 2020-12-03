def definition_word(word):
    import nltk
    nltk.download('wordnet')
    from nltk.corpus import wordnet
    syns = wordnet.synsets(word)
    if len(syns)==0:
        return "Kindly recheck your word"
    return syns[0].definition()