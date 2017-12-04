import csv
import os

from flask import Flask, jsonify, request,render_template
from flask.views import View
    
app = Flask(__name__, template_folder=".")

FILE = os.environ.get("FILE", "data.csv")

terms=None
with open(FILE) as f:
    reader = csv.reader(f)

    terms=[]
    for row in reader:
        try:

            terms.append(str(row[0]))
            
        except Exception as e:
            print e
    # terms = [row[0] for row in reader]
   


class Node:
    def __init__(self, label=None, data=None):
        self.label = label
        self.data = data
        self.children = dict()
    
    def addChild(self, key, data=None):
        if not isinstance(key, Node):
            self.children[key] = Node(key, data)
        else:
            self.children[key.label] = key
    
    def __getitem__(self, key):
        return self.children[key]

class Trie:
    def __init__(self):
        self.head = Node()
    
    def __getitem__(self, key):
        return self.head.children[key]
    
    def add(self, word,index):
        current_node = self.head
        word_finished = True
        
        for i in range(len(word)):
            if word[i] in current_node.children:
                current_node = current_node.children[word[i]]
            else:
                word_finished = False
                break
        if not word_finished:
            while i < len(word):
                current_node.addChild(word[i])
                current_node = current_node.children[word[i]]
                i += 1
        
        current_node.data = word
        current_node.index = index
    
    def has_word(self, word):
        if word == '':
            return False
       
       
        current_node = self.head
        exists = True
        for letter in word:
            if letter in current_node.children:
                current_node = current_node.children[letter]
            else:
                exists = False
                break
        
        
        if exists:
            if current_node.data == None:
                exists = False
        
        return exists
    
    def start_with_prefix(self, prefix):
    
        words = list()
      
        top_node = self.head
        for letter in prefix:
            if letter in top_node.children:
                top_node = top_node.children[letter]
            else:
                
                return words
        
        # Get words under prefix
        if top_node == self.head:
            queue = [node for key, node in top_node.children.iteritems()]
        else:
            queue = [top_node]
        
        while queue:
            current_node = queue.pop()
            if current_node.data != None:
                words.append(current_node.data)
            
            queue = [node for key,node in current_node.children.iteritems()] + queue
        
        return words
    
    def getData(self, word):
    
        if not self.has_word(word):
            raise ValueError('{} not found in trie'.format(word))
        current_node = self.head
        for letter in word:
            current_node = current_node[letter]
        
        return current_node.data
trie = Trie()
for count,word in enumerate(terms):
    
    if len(word)>3:
        trie.add(word,count)
    


    
@app.route('/')
def index(): 
    return render_template('index.html')




@app.route('/auto')
def search():
    query = request.args.get("q", '')
   
    results=trie.start_with_prefix(query)
    resp = jsonify(results=results[:10])  # top 10 results
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

