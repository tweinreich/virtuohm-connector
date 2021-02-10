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
semester_grades = pd.DataFrame()
all_grades = pd.DataFrame()
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
    path = Path("./" + filename)
    print('File saved to path: ')
    print(path.absolute())
    dataframe.to_csv(path, index=True)


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
    # export_dataframe_to_files(dataframe, 'all-grades')

    global all_grades
    all_grades = dataframe

    # TODO: Move this somewhere else
    # without_total = dataframe.iloc[0:len(dataframe) - 1]
    # ects_sum = without_total['ECTS'].sum()
    # print("\n\nReal Current ECTS Count: " + str(ects_sum))
    # print("\nYou finished {percentage_finished}% of your studies".format(
    #     percentage_finished=math.floor(ects_sum / (210.0 / 100))))

    add_table("Table##all", ["", "PNr", "Exam", "Stat", "Grade", "ECTS", "SWS", "Note", "Recognition", "Semester"],
              parent="Main Window", height=600)
    set_table_data("Table##all", dataframe_to_gui_table(dataframe))
    add_button('Export All Grades to Files',
               callback=file_export,
               parent="Main Window", tip='Saves your grades to CSV and HTML')


def dataframe_to_gui_table(dataframe):
    """Transforms a pandas dataframe into an array that can be used by Dear PyGUI"""
    index = dataframe.index
    rows = len(index)
    cols = len(dataframe.columns)
    tabledata = []
    for i in range(0, rows):
        row = []
        for j in range(0, cols):
            row.append(dataframe.iat[i, j])
        tabledata.append(row)
    return tabledata


def export_dataframe_to_files(dataframe, filename):
    """Writes a dataframe to CSV and prettified HTML"""
    dataframe_to_csv_file(dataframe, filename + '.csv')
    dataframe_to_html_file(dataframe, filename + '.html')
    prettify_html(filename + '.html')


def file_export(sender, data):
    print('sender:')
    print(sender)
    print(data)
    if sender == 'Export Semester Grades to Files':
        export_dataframe_to_files(semester_grades, 'semester-grades')
    elif sender == 'Export All Grades to Files':
        export_dataframe_to_files(all_grades, 'all-grades')


def get_semester_grades(url):
    content = browser.follow_link(link=url)
    table = content.soup.find('table')
    dataframe = table_to_dataframe(table)
    dataframe['Note'] = interpret_current_grades(dataframe)
    dataframe = dataframe.loc[:, ~dataframe.columns.str.contains('^Unnamed')]

    global semester_grades
    semester_grades = dataframe

    add_table("Table##semester", ["Module", "Type", "Grade"], parent="Main Window")
    set_table_data("Table##semester", dataframe_to_gui_table(dataframe))
    add_button('Export Semester Grades to Files',
               callback=file_export,
               parent="Main Window", tip='Saves your grades to CSV and HTML')


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
    add_same_line(parent="Main Window")
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
