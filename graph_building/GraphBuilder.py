from py2neo import Graph
import dotenv
import os
dotenv.load_dotenv()

class GraphBuilder:
    '''
    #TODO: This class should be refactored as a proper ORM wrapper
    with models for each kind of node and relationship

    #TODO: Analize which fields should be added to each kind of node and relationship

    #TODO: Add filters to discard some questions or predictions or users

    #TODO: Make performance improvements. As this code was meant to be produced fast for the
    #hackathon, there may be some methods that can be improved

    '''

    def __init__(self, binary_questions, binary_predictions, continuous_questions, continuous_predictions):
        self.neo4j_host = os.environ.get('NEO4J_HOST',)
        self.neo4j_user = os.environ.get('NEO4J_USER')
        self.neo4j_password = os.environ.get('NEO4J_PASSWORD')

        self.graph = Graph("bolt://" + self.neo4j_host,
                             auth=(self.neo4j_user, self.neo4j_password))
        
        self.binary_questions = binary_questions
        self.binary_predictions = binary_predictions
        self.continuous_questions = continuous_questions
        self.continuous_predictions = continuous_predictions



    def __create_relation(self):
        pass