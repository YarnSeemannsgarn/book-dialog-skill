from mycroft import MycroftSkill, intent_file_handler
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from  mycroft.util.log import LOG
from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def uri_to_str(uri):
    str = uri.split("/").pop().split("#").pop()
    if str.startswith("genid"):
        return "blank node"
    return str


GRAPHDB_REPO_URL = 'http://localhost:7200/repositories/OCWS2019'
#GRAPHDB_REPO_URL = 'http://graphdb.sti2.at/repositories/OCWS2019'

class BookDialog(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.wrapper = SPARQLWrapper(GRAPHDB_REPO_URL)
        self.wrapper.addParameter('infer', 'false')
        self.current = []

    @intent_file_handler('explore.new.intent')
    def handle_explore_new(self, message):
        any_str = message.data.get('any')
        sparql = self.read_sparql_file('explore_new.rq').replace('$ANY$', any_str)
        self.wrapper.setQuery(sparql)
        self.wrapper.setReturnFormat(JSON)
        result = self.wrapper.query().convert()

        bindings = result["results"]["bindings"]
        if len(bindings) > 0:
            subj = uri_to_str(bindings[0]["s"]["value"])
            name = "not found"
            rdftype = "not found"
            for b in bindings:
                if b["p"]["value"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    rdftype = uri_to_str(b["o"]["value"])
                if b["p"]["value"] == "http://schema.org/name":
                    name = uri_to_str(b["o"]["value"])
            
            self.current.append(bindings)

            self.speak("I found something. Subject '{}' of type '{}' with name '{}'".format(subj, rdftype, name))
        else:
            self.speak("I found nothing.")

    @intent_file_handler('explore.properties.intent')
    def handle_explore_properties(self, message):
        bindings = self.current[-1]
        if len(bindings) > 0:
            subj = uri_to_str(bindings[0]["s"]["value"])
            props = set()
            for b in bindings:
                props.add(uri_to_str(b["p"]["value"]))

            answer = "The subject uses {} properties. {}".format(len(props), " . ".join(list(props)))
            self.speak(answer)
        else:
            self.speak("I found nothing.")

    @intent_file_handler('explore.details.intent')
    def handle_explore_details(self, message):
        bindings = self.current[-1]
        if len(bindings) > 0:
            subj = uri_to_str(bindings[0]["s"]["value"])
            answer = "Details on subject {}. ".format(subj)
            key_val = {}

            for b in bindings:
                prop = uri_to_str(b["p"]["value"])
                if prop not in key_val:
                    key_val[prop] = []

                if "n" in b:
                    key_val[prop].append("a new {} with name {}".format(
                        "node " + uri_to_str(b["o"]["value"]) if b["o"]["type"] == "uri" else "blank node"
                        ,uri_to_str(b["n"]["value"])))
                else: 
                    key_val[prop].append(uri_to_str(b["o"]["value"]))
        
            for key in key_val:
                answer += "{} {} {}. ".format(key, ("is" if len(key_val[key]) == 1 else "are"), " and ".join(key_val[key]))

            self.speak(answer)
        else:
            self.speak("I found nothing.")

    @intent_file_handler('explore.property.intent')
    def handle_explore_property(self, message):
        any_str = message.data.get('any')
        bindings = self.current[-1]
        if len(bindings) > 0:
            subj = uri_to_str(bindings[0]["s"]["value"])
            vals = []
            real_prop = ""
            for b in bindings:
                prop = uri_to_str(b["p"]["value"])
                if similar(prop, any_str) > 0.85:
                    real_prop = prop
                    if "n" in b:
                        vals.append("a new {} with name {}".format(
                            "node " + uri_to_str(b["o"]["value"]) if b["o"]["type"] == "uri" else "blank node"
                            ,uri_to_str(b["n"]["value"])))
                    else: 
                        vals.append(uri_to_str(b["o"]["value"]))
        
            answer = "I did not find any property called {} on the subject {}".format(any_str, subj)
            if len(vals) > 0:
                answer = "The subject {} has for the property {} the value{}: {}".format(subj, real_prop, ("s" if len(vals) > 1 else ""), " . ".join(vals))
            
            self.speak(answer)
        else:
            self.speak("I found nothing.")

    @intent_file_handler('explore.back.intent')
    def handle_explore_back(self, message):
        if len(self.current) > 1:
            self.current.pop()
            bindings = self.current[-1]
            self.speak("Now at subject " + uri_to_str(bindings[0]["s"]["value"]))
        else:
            self.speak("Cannot go back")

    @intent_file_handler('how.to.create.a.knowledge.graph.intent')
    def handle_how_to_create_a_knowledge_graph(self, message):
        self.handle('how_to_create_a_knowledge_graph.rq', 'text')

    @intent_file_handler('tell.me.chapters.of.knowledge.graphs.methodology.tools.and.selected.use.cases.intent')
    def handle_tell_me_chapters_of_knowledge_graphs_methodology_tools_and_selected_use_cases(self, message):
        self.handle('tell_me_chapters_of_knowledge_graphs_methodology_tools_and_selected_use_cases.rq', 'name')

    @intent_file_handler('tell.me.articles.from.dieter.fensel.intent')
    def handle_tell_me_articles_from_dieter_fensel(self, message):
        self.handle('tell_me_articles_from_dieter_fensel.rq', 'name')

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
        i = 1
        bindings = results["results"]["bindings"]
        for binding in bindings:
            answer += (str(i) + ". " if len(bindings) > 1 else "") + binding[value]["value"] + ".\n"
            i += 1
        return answer


def create_skill():
    return BookDialog()
