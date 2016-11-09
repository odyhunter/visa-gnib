# FINAL VErsion of the FLASK DATASTORE GNIB VISA CHECKER! :-{
#  export GCLOUD_PROJECT=flask-datastore-test


# [START app]
import logging
import os


import requests
import json
import time

from datetime import datetime, timedelta

from google.cloud import datastore

from flask import Flask
from flask import request
from flask import url_for
from flask import redirect
from flask import render_template

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Flask(__name__)

# [Constans]
VISA_RANGE = 90

VISA_URL = "https://burghquayregistrationoffice.inis.gov.ie/Website/AMSREG/AMSRegWeb.nsf/(getApps4DT)?openagent&dt={}/{}/{}&cat=Work&sbcat=All&typ=Renewal"
TOMORROW = datetime.now().date() + timedelta(days=1)

VISA_HOST = 'burghquayregistrationoffice.inis.gov.ie'

HEADERS = {
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko)  Chrome/52.0.2743.116 Safari/537.36',
  'host': '{}'.format(VISA_HOST),
  'Connection': 'keep-alive',
  'Upgrade-Insecure-Requests': '1',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6,pl;q=0.4,de;q=0.2,uk;q=0.2,it;q=0.2',
}

# [API objects]
datastore_api_client = datastore.Client(os.environ['GCLOUD_PROJECT'])



@app.route('/')
def visa_page():
  if request.method == 'GET':
    logging.debug('visa_page requested')
    query = datastore_api_client.query(kind='AppointmentSlot', order=('date_time',))
    query.add_filter('type', '=', 'Visa')
    results = query.fetch()
    print (results)
    return render_template('Visa_template.html', slots=results)


@app.route('/notification_request', methods=['GET', 'POST'])
def notification_request():
  if request.method == 'GET':
    print('GET on notification_request page')
    return render_template('notification_request.html')

  if request.method == 'POST':
    print('POST on notification_request page')
    print (request.form['email'])
    print (request.form['start_date'])
    print (request.form['appointment_type'])
    #create a key for Notification type entity
    Notification_key = datastore_api_client.key('Notification')
    #Create that entity
    Notification_entity = datastore.entity.Entity(Notification_key)
    #Add values to it
    Notification_entity['email'] = request.form['email']
    Notification_entity['appointment_type'] = request.form['appointment_type']
    Notification_entity['start_date'] = datetime.strptime(request.form['start_date'], "%Y-%m-%d %H:%M")
    Notification_entity['start_date'] = datetime.strptime(request.form['end_date'], "%Y-%m-%d %H:%M")
    #Put it into the datastore
    datastore_api_client.put(Notification_entity)

    return redirect(url_for('notification_request'))


# notification = Notification()
#    notification.email = request.get('email')
#    logging.info(self.request.get('date_start'))
#    notification.date_start = datetime.strptime(self.request.get('date_start'), "%Y-%m-%d %H:%M")
#    notification.date_end = datetime.strptime(self.request.get('date_end'), "%Y-%m-%d %H:%M")
#    notification.type = self.request.get('appointment_type')
#    notification.put()
#    self.redirect('/notification_request')

@app.route('/visa_update')
def visa_update():
  if request.method == 'GET':
    # delete all old entities
    datastore_api_query = datastore_api_client.query(kind='AppointmentSlot')
    datastore_api_query.add_filter('type', '=', 'Visa')
    datastore_api_query.keys_only()
    keys_to_delete = [entity.key for entity in datastore_api_query.fetch()]
    datastore_api_client.delete_multi(keys_to_delete)

    for counter in range(VISA_RANGE):
      # [Request parameters setup]
      date_obj = TOMORROW + timedelta(days=counter)  # add the day delta = counter
      day = str(date_obj)[8:10]
      month = str(date_obj)[5:7]
      year = str(date_obj)[0:4]
      print("Visa update request for:" + str(date_obj))
      url = VISA_URL.format(day, month, year)
      print ('url == ' + url)
      response = requests.get(url, headers=HEADERS, verify=False)
      response_json = json.loads(response.text)
      if "empty" not in response.text:
        # Slots in the response
        print (response_json)
        print (response_json["slots"])
        for slot in response_json["slots"]:
          # put the slot into datastore
          slot_datetime_obj = datetime.strptime(slot['time'], "%d/%m/%Y %I:%M %p")

          AppointmentSlot_key = datastore_api_client.key('AppointmentSlot')
          AppointmentSlot_entity = datastore.entity.Entity(AppointmentSlot_key)
          AppointmentSlot_entity['date_time'] = slot_datetime_obj
          AppointmentSlot_entity['type'] = 'Visa'
          datastore_api_client.put(AppointmentSlot_entity)
      else:
        # empty in the response
        print (response_json)
      # wait for 0.5 sec bettwen each requests - not to ddos :)
      time.sleep(0.5)

  return 'OK', 200


@app.errorhandler(500)
def server_error(e):
  logging.exception('An error occurred during a request.')
  return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
  # This is used when running locally. Gunicorn is used to run the
  # application on Google App Engine. See entrypoint in app.yaml.
  app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
