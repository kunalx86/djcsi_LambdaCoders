from urllib.parse import urlparse

def read_file_into_list(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    return lines

def is_in_blocked_list(url, blocked_list):
    parsed_url = urlparse(url)
    for fqdn in blocked_list:
        if parsed_url.netloc == fqdn:
            return True
    return False
  
file = 'sites.txt'
blocked_list=read_file_into_list(file)

url='https://www.instagram.com/stories/bhand.engineer/3075886021175968821/'
url='https://stackoverflow.com/questions/61641533/javascript-how-to-check-for-url-with-specific-domain-name'
print(is_in_blocked_list(url,blocked_list))


