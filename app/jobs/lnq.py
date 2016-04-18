"""
Design pattern using function decorators abandoned, 22 FEB 2016.
Resorting to procedural type design pattern.
Mark for refactor.

Franklin Chou
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from flask import current_app

from ..models import User

#------------------------------------------------------------------------------
# Login specific CSS selectors
#------------------------------------------------------------------------------

user_id         = 'userid'
password_id     = 'password'
submit_id       = 'signInSbmtBtn'

#------------------------------------------------------------------------------

class Lnq(object):

    def __init__(self, la_username, la_password):

        from config import basedir as proj_dir
        import os

        self.la_username = la_username
        self.la_password = la_password

        self.wd = webdriver.PhantomJS(
            service_log_path = os.path.join(proj_dir, 'var', 'ghostdriver'),
            service_args = [
                '--ssl-protocol=any',
                '--ignore-ssl-errors=true'
            ]
        )

        # self.wd = webdriver.Chrome()

        self.wd.set_window_size(1600, 900)

        self.login_passed = False

        self.login_target = current_app.config['LEXIS_LOGIN_TARGET']
        self.base_target  = current_app.config['LEXIS_BASE_URL']

        self.passed = False

    def __enter__(self):

        # Land webdriver on Lexis webpage

        if (self.wd.current_url != self.login_target.strip("\'")):
           self.wd.get(self.base_target)

        return self

    def login(self):

        try:
            user_field  = self.wd.find_element_by_id(user_id)
            pwd_field   = self.wd.find_element_by_id(password_id)
            submit_btn  = self.wd.find_element_by_id(submit_id)
        except NoSuchElementException:
            pass

        user_field.send_keys(self.la_username)

#------------------------------------------------------------------------------
        # Decrypt and enter user's LA password
#------------------------------------------------------------------------------

        user = User.query.filter_by(la_username=self.la_username).first()
        if user is not None:
            pwd_field.send_keys(user.use_la_password().decode('ascii'))

#------------------------------------------------------------------------------

        submit_btn.click()

        if (self.login_target in self.wd.current_url):
            self.login_passed = True

    def overlay(self):

        # The need to deal with the overlay is obviated; `query()` will
        # directly interact with the search submit element.

#------------------------------------------------------------------------------
        # Overlay detection
#------------------------------------------------------------------------------

        overlay_xpath = "//aside[@role='dialog']"
        overlay_close = "//input[@value='Close']"

#------------------------------------------------------------------------------

        try:
            la_overlay = self.wd.find_element_by_xpath()
            la_overlay_close = self.wd.find_element_by_xpath()
        except NoSuchElementException:
            pass

        if (la_overlay is not None):
            la_overlay_close.click()

        # verify click success

    def query(self):

#------------------------------------------------------------------------------
        # Post login verification selectors
#------------------------------------------------------------------------------

        # Unicode `registered` sign following Advance?
        header_xpath = "h2[@class='pagewrapper' and normalize-space(text())='Lexis Advance Home']"

        searchbar_id = 'searchTerms'

#------------------------------------------------------------------------------

        try:
            # self.wd.find_element_by_xpath(header_xpath)
            pass
        except NoSuchElementException:
            pass

        try:
            searchbar = self.wd.find_element_by_id(searchbar_id)
        except NoSuchElementException:
            pass
        else:
            searchbar.send_keys(current_app.config['LEXIS_QUERY'])

        try:
            self.wd.execute_async_script("document.getElementById('mainSearch').click()")
        except:
            pass

        self.passed = True
        # return self.passed

#------------------------------------------------------------------------------
    # Access point
#------------------------------------------------------------------------------
    def login_query(self):
        self.login()
        self.query()
#------------------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        # self.wd.save_screenshot('out.png')
        self.wd.quit()

class VerifyRunner(Lnq):

    # VerifyRunner accepts plaintext LA username & password for use
    # on registration.

    def __init__(self, la_username, la_password):
        super().__init__(la_username, la_password)

    def verify(self):

        # This duplicates much of the functionality found in the super class's
        # `login()` function; should mark for refactor.

        try:
            user_field  = self.wd.find_element_by_id(user_id)
            pwd_field   = self.wd.find_element_by_id(password_id)
            submit_btn  = self.wd.find_element_by_id(submit_id)
        except NoSuchElementException:
            pass

        user_field.send_keys(self.la_username)
        pwd_field.send_keys(self.la_password)
        submit_btn.click()

        if (self.base_target in self.wd.current_url):
            self.login_passed = True
        else:
            raise Exception
