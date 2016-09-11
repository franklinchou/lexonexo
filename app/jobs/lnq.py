"""
Design pattern using function decorators abandoned, 22 FEB 2016.
Resorting to procedural type design pattern.

Refactored for task automation, 02 JUL 2016.

Franklin Chou
"""

import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# from ..models import User

#------------------------------------------------------------------------------
# Automated task queue
#------------------------------------------------------------------------------
from celery import Task,\
    states
from celery.exceptions import Ignore
from .. import celery

@celery.task(name='app.jobs.lnq.query')
def daily_query():
    print('2+2')

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Login specific CSS selectors
#------------------------------------------------------------------------------
user_id         = 'userid'
password_id     = 'password'
submit_id       = 'signInSbmtBtn'
#------------------------------------------------------------------------------

lnq_config = {
    'LEXIS_BASE_URL'        : 'https://advance.lexis.com',
    'LEXIS_LOGIN_TARGET'    : 'https://signin.lexisnexis.com/lnaccess/app/signin/aci/la',
    'LEXIS_QUERY'           : '88 NJ 529',
    # 'LEXIS_VAULT_KEY'       : os.environ.get('LEXIS_VAULT_KEY')
}

# Set to 1 for debugging purposes, else set to 0
MODE = 0

class Lnq(Task):

    def force(self, la_username, la_password):
        self.la_username = la_username
        self.la_password = la_password

        self.launch_webdriver(MODE)
        try:
            self.login()
            self.query()
            self.destroy()
        except NoSuchElementException:
            self.update_state(
                state = states.FAILURE,
                meta = 'FAILED TO COMPLETE QUERY'
            )
            raise Ignore()

    def run(self, la_username, la_password, *args, **kwargs):
        '''
            Accepts Lexis Advance username & password.
        '''
        self.la_username = la_username
        self.la_password = la_password

        self.launch_webdriver(MODE)

        try:
            self.login()
            # self.overlay()
            self.query()
            self.destroy()
        except NoSuchElementException:
            self.update_state(
                state = states.FAILURE,
                meta = 'FAILED TO COMPLETE QUERY'
            )
            raise Ignore()

    def launch_webdriver(self, mode):
        from config import basedir as proj_dir

        self.wd = webdriver.PhantomJS(
            service_args = [
                '--ssl-protocol=any',
                '--ignore-ssl-errors=true'
            ],
            service_log_path = os.path.join(proj_dir, 'var', 'ghostdriver', 'ghostdriver.log')
        )

        if mode == 1:
            self.wd = webdriver.Chrome()

        self.wd.set_window_size(1600, 900)

        self.login_target = lnq_config['LEXIS_LOGIN_TARGET']
        self.base_target  = lnq_config['LEXIS_BASE_URL']

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
            raise NoSuchElementException

        user_field.send_keys(self.la_username)
        pwd_field.send_keys(self.la_password)

        submit_btn.click()

#------------------------------------------------------------------------------
    # Overlay detection

    # The need to deal w/overlay has been obviated (by using phantomjs);
    #   `query()` will directly interact w/the search submit element.
#------------------------------------------------------------------------------
    def overlay(self):

        overlay_xpath = "//aside[@role='dialog']"
        overlay_close = "//input[@value='Close']"

        try:
            la_overlay = self.wd.find_element_by_xpath()
            la_overlay_close = self.wd.find_element_by_xpath()
        except NoSuchElementException:
            raise NoSuchElementException

        if (la_overlay is not None):
            la_overlay_close.click()

        # verify click success
#------------------------------------------------------------------------------

    def query(self):

#------------------------------------------------------------------------------
        # Post login verification selectors
#------------------------------------------------------------------------------
        adv_search_xpath = "//button[@type='button' and normalize-space(text()) = 'Advanced Search']"

        searchbar_id = 'searchTerms'
#------------------------------------------------------------------------------

        try:
            self.wd.find_element_by_xpath(adv_search_xpath)
        except NoSuchElementException:
            raise NoSuchElementException

        try:
            searchbar = self.wd.find_element_by_id(searchbar_id)
        except NoSuchElementException:
            raise NoSuchElementException
        else:
            searchbar.send_keys(lnq_config['LEXIS_QUERY'])

        try:
            self.wd.execute_async_script("document.getElementById('mainSearch').click()")
        except:
            raise NoSuchElementException

    def destroy(self):
        # self.wd.save_screenshot('out.png')
        self.wd.quit()


class VerifyRunner(Lnq):

    # VerifyRunner accepts plaintext LA username & password for use
    # on registration.

    def run(self, la_username, la_password, *args, **kwargs):
        self.la_username = la_username
        self.la_password = la_password
        super().launch_webdriver(MODE)
        self.verify()

    def verify(self):
        super().login()
