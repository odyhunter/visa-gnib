from google.cloud import datastore
from datetime import datetime


datastore_api_client = datastore.Client()

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
        auto_submission_entity['multi_or_single'] = request.form['VisaType']
    elif appointment_type == 'gnib':
        auto_submission_entity['Category'] = request.form['Category']
        auto_submission_entity['SubCategory'] = request.form['SubCategory']
        auto_submission_entity['ConfirmGNIB'] = request.form['ConfirmGNIB']
        auto_submission_entity['GNIBExDT'] = request.form['GNIBExDT']
    else:
        print('appointment_type is not recognized')
        return False

    # [Set the fields common for both appointments]
    auto_submission_entity['GNIBNo'] = request.form['GNIBNo']
    auto_submission_entity['appointment_type'] = appointment_type
    auto_submission_entity['datetime_start'] = datetime.strptime(request.form['datetime_start'], "%d-%m-%Y %H:%M")
    auto_submission_entity['datetime_end'] = datetime.strptime(request.form['datetime_end'], "%d-%m-%Y %H:%M")
    auto_submission_entity['Email'] = request.form['Email']
    auto_submission_entity['GivenName'] = request.form['GivenName']
    auto_submission_entity['SurName'] = request.form['SurName']
    auto_submission_entity['DOB'] = request.form['DOB']
    auto_submission_entity['PassportNo'] = request.form['PassportNo']
    auto_submission_entity['Nationality'] = request.form['Nationality']
    auto_submission_entity['FamAppYN'] = request.form['FamAppYN']
    auto_submission_entity['FamAppNo'] = request.form['FamAppNo']

    datastore_api_client.put(auto_submission_entity)

    # prepare and return template values
    template_values = {'email': auto_submission_entity['Email'],
                       'auto_submission_id': auto_submission_entity.key.id}
    return template_values