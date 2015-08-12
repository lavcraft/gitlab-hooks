#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json

from gitlab import Project

class GitLabCi:
   def __init__(self,url,token):
      self.url=url
      self.token=token

   def get(self,urlPart):
      r = requests.get(self.url+urlPart,headers={'PRIVATE-TOKEN':self.token})
      r.raise_for_status()
      return r

   def post(self,urlPart,data,params=[]):
      r = requests.post(self.url+urlPart,data=json.dumps(data),headers={'PRIVATE-TOKEN':self.token,'Content-Type':'application/json'},params=params)
      r.raise_for_status()
      return r

   def projects(self):
      r = self.get('/projects')
      projectsRaw = r.json()
      projects = []
      for p in projectsRaw:
         ciname = p['name']
         arr = ciname.split('/')
         name = arr[1].strip()
         group = arr[0].strip()
         projects.append(Project(name=name,group=group,token=p['token'],id=p['gitlab_id'],ci_id=p['id'],ssh_url=p['ssh_url_to_repo']))

      return projects

   def project(self,id):
      r = self.get('/projects/'+str(id))
      p = r.json()
      ciname = p['name']
      arr = ciname.split('/')
      name = arr[1].strip()
      group = arr[0].strip()
      return Project(name=name,group=group,token=p['token'],id=p['gitlab_id'],ci_id=p['id'],ssh_url=p['ssh_url_to_repo'])

   def commit(self,ref,after,project,before=None):
      r = self.post(urlPart='/commits',data={'data':{'ref':ref,'after':after,'before':before}},params={'project_id':project.ci_id,'project_token':project.token})
      return r


gl = GitLabCi(url='http://ci.agat/api/v1',token='MNJwAaG9x1P6VdZ7Fv_k')

def printh(h):
   print '\n'
   print '='*(len(h)+15)
   print h
   print '='*(len(h)+15)

def test():
   printh('project get test...')
   for project in gl.projects():
      print '[{}]:{}:{}-{}'.format(project.ci_id,project.group,project.name,project.token)

   printh('get project by id')
   project = gl.project(6)
   print '[{}]:{}:{}-{}'.format(project.ci_id,project.group,project.name,project.token)
   print project

   printh('post commit')
   proj = Project(ci_id=6,token='bfffda166e3934c9a73fd67a4ba0b2')
   print gl.commit(ref='refs/heads/master',project=proj,before='c3c39b43f160c2efed5bbc16d15e91eab3c2ec22',after='5539ffc98f07777b6360e976cbc7a796bb61e315').json()

if __name__ == "__main__":
   test()

