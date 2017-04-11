import config
import re
import json
from collections import defaultdict
from google.cloud import datastore

datastore_api_client = datastore.Client(project=config.GCLOUD_PROJECT)


def create_auto_submission(request):
    """
    Accepts the request object
    Stores the auto_submission object in the datastore
    Returns the template_values dict
    """
    appointment_type = request.form['appointment_type']
    auto_submission_key = datastore_api_client.key('AutoSubmission')
    auto_submission_entity = datastore.entity.Entity(auto_submission_key)

    if appointment_type == 'visa':
        auto_submission_entity['Individual_or_Family'] = request.form['AppointType']
        auto_submission_entity['multi_or_single'] = request.form['VisaType']
        auto_submission_entity['GNIBNo'] = request.form['GNIBNo']
        auto_submission_entity['applicants'] = request.form['AppsNum']

    elif appointment_type == 'gnib':
        auto_submission_entity['Category'] = request.form['Category']
        auto_submission_entity['SubCategory'] = request.form['SubCategory']
        auto_submission_entity['ConfirmGNIB'] = request.form['ConfirmGNIB']
        auto_submission_entity['GNIBNo'] = request.form['GNIBNo']
        auto_submission_entity['GNIBExDT'] = request.form['GNIBExDT']
        auto_submission_entity['FamAppNo'] = request.form['FamAppNo']
        auto_submission_entity['FamAppYN'] = request.form['FamAppYN']

    else:
        print('appointment_type is not recognized')

    # take all fields filter the once which match the date_start_* regx pattern
    # date_times_count == num of date_time pairs in this AutoSubmission
    date_times_count = len([key for key in request.form.keys() if re.search('date_start_(\d+)', key)])
    date_times_dict = defaultdict()
    # go over each start end pair and put them into the defaultdict
    for i in range(date_times_count):
        date_times_dict[i] = {
            "start": request.form['date_start_{}'.format(i)],
            "end": request.form['date_end_{}'.format(i)]}

    # [Set the fields common for both appointments]
    auto_submission_entity['date_times_count'] = date_times_count
    auto_submission_entity['date_times'] = json.dumps(date_times_dict)  # list of data_time tuples(start, end)
    auto_submission_entity['Email'] = request.form['Email']
    auto_submission_entity['GivenName'] = request.form['GivenName']
    auto_submission_entity['SurName'] = request.form['SurName']
    auto_submission_entity['DOB'] = request.form['DOB']
    auto_submission_entity['PassportNo'] = request.form['PassportNo']
    auto_submission_entity['Nationality'] = request.form['Nationality']
    auto_submission_entity['appointment_type'] = appointment_type

    datastore_api_client.put(auto_submission_entity)

    # prepare and return template values
    template_values = {'email': auto_submission_entity['Email'],
                       'auto_submission_id': auto_submission_entity.key.id}
    return template_values
