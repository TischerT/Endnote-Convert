import re
import requests
import random
from bs4 import BeautifulSoup


# iterations for random search
iterations = 20

# output file, name can be changed here
output_file = 'bibliography.txt'

# Put references in this file
ref_file = input("reference file name (e.g. references.txt):\n")

# code starts below
# define some variables
# pretend to be a firefox browser
SESSION = requests.Session()
SESSION.headers.update(
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})

URL_SEARCH = 'https://pubmed.ncbi.nlm.nih.gov/?sort=date&term={q}'
URL_CITE = 'https://pubmed.ncbi.nlm.nih.gov/{ident}/?format=pubmed'

skipped = 0
skipped_refs = ''
r = ''


# define functions
def http_get(url):
    r = SESSION.get(url)
    return BeautifulSoup(r.text, features="html.parser")

# split reference into authors, year and title


def split_reference(reference):
    r = reference
    left = ''
    right = ''
    year = ''
    # find (YEAR)
    regex = r'\(\d\d\d\d\)'
    match = re.search(regex, str(r))
    if match:
        year = str(match.group(0))
    else:
        # if not try to find YEAR
        regex = r'\d\d\d\d'
        match = re.search(regex, str(r))
        if match:
            year = str(match.group(0))
        else:
            return 'Error no YEAR found'
    # where is YEAR in reference? and how long is reference?
    pos_y = r.find(year)
    le = len(r)
    # if YEAR somewhere in the middle of reference, split into left-part YEAR right-part
    if (le - pos_y >= 15):
        left, right = r[:pos_y], r[pos_y+6:]
    # else split on 'et al' into left-part 'et al' right-part
    elif ((le - pos_y <= 15) and (r.find('et al')) != -1):
        rs = r.split('et al')
        left = rs[0]
        right = rs[1]
    # else find the third full-stop from the end and split there into left-part full-stop right-part
    else:
        rs = r.strip('.').rsplit('.', 2)
        left = rs[0]
        right = rs[1]

    # clean up
    right = right.replace(year, '')
    right = right.replace('  ', ' ')
    right = right.strip()
    left = left.replace('  ', ' ')
    left = left.strip()
    year = year.replace('(', '')
    year = year.replace(')', '')
    split_ref = [left, year, right]
    return split_ref

# last fallback if no search quesries find a reference: use random word combinations from the title


def choose_random(reference, leng=3):
    q = reference.split()
    i = 1
    r = []
    while i < 6:
        rand = random.randint(1, len(q)-1)
        if len(q[rand]) > leng:
            if (q[rand] in r):
                continue
            else:
                r.append(q[rand])
                r.append(' ')
                i += 1
    r = ''.join(r)
    return r

# search for Pubmed ID in results page


def get_articles(query):
    url = URL_SEARCH.format(q=query)
    soup = http_get(url)
    pubmed = ''
    for tag in soup.findAll(title="PubMed ID"):
        regex = r'\d+'
        match = re.search(regex, str(tag))
        if match:
            pubmed = str(match.group(0))
        else:
            return 'Error no Pubmed ID found'
    return pubmed

# use Pubmed ID to create URL and copy entry in NML format


def get_citations(ident, resolve=True):
    url = URL_CITE.format(ident=ident)
    soup = http_get(url)
    citations = ''
    for tag in soup.findAll(id="article-details"):
        citations = tag.string.strip()
    return citations


# main code
# open input and output fines
if(ref_file == ''):
    print('Please provide a file')
    quit()

references = open(ref_file, 'r', encoding='utf-8')
myFile = open(output_file, 'w', encoding='utf-8', errors='replace')


# loop through references line by line
for reference in references:
    reference = reference.strip()

    # covert to lower case and remove some special chars
    reference = reference.lower()
    reference = reference.replace('-', ' ')
    reference = reference.replace('/', ' ')
    reference = reference.replace(',', ' ')
    reference = reference.replace('%', ' ')
    reference = reference.replace('&', '')

    # skip empty lines
    if (reference == ''):
        continue

    print("\n---------------------------------------------------------")
    print("Doing reference:", reference)

    # split the reference into author, year, title
    query = split_reference(reference)
    q = []
    for i in query:
        i = i.replace('.', '')
        q.append(i)

    # find article by author and title
    r = get_articles(q[0] + ' ' + q[2])
    print("Query: " + q[0] + ' ' + q[2])

    # find article by author and year
    if len(r) == 0:
        r = get_articles(q[0] + ' ' + q[1])
        print("No results -- trying: " + q[0] + ' ' + q[1])

    # find article by year and title
    if len(r) == 0:
        r = get_articles(q[1] + ' ' + q[2])
        print("Still no results -- trying: " + q[1] + ' ' + q[2])

    # find article by author year and title
    if len(r) == 0:
        r = get_articles(q[0] + ' ' + q[1] + ' ' + q[2])
        print("Still no results -- trying: " + q[0] + ' ' + q[1] + ' ' + q[2])

    # find article by author year and random words from title
    if len(r) == 0:
        its = 0
        while its < iterations:
            q2 = choose_random(reference)
            print("Still no results -- trying again with random words: ", q[0] + q[1] + q2)
            r = get_articles(q[0] + ' ' + q[1] + ' ' + q2)
            if len(r) != 0:
                break
            its += 1

    if len(r) == 0:
        print("Still no results -- skipping")
        skipped += 1
        skipped_refs = skipped_refs + '\n' + reference
        continue
    print("Result written")
    myFile.write(get_citations(r) + '\n\n')

if skipped > 0:
    print("\n---------------------------------------------------------")
    print("Total number of results skipped: ", skipped)
    print("Please check the following references:\n", skipped_refs)
else:
    print("\n---------------------------------------------------------")
    print('Done')

myFile.close()
