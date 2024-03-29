import os
import requests
from inspect import cleandoc

def make_pulls_query():
    url='https://api.github.com/graphql'
    auth = {'Authorization': 'Bearer {token}'.format(token=os.environ['TOKEN'])}
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
              name
              owner {{
                login
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    more_pages = True
    after_token = 'null'
    pushed_repos = {}
    while more_pages:
        maybe_query = requests.post(url, json={'query': query_template.format(after=after_token)}, headers=auth)
        maybe_query.raise_for_status()
        if errors := maybe_query.json().get('errors'): print(errors)
        pulls = maybe_query.json()['data']['user']['pullRequests']
        more_pages = pulls['pageInfo']['hasNextPage']
        after_token = pulls['pageInfo']['endCursor']
        pushed_repos |= {
            f"{node['repository']['name']}/{node['repository']['owner']['login']}": {
                'stars': node['repository']['stargazerCount'],
                'name': node['repository']['name'],
                'org': node['repository']['owner']['login']
            }
            for node in pulls['nodes']
        }
    return pushed_repos


def filter_and_sort_repos(repos):
    return [
        (repos[r]['org'], repos[r]['name'])
        for r in sorted(
            repos,
            key=lambda k: repos[k]['stars'],
            reverse=True,
        )
        if repos[r]['org'] not in ('ucodery', 'ActiveState')
    ]


def build_html(colab_repos):
    html_template = cleandoc('''
    <a href="https://github.com/{user}/{repo}">
      <picture>
        <source
          srcset="https://github-readme-stats.vercel.app/api/pin/?username={user}&repo={repo}&show_owner=true&theme=dark"
          media="(prefers-color-scheme: dark)"
        />
        <source
          srcset="https://github-readme-stats.vercel.app/api/pin/?username={user}&repo={repo}&show_owner=true"
          media="(prefers-color-scheme: light), (prefers-color-scheme: no-preference)"
        />
        <img src="https://github-readme-stats.vercel.app/api/pin/?username={user}&repo={repo}&show_owner=true" />
      </picture>
    </a>
    ''')
    return '\n'.join(html_template.format(user=user, repo=repo) for user, repo in colab_repos) + '\n'


def replace_readme(extra_content):
    with open('README.md', 'r') as readme_read, open('README.new', 'w') as readme_write:
        for line in readme_read:
            readme_write.write(line)
            if line.strip() == '<!-- replace start -->':
                readme_write.write(extra_content)
                while line.strip() != '<!-- replace end -->':
                    line = next(readme_read)
                readme_write.write(line)
    os.rename('README.new', 'README.md')


if __name__ == '__main__':
    repos = make_pulls_query()
    readme_repos = filter_and_sort_repos(repos)
    html = build_html(readme_repos)
    replace_readme(html)
