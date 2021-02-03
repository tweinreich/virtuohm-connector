import mechanicalsoup
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import argparse
import maskpass
import math
from tabulate import tabulate
from pathlib import Path


browser = mechanicalsoup.StatefulBrowser()

def table_to_dataframe(table):
    return pd.read_html(str(table))[0]

def interpret_current_grades(dataframe):
    dataframe['Note'] = dataframe['Note'].apply(lambda x: float(x)/10.0 if '?' not in x else x)
    return dataframe['Note']

def interpret_all_grades(dataframe):
    dataframe['Note'] = dataframe['Note'].apply(lambda x: x/10.0 if type(x) is float else x)
    dataframe['Note'] = dataframe['Note'].apply(lambda x: round(x/10.0, 2) if type(x) is float and x > 6 else x)
    return dataframe

def remove_nan(dataframe):
    return dataframe.replace(to_replace=np.NaN, value='', regex=True)

def dataframe_to_csv_file(dataframe, filename):
    dataframe.to_csv(Path("./" + filename), index=True)

def dataframe_to_html_file(dataframe, filename):
    dataframe.to_html(Path("./" + filename))

def prettify_html(filename):
    content = Path("./" + filename).read_text()
    soup = BeautifulSoup(content, features='lxml')
    css = soup.new_tag('link')
    css['rel'] = 'stylesheet'
    css['href'] = './mvp.css'
    head = soup.new_tag('head')
    head.insert(1, css)
    html = soup.find('html')
    html.insert(1, head)
    with open(Path("./" + filename), 'w') as f: f.write(soup.prettify(formatter='html'))

def print_all_grades(url):
    content = browser.follow_link(link=url)
    table = content.soup.find('table')
    dataframe = table_to_dataframe(table)
    dataframe = interpret_all_grades(dataframe)
    dataframe = remove_nan(dataframe)
    print("\n\nAll Grades\n")
    print(tabulate(dataframe, showindex=False, headers='keys'))
    dataframe_to_csv_file(dataframe, 'all-grades.csv')
    dataframe_to_html_file(dataframe, 'all-grades.html')
    prettify_html('all-grades.html')
    without_total = dataframe.iloc[0:len(dataframe)-1]
    ects_sum = without_total['ECTS'].sum()
    print("\n\nReal Current ECTS Count: " + str(ects_sum))
    print("\nYou finished {percentage_finished}% of your studies".format(percentage_finished=math.floor(ects_sum/(210.0/100))))

def print_current_semester_grades(url):
    content = browser.follow_link(link=url)
    table = content.soup.find('table')
    dataframe = table_to_dataframe(table)
    dataframe['Note'] = interpret_current_grades(dataframe)
    dataframe = dataframe.loc[:, ~dataframe.columns.str.contains('^Unnamed')]
    print("\n\nCurrent Semester Grades\n")
    print(tabulate(dataframe, showindex=False, headers='keys'))
    dataframe_to_csv_file(dataframe, 'current-grades.csv')
    dataframe_to_html_file(dataframe, 'current-grades.html')
    prettify_html('current-grades.html')

def login(user, password):
    browser.open(url)
    browser.select_form('form[action="/pls/portal/portal.authorisation"]')
    browser["in_username"] = user
    browser["in_password"] = password
    browser.submit_selected()
    meta = browser.page.find("meta")
    token_url = meta['content'][6:]
    response = browser.open(base_url + token_url)


# Credentials
parser = argparse.ArgumentParser(description='Login to VirtuOhm')
parser.add_argument("username", help='Your VirtuOhm username')
args = parser.parse_args()
args.password = maskpass.askpass()

# Configuration
user = args.username
password = args.password
base_url = 'https://virtuohm.ohmportal.de'
url = base_url + '/pls/portal/'

login(user, password)

# Collect URLs
all_grades_url = browser.links(url_regex='study_certificate')[0]
current_grades_url = browser.links(url_regex='exammarks')[0]
logout_url = browser.links(url_regex='abmelden')[0]

# Collect Data
print_current_semester_grades(current_grades_url)
print_all_grades(all_grades_url)

browser.follow_link(link=logout_url)
browser.close()
