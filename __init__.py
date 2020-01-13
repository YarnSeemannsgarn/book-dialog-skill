from mycroft import MycroftSkill, intent_file_handler
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from  mycroft.util.log import LOG

class BookDialog(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('what.are.knowledge.graphs.intent')
    def handle_dialog_book(self, message):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sparql_file = open(dir_path + "/sparql/what_are_knowledge_graphs.rq")
        sparql = sparql_file.read()
        wrapper = SPARQLWrapper("http://graphdb.sti2.at:8080/repositories/OCWS2019")

        wrapper.setQuery(sparql)
        wrapper.setReturnFormat(JSON)
        results = wrapper.query().convert()
        answer = results["results"]["bindings"][0]["comment"]["value"]
        
        self.speak_dialog('answer', data={"answer": answer})

def create_skill():
    return BookDialog()
