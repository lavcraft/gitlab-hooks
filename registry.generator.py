#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
output example:
{
    "projects":[
        {
            "name":"demo-0:example-0",
            "deps":["agat:test"]
        },
        {
            "name":"demo-1:example-1",
            "deps":["agat:test"]
        },
        {
            "name":"demo-0:common-cmake",
            "deps":["agat:order-0"]
        },
        {
            "name":"demo-0:dep-0",
            "deps":["agat:order-0"]
        }
    ]
}
"""
import requests, json

gitlab_url= 'http://git.agat/api/v3'
token='MNJwAaG9x1P6VdZ7Fv_k'
def get(urlPart):
   r = requests.get(gitlab_url+urlPart,headers={'PRIVATE-TOKEN':token})
   r.raise_for_status()
   return r

# http://git.agat/api/v3/projects/demo-0%2Fexample-0

def printh(h):
   print '\n'
   print '='*100
   print h
   print '='*100

def writeDependencies():
   r = get('/projects')
   projects = r.json()
   result = { 'projects':[] }
   for i in (x for x in projects if x['namespace']['name'] != 'registry'):
      try:
         treeEntries = get('/projects/{}/repository/tree'.format(i['id'])).json()
         for entry in treeEntries:
            if entry['name'] == 'dependencies':
               depsText = get('/projects/{}/repository/raw_blobs/{}'.format(i['id'],entry['id'])).text
               result['projects'].append({
                     'name': '{}:{}'.format(i['namespace']['name'],i['name']),
                     'deps':[d.split(':')[0].replace('/',':') for d in ( z for z in depsText.split('\n') if z!='')]
                  })
      except:
         pass

   printh('''
   writing dependencies to file dependency.tmp...
   use
      `cat dependencies.tmp`
   for show result

   use
      `mv dependencies.tmp dependencies`
   for use as main dependency descriptor file
   ''')

   f = open('dependencies.tmp', 'w')
   f.write(json.dumps(result,indent=2, sort_keys=True))
   f.close()

if __name__ == "__main__":
   writeDependencies()

