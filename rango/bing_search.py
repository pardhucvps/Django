import json
from urllib import request, parse



def read_bing_key():
    bing_api_key = None
    try:
        with open('bing.key', 'r') as f:
            bing_api_key = f.readline()
    except:
        raise IOError('bing key file note found')
    return bing_api_key


def run_query(search_terms):
    bing_api_key = read_bing_key()
    if not bing_api_key:
        raise KeyError('Bing Key Not Found')
    root_url = 'https://api.datamarket.azure.com/Bing/Search'
    service = 'Web'
    results_per_page = 10
    offset = 0
    query = '{0}'.format(search_terms)
    query = parse.quote(query)
    print(query)
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(root_url, service, results_per_page, offset, query)
    print(search_url)
    username = ''
    password_mgr = request.HTTPPasswordMgrWithDefaultRealm()  # Py3

    password_mgr.add_password(None, search_url,username,bing_api_key)

    results = []

    try:
        handler = request.HTTPBasicAuthHandler(password_mgr)
        opener = request.build_opener(handler)
        request.install_opener(opener)
        response = request.urlopen(search_url).read()
        print('step4')
        response = response.decode('utf-8')
        print('step5')
        json_response = json.loads(response)
        for result in json_response['d']['results']:
            results.append({'title': result['Title'],
                            'link': result['Url'],
                            'summary': result['Description']})

    except:
       print("Error when querying the Bing API")

    return results


def main():
    query = input('Enter a Query')
    results = run_query(query)
    for result in results:
        print(result['title'])
        print('-' * len(result['title']))
        print(result['summary'])
        print(result['link'])
        print()


if __name__ == '__main__':
    main()