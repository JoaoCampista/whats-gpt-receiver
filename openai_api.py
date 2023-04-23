import json
import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import openai
#from openai.embeddings_utils import get_embedding, cosine_similarity
import numpy as np
from typing import List, Optional
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

api_key = os.environ["OPENAI_KEY"]
openai.api_key = api_key

EMBEDDING_MODEL_NAME = "text-embedding-ada-002"

def get_embedding(text: str, engine="text-similarity-davinci-001") -> List[float]:
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], engine=engine)["data"][0]["embedding"]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def classify_text(message):
  
  labels = ['Criar uma imagem', 'Responder uma pergunta']
  label_embeddings = [get_embedding(label,EMBEDDING_MODEL_NAME) for label in labels]
  text_embedding = get_embedding(message,EMBEDDING_MODEL_NAME)
  similarity =[]

  for label in label_embeddings:
    similatity_score = cosine_similarity(text_embedding, label)
    similarity.append(similatity_score)
  
  prediction_index = np.argmax(similarity)
  prediction = labels[prediction_index]
  
  return prediction
    

def gpt_return(prompt):
                
  completions = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      max_tokens=200,
      n=1,
      stop=None,
      temperature=0.7,
  )

  result = completions.choices[0].text

  return result

def dalle_return(message):
  
  prompt=gpt_return(f"Melhore esse prompt para criar uma imagem utilizando o DALL-E, o prompt deve ficar bem detalhado e pode incluir mais elementos: {message}")
  
  print(prompt)
  
  response = openai.Image.create(
  prompt=prompt,
  n=1,
  size="1024x1024")

  image_url = response['data'][0]['url']

  return image_url

