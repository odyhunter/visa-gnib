from __future__ import print_function
from selenium import webdriver
from requests import get, post
from datetime import datetime
from os.path import exists
from time import sleep


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
    print ('in the visa_autosummission func')
    print (str(auto_submission_entity))
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


class CaptchaUpload:
    def __init__(self, key, log=None, waittime=None):
        self.settings = {"url_request": "http://2captcha.com/in.php",
                         "url_response": "http://2captcha.com/res.php",
                         "key": key}
        if log:
            self.log = log
            self.logenabled = True
        else:
            self.logenabled = False

        if waittime:
            self.waittime = waittime
        else:
            self.waittime = 5

    def getbalance(self):
        """
        This request need for get balance
        :return: <YOURBALANCE> OK | 1 ERROR!
        """
        fullurl = "%s?action=getbalance&key=%s" % (
            self.settings['url_response'], self.settings['key'])
        request = get(fullurl)
        if "." in request.text:
            if self.logenabled:
                self.log.info("[2CaptchaUpload] Balance: %s" % request.text)
            return request.text
        elif request.text == "ERROR_KEY_DOES_NOT_EXIST":
            if self.logenabled:
                self.log.error("[2CaptchaUpload] You used the wrong key in the query")
            return 1
        elif request.text == "ERROR_WRONG_ID_FORMAT":
            if self.logenabled:
                self.log.error("[2CaptchaUpload] Wrong format ID CAPTCHA. "
                               "ID must contain only numbers")
            return 1

    def getresult(self, upload_id):
        """
        This function return the captcha solved
        :param upload_id: id captcha returned by upload
        :return: <captchaword> OK | 1 ERROR!
        """
        if self.logenabled:
            self.log.info("[2CaptchaUpload] Wait %s second.." % self.waittime)
        sleep(self.waittime)
        fullurl = "%s?key=%s&action=get&id=%s" % (self.settings['url_response'],
                                                  self.settings['key'], upload_id)
        if self.logenabled:
            self.log.info("[2CaptchaUpload] Get Captcha solved with id %s"
                          % upload_id)
        request = get(fullurl)
        if request.text.split('|')[0] == "OK":
            return request.text.split('|')[1]
        elif request.text == "CAPCHA_NOT_READY":
            if self.logenabled:
                self.log.error("[2CaptchaUpload] CAPTCHA is being solved, "
                              "repeat the request several seconds later, wait "
                              "another %s seconds" % self.waittime)
            return self.getresult(upload_id)
        elif request.text == "ERROR_KEY_DOES_NOT_EXIST":
            if self.logenabled:
               self.log.error("[2CaptchaUpload] You used the wrong key in "
                             "the query")
            return 1
        elif request.text == "ERROR_WRONG_ID_FORMAT":
            if self.logenabled:
                self.log.error("[2CaptchaUpload] Wrong format ID CAPTCHA. "
                               "ID must contain only numbers")
            return 1
        elif request.text == "ERROR_CAPTCHA_UNSOLVABLE":
            if self.logenabled:
                self.log.error("[2CaptchaUpload] Captcha could not solve "
                               "three different employee. Funds for this "
                               "captcha not")
            return 1

    def solve(self, pathfile):
        """
        This function upload read, upload and is the wrapper for solve
            the captcha
        :param pathfile: path of image
        :return: <captchaword> OK | 1 ERROR!
        """
        if exists(pathfile):
            files = {'file': open(pathfile, 'rb')}
            payload = {'key': self.settings['key'],
                       'method': 'post',
                       'regsense': '1',
                       'phrase': '1'}
            if self.logenabled:
                self.log.info("[2CaptchaUpload] Uploading to 2Captcha.com..")
            request = post(self.settings['url_request'], files=files,
                           data=payload)
            if request.ok:
                if request.text.split('|')[0] == "OK":
                    if self.logenabled:
                        self.log.info("[2CaptchaUpload] Upload Ok")
                    return self.getresult(request.text.split('|')[1])
                elif request.text == "ERROR_WRONG_USER_KEY":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] Wrong 'key' parameter"
                                       " format, it should contain 32 symbols")
                    return 1
                elif request.text == "ERROR_KEY_DOES_NOT_EXIST":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The 'key' doesn't "
                                       "exist")
                    return 1
                elif request.text == "ERROR_ZERO_BALANCE":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] You don't have money "
                                       "on your account")
                    return 1
                elif request.text == "ERROR_NO_SLOT_AVAILABLE":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The current bid is "
                                       "higher than the maximum bid set for "
                                       "your account.")
                    return 1
                elif request.text == "ERROR_ZERO_CAPTCHA_FILESIZE":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] CAPTCHA size is less"
                                       " than 100 bites")
                    return 1
                elif request.text == "ERROR_TOO_BIG_CAPTCHA_FILESIZE":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] CAPTCHA size is more"
                                       " than 100 Kbites")
                    return 1
                elif request.text == "ERROR_WRONG_FILE_EXTENSION":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The CAPTCHA has a "
                                       "wrong extension. Possible extensions "
                                       "are: jpg,jpeg,gif,png")
                    return 1
                elif request.text == "ERROR_IMAGE_TYPE_NOT_SUPPORTED":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The server cannot "
                                       "recognize the CAPTCHA file type.")
                    return 1
                elif request.text == "ERROR_IP_NOT_ALLOWED":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The request has sent "
                                       "from the IP that is not on the list of"
                                       " your IPs. Check the list of your IPs "
                                       "in the system.")
                    return 1
                elif request.text == "IP_BANNED":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The IP address you're"
                                       " trying to access our server with is "
                                       "banned due to many frequent attempts "
                                       "to access the server using wrong "
                                       "authorization keys. To lift the ban, "
                                       "please, contact our support team via "
                                       "email: support@2captcha.com")
                    return 1

        else:
            if self.logenabled:
                self.log.error("[2CaptchaUpload] File %s not exists" % pathfile)
            return 1




