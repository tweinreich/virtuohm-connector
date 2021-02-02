import mechanicalsoup
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import maskpass


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
browser = mechanicalsoup.StatefulBrowser()

# Login
browser.open(url)
browser.select_form('form[action="/pls/portal/portal.authorisation"]')
browser["in_username"] = user 
browser["in_password"] = password
browser.submit_selected()
meta = browser.page.find("meta")
token_url = meta['content'][6:]
response = browser.open(base_url + token_url)

# Current Grades
current_grades_link = browser.links(url_regex='exammarks')[0]
current_grades_content = browser.follow_link(link=current_grades_link)
table = current_grades_content.soup.find('table')
df = pd.read_html(str(table))[0]
df['Note'] = df['Note'].apply(lambda x: float(x)/10.0 if '?' not in x else x)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
print("\n\nCurrent Grades\n")
print(df)

page = browser.page 
links = browser.links()


browser.close()
