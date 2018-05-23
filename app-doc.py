import json
import requests
import sys
import datetime

host = ''
port = ''
user = ''
password = ''
account = ''
linha = ''
cabecalho = ''
intervalo = ''
token = ''
cookies = ''

###TS;DURATION;SYSNM;OBJNM;SUBOBJNM;VALUE;DS_SYSNM
#2008-05-22 23:59:00;60;192.168.100.41;MEM_FREE;GLOBAL;2.22E7;192.168.100.41
#2008-05-22 23:58:00;60;192.168.100.41;CPU_UTIL;GLOBAL;0.002;192.168.100.41
#2008-05-22 23:59:00;60;192.168.100.41;SWAP_SPACE;GLOBAL;8.55E8;192.168.100.41

def get_applications():
    url = '{}:{}/controller/rest/applications'.format(host, port)
    auth = ('{}@{}'.format(user, account), password)
    params = {'output': 'json'}
    r = requests.get(url, auth=auth, params=params)
    return sorted(r.json(), key=lambda k: k['name'])

def get_average_response(app, tier, bt, file):
    url = '{}:{}/controller/rest/applications/{}/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{}%7C{}%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins={}&output=json'.format(host, port, app, tier, bt, intervalo)
    auth = ('{}@{}'.format(user, account), password)
    r = requests.get(url, auth=auth)
    
    for metric in r.json():
        linha = '{};{};{};Average Response Time total;{}'.format(cabecalho, app, bt, metric['metricValues'][0]['value'])
        file.write(linha + '\n')
    url = '{}:{}/controller/rest/applications/{}/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{}%7C{}%7CCalls%20per%20Minute&time-range-type=BEFORE_NOW&duration-in-mins={}&output=json'.format(host, port, app, tier, bt, intervalo)
    r = requests.get(url, auth=auth)

    for metric in r.json():
        linha = '{};{};{};Call per Minute por minuto;{}'.format(cabecalho, app, bt, metric['metricValues'][0]['value'])
        file.write(linha + '\n')
        linha = '{};{};{};Call per minute periodo;{}'.format(cabecalho, app, bt, metric['metricValues'][0]['sum'])
        file.write(linha + '\n')
    return 0

def get_business_transactions(app):
    url = '{}:{}/controller/rest/applications/{}/business-transactions?output=json'.format(host, port, app)
    auth = ('{}@{}'.format(user, account), password)
    params = {'output': 'json'}
    r = requests.get(url, auth=auth, params=params)
    if r.status_code == 200:
        file = open('{}.csv'.format(app),'w')
        #file.write("data, intervalo, application, business transaction, Average Response Time total, Call per Minute por minuto, Call per minute periodo" + '\n')

        for bt in r.json():
            if bt['name'] != '_APPDYNAMICS_DEFAULT_TX_':
                get_average_response(app, bt['tierName'], bt['name'], file)
                
        file.close
    return 0

def process():
    APPS = get_applications()
    for app in APPS:
        print(app['name'])
        get_business_transactions(app['name'])
    return 0


def main():
    global host
    global port
    global user
    global password
    global account
    global intervalo
    global cabecalho 

    if len(sys.argv) > 5:
        host = sys.argv[1] 
        port = sys.argv[2]
        user = sys.argv[3]
        password = sys.argv[4]
        account = sys.argv[5]
        intervalo = sys.argv[6]

        cabecalho = '{};{}'.format(datetime.datetime.now(), intervalo)
        print(datetime.datetime.now())
        process()
        print(datetime.datetime.now())
     else:
        print 'app-doc.py <http://host> <port> <user> <password> <account> <periodo>'
        sys.exit(2)

if __name__ == '__main__':
    main()
