from woocommerce import API
import logging as log

import phonenumbers
import argparse
import csv
from pprint import pprint
from datetime import datetime
import pycountry_convert as pc
import locale
locale.setlocale(locale.LC_ALL, '')
import re

import os
import pickle

class Bx:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GREY = '\u001b[30;1m'
    LIGHTGREY = '\u001b[38;5;248m'

class B:
    HEADER = ''
    OKBLUE = ''
    OKCYAN = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''
    GREY = ''
    LIGHTGREY = ''

from datetime import datetime
now_hour = datetime.now().strftime('%Y-%m-%d %H')
now_day = datetime.now().strftime('%Y-%m-%d')
now_month = datetime.now().strftime('%Y-%m')


from tinydb import TinyDB, Query
db = TinyDB('/var/www/python-realtime-poll-pusher/db.json')

class Response:
    def __init__(self, status, json_data):
        self.status_code = status
        self.json = json_data

WC_MAX_API_RESULT_COUNT = 100

wcapi = API(
    url="https://naturallandscapeawards.com/",
    consumer_key="ck_4bd7aaa0abc95316c2a1a8c41f40c1862c6e03f3",
    consumer_secret="cs_590e33818f7d4a04646d30412fc2f8382164664f",
    version="wc/v3",
    query_string_auth=True,
    verify_ssl = True,
)

book_id_mapping = {
    '1': '1843',
    '2': '5657',
    '3': '18713',
    '4': '20049',
    '12': '5695',
    '23': '18722',
    '123': '18715',
    '1234': '20304',
    '13': '20315',
    '14': '20316',
    '24': '20317',
    '124': '20321',
    '134': '20322',
    '234': '20323',
    '34': '20319',
}
id_book_mapping = {}
for k,v in book_id_mapping.items():
    id_book_mapping[v] = k
def wcapi_aggregate_paginated_response(func):
    """
    Decorator that repeat calls a decorated function to get 
    all pages of WooCommerce API response.

    Combines the response data into a single list.

    Decorated function must accept parameters:
        - wcapi object
        - page number
    """
    def wrapper(wcapi, page=0, *args, **kwargs):
        items = []
        page = 0
        num_pages = WC_MAX_API_RESULT_COUNT

        while page < num_pages:
            page += 1
            log.debug(f"{page=}")

            response = func(wcapi, page=page, *args, **kwargs)

            items.extend(response.json())
            num_pages = int(response.headers["X-WP-TotalPages"])
            num_products = int(response.headers["X-WP-Total"])

        log.debug(f"{num_products=}, {len(items)=}")
        return items
    return wrapper





@wcapi_aggregate_paginated_response
def get_all_wc_orders(wcapi, page=1, status=None):
    """
    Query WooCommerce rest api for all products
    """

    response = wcapi.get(
        "orders",
        params={
            "per_page": WC_MAX_API_RESULT_COUNT,
            "page": page,
            'status': status,
        },
    )
    response.raise_for_status()
    return response


def get_orders(wcapi, status=None):
    s = Query()
    d = db.get(s.key == '{}{}'.format(now_hour,status))

    if d:
        return d['orders']
    else:
        orders = get_all_wc_orders(wcapi, status=status)
        db.insert({'key': '{}{}'.format(now_hour,status), 'orders': orders})
        return orders


def getsku(vs):
    v1 = '1' if '1' in vs else '0'
    v2 = '2' if '2' in vs else '0'
    v3 = '3' if '3' in vs else '0'
    v4 = '4' if '4' in vs else '0'
    if '4' in vs:
        product_sku = 'NLPA-{}{}{}{}'.format(v1, v2, v3, v4)
    else:
        product_sku = 'NLPA-{}{}{}'.format(v1, v2, v3)
    return product_sku



