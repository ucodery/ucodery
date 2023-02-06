import requests

def make_pulls_query():
    url='https://api.github.com/graphql'
    query_template = '''
    {
      viewer {
      id
        pullRequests(last: 100, states: MERGED) {
         pageInfo {
          hasNextPage
          endCursor
        }
         nodes {
           repository {
             url
             visibility
             owner {
              id
             }
           }
         }
        }
      }
    }
    '''
    auth = {'Authorization': 'Bearer {token}'.format(token=os.environ['GITHUB_TOKEN'])}
    more_pages = True
    after_token = 'null'
    pushed_repos = set()
    while more_pages:
        maybe_query = requests.post(url, json={'query': query_template.format(after=after_token)}, headers=auth)
        maybe_query.raise_for_status()
        viewer = maybe_query.json()['data']['viewer']
        my_id = viewer['id']
        pulls = viewer['pullRequests']
        more_pages = pulls['pageInfo']['hasNextPage']
        after_token = pulls['pageInfo']['endCursor']
        for node in pulls['nodes']:
            repo = node['repository']
            if repo['visability'] == 'PUBLIC' and repo['owner']['id'] != my_id:
                pushed_repos.add(repo['url'])
    return pushed_repos
        

if __name__ == '__main__':
    print(sorted(make_pulls_query()))
