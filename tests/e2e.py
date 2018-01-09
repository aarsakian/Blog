import urllib2
import logging

HOST='https://arsakian.com'

# [START e2e]
response = urllib2.urlopen("{}".format(HOST))
html = response.read()
assert("Armen Arsakian personal blog" in html)
# [END e2e]