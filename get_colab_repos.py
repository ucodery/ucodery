import os
import requests

def make_pulls_query():
    url='https://api.github.com/graphql'
    query_template = '''
    {{
      user(login: "ucodery") {{
        pullRequests(states: MERGED, first: 100, after: {after}) {{
          pageInfo {{
            hasNextPage
            endCursor
          }}
          nodes {{
            repository {{
              stargazerCount
              url
              owner {{
                login
              }}
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
        pulls = maybe_query.json()['data']['user']['pullRequests']
        more_pages = pulls['pageInfo']['hasNextPage']
        after_token = pulls['pageInfo']['endCursor']
        for node in pulls['nodes']:
            repo = node['repository']
            if repo['owner']['login'] not in ('ucodery', 'ActiveState'):
                pushed_repos[repo['url']] = repo['stargazerCount']
    return pushed_repos
        

if __name__ == '__main__':
    repos = make_pulls_query()
    print(sorted(repos, key=repos.get))
