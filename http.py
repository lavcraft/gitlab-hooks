#!/usr/bin/env python

import json,os
from gitlab import GitLab, Project
from gitlabci import GitLabCi
from time import gmtime, strftime
from subprocess import call
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

def request_start_log():
        print("S========================>\n")

def request_stop_log():
        print("X========================>\n")

class RequestHandler(BaseHTTPRequestHandler):
    gl = GitLab(url='http://git.agat/api/v3',token='MNJwAaG9x1P6VdZ7Fv_k',registry_id=7,deps_sha='148dbe295770028a22d7492e93cddf37a8a7f2c1')
    glc = GitLabCi(url='http://ci.agat/api/v1',token='MNJwAaG9x1P6VdZ7Fv_k')

    def do_GET(self):
        request_path = self.path

        request_start_log()
        print(request_path)
        print(self.headers)
        request_stop_log()

        self.send_response(200)

    def do_POST(self):
        request_path = self.path

        request_start_log()
        request_headers = self.headers
        content_length = request_headers.getheaders('content-length')
        length = int(content_length[0]) if content_length else 0
        content = self.rfile.read(length)

        a = json.loads(content)
        # init push event arguments
        before = a['before']
        after = a['after']
        ref= a['ref']
        ssh_url = a['repository']['git_ssh_url']
        project_id = a['project_id']

        # skip automatically rebuilded project
        if ref.startswith('refs/heads/build'):
           self.send_response(200)
           return

        # handle project dependencies and init some action
        print 'handle project #{}[{}:{}] with before:{} and after:{}'.format(project_id,ssh_url,ref,before,after)

        project = self.gl.project(project_id)
        deps = self.gl.depsBlobs() # deps from registry/order specific project who contain projects and dependencoes matches

        for i in deps: # find current project dependencies and set them
           if i.name == project.name and i.group == project.group:
              project.deps = i.deps

        ciprojects = self.glc.projects() # get all GitLab CI projects

        for i in ciprojects: # start find specific project in gitlab ci by name and group. Not optimal
           for v in project.deps:
              if i.name == v.name and i.group == v.group:
                 project_dir = '/git/'+str(i.id)+'-'+after
                 if os.path.exists(project_dir):
                    print 'repository exist. pull...'
                    call(['git','checkout','master'],cwd=project_dir)
                    call(['git','pull'],cwd=project_dir)
                 else:
                    print 'clone repository...'
                    call(['git','clone',i.ssh_url,project_dir])

                 print 'customize build project...'
                 #call(['git','checkout',after],cwd=project_dir)
                 build_branch='build/number-'+strftime("%Y-%m-%d_%H_%M_%S", gmtime())
                 call(['git','checkout','-b',build_branch],cwd=project_dir)

                 if os.path.exists(project_dir+'/manage.dependency'):
                    call(['./manage.dependency'],cwd=project_dir)
                    call(['git','add','.'],cwd=project_dir)
                    print 'Commit new files'
                    call(['git','commit','-m','automate'],cwd=project_dir)
                    print 'push branch {} to remote'.format(build_branch)
                    call(['git','push','origin',build_branch],cwd=project_dir)

                 # init phantom commit
                 #commits = self.gl.commits(i.id)
                 #last_commit = commits[0]['id']
                 #prev_commit = commits[1]['id']
                 #print 'rebuild project {} last commit: {}'.format(i,last_commit)
                 #self.glc.commit(ref='refs/heads/master',project=i,before=prev_commit,after=last_commit).json()

        request_stop_log()

        self.send_response(200)

    do_PUT = do_POST
    do_DELETE = do_GET

def main():
    port = 50000
    print('Listening on localhost:%s' % port)
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()

main()
