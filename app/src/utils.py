from __future__ import print_function

import json
import logging
import mailjet_rest
import config

from google.cloud import datastore
from datetime import datetime, timedelta, time
from os.path import exists
from requests import post, get
from time import sleep
from selenium_phantomjs import visa_auto_submission, gnib_auto_submission


datastore_api_client = datastore.Client(project=config.GCLOUD_PROJECT)


def make_header(header, appointment_type):
    if appointment_type == 'gnib':
        header['host'] = config.GNIB_HOST
        return header
    elif appointment_type == 'visa':
        header['host'] = config.VISA_HOST
        return header


def send_email(receiver, subject, body):
    client = mailjet_rest.Client(
        auth=(config.MAILJET_API_KEY, config.MAILJET_API_SECRET))
    data = {
        'FromEmail': config.MAILJET_SENDER,
        'FromName': 'visa-gnib.info',
        'Subject': subject,
        'Text-part': body,
        'Recipients': [{'Email': receiver}]
    }
    result = client.send.create(data=data)
    logging.info(result)


def notify_user(notification, list_of_slots):
    """
  :param notification: Notification object
  :param list_of_slots: list containing of appointments that match the requirments of notification
  :return: None, notifies the user
  """
    body = "Hi! There are a new appointment slots for {} : \n".format(notification['appointment_type'])
    for slot in list_of_slots:
        body += "{}\n".format(slot['slot'])
    body += "Register here: {} ".format(
        config.VISA_HOST if notification['appointment_type'] == "visa" else config.GNIB_HOST)

    if notification['email']:
        # send email about the slot(s)
        send_email(receiver=notification['email'],
                   subject="New {} Appointment".format(notification['appointment_type']),
                   body=body, )
        # delete the notification object from datastore
        logging.info(
            'email was send to {}, notification id = {} was deleted'.format(notification['email'], notification.key.id))
        datastore_api_client.delete(notification.key)


# URL to get dict of dates with appointments:
# https://reentryvisa.inis.gov.ie/website/INISOA/IOA.nsf/(getDTAvail)?openagent&type=I&_=UNIX_TIMESTAMP
def fetch_appointments(days, appointment_type):
    for counter in range(days):
        date_obj = datetime.combine(config.TODAY_plus_2 + timedelta(days=counter), time())
        print('Fetch appointments for {} {}'.format(appointment_type, str(date_obj)))
        datastore_api_query = datastore_api_client.query(kind='AppointmentSlot')
        datastore_api_query.add_filter('appointment_type', '=', appointment_type)
        datastore_api_query.add_filter('date', '=', date_obj)
        keys_to_delete = [entity.key for entity in datastore_api_query.fetch()]
        datastore_api_client.delete_multi(keys_to_delete)
        # [Parameters for request]
        # make 1 liner
        day = str(date_obj)[8:10]
        month = str(date_obj)[5:7]
        year = str(date_obj)[0:4]
        url = config.GNIB_UPDATE_URL if appointment_type == 'gnib' else config.VISA_UPDATE_URL
        url = url.format(day, month, year)
        # make request
        response = get(url, headers=make_header(config.HEADERS, appointment_type), verify=False)
        response_json = json.loads(response.text)
        print('Responce = {}'.format(response_json))
        # processing results
        if "empty" not in response.text:
            # Slots in the response
            slots_of_that_date = [(datetime.strptime(slot['time'], '%d/%m/%Y %I:%M %p'), slot['id'])
                                  for slot in response_json["slots"]]
            for appointment_slot, slot_id in slots_of_that_date:
                appointment_slot_key = datastore_api_client.key('AppointmentSlot')
                appointment_slot_entity = datastore.entity.Entity(appointment_slot_key)
                appointment_slot_entity['date'] = date_obj
                appointment_slot_entity['appointment_type'] = str(appointment_type)
                appointment_slot_entity['slot'] = appointment_slot
                appointment_slot_entity['slot_id'] = slot_id
                datastore_api_client.put(appointment_slot_entity)


