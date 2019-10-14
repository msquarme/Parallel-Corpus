from bs4 import BeautifulSoup
import requests, re, os, sys
from urllib.request import urlopen
from glob import glob
import pandas as pd



EN_URL = "https://www.jw.org/en/library/bible/nwt/books/"
AM_URL = "https://www.jw.org/am/ላይብረሪ/መጽሐፍ-ቅዱስ/nwt/መጻሕፍት/"
TI_URL = "https://www.jw.org/ti/ቤተ-መጻሕፍቲ/መጽሓፍ-ቅዱስ/nwt/መጻሕፍቲ/"


def get_books(lang_url):
    url = requests.get(lang_url)
    page =BeautifulSoup(url.text, 'lxml')
    books = page.find('select', attrs={'id':'Book'}).text.split('\n')[1:]
    
    for i in range(len(books)):
        if(len(books[i].split()) > 1):
            hyphen_join = books[i].split()
            books[i] = '-'.join(hyphen_join)
    
    return books


en_books = get_books(EN_URL)
am_books = get_books(AM_URL)
ti_books = get_books(TI_URL)
en_books.remove('')
am_books.remove('')
ti_books.remove('')


def write_book_to_file(sub_url, book,lang):
    for i in range(len(book)):
        os.makedirs("Scrapped/"+lang+book[i])
        address = sub_url + book[i]
        print(address)
        url = requests.get(address)
        page = BeautifulSoup(url.text, 'lxml')
        chapters = page.find('div', attrs={'class': 'chapters clearfix'}).text.split('\n')[1:]
        chapters.remove('')
        ## Get Chapters for Each book
        for ch in chapters:
            url1 = requests.get(sub_url + book[i] +'/' + ch)
            print(sub_url + book[i] +'/' + ch)
            page1 = BeautifulSoup(url1.text,'lxml')
            ch1 = page1.find('div',attrs={'id': "bibleText"})
            tt = [verses.text.replace(u'\xa0', u' ').replace('\n',' ') for verses in ch1.find_all('span',attrs={'class':'verse'})]
            chapter = open("Scrapped/"+lang+book[i]+"/"+str(ch) + ".txt", 'w')
            for item in tt:
                chapter.write("{}\n".format(item))


write_book_to_file(TI_URL, am_books,"Tigrigna/")

write_book_to_file(AM_URL, am_books,"Amharic/")

write_book_to_file(EN_URL, en_books,"English/")


def merge_books(lang, books):
    file_lang = []
    for bk in books:
        file_lang.append((glob("Scrapped/"+lang+"/" + bk + "/*.txt")))

    
    with open("Scrapped/"+lang+"/All.txt","wb") as write_file:
        for f in file_lang:
            for i in f:
                with open(i,'rb') as r:
                    write_file.write(r.read())

merge_books("Tigrigna",ti_books)
merge_books("Amharic",am_books)
merge_books("English",en_books)


# Creating a parallel Corpus


ti = pd.read_csv('Scrapped/Tigrigna/All.txt',delimiter="\n",header=None)
ti.columns = ["Tigrigna"]

en = pd.read_csv('Scrapped/English/All.txt',delimiter="\n",header=None)
en.columns = ["English"]

data = pd.concat([en,ti],axis=1)
print(data.head())

data.to_csv("en_ti.csv",index=False)



am = pd.read_fwf('Scrapped/Amharic/All.txt',delimiter="\n",header=None)
am.columns = ["Amharic"]

#reset 'data' dataframe
data = []

data = pd.concat([en,am],axis=1)
print(data.head())

data.to_csv("en_am.csv",index=False)





