

class RelBuilder:
    '''
    #TODO: This class should be refactored as a proper ORM wrapper
    with models for each kind of node and relationship

    #TODO: Analize which fields should be added to each kind of node and relationship

    #TODO: Add filters to discard some questions or predictions or users

    #TODO: Make performance improvements. As this code was meant to be produced fast for the
    #hackathon, there may be some methods that can be improved

    This class is used for creating Neo4j relationships using Cypher queries.
    There is a method for each type of relationship, extracting the required data
    from the questions and predictions datasets.
    
    '''
    def __init__(self, graph, binary_questions, binary_predictions, continuous_questions, continuous_predictions):

        self.graph = graph
        
        self.binary_questions = binary_questions
        self.binary_predictions = binary_predictions
        self.continuous_questions = continuous_questions
        self.continuous_predictions = continuous_predictions


    def create_category_topic_relations(self):
        '''
        Creates the relationship between categories and topics.
        The weight of the relationship is determined by how many times
        the same topic is extracted within questions that has a given category.

        Relationship structure:

        "CONTAINS" : {
            "weight": float
        }

        '''
        categories_topics = {}
        categories_topics = self.__get_category_topic_relations(categories_topics, self.binary_questions)
        categories_topics = self.__get_category_topic_relations(categories_topics, self.continuous_questions)

        cont_rels = 0
        for i in categories_topics:
            for j in categories_topics[i]:
                try:
                    # Replace quotes on topic names for avoding conflicts in the query
                    title = i.replace("'","´")
                    self.graph.run("MATCH (a:Category), (b:Topic) WHERE a.title ='" + title + "' AND b.topic_id ='" + str(j) + "' CREATE (a)-[r:CONTAINS{weight:"+str(categories_topics[i][j])+" }]->(b)")
                    cont_rels += 1

                except Exception as e:
                    print("Coudn't create relationship:" + str(e))
        
        print("Created " + str(cont_rels) + " relationships")

    def __get_category_topic_relations(self, categories_topics, questions):
        '''
        Associate unique categories with unique topics
        '''
        for index, row in questions.iterrows():
            if(row['categories'] != None):
                for category in row['categories']:

                    if("Tournament" not in category):
                        if(category not in categories_topics):
                            categories_topics[category] = {}

                        if(row['topics'] != None):
                            for topic in row['topics']:
                                if(topic['id'] not in categories_topics[category]):
                                    categories_topics[category][topic['id']] = 1
                                else:
                                    categories_topics[category][topic['id']] += 1
        
        return categories_topics
    
    def create_question_topic_relations(self):
        '''
        Creates the relationship between questions and topics.
        Relationship structure:

        "HAS" : {
        }
        '''
        continuous_questions_topics = {}
        binary_questions_topics = {}

        for i in range(len(self.continuous_questions)):
            continuous_questions_topics[self.continuous_questions['question_id'][i]] = self.continuous_questions['topics'][i]

        for i in range(len(self.binary_questions)):
            binary_questions_topics[self.binary_questions['question_id'][i]] = self.binary_questions['topics'][i]

        for i in continuous_questions_topics:
            temporal_array = []
            for j in continuous_questions_topics[i]:
                temporal_array.append(j['id'])
            continuous_questions_topics[i] = temporal_array

        for i in binary_questions_topics:
            temporal_array = []
            for j in binary_questions_topics[i]:
                temporal_array.append(j['id'])
            binary_questions_topics[i] = temporal_array

        cont_rels = 0

        for i in continuous_questions_topics:
            if continuous_questions_topics[i] != [] and continuous_questions_topics[i] != None:
                for j in continuous_questions_topics[i]:
                    try:
                        self.graph.run("MATCH (a:Question), (b:Topic) WHERE a.question_id = " + str(i) + " AND b.topic_id ='" + str(j) + "' CREATE (a)-[r:HAS]->(b)")
                        cont_rels += 1
                    except Exception as e:
                        print("Coudn't create relationship:" + str(e))

        for i in binary_questions_topics:
            if binary_questions_topics[i] != [] and binary_questions_topics[i] != None:
                for j in binary_questions_topics[i]:
                    try:
                        self.graph.run("MATCH (a:Question), (b:Topic) WHERE a.question_id = " + str(i) + " AND b.topic_id ='" + str(j) + "' CREATE (a)-[r:HAS]->(b)")
                        cont_rels += 1
                    except Exception as e:
                        print("Coudn't create relationship:" + str(e))

        print("Created " + str(cont_rels) + " relationships")


    def create_question_category_relations(self):
        '''
        Creates the relationship between categories and questions. 
        The tournament categories are ignored.
        Relationship structure:

        "BELONGSTO" : {
        }
        '''
        continuous_questions_categories = {}
        binary_questions_categories = {}
        for i in range(len(self.continuous_questions)):
            continuous_questions_categories[self.continuous_questions['question_id'][i]] = self.continuous_questions['categories'][i]
        for i in range(len(self.binary_questions)):
            binary_questions_categories[self.binary_questions['question_id'][i]] = self.binary_questions['categories'][i]

        cont_rels = 0

        for i in continuous_questions_categories:
            if continuous_questions_categories[i] != None:
                for j in continuous_questions_categories[i]:
                    if "Tournament" not in j:
                        try:
                            title = j.replace("'", "´")
                            self.graph.run("MATCH (a:Question), (b:Category) WHERE a.question_id = " + str(i) + " AND b.title ='" + title + "' CREATE (a)-[r:BELONGSTO]->(b)")
                            cont_rels += 1
                        except Exception as e:
                            print("Coudn't create relationship:" + str(e))

        for i in binary_questions_categories:
            if binary_questions_categories[i] != None:
                for j in binary_questions_categories[i]:
                    if "Tournament" not in j:
                        try:
                            title = j.replace("'", "´")
                            self.graph.run("MATCH (a:Question), (b:Category) WHERE a.question_id = " + str(i) + " AND b.title ='" + title + "' CREATE (a)-[r:BELONGSTO]->(b)")
                            cont_rels += 1
                        except Exception as e:
                            print("Coudn't create relationship:" + str(e))
        
        print("Created " + str(cont_rels) + " relationships")

    def create_user_question_relations(self):
        '''
        #TODO: Add more information about the prediction for enabling more analysis types
        Creates the relationship between users and questions. 
        Relationship structure:

        "PREDICTS" : {
        }
        '''
        most_frequent_values = self.continuous_predictions['user_id'].value_counts(ascending=False).loc[:10].index.tolist()
        selected_pairs = {}

        for i in range(len(self.continuous_predictions)):    
            if self.continuous_predictions['user_id'][i] in most_frequent_values:
                selected_pairs[self.continuous_predictions['user_id'][i]] = []
                if self.continuous_predictions['question_id'][i] not in selected_pairs[self.continuous_predictions['user_id'][i]]:
                    selected_pairs[self.continuous_predictions['user_id'][i]].append(self.continuous_predictions['question_id'][i])

        for i in range(len(self.binary_predictions)):    
            if self.binary_predictions['user_id'][i] in most_frequent_values:
                if self.binary_predictions['question_id'][i] not in selected_pairs[self.binary_predictions['user_id'][i]]:
                    selected_pairs[self.binary_predictions['user_id'][i]].append(self.binary_predictions['question_id'][i])
        
        cont_rels = 0

        for i in selected_pairs:
            for j in selected_pairs[i]:
                try:
                    self.graph.run("MATCH (a:User), (b:Question) WHERE a.user_id = " + str(i) + " AND b.question_id =" + str(j) + " CREATE (a)-[r:PREDICTS]->(b)")
                    cont_rels += 1
                except Exception as e:
                    print("Coudn't create relationship:" + str(e))
        
        print("Created " + str(cont_rels) + " relationships")

            
