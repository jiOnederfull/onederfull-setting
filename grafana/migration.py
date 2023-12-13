#!/usr/bin/env python3

import json
import os
import urllib.request

org_domain = os.getenv('ORG_DOMAIN')
org_apikey = os.getenv('ORG_APIKEY')
new_domain = os.getenv('NEW_DOMAIN')
new_apikey = os.getenv('NEW_APIKEY')

print('ORG_DOMAIN :', org_domain)
print('ORG_APIKEY :', org_apikey)
print('NEW_DOMAIN :', new_domain)
print('NEW_APIKEY :', new_apikey)

def get(url, apikey):
    try:
        req = urllib.request.Request(url)
        req.add_header('Authorization', 'Bearer {}'.format(apikey))
        with urllib.request.urlopen(req) as res:
            data = res.read()
        return json.loads(data)
    except Exception as e:
        raise e

def post(url, apikey, data):
    try:
        d = json.dumps(data).encode()
        req = urllib.request.Request(url, data=d)
        req.add_header('Authorization', 'Bearer {}'.format(apikey))
        req.add_header('Content-Type', 'application/json')
        res = urllib.request.urlopen(req)
    except Exception as e:
        print(e)

def migration_datasources():
    print('------- DATA SOURCES ------')
    try:
        data = get('http://{}/api/datasources'.format(org_domain), org_apikey)
        with open('./data/datasources.json', 'w') as f:
            f.write(json.dumps(data))
    except:
        pass

    for d in data:
        post('http://{}/api/datasources'.format(new_domain), new_apikey, d)

def migration_folder():
    print('--------- FOLDER ----------')
    try:
        data = get('http://{}/api/folders'.format(org_domain), org_apikey)
        with open('./data/folders.json', 'w') as f:
            f.write(json.dumps(data))
    except:
        pass

    for d in data:
        post('http://{}/api/folders'.format(new_domain), new_apikey, d)

def migration_dashboard():
    print('-------- DASHBOARD --------')
    try:
        data = get('http://{}/api/search'.format(org_domain), org_apikey)
        dashboards = []
        for d in data:
            dashboard = get('http://{}/api/dashboards/uid/{}'.format(org_domain, d['uid']), org_apikey)
            if dashboard['meta']['isFolder']:
                continue
            dashboards.append(dashboard)

        with open('./data/dashboards.json', 'w') as f:
             f.write(json.dumps(dashboards))
    except:
        pass

    with open('./data/dashboards.json', 'r') as f:
        for dashboard in json.load(f):
            folderId = 0
            uid = None
            with open('./data/folders.json', 'r') as f:
                for d in json.load(f):
                    if d['id'] == dashboard['meta']['folderId']:
                        uid = d['uid']
                        break

            if uid:
                folderId = get('http://{}/api/folders/{}'.format(new_domain, uid), new_apikey)['id']

            dashboard['folderId'] = folderId
            dashboard['inputs'] = []
            dashboard['overwrite'] = False
            del dashboard['meta']
            dashboard['dashboard']['id'] = None

            post('http://{}/api/dashboards/import'.format(new_domain), new_apikey, dashboard)

if __name__ == '__main__':
    if not new_domain or not new_apikey:
        print('NEW is empty.')
        exit(0)

    print('========== START ==========')
    migration_datasources()
    migration_folder()
    migration_dashboard()
    print('==========  END  ==========')
