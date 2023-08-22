import PyPDF2

# Open the PDF file
pdf_file = open('file.pdf', 'rb')
# pdf_file = open('CAO_JINMING_resume.pdf', 'rb')

# 
# Create a PDF reader object
pdf_reader = PyPDF2.PdfReader(pdf_file)

# Get the number of pages in the PDF
pages = len(pdf_reader.pages)
print(f"Total Pages: {pages}")

# Loop through each page 
for page in range(pages):
    current_page = pdf_reader.pages[page]
    text = current_page.extract_text()
    print(f"Page {page+1} Text: \n{text}")
    
# Close the PDF file
pdf_file.close()