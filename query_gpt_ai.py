import openai
import PyPDF2
import re

openai.api_key = "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"

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
  pdf_file = open(file_directory, 'rb')
  pdf_reader = PyPDF2.PdfReader(pdf_file)

  pages = len(pdf_reader.pages)
  print(f"Total Pages: {pages}")

  page_summaries = []

  for page_num in range(pages):

    print(f"Summarizing page {page_num+1}...")
    
    page = pdf_reader.pages[page_num]

    text = get_page_text(page)

    page_summary = summarize_text(text)  

    page_summaries.append(page_summary)

    print(page_summary)
    print()

    
  all_summaries = ". ".join(page_summaries)

  final_summary = summarize_text(all_summaries)  
  topics = summarize_text2_topic(final_summary)

  print()
  print("Final Summary:")
  print(final_summary)

  print("Topics Involved:")
  print(topics)




  pdf_file.close()

  return final_summary
