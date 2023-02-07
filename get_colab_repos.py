import os
import requests

def make_pulls_query():
    url='https://api.github.com/graphql'
    query_template = '''
    {{
      viewer {{
        id
        pullRequests(first: 100, states: MERGED, after: {after}) {{
          pageInfo {{
            hasNextPage
            endCursor
          }}
          nodes {{
            repository {{
              url
              visibility
              owner {{
                id
              }}
              stargazerCount
            }}
          }}
        }}
      }}
    }}
    '''
    auth = {'Authorization': 'Bearer {token}'.format(token=os.environ['TOKEN'])}
    more_pages = True
    after_token = 'null'
    pushed_repos = {}
    while more_pages:
        maybe_query = requests.post(url, json={'query': query_template.format(after=after_token)}, headers=auth)
        maybe_query.raise_for_status()
        if errors := maybe_query.json().get('errors'):
                print(errors)
        viewer = maybe_query.json()['data']['viewer']
        my_id = viewer['id']
        pulls = viewer['pullRequests']
        more_pages = pulls['pageInfo']['hasNextPage']
        after_token = pulls['pageInfo']['endCursor']
        print('#', len(pulls['nodes']))
        for node in pulls['nodes']:
            repo = node['repository']
            if repo['visability'] == 'PUBLIC' and repo['owner']['id'] != my_id:
                pushed_repos[repo['url']] = repo['stargazerCount']
    return pushed_repos
        

if __name__ == '__main__':
    print(sorted(make_pulls_query()))
