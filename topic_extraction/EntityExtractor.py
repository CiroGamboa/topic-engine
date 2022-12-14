import requests
import dotenv
import os
import pandas as pd
import json
dotenv.load_dotenv()

class EntityExtractor:
    '''
    #TODO: Add parameter to limit the amount of extracted topics per question
    This class contains methods for extracting entities from a given text using Wikifier.
    Two methods are presented, the first one using the Wikifier API directly
    and the second one, uses the Wikifier demo capabilities.
    '''
    def __init__(self, page_rank=0.006, wiki_data_classes=3):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        self.page_rank = page_rank
        self.wiki_data_classes = wiki_data_classes


    def get_entities_from_api(self,extraction_string,
                apply_page_rank_sq_threshold,          # to actually discard the annotations whose pagerank is < minPageRank (defaultis False)
                min_link_freq,                         # default 1
                max_mention_entropy,                   # cause all highly ambiguous mentions to be ignored float (default -1)
                max_targets_per_mention,               # to use only the most frequent x candidate annotations for each mention (default x=20)
                wiki_data_classes,                     # wikiDataClasses (true or false)
                wiki_data_class_ids):                   # wikiDataClassIds (true or false)
        
        '''
        Extracts the entities from a given text, using a set of tunning parameters for
        performing a request to the Wikifier API.

        To get a user key, go to https://wikifier.org/register.html
        '''

        user_key = os.environ.get('WIKIFIER_EXTRACTION_KEY')

        api_url = 'http://www.wikifier.org/annotate-article?'

        payload = {'userKey': user_key, 'text': extraction_string, 
                    'lang': 'en',
                    'wikiDataClasses': wiki_data_classes,
                    'wikiDataClassIds':wiki_data_class_ids,
                    'includeCosines':'false',
                    'maxMentionEntropy':max_mention_entropy,
                    'maxTargetsPerMention':max_targets_per_mention,
                    'minLinkFrequency': min_link_freq,
                    'applyPageRankSqThreshold': apply_page_rank_sq_threshold,
                    'pageRankSqThreshold':self.page_rank
                 }

        try:
            res = requests.post(api_url, headers=self.headers, data=payload)
            if (res.status_code == 200):
                titles = []
                data = res.json()['annotations']

                filtered_annotations = self.__filter_annotations(data, self.page_rank)
                return filtered_annotations

            else:
                raise Exception("Response code: ", res.status_code)

        except Exception as e:
            print("API call failed: " + str(e))
            return None

    def get_annotations_from_submit(self,text):
        '''
        Extracts the entities from a given text using the demo tool of Wikifier.
        The demo tool is used emulating an user from the browser.
        The entities are extracted with the demo predifined parameters and 
        then filtered by relevance using the page rank.
        '''
        data = self.__get_annotated_data(text)
        annotations = self.__filter_annotations(data)
        return annotations

    def __get_annotated_data(self,text):
        '''
        Performs the request for obtaining the entities to the wikifier demo, using a token
        for accesing the specific text processing output of the provided text.
        '''
        split_token = self.__get_extraction_token(text)
        data = requests.get('https://wikifier.org/submit.py?cmd=annotate-article&splitToken=' + split_token + '&splitResponse=start')
        return data.json()


    def __get_extraction_token(self,text):
        '''
        Performs the request to the wikifier demo server for obtaining a token,
        that is necessary for querying the output of the text processing.
        '''
        url = 'https://wikifier.org/submit.py'

        payload = {
            'languages': 'en',
            'secondaryAnnotLanguage': 'en',
            'text': text,
            'extraArgs': '',
            'host': 'posta',
            'port': 8095,
            'splitResponse': 'prepare'
        }

        try:
            res = requests.post(url, headers=self.headers, data=payload)

            if(res.status_code == 200):
                res_text = res.text
                index1 = res_text.find("splitToken") + 14
                index2 = res_text.find("splitResponse") - 4
                split_token = res_text[index1:index2]

                return split_token
            else:
                raise Exception("Response code: ", res.status_code)
        
        except Exception as e:
            print("Token extraction failed: " + str(e))
            return None
        

    def __filter_annotations(self, data):
        '''
        The obtained entities are filtered by relevance using the page rank
        '''
        annotations = data['annotations']
        filtered_annotations = []

        for annotation in annotations:
            # In case there are missing fields
            try:
                if(annotation['pageRank'] > self.page_rank):
                    annot = {}
                    annot['title'] = annotation['title']
                    annot['id'] = annotation['wikiDataItemId']
                    annot['types'], annot['classes'] = self.__filter_types(annotation)
                    filtered_annotations.append(annot)
            except Exception as e:
                print("Topic extraction failed: " + str(e))

        return filtered_annotations

    def __filter_types(self, annotation):
        '''
        The ammount of wiki data classes is limited for avoiding low quality associations
        with the dbPedia and Wiki Data predefined classes.
        '''
        dbpedia_types = annotation['dbPediaTypes']
        wikidata_classes = annotation['wikiDataClasses'][0:self.wiki_data_classes]

        return dbpedia_types, wikidata_classes

    def generate_topic_dataset(self, question_dataset, topic_dataset_name, starts_at, finishes_at):
        '''
        Generates a topic dataset in a JSON file from a given question dataset.
        The inverval for processing the questions can be set usinf starts_at and finishes_at.
        '''
        filtered_questions_dataset = question_dataset.iloc[starts_at:finishes_at]
        
        with open(topic_dataset_name, 'w') as outfile:

            cont = starts_at + 1
            topics = []
            for index, question in filtered_questions_dataset.iterrows():
                
                try:
                    title = question['title']
                    description = question['description']
                    text = title + '. ' + description

                    annotations = self.get_annotations_from_submit(text)
                    topics.append(annotations)

                except Exception as e:
                    print('Error:', str(e))
                    topics.append([])

                print("Processed questions: ",cont)
                cont += 1

            json.dump(topics, outfile)
    
    @staticmethod
    def join_datasets(question_dataset, topic_dataset, column_index, outfile_name):
        '''
        Generates a JSON file with the the merged question dataset and the topic
        '''
        enriched_dataset = question_dataset.copy()
        enriched_dataset.insert(loc=column_index, column='topics', value=topic_dataset)
        
        enriched_dataset.to_json(outfile_name)
        return enriched_dataset


