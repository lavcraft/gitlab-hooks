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
        project_id = a['project_id']
        project = self.gl.project(project_id)
        deps = self.gl.depsBlobs()
        print '='*100
        for i in deps:
           if i.name == project.name and i.group == project.group:
              project.deps = i.deps

        ciprojects = self.glc.projects()

        for i in ciprojects:
           for v in project.deps:
              if i.name == v.name and i.group == v.group:
                 project_dir = '/git/'+str(i.id)
                 if os.path.exists(project_dir):
                    print 'repository exist. pull...'
                    call(['git','fetch','origin'],cwd=project_dir)
                 else:
                    print 'clone repository...'
                    call(['git','clone',ssh_url,'/git/'+str(i.id)])

                 print 'customize build project'
                 #call(['git','checkout',after],cwd=project_dir)
                 build_branch='build/number-'+strftime("%Y-%m-%d_%H_%M_%S", gmtime())
                 call(['git','checkout','-b',build_branch],cwd=project_dir)

                 if ref.startswith('refs/heads/build'):
                    self.send_response(200)
                    return

                 if os.path.exists(project_dir+'/manage.dependency'):
                    call(['./manage.dependency'],cwd=project_dir)
                    call(['git','add','.'],cwd=project_dir)
                    print 'Commit new files'
                    call(['git','commit','-m','automate'],cwd=project_dir)
                    print 'push branch {} to remote'.format(build_branch)
                    call(['git','push','origin',build_branch],cwd=project_dir)

                 #commits = self.gl.commits(i.id)
                 #last_commit = commits[0]['id']
                 #prev_commit = commits[1]['id']
                 #print 'rebuild project {} last commit: {}'.format(i,last_commit)
                 #self.glc.commit(ref='refs/heads/master',project=i,before=prev_commit,after=last_commit).json()


        before = a['before']
        after = a['after']
        ref= a['ref']
        ssh_url = a['repository']['git_ssh_url']
        print 'handle project #{}[{}:{}] with before:{} and after:{}'.format(project_id,ssh_url,ref,before,after)
        request_stop_log()

        if ref.startswith('refs/heads/build'):
           self.send_response(200)
           return

        project_dir = '/git/'+str(project_id)
        if os.path.exists(project_dir):
           print 'repository exist. pull...'
           call(['git','fetch','origin'],cwd=project_dir)
        else:
           print 'clone repository...'
           call(['git','clone',ssh_url,'/git/'+str(project_id)])

        print 'customize build project'
        call(['git','checkout',after],cwd=project_dir)
        build_branch='build/number-'+strftime("%Y-%m-%d_%H_%M_%S", gmtime())
        call(['git','checkout','-b',build_branch],cwd=project_dir)

        if os.path.exists(project_dir+'/manage.dependency'):
           call(['./manage.dependency'],cwd=project_dir)
           print 'push branch {} to remote'.format(build_branch)
           call(['git','push','origin',build_branch],cwd=project_dir)

        self.send_response(200)

    do_PUT = do_POST
    do_DELETE = do_GET

def main():
    port = 50000
    print('Listening on localhost:%s' % port)
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()

main()
