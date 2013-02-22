#!/usr/bin/python
import sys

import XMLConfHandler

ch=XMLConfHandler.XMLConfig()
ch.open("CommonSetting.xml")

section=["haconfig", "dhcp", "server"]

#ch.getElements(".".join(section))

print ch.getAttr(["haconfig", "dhcp", "server", "delete_lease_info"], "minute" )
print ch.getAttrDict(["haconfig", "dhcp", "server", "delete_lease_info"])
print ch.getAttrDictList(["haconfig", "dhcp", "clientList"], "client")
print ch.getAttrDictList(["haconfig", "dhcp", "clientList"], "client", 1, 1)
#ch.setElements(dict(abc="bb", add="aa"))

