from mycroft import MycroftSkill, intent_file_handler
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from  mycroft.util.log import LOG

GRAPHDB_REPO_URL = 'http://graphdb.sti2.at:8080/repositories/OCWS2019'


class BookDialog(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.wrapper = SPARQLWrapper(GRAPHDB_REPO_URL)
        self.wrapper.addParameter('infer', 'false')

    @intent_file_handler('what.are.knowledge.graphs.intent')
    def handle_what_are_knowledge_graphs(self, message):
        self.handle('what_are_knowledge_graphs.rq', 'comment')

    @intent_file_handler('tell.me.sub.types.of.knowledge.graphs.intent')
    def handle_tell_me_sub_types_of_knowledge_graphs(self, message):
        self.handle('tell_me_sub_types_of_knowledge_graphs.rq', 'label')

    @intent_file_handler('tell.me.some.open.knowledge.graphs.intent')
    def handle_tell_me_some_open_knowledge_graphs_intent(self, message):
        self.handle('tell_me_some_open_knowledge_graphs.rq', 'name')

    @intent_file_handler('tell.me.some.proprietary.knowledge.graphs.intent')
    def handle_tell_me_some_open_knowledge_graphs_intent(self, message):
        self.handle('tell_me_some_proprietary_knowledge_graphs.rq', 'name')

    def handle(self, sparql_file_name, value):
        results = self.run_file_query(sparql_file_name)
        answer = self.create_answer(results, value)
        self.speak(answer)

    def run_file_query(self, file_name):
        sparql = self.read_sparql_file(file_name)
        return self.run_query(sparql)

    @staticmethod
    def read_sparql_file(file_name):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sparql_file = open(dir_path + "/sparql/" + file_name)
        return sparql_file.read()

    def run_query(self, sparql):
        self.wrapper.setQuery(sparql)
        self.wrapper.setReturnFormat(JSON)
        return self.wrapper.query().convert()

    @staticmethod
    def create_answer(results, value):
        answer = ''
        for binding in results["results"]["bindings"]:
            answer += binding[value]["value"] + "\n"
        return answer


def create_skill():
    return BookDialog()
