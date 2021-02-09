import mechanicalsoup
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import math
from tabulate import tabulate
from pathlib import Path
from dearpygui.core import *
from dearpygui.simple import *

base_url = 'https://virtuohm.ohmportal.de'
url = base_url + '/pls/portal/'
links = {}
browser = mechanicalsoup.StatefulBrowser()


def table_to_dataframe(table):
    return pd.read_html(str(table))[0]


def interpret_current_grades(dataframe):
    dataframe['Note'] = dataframe['Note'].apply(lambda x: float(x) / 10.0 if '?' not in x else x)
    return dataframe['Note']


def interpret_all_grades(dataframe):
    dataframe['Note'] = dataframe['Note'].apply(lambda x: x / 10.0 if type(x) is float else x)
    dataframe['Note'] = dataframe['Note'].apply(lambda x: round(x / 10.0, 2) if type(x) is float and x > 6 else x)
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


def get_all_grades(url):
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
    without_total = dataframe.iloc[0:len(dataframe) - 1]
    ects_sum = without_total['ECTS'].sum()
    print("\n\nReal Current ECTS Count: " + str(ects_sum))
    print("\nYou finished {percentage_finished}% of your studies".format(
        percentage_finished=math.floor(ects_sum / (210.0 / 100))))


def get_semester_grades(url):
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
    add_table("Table##widget", ["Column 1", "Column 2", "Column 3"], parent="Main Window")
    print('dataframe')
    print(dataframe)
    print('dataframe.values')
    print(dataframe.values)
    set_table_data("Table##widget", dataframe.values)


def logout_link_present():
    page = browser.page
    logout_link = page.select('a[href="portal.abmelden"]')
    if len(logout_link) > 0:
        return True
    else:
        return False


def login(user, password):
    browser.open(url)
    browser.select_form('form[action="/pls/portal/portal.authorisation"]')
    browser["in_username"] = user
    browser["in_password"] = password
    browser.submit_selected()
    meta = browser.page.find("meta")
    token_url = meta['content'][6:]
    response = browser.open(base_url + token_url)
    return logout_link_present()


def recursively_show(container):
    for item in get_item_children(container):
        if get_item_children(item):
            show_item(item)
            recursively_show(item)
        else:
            show_item(item)


def download_current(sender, data):
    get_semester_grades(links['semester_grades'])


def download_all(sender, data):
    get_all_grades(links['all_grades'])


def show_actions():
    add_text("You are now logged in.", parent="Main Window")
    add_button('Semester Grades', callback=download_current, parent="Main Window")
    add_button('All Grades', callback=download_all, parent="Main Window")


def collect_links():
    """Get all interesting links from the entry site"""
    links['all_grades'] = browser.links(url_regex='study_certificate')[0]
    links['semester_grades'] = browser.links(url_regex='exammarks')[0]
    links['logout'] = browser.links(url_regex='abmelden')[0]


def try_login(sender, data):
    print('sender: ' + sender)
    print('data: ')
    print(data)
    password = get_value('Password')
    user = get_value('User')
    if password and user:
        login_valid = login(user, password)
        print('login valid:')
        print(login_valid)
        if login_valid:
            delete_item('Login Window')
            recursively_show('Main Window')
            collect_links()
            show_actions()
        else:
            add_text('Incorrect Credentials!', color=[255, 0, 0], parent='Login Window')
    else:
        show_item('You have to enter a username and a password!')


def position_login_window(sender, data):
    if does_item_exist('Login Window'):
        main_width = get_item_width('Main Window')
        main_height = get_item_height('Main Window')
        login_width = get_item_width('Login Window')
        login_height = get_item_height('Login Window')
        set_window_pos('Login Window', int((main_width / 2 - login_width / 2)),
                       int((main_height / 2 - login_height / 2)))
    else:
        # this replaces the callback with None so we dont waste resources running the login window position callback
        set_render_callback(None)


with window('Login Window', no_title_bar=True, autosize=True, no_resize=True):
    add_input_text('User',
                   hint='first part of your email',
                   on_enter=True,
                   callback=try_login,
                   tip='Will not be saved')
    add_input_text('Password',
                   hint='VirtuOhm password',
                   password=True,
                   on_enter=True,
                   callback=try_login,
                   tip='Will not be saved')
    add_button('Try Login', callback=try_login)
    add_text('Incorrect Credentials.', color=[255, 0, 0], parent='Login Window')
    hide_item('Incorrect Credentials.')
    set_render_callback(position_login_window)


with window("Main Window"):
    add_text("Use this tool to access and download your data from VirtuOhm.")


start_dearpygui(primary_window="Main Window")
browser.close()
