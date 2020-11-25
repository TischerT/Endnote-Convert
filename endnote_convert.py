import re
from bs4 import BeautifulSoup

# HTM(L) full text file aka converted docx file
input_file = input("HTM(L) file name (e.g. myText.htm):\n")


def http_get(url):
    fp = open(url, 'r')
    return BeautifulSoup(fp, 'html.parser')


# this function does all the work
# find superscript numbers and convert them to endnote readable unformatted references
def replace_sup(file):
    for i in file.find_all('sup'):
        # single refs like 1 or 12
        regex1 = r'yes">(\,\s){0,1}(\d+)</span>'
        # a group of refs like 1, 2, 34
        regex2 = r'yes">((\d+\,\s)+(\d+))</span>'
        # range of refs like 1-4
        regex3 = r'yes">((\d+)(\-)(\d+))</span>'
        match1 = re.search(regex1, str(i), re.MULTILINE)
        match2 = re.search(regex2, str(i), re.MULTILINE)
        match3 = re.search(regex3, str(i), re.MULTILINE)
        if match1:
            m = str(match1.group(2))
            n_m = re.sub(r'(\d+)', '{#' + r'\1' + '}', m)
            n_m = n_m.replace(' ', '')
        elif match2:
            m = str(match2.group(1))
            n_m = re.sub(r'(\d+)', '{#' + r'\1' + '}', m)
            n_m = n_m.replace(', ', '')
        elif match3:
            m = str(match3.group(1))
            first = int(match3.group(2))
            last = int(match3.group(4))
            r = ''
            # fill in the range of refs, because endnote likes to have {#1}{#2}{#3}{#4}
            while (first <= last):
                a = '{#' + str(first) + '}'
                r = r + a
                first = int(first) + 1
            n_m = re.sub(r'(\d+)(\-)(\d+)', r, m)
        else:
            continue
        i.replace_with(n_m)
    return file


# main code
if(input_file == ''):
    print('Please provide a file')
else:
    soup = http_get(input_file)
    soup = replace_sup(soup)
    with open(input_file + "_modified.htm", "wb") as f_output:
        f_output.write(soup.prettify("utf-8"))
        print('References exchanged. Ready to open the modified HTM file in Microsoft Word.')
