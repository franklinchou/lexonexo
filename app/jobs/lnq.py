"""
Design pattern using function decorators abandoned, 22 FEB 2016.
Resorting to procedural type design pattern.
Mark for refactor.

Refactored for task automation, 02 JUL 2016.

Franklin Chou
"""

import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from ..models import User

#------------------------------------------------------------------------------
# Automated task queue
#------------------------------------------------------------------------------
# from app import celery
from celery import Celery
from celery import Task
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Login specific CSS selectors
#------------------------------------------------------------------------------
user_id         = 'userid'
password_id     = 'password'
submit_id       = 'signInSbmtBtn'
#------------------------------------------------------------------------------

celery = Celery('tasks', broker='redis://localhost:6379')

lnq_config = {
    'LEXIS_BASE_URL'        : 'https://advance.lexis.com',
    'LEXIS_LOGIN_TARGET'    : 'https://signin.lexisnexis.com/lnaccess/app/signin/aci/la',
    'LEXIS_QUERY'           : '88 NJ 529',
    # 'LEXIS_VAULT_KEY'       : os.environ.get('LEXIS_VAULT_KEY')
}

class Lnq(Task):

    def force(self, la_username, la_password):
        self.la_username = la_username
        self.la_password = la_password
        self.launch_webdriver()
        self.login()
        self.query()
        self.destroy()

    def run(self, la_username, la_password, *args, **kwargs):
        '''
            Accepts Lexis Advance username & password.
            Decryption/decode to be done by calling function.
        '''
        self.la_username = la_username
        self.la_password = la_password

        self.launch_webdriver()
        self.login()
        # self.overlay()
        self.query()
        self.destroy()

    def launch_webdriver(self):
        from config import basedir as proj_dir
        self.wd = webdriver.PhantomJS(
            service_args = [
                '--ssl-protocol=any',
                '--ignore-ssl-errors=true'
            ],
            service_log_path = os.path.join(proj_dir, 'var', 'ghostdriver', 'ghostdriver.log')
        )

        # self.wd = webdriver.Chrome()

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
            pass

        user_field.send_keys(self.la_username)
        pwd_field.send_keys(self.la_password)

        submit_btn.click()

        if (lnq_config['LEXIS_LOGIN_TARGET'] in self.wd.current_url):
            pass
        else:
            pass
            # raise Exception


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
            pass

        if (la_overlay is not None):
            la_overlay_close.click()

        # verify click success
#------------------------------------------------------------------------------

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
            searchbar.send_keys(lnq_config['LEXIS_QUERY'])

        try:
            self.wd.execute_async_script("document.getElementById('mainSearch').click()")
        except:
            pass

        self.passed = True
        # return self.passed

    def destroy(self):
        # self.wd.save_screenshot('out.png')
        self.wd.quit()


class VerifyRunner(Lnq):

    # VerifyRunner accepts plaintext LA username & password for use
    # on registration.

    def run(self, la_username, la_password, *args, **kwargs):
        self.la_username = la_username
        self.la_password = la_password
        super().launch_webdriver()
        self.verify()

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

        if(lnq_config['LEXIS_BASE_URL'] in self.wd.current_url):
            self.login_passed = True
        else:
            raise Exception
            # return False
