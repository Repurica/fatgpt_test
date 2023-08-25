import json
import requests

# def recommended_readings(topic: str):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search?"
#     # params = {'query':topic, 'fields':"title,year,authors,externalIds", "limit": 10}
#     params = {'query':topic, 'fields':"externalIds", "limit": 10}
#     response = requests.get(url, params)

#     return response.json()

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
    for book in res:
        titleDOI = []
        if (len(recs)>9):
            break
        if (book.get("prism:doi") and len(recs) < 11):
            titleDOI.append(book["dc:title"])
            titleDOI.append(book["prism:doi"])
            recs.append(titleDOI)
        


    # print(type(res))
    return recs





# print(json.dumps(recommended_readings("climate change"), indent=4))
print(recommended_readings("climate change"))
# print(json.dumps(scpous("Climate Change"), indent=4))
# scpous("Climate Change")
# print(scpous("Covid"))
