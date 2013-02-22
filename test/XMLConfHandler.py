import xml.dom, xml.dom.minidom
import os
import sys

MAX_COMMON_CLIENT = 25000

class XMLConfig:
    doc=None
    filename=""
    def open(self, f):
        self.doc = xml.dom.minidom.parse(f)

    def getAttr(self, tag_list, key):
        print tag_list
        elems=self._getElements(self.doc, tag_list[0], True)
        for tag in tag_list[1:]:
            elems=self._getElements(elems[0], tag, True)
        return elems[0].getAttribute(key)

    def getAttrDict(self, tag_list):
        elems=self._getElements(self.doc, tag_list[0], True)
        for tag in tag_list[1:]:
            elems=self._getElements(elems[0], tag, True)
        dic = dict()
        for key in elems[0].attributes.keys():
            dic[key] = elems[0].getAttribute(key)
        return dic

    def getAttrDictList(self, tag_list, enum_key_tag, start=0, limit=None):
        _id=start
        elems=self._getElements(self.doc, tag_list[0], True)
        for tag in tag_list[1:]:
            elems=self._getElements(elems[0], tag, True)
        elems=self._getElements(elems[0], enum_key_tag, True)
        l=[]
        es=elems[start:]
        if limit:
            es=elems[start:start+limit]
        for elem in es:
            dic = dict(id=_id)
            for key in elems[0].attributes.keys():
                dic[key] = elems[0].getAttribute(key)
            l.append(dic)
            _id=_id+1
        return l
    
    def setDhcpClient(self, data):
        items = []
        try:
            items = self.getAttrDicList(["haconfig", "dhcp", "clientList"],
               'client')
        except TypeError, e:
            pass
        for i in range(len(items)):
            if items[i]['mac'] == data['mac']:
                if data.has_key('item_id'):
                    if i != int(data['item_id']):
                        raise ValueError('duplication')
                else:
                    raise ValueError('duplication')

        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "clientList")
        client = self.doc.createElement("client")
        client.setAttribute("mac", data['mac'])

        if data.has_key('item_id'):
            op = 'edit'
            elems = self._getElements(elems[0], "client")
            elems[0].parentNode.replaceChild(client,elems[int(data['item_id'])])
        else:
            op = 'add'
            items = self.getDhcpClientList()
            if len(items) > MAX_COMMON_CLIENT:
                raise TypeError('full')
            elems[0].appendChild(client)

    def delDhcpClient(self, _id):
        logDic = []
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "clientList")
        if id == "all":
            op = "all_delete"
            elems[0].parentNode.removeChild(elems[0])
        else:
            op = "delete"
            list = id.split(",")
            list.sort(reverse=True)
            for i in range(len(list)):
                items = self.getDhcpClient(list[i])
                logDic.append({'mac': items['mac']})
            elems = self._getElements(elems[0], "client")
            for i in range(len(list)):
                elems[0].parentNode.removeChild(elems[int(list[i])])

    def write():
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

    def _getElements(self, elem, tagname, ro = False):
        if len(elem.getElementsByTagName(tagname)) <= 0:
            if ro:
                raise ValueError
            else:
               child = self.doc.createElement(tagname)
               elem.appendChild(child)
        return elem.getElementsByTagName(tagname)


