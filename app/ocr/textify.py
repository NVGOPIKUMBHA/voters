import pytesseract
from PIL import Image
import pandas as pd
import fitz
import re

random = 0

def extract_images(path):
    global r
    doc = fitz.open(path)
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Identity, dpi=None,
                              colorspace=fitz.csRGB, clip=None, alpha=True, annots=True)
        pix.save(f"{random}-image-{page.number}.jpg")
    r = r+1
    return r

path = "C:\\Users\\prana\\OneDrive\\Documents\\harry\\BRS2\\app\\ocr\\files\\43-1.xlsx"
r = extract_images(path=path)

path='C:\\Users\\PC\\Desktop\\nithin-test\\43-1\\43-1-07.jpg'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

'''
def extract_text(r,path):    
    text=pytesseract.image_to_string(Image.open(path))
    names = extract_names(text)
    ages = extract_ages(text)
    guardians = extract_guardians(text)
    house_nos = extract_house_no(text)
    genders = extract_gender(text)
    epics = extract_epics(text)

def extract_names(text):
    name = "Name:" 
    name_after = [] 
    lines = text.split("\n")
    for line in lines:
        if name in line:
            words = line.split()
            string_index = words.index(name)
            name_after.append(words[string_index + 1])
    print(name_after)
    return name_after

def extract_ages(text):
    age = "Age:" 
    age_after = [] 
    lines = text.split("\n")

    for line in lines:
        if age in line:
            words = line.split()
            string_index = words.index(age)
            age_after.append(words[string_index + 1])
    print(age_after)
    return age_after

def extract_guardians(text):
    f= "Father's Name:"
    h= "Husband's Name"
    guardian = {}
    lines = text.split("\n")
    for line in lines:
        if f in line:
            a = re.search(r'\b(Father\'s Name:)\b', line)
            line = line[a.end()+1:]
            words = line.split()
            for i in words:
                if i!= '':
                    guardian.update({'father':i})
                    break
            continue
        if h in line:
            a = re.search(r'\b(Husband\'s Name:)\b', line)
            line = line[a.end()+1:]
            words = line.split()
            for i in words:
                if i!= '':
                    guardian.update({'husband':i})
                    break
            continue
    return guardian

def extract_house_no(text):
    nos = []
    name = "House Number:"
    lines = text.split("\n")
    for line in lines:
        if name in line:
            words = line.split()
            a = re.search(r'\b(House Number:)\b', line)
            line = line[a.end()+1:]
            words = line.split()
            for i in words:
                if i!= '':
                    nos.append(i)
                    break
            continue
    print(nos)
    return nos

def extract_gender(text):
    name = "Gender:" 
    genders = [] 
    lines = text.split("\n")
    for line in lines:
        if name in line:
            words = line.split()
            string_index = words.index(name)
            genders.append(words[string_index + 1])
    print(genders)
    return genders

def extract_epics(text):
    epics = []
    return epics

'''

def extract_fields(path,page):
    text=pytesseract.image_to_string(Image.open(path))
    all_words = re.split(', [;:*|]}= @_ __ L_>\n', text)
    names, guardians, house_nos, ages, epics, genders = [[],[],[],[],[],[]]
    for i in range(all_words):
        j = all_words[i]
        
        # Name
        if j == "Name":
            name = ''
            for k in (i+1,i+2,i+2):
                d = all_words[k]
                if "Father" in d or "Husband" in d:
                    break
                name = name+' '+d
            names.append(name.strip())
            continue
        
        # Guardian
        elif j == "Father's" or j == "Husband's":
            guardian = ['','']
            if j.strip()[0]=="F":
                guardian[0] = "father"
            else:
                guardian[0] = "husband"
            for k in (i+2,i+3,i+4):
                d = all_words[k]
                if "Hous" in d:
                    break
                guardian[1] = guardian[1]+' '+d
            guardians.append(guardian)
            continue
        
        # House Number
        elif j == "House":
            house_no = all_words[i+2]
            house_nos.append(house_no)
            continue
        
        #Age
        elif j == "Age":
            age = all_words[i+1]
            ages.append(age)
            continue
        
        elif j == "Gender":
            gender = all_words[i+1]
            genders.append(gender)
            continue
        
        # Epic Number
        elif len(j)==10:
            c = check_epic(j)
            if c:
                epic = c
                epics.append(epic)
    
    nl,gl,hl,al,el,gel = [len(names),len(guardians),len(house_nos),len(ages),len(epics),len(genders)]
    if nl == gl and hl==gl and al==hl and el==al and gel==el:
        msg = f"Missing in page no. {page}"
    else:
        msg = "Perfect!"
    
    res = (names,guardians,house_nos, ages, epics,genders,msg)
    return res

def process_pdf(pdf_path):
    return True


alphabets = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')
def check_epic(number):
    if len(number)!=10:
        return False
    try:
        a, b, c = [number[0],number[1],number[2]]
        if a in alphabets and b in alphabets and c in alphabets and number[3] not in alphabets:
            return number
    except:
        return False
    
#df = pd.DataFrame({'Name': e_name, 'Age': e_age})
#df.to_excel('excel2.xlsx', index=False)