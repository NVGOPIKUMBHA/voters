import pytesseract
from PIL import Image
import pandas as pd
import os
import re
import fitz
from pdf2image import convert_from_path

'''
def pdf_to_jpg(input_path, output_path):
    images = convert_from_path(input_path)
    for i, image in enumerate(images):
        image.save(f"{output_path}/page{i}.jpeg", 'JPEG')
'''

def pdf_to_jpg(path,out):
    doc = fitz.open(path)
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Identity, dpi=None,
                              colorspace=fitz.csRGB, clip=None, alpha=True, annots=True)
        pix.save(f"{out}/image-{page.number}.jpeg")

out = r"C:\Users\prana\OneDrive\Desktop\BRS00\BRS3\app\static\extracted"
inp = r"C:\Users\prana\OneDrive\Desktop\BRS00\BRS3\app\static\pdfs\43-1.xlsx"

pdf_to_jpg(inp, out)

print('yes')

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\t'

input_path = out
text = ''
for filename in os.listdir(input_path):
    if filename.endswith('.jpg') or filename.endswith('.jpeg'):
        img_path = os.path.join(input_path, filename)
        img = Image.open(img_path).convert('L')
        extracted_text = pytesseract.image_to_string(img, lang='eng')
        text += f'=== {filename} ===\n{extracted_text}\n\n'
print(text)

lines = text.split("\n")

def extract_lines_with_word(text, search_word):
    global lines
    result = []
    for line in lines:
        if search_word in line:
            result.append(line.replace(search_word, "").strip())
    return result

search_word = "Name:"
names = extract_lines_with_word(text, search_word)
print(names)

def extract_word_after_line(text, search_word):
    results = []
    global lines
    for line in lines:
        if search_word in line:
            words = line.split()
            string_index = words.index(search_word)
            results.append(words[string_index + 1])
    return results

search_word = "Age:"
Age = extract_word_after_line(text, search_word)
print(Age)

search_word = "Gender:"
gender = extract_word_after_line(text, search_word)
print(gender)

def extract_lines_with_word(text, search_word):
    global lines
    result = []
    for line in lines:
        if search_word in line:
            result.append(line.replace(search_word, "").strip())
    return result

search_word = "Father's Name :"
father_name = extract_lines_with_word(text, search_word)
print(father_name)
search_word = "House Number :"
house_no = extract_lines_with_word(text, search_word)
print(house_no)

def extract_specific_text(text):
    global lines
    result = []
    for line in lines:
        if re.match("^[a-zA-Z]{3}\d+$", line):
            result.append(line)
    return result
result = extract_specific_text(text)
print(result)

e_name = names
e_age = Age
e_father = father_name
e_hno = house_no
e_gender = gender
e_yav = result

df = pd.DataFrame({'Name': e_name, 'Age': e_age,'Father name':e_father,'House No.':e_hno,'Gender':e_gender,'Epic No.':e_yav})
df.to_excel('excel1.xlsx', index=False)