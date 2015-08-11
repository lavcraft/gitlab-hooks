# gitlab-hooks

# Configuration

Need to configure next properties:
* *url* gitlab and gitlab ci entrypoint
* *token* for authentication in gitlab API
* *registry_id* for search projects dependencies in project with id..
* *deps_sha* registry project version, need set last valid version

Configure properties in this lines [http.py]:
```python
gl = GitLab(url='http://git.agat/api/v3',token='MNJwAaG9x1P6VdZ7Fv_k',registry_id=7,deps_sha='148dbe295770028a22d7492e93cddf37a8a7f2c1')
glc = GitLabCi(url='http://ci.agat/api/v1',token='MNJwAaG9x1P6VdZ7Fv_k')
```
