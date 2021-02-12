def logout_link_present(browser):
    """Crude way to check for valid login on our side"""
    page = browser.page
    logout_link = page.select('a[href="portal.abmelden"]')
    if len(logout_link) > 0:
        return True
    else:
        return False
