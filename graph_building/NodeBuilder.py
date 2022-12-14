

class NodeBuilder:
    '''
    
    '''
    def __init__(self, host, user, password, graph, binary_questions, binary_predictions, continuous_questions, continuous_predictions):
        self.neo4j_host = host
        self.neo4j_user = user
        self.neo4j_password = password

        self.graph = graph
        
        self.binary_questions = binary_questions
        self.binary_predictions = binary_predictions
        self.continuous_questions = continuous_questions
        self.continuous_predictions = continuous_predictions

    def create_question_nodes(self, question_type):
        '''
        
        '''
        cont_nodes = 0
        if(question_type == 'continuous'):
            for i in range(len(self.continuous_questions)):

                try:
                    # Replace quotes ins text to avoid conflicts in the query
                    title = str(self.continuous_questions['title'][i]).replace("'","´")
                    self.graph.run("CREATE (n:Question{question_id:"
                                    +str(self.continuous_questions['question_id'][i])
                                    + ", title:'"+title+"', resolution_comment:'"
                                    + str(self.continuous_questions['resolution_comment'][i])
                                    + "', question_type:'continuous'})")
                    cont_nodes += 1
                
                except Exception as e:
                    print("Could't create node:" + str(e))

        elif(question_type == 'binary'):
            for i in range(len(self.binary_questions)):

                try:
                    # Replace quotes ins text to avoid conflicts in the query
                    title = str(self.binary_questions['title'][i]).replace("'","´")
                    self.graph.run("CREATE (n:Question{question_id:"
                                    +str(self.binary_questions['question_id'][i])
                                    + ", title:'"+title+"', resolution_comment:'"
                                    +str(self.binary_questions['resolution_comment'][i])
                                    +"', question_type:'binary'})")
                    cont_nodes += 1

                except Exception as e:
                    print("Could't create node:" + str(e))
        else:
            raise Exception("Invalid question type")
        
        print("Created " + str(cont_nodes) + " nodes")

    def create_category_nodes(self):
        '''
        '''
        binary_categories = self.binary_questions['categories'].tolist()
        continuous_categories = self.continuous_questions['categories'].tolist()
        all_categories = binary_categories + continuous_categories

        unique_categories = {}
        cont_nodes = 0
        cont = 0
        for i in all_categories:
            if i != None:
                for j in i:
                    unique_categories[j] = cont
                    cont += 1

        keys_to_delete = []
        for i in unique_categories:
            # Discard categories related directly to tournaments
            if "Tournament" in i or "tournament" in i:
                keys_to_delete.append(i)

        for i in keys_to_delete:
            unique_categories.pop(i)

        for i in unique_categories:
            try:
                # Replace quotes on category names for avoding conflicts in the query
                title = str(i.replace("'","´"))
                self.graph.run("CREATE (n:Category{category_id:"
                                +str(unique_categories[i])+", title:'"+title+"'})")
                cont_nodes += 1
            except Exception as e:
                print("Could't create node:" + str(e))
        
        print("Created " + str(cont_nodes) + " nodes")

    def create_topic_nodes(self):
        '''
        '''
        binary_topics = self.binary_questions['topics'].tolist()
        continuous_topics = self.continuous_questions['topics'].tolist()
        all_topics = binary_topics + continuous_topics

        unique_topics = {}
        for i in all_topics:
            for j in i:
                unique_topics[j['id']] = j
        
        cont_nodes = 0
        for i in unique_topics:
            try:
                # Replace quotes on topic names for avoding conflicts in the query
                title = unique_topics[i]['title'].replace("'","´")
                self.graph.run("CREATE (n:Topic{topic_id:'"+str(i)+"', title:'"+title+"'})")
                cont_nodes += 1

            except Exception as e:
                print("Could't create node:" + str(e))
        
        print("Created " + str(cont_nodes) + " nodes")

    def create_user_nodes(self):
        '''
        '''
        user_con = self.continuous_predictions['user_id'].unique().tolist()
        user_bin = self.binary_predictions['user_id'].unique().tolist()

        users_set = set(user_con+user_bin)
        users_list = list(users_set)

        for i in users_list:
            self.graph.run("CREATE (n:User{user_id:"+str(i)+"})")