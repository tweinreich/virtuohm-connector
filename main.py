import mechanicalsoup
from dearpygui.core import *
from dearpygui.simple import *
import virtuohm as vo


links = {}
browser = mechanicalsoup.StatefulBrowser()


def delete_elements(elements_to_delete):
    """Check for several widgets presence before deleting them if they are shown"""
    for name in elements_to_delete:
        shown = is_item_shown(name)
        if shown:
            delete_item(name)


def recursively_show(container):
    for item in get_item_children(container):
        if get_item_children(item):
            show_item(item)
            recursively_show(item)
        else:
            show_item(item)


def download_semester_grades(sender, data):
    log_debug(sender)
    log_debug(data)
    vo.get_semester_grades(browser, links['semester_grades'])


def download_all_grades(sender, data):
    log_debug(sender)
    log_debug(data)
    vo.get_all_grades(browser, links['all_grades'])


def show_user_actions():
    """After successful login these actions can be performed within VirtuOhm"""
    add_dummy(parent="Main Window")
    add_text("You are now logged in.", parent="Main Window")
    add_dummy(parent="Main Window")
    add_button('Semester Grades',
               callback=download_semester_grades,
               parent="Main Window")
    add_same_line(parent="Main Window")
    add_button('All Grades',
               callback=download_all_grades,
               parent="Main Window")


def collect_links():
    """Get all interesting links from the entry site"""
    links['all_grades'] = browser.links(url_regex='study_certificate')[0]
    links['semester_grades'] = browser.links(url_regex='exammarks')[0]
    links['logout'] = browser.links(url_regex='abmelden')[0]


def try_login(sender, data):
    log_debug(sender)
    log_debug(data)
    password = get_value('Password')
    user = get_value('User')
    if password and user:
        login_valid = vo.login(browser, user, password)
        if login_valid:
            delete_item('Login Window')
            recursively_show('Main Window')
            collect_links()
            show_user_actions()
        else:
            add_text('Incorrect Credentials!', color=[255, 0, 0], parent='Login Window')
    else:
        show_item('You have to enter a username and a password!')


def position_login_window(sender, data):
    log_debug(sender)
    log_debug(data)
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

# Activate logging
# show_logger()
start_dearpygui(primary_window="Main Window")
browser.close()
