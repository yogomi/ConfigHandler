#!/usr/bin/python
import sys

sys.path.append("../lib")

import XMLConfHandler

ch=XMLConfHandler.XMLConfig()
ch.open("CommonSetting.xml")

section=["haconfig", "dhcp", "server"]

#ch.getElements(".".join(section))

ch.read("haconfig.dhcp.server.delete_lease_info.<xmlattr>.hour")