def printorder(compiled_order):
    order = compiled_order['o']

    if order['status'] == 'processing':
        status = B.FAIL+'processing'+B.ENDC
    else:
        status = B.OKGREEN+order['status']+B.ENDC
    o_url = "https://naturallandscapeawards.com/wp-admin/post.php?action=edit&post="
    print('<strong>')
    print(B.HEADER+'##########################################################################'+len(status)*'#'+len(str(order['id']))*'#')
    print(B.HEADER+'#############'+B.ENDC+' <a href="{}{}">{}</a> ({})'.format(o_url,order['id'],B.HEADER+str(order['id'])+B.ENDC, status)+B.HEADER+' ########################################################'+B.ENDC)
    print(B.HEADER+'##########################################################################'+len(status)*'#'+len(str(order['id']))*'#'+'\n')
    print('</strong>')

    s = order['shipping']
    b = order['billing']

    dt = datetime.strptime(order['date_created'], '%Y-%m-%dT%H:%M:%S')
    print(B.OKGREEN+'{} {}'.format(b['first_name'],b['last_name'])+B.ENDC)
    print(B.LIGHTGREY+dt.strftime('%a %d %b %Y, %I:%M%p')+B.ENDC)

    for l in compiled_order['line_items']:
        if l['quantity'] != '1':
            print(' - {} x {}'.format(l['name'],l['quantity']))
        else:
            print(' - {}'.format(l['name']))

    print()
    vo = ','.join(compiled_order["vols"])
    print(f'Volumes Ordered: {vo}')
    vls = ','.join(compiled_order["vols_less_shipped"])
    print(f'Volumes Left to Ship:  {vls}')

    print()

    print(B.GREY+'shipping:' + B.ENDC + ' {}'.format(B.BOLD+str(order['shipping_total'])+B.ENDC))
    print(B.LIGHTGREY+'total:' + B.ENDC + ' {}'.format(B.BOLD+str(order['total']))+B.ENDC)



    print(B.BOLD+B.UNDERLINE+'\nSHIPPING'+B.ENDC)
    print(B.LIGHTGREY)
    print('{} {}'.format(s['first_name'],s['last_name']))
    print(' %s'%b['email'])
    print(' %s'%s['phone'])

    if s['company']:
        print(s['company'])
    print(s['address_1'])
    if s['address_2']:
        print(s['address_2'])
    print(s['city'])
    print(s['state'])
    print(s['postcode'])
    try:
        s_country_name = pc.country_alpha2_to_country_name(s['country'])
    except KeyError:
        s_country_name = ''
    print('{} ({})'.format( s_country_name,s['country']))
    print(B.ENDC)


    if b['postcode'] != s['postcode']:
        print(B.BOLD+B.UNDERLINE+'BILLING'+B.ENDC)
        print(B.LIGHTGREY)
        print('{} {}'.format(b['first_name'],b['last_name']))
        print(' %s'%b['email'])
        print(' %s'%b['phone'])

        if b['company']:
            print(b['company'])
        print(b['address_1'])
        if b['address_2']:
            print(b['address_2'])
        print(b['city'])
        print(b['state'])
        print(b['postcode'])
        try:
            b_country_name = pc.country_alpha2_to_country_name(b['country'])
        except KeyError:
            b_country_name = ''
        print('{} ({})'.format( b_country_name,b['country']))
        print(B.ENDC)
    print()


def get_vols(notes):
    vols = set()
    for note in notes:
        note_lower = note.lower()
        if 'vol' in note_lower and ('shipped' in note_lower or 'sent' in note_lower):
            num = re.findall(r'\d+', note)
            for n in num:
                for v in list(n):
                    vols.add(v)
    lvols = list(vols)
    lvols.sort()

    return lvols


def search_for_partial_complete_notes(wcapi, order_id):

    s = Query()
    response = wcapi.get(
        "orders/{}/notes".format(order_id)
    )
    data = response.json()
    notes = [d['note'].lower() for d in data]
    print(notes)
    vols = get_vols(notes)
    print(vols)
    return vols






