
'''
id: unique identifier
domains: List of string
'''
def write_blocklist(id, domains):
    # path = f"/etc/squid/blocked-${id}.txt"
    path = f"./blocked-{id}.txt"
    f = open(path, "w+")
    f.write("\n".join(domains))
    return path

def main():
    # conf_path = "/etc/squid/squid.conf"
    conf_path = "./squid.conf"
    block_list_path = write_blocklist("123", ["google.com", "facebook.com", "youtube.com"])
    src_ip = "10.0.0.0"
    f = open(conf_path, "a+")
    f.write(
        f'''
acl blocklist src {src_ip}    
acl block_domains dstdomain "{block_list_path}"
        '''
    )

main()
    