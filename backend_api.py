import openai
import PyPDF2
import re
import json
import requests
import cohere 
import json
from unpywall import Unpywall
from unpywall.utils import UnpywallCredentials



co = cohere.Client('L3YxAjptxoiLXbhbiSh9C2yuB7mCIRQCLoMIcxqa') # This is your trial API key
openai.api_key = "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"


UnpywallCredentials('nick.haupka@gmail.com')
# Loop through all the retrived DOIs from Scopus/Semantic Scholar to check if there are OpenAccess Articles
def CheckOpenAccess(titleDOI):
    for book in titleDOI:
      try:
          response = requests.get(Unpywall.get_pdf_link(doi=book[1]))
          filename = book[0] + ".pdf"
          with open(filename, 'wb') as f:
              f.write(response.content)
      except:
          print("Sorry, no open access articles found")
    


def summarisation(file_directory):
  def get_page_text(page):
    try:
      text = page.extract_text()
    except:  
      text = ""
    
    text = str(text)
    text = text.strip()
    text = re.sub(r'\W+', ' ', text)

    return text

  def summarize_text(text):
    messages = [
      {"role": "system", "content": "Please provide a 1 sentence summary of the following:"}, 
      {"role": "user", "content": text}
    ]

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )

    return response["choices"][0]["message"]["content"]

  def summarize_text2_topic(text):
    messages = [
      {"role": "system", "content": "Provide a keywords for the paragraph. Return in JSON format."}, 
      {"role": "user", "content": text}
    ]

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )

    return response["choices"][0]["message"]["content"]
  

  def summarise_cohere(text):
    response = co.summarize( 
      text=text,
      length='auto',
      format='auto',
      model='summarize-xlarge',
      additional_command='',
      temperature=0.8,
  ) 
    return response.summary
  
  pdf_file = open(file_directory, 'rb')
  pdf_reader = PyPDF2.PdfReader(pdf_file)

  pages = len(pdf_reader.pages)
  print(f"Total Pages: {pages}")

  page_summaries = []
  page_summary_cohere = []

  for page_num in range(pages):

    print(f"Summarizing page {page_num+1}...")
    
    page = pdf_reader.pages[page_num]

    text = get_page_text(page)

    page_summary = summarize_text(text)
    # page_ch_summary = summarise_cohere(text)  

    page_summaries.append(page_summary)
    # page_summary_cohere.append(page_summary_cohere)

    print(page_summary)
    print()
    print(page_summary_cohere)

    
  all_summaries = ". ".join(page_summaries)

  final_summary = summarize_text(all_summaries)  
  topics = summarize_text2_topic(final_summary)
  # cohere_summary = summarise_cohere(final_summary)

  print()
  print("OpenAI's Final Summary:")
  print(final_summary)

  print("Topics Involved:")
  print(topics)

  # print("Cohere's Final Summary:")
  # print(cohere_summary)




  pdf_file.close()

  return final_summary,json.loads(topics)




def recommended_readings(topic: str):
    url = "https://api.semanticscholar.org/graph/v1/paper/search?"
    # params = {'query':topic, 'fields':"title,year,authors,externalIds", "limit": 10}
    params = {'query':topic, 'fields':"externalIds", "limit": 10}
    response = requests.get(url, params)
    recs = []
    res_dict = response.json()
    data_dict = res_dict["data"] # This is array of dicts with all info of results
    # print(data_dict)
    for item in data_dict:
        for key in item :
            #print(key)
            if (key == "externalIds"):
                if (item[key].get("DOI")):
                    # print(item[key])
                    doi = item[key]["DOI"]
                    recs.append(doi)

    return recs

scopusKey = "17abfb9454e405a8ebb7b7e73b1c7695"

def scpous(topic : str):
    url = "https://api.elsevier.com/content/search/scopus?"
    params = {'query':topic, 'apikey':scopusKey}
    response = requests.get(url, params)
    recs = []
    res_dict = response.json()
    res = res_dict["search-results"]["entry"] #Returns a list of all results

    # print(res)
    # print(res)
    for book in res:
        # print(book)
        titleDOI = []
        if (len(recs)>9):
            break
        if (book.get("prism:doi") and len(recs) < 11):
            titleDOI.append(book["dc:title"])
            # print(book["dc:title"])
            # titleDOI.append(book["prism:doi"])
            recs.append(titleDOI)

    # print(type(res))
    return recs

def OpenAlexAbstract(doi : str):
    url = "https://api.openalex.org/works/"
    url += doi

    response = requests.get(url)
    res_dict = response.json()

    # Returns an inverted index/ dict with key of a word that appears with values index of where it appears
    abi = res_dict["abstract_inverted_index"] 

    #Using this to store the max value for each key which in this case is the word
    len_index = []  

    # Add the largest number from each key value into len_index first
    for indices in abi.values():
        len_index.append(max(indices))

    #Find the max value among all the max values in each list
    max_index = max(len_index) 


    # Create a list to store the words in their respective positions
    sentence = [''] * (max_index + 1)

    # Send each word back into its original position in the sentence
    for word, indices in abi.items():
        for index in indices:
            sentence[index] = word

    # Convert the list to a string
    reconstructed_sentence = ' '.join(sentence)

    return reconstructed_sentence

def OpenAlexRelated(topic : str):
        #Used for looking for actual concepts reltaed to the search'
        url = "https://api.openalex.org/concepts?" 
        params = {'search': topic}
        response = requests.get(url, params)
        related = []
        res_dict = response.json()

        
        res = res_dict["results"]
        

        for concept in res:
            if (len(related) < 3):
                related.append(concept["display_name"])
                
        
        return related

print(OpenAlexRelated('Cloud Computing'))