# check if there are appointments that fulfil the notification requests
def notification_check():
    query = datastore_api_client.query(kind='Notification')
    query.keys_only()
    query_result_keys = [entity.key for entity in query.fetch()]
    for key in query_result_keys:
        notification = datastore_api_client.get(key)
        query = datastore_api_client.query(kind='AppointmentSlot')
        query.add_filter('appointment_type', '=', notification['appointment_type'].lower())
        query.add_filter('slot', '>=', notification['date_start'])
        query.add_filter('slot', '<=', notification['date_end'])
        list_of_slots = [dict(entity) for entity in query.fetch()]
        if len(list_of_slots) > 0:
            # results found notify user
            notify_user(notification, list_of_slots)
        else:
            print('No matching appointments for notification id = {}'.format(notification.key.id))


def cleanup():
    # delete all slots which date < today
    query = datastore_api_client.query(kind='AppointmentSlot')
    query.add_filter('date', '<', datetime.today())
    datastore_api_client.delete_multi([entity.key for entity in query.fetch()])

    # get all notification objects where date end < today
    query = datastore_api_client.query(kind='Notification')
    query.add_filter('date_end', '<', config.TODAY_plus_2)
    query_results = [entity for entity in query.fetch()]
    query_results_keys = [ent.key for ent in query_results]
    for notification in query_results:
        print('slot not found deleting request for {}'.format(notification.key.id))
        print('date_start = {} date end = {}'.format(notification['date_start'], notification['date_end']))
        send_email(receiver=notification['email'],
                   subject="Your Appointment for {} was not met".format(notification['appointment_type']),
                   body="Your notification end date ({}) has passed and there were no new appointments. :( \n"
                        "We are deleting this request, please feel free for create a new one here: \n"
                        "http://visa-gnib.info".format(notification['date_end'])
                   )
    # delete expired notifications
    datastore_api_client.delete_multi(query_results_keys)


def auto_submission_check():
    query = datastore_api_client.query(kind='AutoSubmission')
    # get all AutoSubmission entities for the check
    for auto_submission_entity in query.fetch():
        print('AutoSubmission check for {}'.format(str(auto_submission_entity)))
        print('\n')
        # grab the date_times pairs from these entities
        # TODO: refactor the form to only accept one date range, and get rid of this JSON
        all_date_times_dict = json.loads(auto_submission_entity['date_times'])
        # go over each pair to check if there is a matching appointment slot
        for i in range(auto_submission_entity['date_times_count']):
            # prepare the datetime object
            index_date_time_dict = all_date_times_dict[str(i)]
            index_date_time_start = datetime.strptime(index_date_time_dict['start'], "%d-%m-%Y %H:%M")
            index_date_time_end = datetime.strptime(index_date_time_dict['end'], "%d-%m-%Y %H:%M")
            # create the checking query
            query = datastore_api_client.query(kind='AppointmentSlot')
            query.add_filter('appointment_type', '=', auto_submission_entity['appointment_type'])
            query.add_filter('slot', '>=', index_date_time_start)
            query.add_filter('slot', '<=', index_date_time_end)
            list_of_slots = [entity for entity in query.fetch()]
            if len(list_of_slots) > 0:
                # match for auto_submission() found trying to register user
                for slot in list_of_slots:
                    # try each slot
                    if auto_submission_entity['appointment_type'] == 'visa':
                        auto_subm_result = visa_auto_submission(auto_submission_entity=auto_submission_entity,
                                                                slot_id=slot['slot_id'],
                                                                date=slot['date'].strftime('%d/%m/%Y'))
                    elif auto_submission_entity['appointment_type'] == 'gnib':
                        auto_subm_result = gnib_auto_submission(auto_submission_entity=auto_submission_entity,
                                                                slot_id=slot['slot_id'],
                                                                date=slot['date'].strftime('%d/%m/%Y'))

                    # once submit is successful - stop the slots loop
                    if auto_subm_result:
                        # notify user with email
                        send_email(receiver=auto_submission_entity['Email'],
                                   subject="{} Appointment has been registered".format(
                                       auto_submission_entity['appointment_type']),
                                   # TODO: email body text
                                   body='body: {}'.format('submission successful'.encode('utf-8')))
                        # delete the auto_submission_entity from DS
                        datastore_api_client.delete(auto_submission_entity.key)
                        break


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

