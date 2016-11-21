from selenium import webdriver

from selenium.webdriver.remote.command import Command

from selenium.common.exceptions import NoSuchElementException,\
        TimeoutException

from celery import Celery

from automation_exception import InvalidLanding

from socket import error as socket_error

celery = Celery(__name__, broker='redis://localhost:6379/0')

lnq_config = {
    'LEXIS_BASE_URL'    : "https://advance.lexis.com",
    'LEXIS_LOGIN_TARGET': "https://signin.lexisnexis.com/lnaccess/app/signin/aci/la"
}

@celery.task(name='tasks.get_points')
def get_points(username, password):
    driver = create_driver()
    login(driver, username, password)
    query(driver)
    destroy_driver(driver)

def create_driver():
    driver = webdriver.Chrome()

    # Land webdriver on Lexis webpage
    driver.get(lnq_config['LEXIS_BASE_URL'])

    # VERIFY
    if (driver.current_url != lnq_config['LEXIS_LOGIN_TARGET']):
        destroy_driver(driver)
        raise InvalidLanding(1)

    return driver

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
        driver.find_element_by_xpath(login_banner)
    except NoSuchElementException:
        destroy_driver(driver)
        raise InvalidLanding(2)

def query(driver, query="njsa 2c:2-11"):

    searchbar_id = 'searchTerms'

    try:
        searchbar = driver.find_element_by_id(searchbar_id)
    except NoSuchElementException:
        raise NoSuchElementException
    else:
        searchbar.send_keys(query)


#------------------------------------------------------------------------------

    # PRESS BUTTON
    try:
        driver.execute_async_script("document.getElementById('mainSearch').click()")
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