if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-C','--country', help="add a country filter (two letter code, prefix '-' for exclude)")
    parser.add_argument('-V','--volume', help="add a volume filter comma separated. (prefix '-' for exclude)")
    parser.add_argument('-c','--csv', help='save a csv with this name')

    parser.add_argument('-r', '--report', action='store_true', help='give a report on how many outstanding')

    parser.add_argument('-n','--findbyname', help='Find orders by name')
    parser.add_argument('-i','--findbyid', help='Find orders by order id')

    parser.add_argument('-a','--archived', action='store_true', help='include archived orders')


    parser.add_argument('-v','--verbose', action='store_true', help="print out stuff")
    parser.add_argument('-p','--packing', action='store_true', help="just print out what needs packing")

    parser.add_argument('-P','--printcsv', action='store_true', help="print out the csv file")
    parser.add_argument('-X','--clearcache', action='store_true', help="clear cache")




    args = parser.parse_args()

    verbose = args.verbose
    csv_out = args.csv
    country_filter = args.country
    volume_filter = args.volume
    report = args.report
    packing = args.packing
    findbyname = args.findbyname
    findbyid = args.findbyid
    archived = args.archived
    printcsv = args.printcsv
    clearcache = args.clearcache


    compiled_orders = {}

    countries = set()



    if os.path.isfile('orders_cache.pickle') and not clearcache:
        with open('orders_cache.pickle', 'rb') as f:
            compiled_orders = pickle.load(f)
    else:
        if archived:
            orders = get_orders(wcapi, status=None)
        else:
            orders = get_orders(wcapi, status='processing')
        for o in orders:
            id = o['id']
            s = o['shipping']
            b = o['billing']
            fname = s['first_name']
            lname = s['last_name']

            address_1 = s['address_1']
            address_2 = s['address_2']
            company = s['company']
            city = s['city']
            state = s['state']
            country = s['country']
            postcode = s['postcode']
            s_phone = s['phone']
            b_phone = b['phone']
            email = b['email']


            vols = []
            for li in o['line_items']:
                if str(li['product_id']) not in id_book_mapping:
                    continue
                li_vols = list( id_book_mapping[str(li['product_id'])] )
                vols.extend(li_vols)

            vols.sort()

            shipped_orders = search_for_partial_complete_notes(wcapi, id)

            vols_less_shipped = []
            for v in vols:
                if v not in shipped_orders:
                    vols_less_shipped.append(v)




            if s_phone.strip() == '':
                phone = b_phone
            else:
                phone = s_phone




            if phone[0:2] == '+0':
                phone = '{}{}'.format(phone[0],phone[2:])
            if phone[0:2] == '1+':
                phone = phone[2:]
            try:
                pn = phonenumbers.parse(phone, country)
                phone_format = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                phone_format[1:].replace('-', ' ')
            except Exception as e:
                if verbose:
                    print('**************** {} ***************'.format(e))
                phone_format = ''





            try:
                country_name = pc.country_alpha2_to_country_name(country)
            except KeyError:
                country_name = ''



            order = {
                'id': id,
                'fname': fname,
                'lname': lname,
                'email': email,
                'address_1': address_1,
                'address_2': address_2,
                'company': company,
                'city': city,
                'state': state,
                'country': country,
                'country_name': country_name,
                'postcode': postcode,
                'phone': phone,
                'phone_format': phone_format,

                'vols': vols,
                'vols_less_shipped': vols_less_shipped,
                'multi': False, 
                'o': o,
            }

            # check for duplicates
            key = '{}:{},{},{},{}'.format(lname,address_1, city, country, postcode)

            if key in compiled_orders:
                compiled_orders[key]['vols'].extend(vols)
                compiled_orders[key]['vols_less_shipped'].extend(vols_less_shipped)
                compiled_orders[key]['multi'] = '**** vols ****'
                compiled_orders[key]['line_items'].extend( o['line_items'] )
            else:
                compiled_orders[key] = order
                compiled_orders[key]['line_items'] = o['line_items']


        with open('orders_cache.pickle','wb') as f:
            pickle.dump(compiled_orders, f)

    csv_headers = [
        "order_id",
        "billing_email",
        "shipping_first_name",
        "shipping_last_name",
        "shipping_company",
        "phone",
        "shipping_address_1",
        "shipping_address_2",
        "shipping_postcode",
        "shipping_city",
        "shipping_state",
        "Country",
        "SKU"
    ]
    if printcsv:
        print('</pre><table id="customers"><tr>')
        for h in csv_headers:
            print('<th>{}</th>'.format(h))
        print('</tr>')

          
        
    csv_data = []
    packing_data = {}
    packing_data_per_book = {}


    find_ids = []
    if findbyname or findbyid:
        for k, order in compiled_orders.items():

            if findbyname and findbyname in '{} {}'.format(order['o']['billing']['first_name'], order['o']['billing']['last_name']):
                find_ids.append(order['o']['id'])
            if findbyid and str(findbyid) == str(order['o']['id']) :
                find_ids.append(order['o']['id'])



    if csv_out:
        for k, order in compiled_orders.items():

            vs = order['vols_less_shipped']
            vs.sort()
            sku = getsku(vs)

            if country_filter:

                if country_filter.startswith('-'):
                    if order['country'] == country_filter[1:]:
                        continue
                else:
                    if order['country'] != country_filter:
                        continue

            if volume_filter:

                if volume_filter.startswith('-'):
                    AND = False
                    ONLY = False
                    if ',' in volume_filter:
                        filter = volume_filter[1:].split(',')
                    elif '&' in volume_filter or volume_filter.startswith('-&'):
                        filter = volume_filter[1:].split('&')
                        AND = True
                    else:
                        filter = [volume_filter[1:]]


                    exclude_count = 0
                    for f in filter:
                        if f in vs:
                            exclude_count += 1
                    if AND and exclude_count == len(filter):
                        continue
                    elif not AND and exclude_count >0:
                        continue

                else:
                    AND = False
                    ONLY = False
                    if ',' in volume_filter:
                        filter = volume_filter.split(',')
                    elif '&' in volume_filter or volume_filter.startswith('&'):
                        filter = volume_filter.split('&')
                        AND = True
                    elif volume_filter.startswith('!'):
                        filter = volume_filter[1:]
                        ONLY = True
                    else:
                        filter = [volume_filter]
                    is_in_count = 0
                    has_others = False
                    for f in filter:
                        if f in vs:
                            is_in_count += 1

                    for v in vs:
                        if v not in filter:
                            has_others = True
                        
                    if is_in_count == 0:
                        continue
                    elif AND and is_in_count < len(filter):
                        continue
                    elif ONLY and has_others:
                        continue





            if findbyname or findbyid:
                if order['id'] not in find_ids:
                    continue

            order['infilter'] = True


            csv_row = (
                    order['id'],
                    order['email'],
                    order['fname'],
                    order['lname'],
                    order['company'],
                    order['phone'],
                    order['address_1'],
                    order['address_2'],
                    order['postcode'],
                    order['city'],
                    order['state'],
                    order['country_name'],
                    sku,
                )
            csv_data.append( csv_row )
            if printcsv:
                print('<tr>')
                for n, i in enumerate(csv_row):
                    if n == 0: 
                        o_url = "https://naturallandscapeawards.com/wp-admin/post.php?action=edit&post="
                        print('<td><a href="{}{}">{}</a></td>'.format(o_url,str(i),str(i)))
                    else:
                        print('<td>{}</td>'.format(str(i)))

                print('</tr>')
                    
            if verbose:
                print(csv_data)
            if ''.join(vs) in packing_data:
                packing_data[''.join(vs)] += 1
            else:
                packing_data[''.join(vs)] = 1

            for v in vs:
                if v in packing_data_per_book:
                    packing_data_per_book[v] += 1
                else:
                    packing_data_per_book[v] = 1

        with open('/var/www/python-realtime-poll-pusher/%s'%csv_out, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Write the header
            writer.writerow(csv_headers)

            # Write the rows
            writer.writerows(csv_data)

    print('</table><pre>')
    if packing:
        print()
        print(B.HEADER+B.UNDERLINE+'<h3 style="margin-bottom:0">PACKING LIST</h3>'+B.ENDC, end='')
        print(B.UNDERLINE+'<h4>Combined</h4>'+B.ENDC, end='')

        for k,v in packing_data.items():
            print('NLPA-{} x{}'.format(k,v))
        print()
        print(B.UNDERLINE+'<h4>Number of Books</h4>'+B.ENDC, end='')
        for k,v in packing_data_per_book.items():
            print('NLPA-{} x{}'.format(k,v))
        print()





    if report:
        num_by_vol_US = {
            '1': 0,
            '2': 0,
            '3': 0,
            '4': 0,
        }
        num_by_vol_ROW = {
            '1': 0,
            '2': 0,
            '3': 0,
            '4': 0,
        }

        for k, order in compiled_orders.items():

            if 'infilter' not in order:
                continue

            vs = order['vols']
            if order['country'] == 'US':
                for v in vs:
                    num_by_vol_US[v] += 1

            else:
                for v in vs:
                    num_by_vol_ROW[v] += 1
        print(B.HEADER+B.UNDERLINE+'<h3 style="margin-bottom:0">FULL REPORT</h3>'+B.ENDC, end='')
        print(B.UNDERLINE+'<h4>US Orders</h4>'+B.ENDC, end='')

        print('Vol 1 = {}'.format(num_by_vol_US['1']))
        print('Vol 2 = {}'.format(num_by_vol_US['2']))
        print('Vol 3 = {}'.format(num_by_vol_US['3']))
        print('Vol 4 = {}'.format(num_by_vol_US['4']))
        print()
        print(B.UNDERLINE+'<h4>ROW Orders</h4>'+B.ENDC, end='')

        print('Vol 1 = {}'.format(num_by_vol_ROW['1']))
        print('Vol 2 = {}'.format(num_by_vol_ROW['2']))
        print('Vol 3 = {}'.format(num_by_vol_ROW['3']))
        print('Vol 4 = {}'.format(num_by_vol_ROW['4']))
        print(B.UNDERLINE+'<h4>All Orders</h4>'+B.ENDC, end='')

        print('Vol 1 = {}'.format(num_by_vol_ROW['1']+num_by_vol_US['1']))
        print('Vol 2 = {}'.format(num_by_vol_ROW['2']+num_by_vol_US['2']))
        print('Vol 3 = {}'.format(num_by_vol_ROW['3']+num_by_vol_US['3']))
        print('Vol 4 = {}'.format(num_by_vol_ROW['4']+num_by_vol_US['4']))
        print()


    if printcsv:
        for k, order in compiled_orders.items():

            if 'infilter' not in order:
                continue
            printorder(order)
