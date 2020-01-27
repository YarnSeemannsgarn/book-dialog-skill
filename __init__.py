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

    @intent_file_handler('how.to.create.a.knowledge.graph.intent')
    def handle_how_to_create_a_knowledge_graph(self, message):
        self.handle('how_to_create_a_knowledge_graph.rq', 'text')

    @intent_file_handler('tell.me.some.open.knowledge.graphs.intent')
    def handle_tell_me_some_open_knowledge_graphs_intent(self, message):
        self.handle('tell_me_some_open_knowledge_graphs.rq', 'name')

    @intent_file_handler('tell.me.some.proprietary.knowledge.graphs.intent')
    def handle_tell_me_some_proprietary_graphs_intent(self, message):
        self.handle('tell_me_some_proprietary_knowledge_graphs.rq', 'name')

    @intent_file_handler('tell.me.sub.types.of.knowledge.graphs.intent')
    def handle_tell_me_sub_types_of_knowledge_graphs(self, message):
        self.handle('tell_me_sub_types_of_knowledge_graphs.rq', 'label')

    @intent_file_handler('what.are.knowledge.graphs.intent')
    def handle_what_are_knowledge_graphs(self, message):
        self.handle('what_are_knowledge_graphs.rq', 'comment')

    @intent_file_handler('what.is.a.graph.intent')
    def handle_what_is_a_graph(self, message):
        self.handle('what_is_a_graph.rq', 'description')

    @intent_file_handler('which.knowledge.graph.has.the.highest.number.of.triples.intent')
    def handle_which_knowledge_graph_has_the_highest_number_of_triples(self, message):
        # Inference important for result (correct rdf:type handling)
        self.wrapper.clearParameter('infer')
        results = self.run_file_query('which_knowledge_graph_has_the_highest_number_of_triples.rq')
        self.wrapper.addParameter('infer', 'false')

        binding = results["results"]["bindings"][0]
        answer = 'The graph {} with {} triples'.format(
            binding["name"]["value"],
            binding["numTriples"]["value"])

        self.speak(answer)

    @intent_file_handler('who.are.the.authors.of.knowledge.graphs.methodology.tools.and.selected.use.cases.intent')
    def handle_who_are_the_authors_of_knowledge_graphs_methodology_tools_and_selected_use_cases(self, message):
        self.handle('who_are_the_authors_of_knowledge_graphs_methodology_tools_and_selected_use_cases.rq', 'name')

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
