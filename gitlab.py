#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json

class Project:
   def __init__(self,group=None,name=None,id=None,ci_id=None,deps=[],token=None,ssh_url=None):
      self.id = id
      self.ci_id = ci_id
      self.group = group
      self.name = name
      self.deps = deps
      self.token = token
      self.ssh_url = ssh_url

   def __str__(self):
      d=[]
      for i in self.deps:
         d.append(str(i))
      return '{}:{},[deps={}],id={},ci_id={}'.format(self.group,self.name,','.join(d),self.id,self.ci_id)

   def __repr__(self):
      d=[]
      for i in self.deps:
         d.append(str(i))
      return '{}:{},[deps={}],id={},ci_id={}'.format(self.group,self.name,','.join(d),self.id,self.ci_id)

class GitLab:
   def __init__(self,url,token,registry_id,deps_sha):
      self.url=url
      self.token=token
      self.registry_id=registry_id
      self.deps_sha=deps_sha

   def get(self,urlPart):
      r = requests.get(self.url+urlPart,headers={'PRIVATE-TOKEN':self.token})
      r.raise_for_status()
      return r

   def projects(self):
      r = self.get('/projects')
      projectsRaw = r.json()
      return [Project(group=p['namespace']['name'],name=p['name'],id=p['id']) for p in projectsRaw]

   def project(self,id):
      r = self.get('/projects/'+str(id))
      p = r.json()
      return Project(group=p['namespace']['name'],name=p['name'],id=p['id'])

   def lastCommit(self,project_id):
      r = self.get('/projects/'+str(project_id)+'/repository/commits')
      return r.json()[0]

   def commits(self,project_id):
      r = self.get('/projects/'+str(project_id)+'/repository/commits')
      return r.json()

   def rawBlobs(self,project_id,sha):
      r = self.get('/projects/'+str(project_id)+'/repository/raw_blobs/'+sha)
      return r

   def depsBlobs(self):
      r = self.get('/projects/'+str(self.registry_id)+'/repository/raw_blobs/'+self.deps_sha)
      return [Project(p['name'].split(":")[0],p['name'].split(":")[1],deps=[Project(d.split(":")[0],d.split(":")[1]) for d in p['deps']]) for p in r.json()['projects']]

gitlab_url= 'http://git.agat/api/v3'

gl = GitLab(url=gitlab_url,token='MNJwAaG9x1P6VdZ7Fv_k',registry_id=7,deps_sha='67d87be8cf7efc32540777a0416fd8fba7eeee2a')

def printh(h):
   print '\n'
   print '='*(len(h)+15)
   print h
   print '='*(len(h)+15)

def test():
   printh('project get test...')
   for project in gl.projects():
      print '[{}]:{}:{}'.format(project.id,project.group,project.name)

   printh('get project by id')
   print gl.project(7)

   printh('rawBlobs test...')
   print gl.rawBlobs(7,'67d87be8cf7efc32540777a0416fd8fba7eeee2a').json()

   printh('deps get test...')
   print gl.depsBlobs()

   printh('get last commit...')
   print gl.lastCommit(7)

if __name__ == "__main__":
   test()

