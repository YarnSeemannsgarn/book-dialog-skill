from mycroft import MycroftSkill, intent_file_handler
from SPARQLWrapper import SPARQLWrapper, JSON

class BookDialog(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('what.are.knowledge.graphs.intent')
    def handle_dialog_book(self, message):
        sparql = open("sparql/what_are_knowledge_graphs.rq")
        wrapper = SPARQLWrapper("http://graphdb.sti2.at:8080/repositories/OCWS2019")
        wrapper.setQuery(sparql)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        self.speak_dialog('answer', data={"answer": results["results"]["bindings"][0]["comment"]["value"]})

def create_skill():
    return BookDialog()
