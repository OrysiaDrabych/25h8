 #!/usr/bin/python
 # -*- coding: utf-8 -*-

from datetime import datetime
from iso8601 import parse_date
from pytz import timezone
import urllib
import json
import os

def convert_time(date):
    date = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
    return timezone('Europe/Kiev').localize(date).strftime('%Y-%m-%dT%H:%M:%S.%f%z')


def convert_datetime_to_25h8_format(isodate):
    iso_dt = parse_date(isodate)
    day_string = iso_dt.strftime("%d/%m/%Y %H:%M")
    return day_string


def convert_string_from_dict_25h8(string):
    return {
        u"грн.": u"UAH",
        u"True": u"1",
        u"False": u"0",
        u"Відкриті торги": u"aboveThresholdUA",
        u"Відкриті торги з публікацією англ. мовою": u"aboveThresholdEU",
        u'Код ДК 021-2015 (CPV)': u'CPV',
        u'Код ДК': u'ДК003',
        u'з урахуванням ПДВ': True,
        u'з ПДВ': True,
        u'без урахуванням ПДВ': False,
        u'ОЧIКУВАННЯ ПРОПОЗИЦIЙ': u'active.tendering',
        u'ПЕРIОД УТОЧНЕНЬ': u'active.enquiries',
        u'АУКЦIОН': u'active.auction',
        u'ПРЕКВАЛІФІКАЦІЯ': u'active.pre-qualification',
        u'ОСКАРЖЕННЯ ПРЕКВАЛІФІКАЦІЇ': u'active.pre-qualification.stand-still',
        u'вимога': u'claim',
        u'дано відповідь': u'answered',
        u'вирішено': u'resolved',
        u'Так': True,
        u'Ні': False,
        u'на розглядi': u'pending',
        u'На розгляді': u'pending',
        u'відмінена': u'cancelled',
        u'Переможець': u'active',
    }.get(string, string)


def adapt_procuringEntity(role_name, tender_data):
    if role_name == 'tender_owner':
        ph = tender_data['data']['procuringEntity']['contactPoint']['telephone'][-10:]
        tender_data['data']['procuringEntity']['name'] = u"Ольмек"
        tender_data['data']['procuringEntity']['address']['postalCode'] = u"01100"
        tender_data['data']['procuringEntity']['address']['region'] = u"місто Київ"
        tender_data['data']['procuringEntity']['address']['locality'] = u"Київ"
        tender_data['data']['procuringEntity']['address']['streetAddress'] = u"вул. Фрунзе 77"
        tender_data['data']['procuringEntity']['identifier']['legalName'] = u"Ольмек"
        tender_data['data']['procuringEntity']['identifier']['id'] = u"01234567"
       # tender_data = adapt_delivery_data(tender_data)
       # tender_data['data']['procuringEntity']['contactPoint']['telephone'] = "+38({}){}-{}-{}".format(ph[:3], ph[3:6], ph[6:8], ph[8:10])
    return tender_data


def adapt_delivery_data(tender_data):
    for index in range(len(tender_data['data']['items'])):
        value = tender_data['data']['items'][index]['deliveryAddress']['region']
        if value == u"місто Київ":
            tender_data['data']['items'][index]['deliveryAddress']['region'] = u"Київ"
    return tender_data


def adapt_view_data(value, field_name):
    if 'value.amount' in field_name:
        value = float(value.split(' ')[0])
    elif 'currency' in field_name:
        value = value.split(' ')[1]
    elif 'valueAddedTaxIncluded' in field_name:
        value = ' '.join(value.split(' ')[2:])
    elif 'minimalStep.amount' in field_name:
        value = float(value.split(' ')[0])
    elif 'unit.name' in field_name:
        value = value.split(' ')[1]
    elif 'quantity' in field_name:
        value = float(value.split(' ')[0])
    elif 'questions' in field_name and '.date' in field_name:
        value = convert_time(value.split(' - ')[0])
    elif 'Date' in field_name:
        value = convert_time(value)
 #   elif 'deliveryAddress' in field_name:
 #       value = value.replace(" область", "")
    return convert_string_from_dict_25h8(value)


def adapt_view_item_data(value, field_name):
    if 'unit.name' in field_name:
        value = ' '.join(value.split(' ')[1:])
    elif 'quantity' in field_name:
        value = float(value.split(' ')[0])
    elif 'Date' in field_name:
        value = convert_time(value)
    return convert_string_from_dict_25h8(value)


def get_related_elem_description(tender_data, feature, item_id):
    if item_id == "":
        for elem in tender_data['data']['{}s'.format(feature['featureOf'])]:
            if feature['relatedItem'] == elem['id']:
                return elem['description']
    else: return item_id


def custom_download_file(url, file_name, output_dir):
    urllib.urlretrieve(url, ('{}/{}'.format(output_dir, file_name)))


def add_second_sign_after_point(amount):
    amount = str(repr(amount))
    if '.' in amount and len(amount.split('.')[1]) == 1:
        amount += '0'
    return amount


def get_bid_phone(internal_id, bid_index):
    r = urllib.urlopen('https://lb.api-sandbox.openprocurement.org/api/2.3/tenders/{}'.format(internal_id)).read()
    tender = json.loads(r)
    bid_id = tender['data']['qualifications'][int(bid_index)]["bidID"]
    for bid in tender['data']['bids']:
        if bid['id'] == bid_id:
            return bid['tenderers'][0]['contactPoint']['telephone']


def get_upload_file_path():
    return os.path.join(os.getcwd(), 'src/robot_tests.broker.25h8/testFileForUpload.txt')