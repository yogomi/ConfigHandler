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

data=dict(mac="22:22:22:22:22:22")
print ch.setDhcpClient(data)
print ch.getAttrDictList(["haconfig", "dhcp", "clientList"], "client")

data=dict(mac="22:22:22:22:22:00", item_id="1")
print ch.setDhcpClient(data)
print ch.getAttrDictList(["haconfig", "dhcp", "clientList"], "client")

print ch.delDhcpClient("0,3")
print ch.getAttrDictList(["haconfig", "dhcp", "clientList"], "client")

print ch.delDhcpClient("all")
print ch.getAttrDictList(["haconfig", "dhcp", "clientList"], "client")

ch.write("output.xml")
ch.write()

#ch.setElements(dict(abc="bb", add="aa"))

