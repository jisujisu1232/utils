from ipwhois import IPWhois
from pprint import pprint


def main(ip32):
    ip_obj = IPWhois(ip32.split('/')[0])
    #pprint(ip_obj.lookup_whois())
    pprint(ip_obj.lookup_whois()['asn_description'])


if __name__ == '__main__':
    # main(sys.argv[1:])
    main('123.123.123.123')
