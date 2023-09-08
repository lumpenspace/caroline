from dotenv import load_dotenv
from neomodel import config, db
import neomodel
import nltk
import os
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

config.DATABASE_URL = 'neo4j+s://neo4j:'+os.getenv('NEO4J_PASSWORD')+'@'+os.getenv('NEO4J_URL')+':7687'
nltk.download('punkt')
load_dotenv() 
