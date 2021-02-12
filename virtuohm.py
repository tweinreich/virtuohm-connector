import math
from dearpygui.core import *
from dearpygui.simple import *
from pathlib import Path

import browser_helper as bh
import dataframe_operator as do
import pandas as pd

base_url = 'https://virtuohm.ohmportal.de'
portal_url = base_url + '/pls/portal/'
semester_grades = pd.DataFrame()
all_grades = pd.DataFrame()


def interpret_current_grades(dataframe):
    dataframe['Note'] = dataframe['Note'].apply(lambda x: float(x) / 10.0 if '?' not in x else x)
    return dataframe['Note']


def interpret_all_grades(dataframe):
    dataframe['Note'] = dataframe['Note'].apply(lambda x: x / 10.0 if type(x) is float else x)
    dataframe['Note'] = dataframe['Note'].apply(lambda x: round(x / 10.0, 2) if type(x) is float and x > 6 else x)
    return dataframe


def calculate_current_credits(dataframe):
    without_total = dataframe.iloc[0:len(dataframe) - 1]
    return without_total['ECTS'].sum()


def login(browser, user, password):
    """Uses the provided credentials to log into VirtuOhm"""
    browser.open(portal_url)
    browser.select_form('form[action="/pls/portal/portal.authorisation"]')
    browser["in_username"] = user
    browser["in_password"] = password
    browser.submit_selected()
    browser.open(base_url + get_sessions_token_url(browser))
    return bh.logout_link_present(browser)


def get_sessions_token_url(browser):
    meta = browser.page.find("meta")
    token_url = meta['content'][6:]
    return token_url


def get_user_real_name(browser):
    page = browser.page
    greeting = page.find(
        lambda tag: tag.name == 'h4' and 'Willkommen' in tag.text
    ).getText()
    name_parts = greeting.split('-')[0].split()[2:]
    name = ''
    for part in name_parts:
        name += part + ' '
    return name


def close_export_finished_window(sender, data):
    log_debug(sender)
    log_debug(data)
    delete_elements(['File Saved'])


def close_export_failed_window(sender, data):
    log_debug(sender)
    log_debug(data)
    delete_elements(['Error saving file!'])


def position_export_error_window(sender, data):
    log_debug(sender)
    log_debug(data)
    if does_item_exist('Error saving file!'):
        main_width = get_item_width('Main Window')
        main_height = get_item_height('Main Window')
        login_width = get_item_width('Error saving file!')
        login_height = get_item_height('Error saving file!')
        set_window_pos('Error saving file!', int((main_width / 2 - login_width / 2)),
                       int((main_height / 2 - login_height / 2)))
    else:
        # this replaces the callback with None so we dont waste resources running the login window position callback
        set_render_callback(None)


def position_export_window(sender, data):
    log_debug(sender)
    log_debug(data)
    if does_item_exist('File Saved'):
        main_width = get_item_width('Main Window')
        main_height = get_item_height('Main Window')
        login_width = get_item_width('File Saved')
        login_height = get_item_height('File Saved')
        set_window_pos('File Saved', int((main_width / 2 - login_width / 2)),
                       int((main_height / 2 - login_height / 2)))
    else:
        # this replaces the callback with None so we dont waste resources running the login window position callback
        set_render_callback(None)


def export_finished(path):
    absolute_path = Path(path).resolve()
    with window('File Saved', autosize=True, no_resize=True):
        add_text('Your export has been saved to: ' + str(absolute_path))
        add_button('Ok', callback=close_export_finished_window)
    set_render_callback(position_export_window)


def export_error():
    with window('Error saving file!', autosize=True, no_resize=True):
        add_text('There was an error saving your file.')
        add_button('Ok', callback=close_export_failed_window)


def file_export_csv(sender, data):
    log_debug(sender)
    log_debug(data)
    if sender == 'Export Semester Grades to CSV':
        filename = 'semester-grades'
        result = do.export_dataframe_to_csv(semester_grades, filename)
        if result:
            export_finished(filename + '.csv')
        else:
            export_error()
    elif sender == 'Export All Grades to CSV':
        filename = 'all-grades'
        result = do.export_dataframe_to_csv(all_grades, filename)
        if result:
            export_finished(filename + '.csv')
        else:
            export_error()


