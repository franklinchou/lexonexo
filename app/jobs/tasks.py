import os

from selenium import webdriver

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException,\
        TimeoutException


from celery import Celery

from .automation_exception import InvalidLanding
from .automation_exception import InvalidLogin

from datetime import datetime as DT
from datetime import timedelta

from app import db
from .. import models

from config import Config
from config import config

from socket import error as socket_error

# celery = Celery(__name__, broker='redis://localhost:6379/0')
celery = Celery(__name__, broker=config[os.environ.get('CONFIG').strip('\'')].REDIS_URL)
celery.config_from_object('app.celery_config')

lnq_config = {
    'LEXIS_BASE_URL'    : "https://advance.lexis.com",
    'LEXIS_LOGIN_TARGET': "https://signin.lexisnexis.com/lnaccess/app/signin/aci/la"
}


@celery.task(name='tasks.run_outstanding_query')
def run_outstanding_query():
    try:
        # Search for all accounts where the query has not been run in 24 hours
        users = models.User.query.filter(User.last_run < DT.now() - timedelta(days=1)).all()
        print(users)
        if (len(users) != 0):
            for user in users:
                tasks.get_points.delay(user.la_username, user.la_password)
                user.last_run = DT.now()
            try:
                db.session.commit()
            except:
                pass
    except:
        raise


    def on_failure(self, *args, **kwargs):
        pass

@celery.task(name='tasks.get_points')
def get_points(username, password):

    # driver = create_diagnostic_driver()

    driver = create_driver()

    land(driver)
    login(driver, username, password)
    query(driver, query = '402njsuper1')
    destroy_driver(driver)

def create_driver():
    driver = webdriver.PhantomJS(

        service_args = [
            '--ssl-protocol=any',
            '--ignore-ssl-errors=true'
        ],
        # service_log_path = os.path.join(proj_dir, 'var', 'ghostdriver', 'ghostdriver.log')
        # service_log_path = Config.SERVICE_LOG_PATH
        service_log_path = config[os.environ.get('CONFIG').strip('\'')].SERVICE_LOG_PATH
    )
    driver.set_window_size(1600, 900)

    return driver

def create_diagnostic_driver():
    driver = webdriver.Chrome()

    return driver

def land(driver):
    # Land webdriver on Lexis webpage
    driver.get(lnq_config['LEXIS_BASE_URL'])

    # VERIFY
    if (driver.current_url != lnq_config['LEXIS_LOGIN_TARGET']):
        destroy_driver(driver)
        raise InvalidLanding(1)


def login(driver, username, password):

    user_id     = 'userid'
    password_id = 'password'
    submit_id   = 'signInSbmtBtn'

    try:
        user_field  = driver.find_element_by_id(user_id)
        pwd_field   = driver.find_element_by_id(password_id)
        submit_btn  = driver.find_element_by_id(submit_id)
    except NoSuchElementException:
        raise NoSuchElementException

    user_field.send_keys(username)
    pwd_field.send_keys(password)
    submit_btn.click()

    # VERIFY
    login_banner = '//div[@class="content"]/h1[text()="Lexis Advance"]'
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, login_banner))
        )
        # driver.find_element_by_xpath(login_banner)
    except NoSuchElementException:
        destroy_driver(driver)
        driver.save_screenshot('error.png')
        raise InvalidLogin

def query(driver, query="njsa 2c:2-11"):

    searchbar_id = 'searchTerms'

    try:
        searchbar = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, searchbar_id))
        )
        # searchbar = driver.find_element_by_id(searchbar_id)
    except NoSuchElementException:
        raise NoSuchElementException
    else:
        searchbar.send_keys(query)


#------------------------------------------------------------------------------

    # PRESS BUTTON
    try:
        driver.execute_script("document.getElementById('mainSearch').click()")
    except TimeoutException:

        '''
            `res` should always be None, if `res` returns item, then the driver
            has landed on the results page
        '''
        try:
            res = None
            results_header = '//h2[@class="pagewrapper" and contains(text(), "Results for")]'
            res = driver.find_element_by_xpath(results_header)
        except NoSuchElementException:
            pass
        else:
            if res is not None:
                destroy_driver(driver)
                raise InvalidLanding(4)

        try:
            document_header = '//span[@class="documenttitle col"]'
            doc = driver.find_element_by_xpath(document_header)
        except NoSuchElementException:
            destroy_driver(driver)
            raise InvalidLanding(3)


#------------------------------------------------------------------------------

def destroy_driver(driver):
    driver.quit()
    try:
        driver.execute(Command.STATUS)
    except socket_error:
        return 0
