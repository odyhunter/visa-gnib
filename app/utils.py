from __future__ import print_function
import config
import time
import json
import requests
import logging
import mailjet_rest

from google.cloud import datastore
from datetime import datetime, timedelta, time

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
        response = requests.get(url, headers=make_header(config.HEADERS, appointment_type), verify=False)
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
    query_results = [entity for entity in query.fetch()]
    for auto_submission_entity in query_results:
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
            print(len(list_of_slots))
            if len(list_of_slots) > 0:
                # match for auto_submission() found trying to register user
                for slot in list_of_slots:
                    # try each slot
                    result = register_appointment(
                        # appointment_type=auto_submission_entity['appointment_type'],
                        # auto_submission_entity=auto_submission_entity,
                        # slot_id=slot['slot_id'],
                        # slot_date=slot['date'].strftime('%d/%m/%Y'),
                    )
                    # once subm is successful - stop the slots loop
                    if result:
                        # notify user wuth email
                        send_email(receiver=auto_submission_entity['Email'],
                                   subject="{} Appointment has been registered".format(
                                       auto_submission_entity['appointment_type']),
                                   # TODO: email body text
                                   body='body: {}'.format('your appointment is registered '.encode('utf-8'))
                                   )
                        # delete the auto_submission_entity from DS
                        datastore_api_client.delete(auto_submission_entity.key)
                        break


def register_appointment():
    # programaticly submits the application on the website
    return True