def file_export_html(sender, data):
    log_debug(sender)
    log_debug(data)
    if sender == 'Export Semester Grades to HTML':
        filename = 'semester-grades'
        result = do.export_dataframe_to_html(semester_grades, filename)
        if result:
            export_finished(filename + '.html')
        else:
            export_error()
    elif sender == 'Export All Grades to HTML':
        filename = 'all-grades'
        result = do.export_dataframe_to_html(all_grades, filename)
        if result:
            export_finished(filename + '.html')
        else:
            export_error()


def get_semester_grades(browser, url):
    content = browser.follow_link(link=url)
    table = content.soup.find('table')
    dataframe = do.table_to_dataframe(table)
    dataframe['Note'] = interpret_current_grades(dataframe)
    dataframe = dataframe.loc[:, ~dataframe.columns.str.contains('^Unnamed')]

    global semester_grades
    semester_grades = dataframe

    delete_elements(['all-grades'])

    with group('semester', parent='Main Window'):
        add_dummy(parent='semester', height=10)
        add_table("Table##semester",
                  ["Module", "Type", "Grade"],
                  parent="semester",
                  show=True)
        set_table_data("Table##semester", do.dataframe_to_gui_table(dataframe))
        add_button('Export Semester Grades to CSV',
                   callback=file_export_csv,
                   parent="semester",
                   tip='Saves your grades to CSV')
        add_same_line(parent="semester")
        add_button('Export Semester Grades to HTML',
                   callback=file_export_html,
                   parent="semester",
                   tip='Saves your grades to HTML')


def get_all_grades(browser, url):
    content = browser.follow_link(link=url)
    table = content.soup.find('table')
    dataframe = do.table_to_dataframe(table)
    dataframe = interpret_all_grades(dataframe)
    dataframe = do.remove_nan(dataframe)

    global all_grades
    all_grades = dataframe

    credits_total = calculate_current_credits(dataframe)
    finished_percentage = math.floor(credits_total / (210.0 / 100))
    finished_percentage_float = math.floor((finished_percentage / 100.0) * 10) / 10

    delete_elements(['semester'])

    with group('all-grades', parent="Main Window"):
        add_dummy(parent="all-grades", height=10)
        add_table("Table##all",
                  ["PNr", "Exam", "Stat", "Grade", "ECTS", "SWS", "Note", "Recognition", "Semester"],
                  parent="all-grades",
                  height=400,
                  show=True)
        add_button('Export All Grades to CSV',
                   callback=file_export_csv,
                   parent="all-grades",
                   tip='Saves your grades to CSV')
        add_same_line(parent="all-grades")
        add_button('Export All Grades to HTML',
                   callback=file_export_html,
                   parent="all-grades",
                   tip='Saves your grades to HTML')
        add_dummy(parent="all-grades", height=10)
        add_text("Credits: " + str(credits_total),
                 tip='Calculated total including current achievements',
                 parent="all-grades")
        add_dummy(parent="all-grades", height=10)
        add_text('Study Progress', parent='all-grades')
        add_same_line(parent="all-grades")
        add_progress_bar("study-progress",
                         overlay=str(finished_percentage) + '%',
                         parent="all-grades")
        set_value("study-progress", finished_percentage_float)
        set_table_data("Table##all", do.dataframe_to_gui_table(dataframe))


def delete_elements(elements_to_delete):
    """Check for several widgets presence before deleting them if they are shown"""
    for name in elements_to_delete:
        shown = is_item_shown(name)
        if shown:
            delete_item(name)


def file_export(sender, data):
    log_debug(sender)
    log_debug(data)
    if sender == 'Export Semester Grades to Files':
        do.export_dataframe_to_files(semester_grades, 'semester-grades')
    elif sender == 'Export All Grades to Files':
        do.export_dataframe_to_files(all_grades, 'all-grades')
