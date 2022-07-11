import os
import app
import json
from flaskext.mysql import MySQL
from flask import Blueprint, render_template, request, make_response

basedir = os.path.abspath(os.path.dirname(__file__))
views = Blueprint("views", __name__)
vowels = ['a', 'i', 'u', 'e', 'o']

def checkDict(word):
    conn = app.mysql.connect()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM tb_katadasar WHERE katadasar = %s""", (word,))
    data = cursor.fetchone()
    conn.close()
    return data

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def checkParticle1(word):
    particle1 = ['kah', 'lah', 'pun']
    for p in particle1:
        if word.endswith(p):
            word = rreplace(word, p, '', 1)
            return word
    return word

def checkParticle2(word):
    particle2 = ['ku', 'mu', 'nya']
    for p in particle2:
        if word.endswith(p):
            word = rreplace(word, p, '', 1)
            return word
    return word

def checkParticle3(word):
    particle3V1 = ['meny', 'peny']
    for p in particle3V1:
        if word.startswith(p) and word[4] in vowels:
            word = word.replace(p, 's', 1)
            return word

    particle3V2 = ['mem', 'pem']
    for p in particle3V2:
        if word.startswith(p) and word[4] in vowels:
            word = word.replace(p, 'p', 1)
            return word

    particle3 = ['meng', 'men', 'mem', 'me', 'peng', 'pen', 'pem', 'di', 'ter', 'ke']
    for p in particle3:
        if word.startswith(p):
            word = word.replace(p, '', 1)
            return word

    return word

def checkParticle4(word):
    particle4V1 = ['bel', 'pel']
    for p in particle4V1:
        if word.startswith(p) and word.endswith('ajar'):
            word = word.replace(p, '', 1)
            return word

    if word.startswith('be') and word[2] == 'k' and f'{word[3]}{word[4]}' == 'er':
        word = word.replace('be', '', 1)
        return word

    particle4 = ['ber', 'per', 'pe']
    for p in particle4:
        if word.startswith(p):
            word = word.replace(p, '', 1)
            return word

    return word

def checkParticle5(word, wordOriginal):
    if word.endswith('kan') and not wordOriginal.startswith(('ke', 'peng')):
        word = rreplace(word, 'kan', '', 1)
        return word

    if word.endswith('an') and not wordOriginal.startswith(('di', 'meng', 'ter')):
        word = rreplace(word, 'an', '', 1)
        return word

    if word.endswith('i') and not wordOriginal.startswith(('ber', 'ke', 'peng')):
        word = rreplace(word, 'i', '', 1)
        return word

    return word

@views.route("/", methods = ['GET', 'POST'])
def home():
    if (request.method == "GET"):
        return render_template("home.html")
    else:
        doc = request.form['document']

        #1 - Cleaning
        doc1 = request.form['document']
        for ch in ['\\','`','*','_','{','}','[',']','(',')','>','#','+','-','.','!','$','\'',',']:
            if ch in doc1:
                doc1 = doc1.replace(ch, " ")
        doc1 = ''.join([i for i in doc1 if not i.isdigit()])

        #2 - Case Folding
        doc2 = doc1.lower()

        #3 - Tokenization
        doc3 = doc2.split()

        #4 - Filtering
        data_file = os.path.join(basedir, 'static/datas/stopwords.txt')
        stopwords = []
        with open(data_file, "r") as file:
            for line in file.readlines():
                stopwords.append(line.rstrip())
        doc4 = doc2.split()
        for word in doc4:
            if word in stopwords:
                doc4.remove(word)
        doc4 = ' '.join(doc4)

        #5 - Stemming
        doc5 = []
        for idx, word in enumerate(doc4.split()):
            doc5Part = {}
            doc5Part['data'] = ''
            doc5Part['steps'] = []

            wordOriginal = word
            #5.1 - Hapus partikel
            wordBefore = word
            word = checkParticle1(word)
            data = checkDict(word)
            doc5Step = {}
            doc5Step['wordBefore'] = wordBefore
            doc5Step['word'] = word
            doc5Step['isFound'] = False
            doc5Part['steps'].append(doc5Step)
            if data:
                doc5Part['steps'][len(doc5Part['steps']) - 1]['isFound'] = True
                doc5Part['data'] = data
                doc5.append(doc5Part)
                continue

            #5.2 - Hapus akhiran kepemilikan
            wordBefore = word
            word = checkParticle2(word)
            data = checkDict(word)
            doc5Step = {}
            doc5Step['wordBefore'] = wordBefore
            doc5Step['word'] = word
            doc5Step['isFound'] = False
            doc5Part['steps'].append(doc5Step)
            if data:
                doc5Part['steps'][len(doc5Part['steps']) - 1]['isFound'] = True
                doc5Part['data'] = data
                doc5.append(doc5Part)
                continue

            #5.3 - Hapus awalan ke-1
            wordBefore = word
            word = checkParticle3(word)
            data = checkDict(word)
            doc5Step = {}
            doc5Step['wordBefore'] = wordBefore
            doc5Step['word'] = word
            doc5Step['isFound'] = False
            doc5Part['steps'].append(doc5Step)
            if data:
                doc5Part['steps'][len(doc5Part['steps']) - 1]['isFound'] = True
                doc5Part['data'] = data
                doc5.append(doc5Part)
                continue

            #5.4 - Hapus awalan ke-2
            wordBefore = word
            word = checkParticle4(word)
            data = checkDict(word)
            doc5Step = {}
            doc5Step['wordBefore'] = wordBefore
            doc5Step['word'] = word
            doc5Step['isFound'] = False
            doc5Part['steps'].append(doc5Step)
            if data:
                doc5Part['steps'][len(doc5Part['steps']) - 1]['isFound'] = True
                doc5Part['data'] = data
                doc5.append(doc5Part)
                continue

            #5.5 - Hapus akhiran
            wordBefore = word
            word = checkParticle5(word, wordOriginal)
            data = checkDict(word)
            doc5Step = {}
            doc5Step['wordBefore'] = wordBefore
            doc5Step['word'] = word
            doc5Step['isFound'] = False
            doc5Part['steps'].append(doc5Step)
            if data:
                doc5Part['steps'][len(doc5Part['steps']) - 1]['isFound'] = True
                doc5Part['data'] = data
                doc5.append(doc5Part)
                continue

            doc5.append(doc5Part)


        return render_template("home.html", doc=doc, doc1=doc1, doc2=doc2, doc3=doc3, doc4=doc4, doc5=doc5, doc5Part=json.dumps(doc5Part))