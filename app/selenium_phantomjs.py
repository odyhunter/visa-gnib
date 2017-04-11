from __future__ import print_function
from selenium import webdriver

browser = webdriver.PhantomJS()

YEAR_CSS_SELECTOR = 'body > div > div.datepicker-years > table > tbody > tr > td > span.year'
MONTH_CSS_SELECTOR = 'body > div > div.datepicker-months > table > tbody > tr > td > span'
DATE_CSS_SELECTOR = 'body > div > div.datepicker-days > table > tbody > tr > td.day'


def dropdown_selector_helper(css_selector, value):
    """
    :param css_selector :(str) of the dropdown field that is targeted 
    :param value :(str) the text value of the field that, function is lowercasing this input.  
    :return: None, if search is successful the first option that equals the value is clicked
    Function is case insensitive 
    """
    element = browser.find_element_by_css_selector(css_selector)
    all_options = element.find_element_by_name('option')
    for option in all_options:
        if option.text.lower() == value.lower():
            option.click()
            return


def find_date_helper(css_selector, value):
    """
    finds elements that match the selector, then searches for the text that matches the given value
     if fn finds match returns WebElement object, otherwise returns False
    :param css_selector: that is selecting the elements within the given html element  
    :param value: which is compared 
    :return: WebElement object or False
    """
    elements = browser.find_elements_by_css_selector(css_selector)
    for element in elements:
        if element.text.lower() == str(value).lower():
            return element
    return False


def visa_auto_submission(date, month, year, slot_id, auto_submission_entity):

    browser.get('https://reentryvisa.inis.gov.ie/website/INISOA/IOA.nsf/AppointmentSelection?OpenForm')
    # Click the agree btn
    agree_btn = browser.find_element_by_css_selector('#btCom')
    agree_btn.click()
    # Name
    givenname_field = browser.find_element_by_css_selector('#GivenName')
    givenname_field.send_keys(auto_submission_entity.GivenName)
    # Surname
    surname_field = browser.find_element_by_css_selector('#Surname')
    surname_field.send_keys(auto_submission_entity.SurName)
    # Email
    email_field = browser.find_element_by_css_selector('#Email')
    email_field.send_keys(auto_submission_entity.Email)
    # Confirm Email
    emailconf_field = browser.find_elements_by_css_selector('#EmailConfirm')
    emailconf_field.send_keys(auto_submission_entity.Email)
    # Passpt Number
    passport_field = browser.find_element_by_css_selector('#PassportNo')
    passport_field.send_keys(auto_submission_entity.PassportNo)
    # GNIB Number
    gnib_field_element = browser.find_element_by_css_selector('#GNIBNo')
    gnib_field_element.send_keys(auto_submission_entity.GNIBNo)

    # Appointment Type
    dropdown_selector_helper('#AppointType', auto_submission_entity.Individual_or_Family)
    # Numbr of Applicants
    dropdown_selector_helper('#AppsNum', auto_submission_entity.applicants)
    # Nationality
    dropdown_selector_helper('#Nationality', auto_submission_entity.Nationality)
    # Type of visa
    dropdown_selector_helper('#VisaType', auto_submission_entity.multi_or_single)
    ## DOB
    dob_field = browser.find_element_by_css_selector('#DOB')
    dob_field.click()  # open the date picker pop up
    # Year Search
    while True:
        result = find_date_helper(YEAR_CSS_SELECTOR, year)
        if result:
            result.click()
            break
        else:
            # click previous year btn to continue the search
            previous_btn = browser.find_element_by_xpath('/html/body/div/div[3]/table/thead/tr/th[1]')
            previous_btn.click()
    # Month Search
    month_element = find_date_helper(MONTH_CSS_SELECTOR, month)
    month_element.click()
    # Date Search
    for date in browser.find_elements_by_css_selector('body > div > div.datepicker-days > table > tbody > tr > td.day'):
        if date.text == date:
            date.click()
            break



    browser.quit()

