from __future__ import print_function
from selenium import webdriver
from utils import CaptchaUpload
from requests import get
from datetime import datetime


YEAR_CSS_SELECTOR = 'body > div > div.datepicker-years > table > tbody > tr > td > span.year'
MONTH_CSS_SELECTOR = 'body > div > div.datepicker-months > table > tbody > tr > td > span'
DATE_CSS_SELECTOR = 'body > div > div.datepicker-days > table > tbody > tr > td.day'
CAPTCHA_SOLVER_API_KEY = '69e9ac9b83b9fa122a2e6843b6a7a922'


def captcha_solver(browser):
    """
    Function should be invouced on the page with the recaptcha challenge 
    :return: string with solution
    """
    # Get the captcha img source
    recaptcha_image_url = browser.find_element_by_css_selector('#recaptcha_challenge_image').get_attribute('src')
    # download that img into the file captcha_image.jpeg
    response = get(recaptcha_image_url)
    with open('captcha_image.jpeg', 'w') as image_file:
        image_file.write(response.content)
    # solve the captcha with 2captcha.com API
    captcha = CaptchaUpload(key=CAPTCHA_SOLVER_API_KEY)
    return captcha.solve('captcha_image.jpeg')


def gnib_auto_submission():
    # TODO: implement both submissions.
    return True


def visa_auto_submission(date, slot_id, auto_submission_entity):
    """
    Register visa appointment slot for the give auto_submission_entity
    :param date:[str] date of the appointment which would be registered by this func    
    :param slot_id: [str] id of the specific time slot for registration
    :param auto_submission_entity: 
    :return: reference_no, apt_date - tuple with to strings confirming the registration. 
    If registration is not successful returns - False
    """
    with webdriver.PhantomJS() as browser:
        browser.get('https://reentryvisa.inis.gov.ie/website/INISOA/IOA.nsf/AppointmentSelection?OpenForm')
        # Click the agree btn
        browser.find_element_by_css_selector('#btCom').click()
        # Given Name
        browser.find_element_by_css_selector('#GivenName').send_keys(auto_submission_entity.GivenName)
        # Surname
        browser.find_element_by_css_selector('#Surname').send_keys(auto_submission_entity.SurName)
        # Set Date of Birth:
        browser.execute_script('$("#DOB").val("{}")'.format(auto_submission_entity.DOB))
        # Email
        browser.find_element_by_css_selector('#Email').send_keys(auto_submission_entity.Email)
        # Confirm Email
        browser.find_elements_by_css_selector('#EmailConfirm').send_keys(auto_submission_entity.Email)
        # Appointment Type
        browser.execute_script('$("#AppointType").val("{}")'.format(auto_submission_entity.Individual_or_Family))
        # Number of Applicants
        browser.execute_script('$("#AppsNum").val("{}")'.format(auto_submission_entity.applicants))
        # Passport Number
        browser.find_element_by_css_selector('#PassportNo').send_keys(auto_submission_entity.PassportNo)
        # GNIB Number
        browser.find_element_by_css_selector('#GNIBNo').send_keys(auto_submission_entity.GNIBNo)
        # Nationality
        browser.execute_script('$("#Nationality").val("{}")'.format(auto_submission_entity.Nationality))
        # Type of visa
        browser.execute_script('$("#VisaType").val("{}")'.format(auto_submission_entity.multi_or_single))
        # Set the appointment date
        browser.execute_script('$("#Appdate").val("{}")'.format(date))
        # Call JS function bookit() passing the appointment ID as a parameter to invoke the booking.
        browser.execute_script('bookit("{}")'.format(slot_id))
        # Solve captcha
        captcha_solution = captcha_solver(browser)
        # input the solution into the field
        browser.execute_script('$("#recaptcha_response_field").val("{}")'.format(captcha_solution))
        # Submit the form
        browser.find_element_by_css_selector('#SubmitButton_1_1_1').click()
        # wait for 8 sec to load:
        browser.implicitly_wait(10)

        # submission successful:
        if browser.find_element_by_css_selector('#AppConfirmed'):
            reference_no = browser.find_element_by_css_selector(
                '#AppConfirmed>div:nth-child(1)>h3:nth-child(1)').text[14:]  # slice the ID reference no from the str
            apt_date = browser.find_element_by_css_selector('#AppConfirmed>div:nth-child(1)>h3:nth-child(2)').text
            return {'reference_no': reference_no,
                    'appointment_date': apt_date}

        # if there is an error on the page
        elif browser.find_element_by_css_selector('#dvGenError'):
            browser.save_screenshot('error_screenshot_{}.png'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            print('Error when submitting: \n')
            print(browser.find_element_by_css_selector('#dvGenError > spam').text)
            return False

        else:
            # something else is wrong:
            browser.save_screenshot('error_screenshot_{}.png'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            print('Error when submitting: \n')
            print(browser.find_element_by_css_selector('#dvGenError > spam').text)
            return False





