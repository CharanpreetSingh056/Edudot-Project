# get data
# create two articles on with punctuation and the other with any punctuations
# count word frequency with the second type of article
# find the most relevant sentences from 1 st article based on word frequency
# use these sentences as summary by joining all these articles


#from gensim.summarization import summarize
def final_summary_text(text,nos):
    import re
    import urllib.request
    import requests
    from bs4 import BeautifulSoup
    from nltk.corpus import stopwords
    from string import punctuation
    import nltk
    nltk.download('punkt')
    import sys


    stop_words=stopwords.words('english')
    punctuation=punctuation + '\n'

    def get_semiclean_content(text):
        #obj=requests.get(url)
        #text=obj.text
        #soup=BeautifulSoup(text,features="lxml")
        #paras=soup.find_all("p")
        #newtext=' '
        #for para in paras:
            #newtext+=para.text
        text=nltk.sent_tokenize(text)
        semi_cleaned=semi_cleaned_text(text)
        return semi_cleaned


    def semi_cleaned_text(doc):
        # Removing Square Brackets and Extra Spaces
        newdoc=' '
        for sen in doc:
            newdoc+=sen
        newdoc= re.sub(r'\[[0-9]*\]', ' ', newdoc)
        newdoc= re.sub(r'\s+', ' ', newdoc)
        return newdoc
    


    def cleaned_text(doc):
        newdoc=' '
        for sen in doc:
            newdoc+=sen
        newdoc = re.sub('[^a-zA-Z]'," ",newdoc) # only alphabets
        newdoc= re.sub('\s+'," ",newdoc)
        return newdoc


    def get_clean_content(text):
        #obj=requests.get(url)
        #text=obj.text
        #soup=BeautifulSoup(text,features="lxml")
        #paras=soup.find_all("p")
        #newtext=' '
        #for para in paras:
            #newtext+=para.text
        text=nltk.sent_tokenize(text)
        cleaned=cleaned_text(text)
        return cleaned


    final=get_clean_content(text)
    semi_final=get_semiclean_content(text)
    sentences=nltk.sent_tokenize(final)


    word_frequencies= {}

    for word in nltk.word_tokenize(final):
        if word.lower() not in stop_words:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
        

    mx=max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word]=word_frequencies[word]/mx

    sentences=nltk.sent_tokenize(semi_final)
    total=len(sentences)

    scores= {}
    for sen in sentences:
        for word in nltk.word_tokenize(sen.lower()):
            if word in word_frequencies.keys():
                if len(sen.split(' ')) < 50:
                    if sen not in scores:
                        scores[sen]=word_frequencies[word]
                    else:
                        scores[sen]+=word_frequencies[word]

    import heapq
    number=nos
    summary_sen=heapq.nlargest(number,scores,key=scores.get)
    summary= ' '.join(summary_sen)
    return summary

