import os
import datetime
from configparser import ConfigParser
config = ConfigParser()
config.read(os.environ['CONFIG_PATH'])
GCLOUD_PROJECT = config['app']['GCLOUD_PROJECT']
MAILJET_API_KEY = config['app']['MAILJET_API_KEY']
MAILJET_API_SECRET = config['app']['MAILJET_API_SECRET']
MAILJET_SENDER = config['app']['MAILJET_SENDER']

VISA_UPDATE_URL = 'https://reentryvisa.inis.gov.ie/website/INISOA/IOA.nsf/(getApps4DT)?openagent&' \
                  'dt={}/{}/{}&type=I&num=1'
GNIB_UPDATE_URL = 'https://burghquayregistrationoffice.inis.gov.ie/Website/AMSREG/AMSRegWeb.nsf/(getApps4DT)' \
                  '?openagent&dt={}/{}/{}&cat=Work&sbcat=All&typ=Renewal'

VISA_HOST = 'reentryvisa.inis.gov.ie'
GNIB_HOST = 'burghquayregistrationoffice.inis.gov.ie'

TODAY_plus_2 = datetime.datetime.today() + datetime.timedelta(days=2)
DAYS_UPDATE_RANGE = 90
FETCH_APPOINTMENTS_TIMEOUT = 60
TYPE_VISA = 'visa'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  ' Chrome/52.0.2743.116 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6,pl;q=0.4,de;q=0.2,uk;q=0.2,it;q=0.2',
}
