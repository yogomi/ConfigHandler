# -*- coding: utf-8 -*-
# NetAttest D3Managerアプライアンス システム設定ファイル

import xml.dom, xml.dom.minidom
import os
import sys

from ValidChecker import IsMacAddress
from ValidChecker import is_address
from ValidChecker import is_null_or_address
from ValidChecker import IsSubnetMask
from ValidChecker import IsNullOrGoodIpAddresses
from ValidChecker import IsNullOrGoodZoneName
from ValidChecker import IsGoodHostName
from ValidChecker import IsValidMailAddress
from ValidChecker import IsNaGlobalHostName
from ValidChecker import IsDUIDAddress
from IPy import IPint,IP
import ndlog

OPCODE_ADD = 0
OPCODE_ADD_DIFFERENCE = 1
OPCODE_REPLACE = 2
OPCODE_DELETE = 3

MAX_COMMON_CLIENT = 25000

class ConfigManager:
    def __init__(self, f):
        if(os.access(f, os.W_OK)):
            try:
                self.doc = xml.dom.minidom.parse(f)
            except Exception, e:
                print("Error reading %s", repr(f))
                print(str(e))
                sys.exit(1)
        else:
            print("Not found '%s'", repr(f))
            print("Open new file.")
            self.doc = xml.dom.minidom.parseString('<?xml version="1.0" encoding="UTF-8"?><haconfig></haconfig>')
        self.filename = f
        self.syslog = ndlog.NdLog()

    def getSessionTime(self):
        # この関数の処理は全てC++に置き換える必要があります
        elems = self._getElements(self.doc, "tenantsetting", True)
        elems = self._getElements(elems[0], "sessionTimeOut", True)
        for elem in elems:
            hour = elem.getAttribute('hour')
            minute = elem.getAttribute('minute')
        return int(hour) * 60 + int(minute)

    def setHomeConf(self, data):
        op = 'set'
        error_code = []
        try:
            items = self.getHomeConf()
        except TypeError, e:
            pass

        try:
            if int(data['hour']) > 168 or int(data['hour']) < 0 or int(data['minute']) > 59 or int(data['minute']) < 0:
                error_code.append(41)
            if int(data['hour']) == 0 and int(data['minute']) == 0:
                error_code.append(41)
        except ValueError:
            error_code.append(42)
        if error_code != []:
            return error_code
        home = self.doc.createElement("sessionTimeOut")
        logDic = {}
        elems = self._getElements(self.doc, "tenantsetting", True)
        elems = self._getElements(elems[0], "sessionTimeOut", True)

        home.setAttribute('hour', data['hour'])
        home.setAttribute('minute', data['minute'])
        logDic['hour'] = data['hour']
        logDic['minute'] = data['minute']

        elems[0].parentNode.replaceChild(home,elems[0])

        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        # ログ出力
        service = 'home'
        section = 'session'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def getHomeConf(self):
        # この関数の処理は全てC++に置き換える必要があります
        elems = self._getElements(self.doc, "tenantsetting", True)
        elems = self._getElements(elems[0], "sessionTimeOut", True)
        for elem in elems:
            items = {
                'hour':elem.getAttribute('hour')
                , 'minute':elem.getAttribute('minute')
            }
        return items

    def setHA(self, tenant, name):
        # 仮重複チェック C++に以降
        items = []
        op = 'add'
        logDic = {}
        try:
            items = self.getHAList(tenant)
        except TypeError, e:
            pass
        for i in range(len(items)):
            if items[i]['text'] == name:
                return 422
        # xmlファイル内を参照しリストに追加 C++に移行した場合記述を削除する
        elems = self._getElements(self.doc, "tenantlist", True)
        elems = self._getElements(elems[0], "tenant", True)
        for elem in elems:
            if elem.getAttribute('name') == tenant:
                halist = self._getElements(elem, "halist", True)
                ha = self.doc.createElement("ha")
                ha.setAttribute("name", name)
                halist[0].appendChild(ha)
        logDic['ha'] = name

        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        # ログ出力
        service = 'd3m'
        section = 'ha'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def getHAList(self, tenant):
        # この関数の処理は全てC++に置き換える必要があります
        elems = self._getElements(self.doc, "tenantlist", True)
        elems = self._getElements(elems[0], "tenant", True)
        items = []
        for elem in elems:
            if elem.getAttribute('name') == tenant:
                try:
                    halist = self._getElements(elem, "halist", True)
                    halist = self._getElements(halist[0], "ha", True)
                except ValueError:
                    return items
                try:
                    for ha in halist:
                        items.append({
                            'text':ha.getAttribute('name'),
                            'leaf':True
                        })
                except TypeError:
                    return items
        return items

    def delHA(self, tenant, name):
        op = 'delete'
        logDic = {}
        # xmlファイル内を参照 C++に移行した場合記述を削除する#
        elems = self._getElements(self.doc, "tenantlist", True)
        elems = self._getElements(elems[0], "tenant", True)
        for elem in elems:
            if elem.getAttribute('name') == tenant:
                halist = self._getElements(elem, "halist", True)
                halist = self._getElements(halist[0], "ha")
                id = 0
                for ha in halist:
                    if ha.getAttribute('name') == name:
                        halist[0].parentNode.removeChild(halist[id])
                    id += 1
        logDic['ha'] = name
        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()
        # ログ出力
        service = 'd3m'
        section = 'ha'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def getCommonMenu(self):
        items = []
        #dns
        items.append({
            'name':'dns',
            'expanded':False,
            'children':[{
                'name':'server_setting',
                'form':'dns.Server',
                'leaf':True
            },{
                'name':'parent_dns_setting',
                'form':'dns.ParentDNS',
                'leaf':True
            }]
        })
        #dhcp
        items.append({
            'name':'dhcp',
            'expanded':False,
            'children':[{
                'name':'server_setting',
                'form':'dhcp.Server',
                'leaf':True
            },{
                'name':'client',
                'form':'dhcp.Client',
                'leaf':True
            },{
                'name':'nap_setting',
                'form':'dhcp.NAP',
                'leaf':True
            }]
        })
        #dhcpv6
        items.append({
            'name':'dhcpv6',
            'expanded':False,
            'children':[{
                'name':'server_setting',
                'form':'dhcpv6.Serverv6',
                'leaf':True
            },{
                'name':'client',
                'form':'dhcpv6.Clientv6',
                'leaf':True
            }]
        })
        return items

    def getMenu(self,expanded):
        items = []
        #dns
        items.append({
            'name':'dns',
            'expanded':False,
            'children':[{
                'name':'server_setting',
                'form':'Form',
                'type':'dns_server',
                'leaf':True
            },{
                'name':'zone',
                'form':'List',
                'type':'zone',
                'expanded':False,
                'children':[]
            },{
                'name':'easy_zone_setup',
                'form':'Form',
                'type':'easy_zone',
                'leaf':True
            },{
                'name':'parent_dns_setting',
                'form':'Form',
                'type':'parent_dns',
                'leaf':True
            },{
                'name':'recursion_dns_setting',
                'form':'Form',
                'type':'recursion_dns',
                'leaf':True
            },{
                'name':'root_server_setting',
                'form':'List',
                'type':'root_server',
                'leaf':True
            },{
                'name':'trust_anchor_setting',
                'form':'List',
                'type':'trust_anchor',
                'leaf':True
            }]
        })
        #dhcp
        scopeList = []
        scopes = self.getDhcpScopeList()
        for i in range(len(scopes)):
            scopeList.append({
                'text':scopes[i]['network'],
                'expanded':False,
                'children': [{
                    'ID':i,
                    'name':'range',
                    'form':'List',
                    'type':'range',
                    'leaf':True
                },{
                    'ID':i,
                    'name':'vendor_code_filter',
                    'form':'List',
                    'type':'vendor_code_filter',
                    'leaf':True
                },{
                    'ID':i,
                    'name':'client_configuration',
                    'form':'scope',
                    'type':'client_configuration',
                    'leaf':True
                }]
            })
        items.append({
            'name':'dhcp',
            'expanded':False,
            'children':[{
                'name':'server_setting',
                'form':'Form',
                'type':'dhcpServer',
                'leaf':True
            },{
                'name':'scope',
                'form':'List',
                'type':'scope',
                'expanded':False,
                'children':scopeList
            },{
                'name':'client',
                'form':'List',
                'type':'client',
                'leaf':True
            },{
                'name':'host',
                'form':'List',
                'type':'host',
                'leaf':True
            },{
                'name':'ha_setting',
                'form':'Form',
                'type':'ha',
                'leaf':True
            },{
                'name':'user_option',
                'form':'List',
                'type':'userOption',
                'leaf':True
            },{
                'name':'vendor_option',
                'form':'List',
                'type':'vendorOption',
                'leaf':True
            },{
                'name':'nap_setting',
                'form':'Form',
                'type':'nap',
                'leaf':True
            }]
        })
        #dhcpv6
        items.append({
            'name':'dhcpv6',
            'expanded':False,
            'children':[{
                'name':'server_setting',
                'form':'Form',
                'type':'dhcp_server_v6',
                'leaf':True
            },{
                'name':'scope',
                'form':'List',
                'type':'scope_v6',
                'expanded':False,
                'children':[]
            },{
                'name':'client',
                'form':'List',
                'type':'client_v6',
                'leaf':True
            },{
                'name':'host',
                'form':'List',
                'type':'host_v6',
                'leaf':True
            },{
                'name':'ha_setting',
                'form':'Form',
                'type':'ha_v6',
                'leaf':True
            },{
                'name':'user_option',
                'form':'List',
                'type':'user_option_v6',
                'leaf':True
            }]
        })
        if expanded != 'undefined':
            if expanded == 'scope':
                items[1]['expanded'] = True
                items[1]['children'][1]['expanded'] = True
        return items

    def setDhcpServerConf(self, data):
        op = 'set'
        error_code = []
        try:
            items = self.getDhcpServerConf()
        except TypeError, e:
            pass

        server = self.doc.createElement("server")
        use_common_setting = ""
        logDic = {}
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp", True)
        elems = self._getElements(elems[0], "server", True)

        if data.has_key('name'):
            logDic['name'] = data['name']
            if data['use_vip'] == 'on':
                if not is_address(data['vip']):
                    error_code.append(46)
            else:
                data['vip'] = items['vip']
            server.setAttribute('use_vip', data['use_vip'])
            server.setAttribute('vip', data['vip'])
            logDic['use_common_setting'] = data['use_common_setting']
            logDic['use_vip'] = data['use_vip']
            logDic['vip'] = data['vip']
            server.setAttribute('use_common_setting', data['use_common_setting'])
            use_common_setting = data['use_common_setting']

        if use_common_setting == "":
            if data['sun'] == 'on' or data['mon'] == 'on' or data['tues'] == 'on' or data['webnes'] == 'on' or data['thurs'] == 'on' or data['fri'] == 'on' or data['satur'] == 'on':
                try:
                    if int(data['hour']) > 23 or int(data['hour']) < 1 or int(data['minute']) > 59 or int(data['minute']) < 0:
                        error_code.append(41)
                except ValueError:
                    error_code.append(42)
            else:
                data['hour'] = items['hour']
                data['minute'] = items['minute']

            if data['status_check'] == 'on' or data['active_standby_check'] == 'on':
                try:
                    if not IsNaGlobalHostName(data['smtp_server']):
                        error_code.append(43)
                except IndexError:
                    error_code.append(43)
                if not IsValidMailAddress(data['d3_mail_account']):
                    error_code.append(44)
                if not IsValidMailAddress(data['mail_account']):
                    error_code.append(45)
            else:
                data['smtp_server'] = items['smtp_server']
                data['d3_mail_account'] = items['d3_mail_account']
                data['mail_account'] = items['mail_account']
            if error_code != []:
                return error_code
        else:
            data['launch_on_start'] = items['launch_on_start']
            ata['server_on_manager_port'] = items['server_on_manager_port']
            data['watch_server_exist'] = items['watch_server_exist']
            data['auto_server_restart'] = items['auto_server_restart']
            data['sun'] = items['sun']
            data['mon'] = items['mon']
            data['tues'] = items['tues']
            data['webnes'] = items['webnes']
            data['thurs'] = items['thurs']
            data['fri'] = items['fri']
            data['satur'] = items['satur']
            data['hour'] = items['hour']
            data['minute'] = items['minute']
            data['status_check'] = items['status_check']
            data['active_standby_check'] = items['active_standby_check']
            data['smtp_server'] = items['smtp_server']
            data['d3_mail_account'] = items['d3_mail_account']
            data['mail_account'] = items['mail_account']

        server.setAttribute('launch_on_start', data['launch_on_start'])
        server.setAttribute('server_on_manager_port', data['server_on_manager_port'])
        server.setAttribute('watch_server_exist', data['watch_server_exist'])
        server.setAttribute('auto_server_restart', data['auto_server_restart'])
        delete_lease_info = self.doc.createElement("delete_lease_info")
        delete_lease_info.setAttribute('sun', data['sun'])
        delete_lease_info.setAttribute('mon', data['mon'])
        delete_lease_info.setAttribute('tues', data['tues'])
        delete_lease_info.setAttribute('webnes', data['webnes'])
        delete_lease_info.setAttribute('thurs', data['thurs'])
        delete_lease_info.setAttribute('fri', data['fri'])
        delete_lease_info.setAttribute('satur', data['satur'])
        delete_lease_info.setAttribute('hour', data['hour'])
        delete_lease_info.setAttribute('minute', data['minute'])
        mail = self.doc.createElement("mail")
        mail.setAttribute('status_check', data['status_check'])
        mail.setAttribute('active_standby_check', data['active_standby_check'])
        mail.setAttribute('smtp_server', data['smtp_server'])
        mail.setAttribute('d3_mail_account', data['d3_mail_account'])
        mail.setAttribute('mail_account', data['mail_account'])

        logDic['launch_on_start'] = data['launch_on_start']
        logDic['server_on_manager_port'] = data['server_on_manager_port']
        logDic['watch_server_exist'] = data['watch_server_exist']
        logDic['auto_server_restart'] = data['auto_server_restart']
        logDic['sun'] = data['sun']
        logDic['mon'] = data['mon']
        logDic['tues'] = data['tues']
        logDic['webnes'] = data['webnes']
        logDic['thurs'] = data['thurs']
        logDic['fri'] = data['fri']
        logDic['satur'] = data['satur']
        logDic['hour'] = data['hour']
        logDic['minute'] = data['minute']
        logDic['status_check'] = data['status_check']
        logDic['active_standby_check'] = data['active_standby_check']
        logDic['smtp_server'] = data['smtp_server']
        logDic['d3_mail_account'] = data['d3_mail_account']
        logDic['mail_account'] = data['mail_account']

        server.appendChild(delete_lease_info)
        server.appendChild(mail)
        elems[0].parentNode.replaceChild(server,elems[0])

        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        # ログ出力
        service = 'dhcp'
        section = 'server'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def getDhcpCommonServerConf(self):
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp", True)
        elems = self._getElements(elems[0], "server", True)
        for elem in elems:
            delete = self._getElements(elem, "delete_lease_info", True)
            mail = self._getElements(elem, "mail", True)
            items = {
                'launch_on_start':elem.getAttribute('launch_on_start')
                , 'server_on_manager_port':elem.getAttribute('server_on_manager_port')
                , 'watch_server_exist':elem.getAttribute('watch_server_exist')
                , 'auto_server_restart':elem.getAttribute('auto_server_restart')
                , 'sun':delete[0].getAttribute('sun')
                , 'mon':delete[0].getAttribute('mon')
                , 'tues':delete[0].getAttribute('tues')
                , 'webnes':delete[0].getAttribute('webnes')
                , 'thurs':delete[0].getAttribute('thurs')
                , 'fri':delete[0].getAttribute('fri')
                , 'satur':delete[0].getAttribute('satur')
                , 'hour':delete[0].getAttribute('hour')
                , 'minute':delete[0].getAttribute('minute')
                , 'status_check': mail[0].getAttribute('status_check')
                , 'active_standby_check': mail[0].getAttribute('active_standby_check')
                , 'smtp_server': mail[0].getAttribute('smtp_server')
                , 'd3_mail_account': mail[0].getAttribute('d3_mail_account')
                , 'mail_account': mail[0].getAttribute('mail_account')
            }
        return items

    def getDhcpServerConf(self):
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp", True)
        elems = self._getElements(elems[0], "server", True)
        for elem in elems:
            delete = self._getElements(elem, "delete_lease_info", True)
            mail = self._getElements(elem, "mail", True)
            items = {
                'use_common_setting':elem.getAttribute('use_common_setting')
                , 'launch_on_start':elem.getAttribute('launch_on_start')
                , 'server_on_manager_port':elem.getAttribute('server_on_manager_port')
                , 'watch_server_exist':elem.getAttribute('watch_server_exist')
                , 'auto_server_restart':elem.getAttribute('auto_server_restart')
                , 'use_vip':elem.getAttribute('use_vip')
                , 'vip':elem.getAttribute('vip')
                , 'sun':delete[0].getAttribute('sun')
                , 'mon':delete[0].getAttribute('mon')
                , 'tues':delete[0].getAttribute('tues')
                , 'webnes':delete[0].getAttribute('webnes')
                , 'thurs':delete[0].getAttribute('thurs')
                , 'fri':delete[0].getAttribute('fri')
                , 'satur':delete[0].getAttribute('satur')
                , 'hour':delete[0].getAttribute('hour')
                , 'minute':delete[0].getAttribute('minute')
                , 'status_check': mail[0].getAttribute('status_check')
                , 'active_standby_check': mail[0].getAttribute('active_standby_check')
                , 'smtp_server': mail[0].getAttribute('smtp_server')
                , 'd3_mail_account': mail[0].getAttribute('d3_mail_account')
                , 'mail_account': mail[0].getAttribute('mail_account')
            }
        return items

    def setDhcpClient(self, data):
        error_code = []
        # ValidChecker はここで実行
        if not IsMacAddress(data['mac']):
            error_code.append(41)
        if error_code != []:
            return error_code
        # 仮重複チェック C++に以降
        logDic = {}
        try:
            ch.setDhcpClient(data)
        except ValueError, e:
            return 422

        # ログ出力
        service = 'dhcp'
        section = 'client'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def setDhcpClientv6(self, data):
        error_code = []
        # ValidChecker はここで実行
        if not IsDUIDAddress(data['duid']):
            error_code.append(41)
        if error_code != []:
            return error_code
        # 仮重複チェック C++に以降
        items = []
        logDic = {}
        try:
            items = self.getDhcpClientListv6()
        except TypeError, e:
            pass
        for i in range(len(items)):
            if items[i]['duid'] == data['duid']:
                if data.has_key('item_id'):
                    if i != int(data['item_id']):
                        return 422
                else:
                    return 422
        # xmlファイル内を参照 C++に移行した場合記述を削除する
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcpv6")
        elems = self._getElements(elems[0], "clientList")
        client = self.doc.createElement("client")
        client.setAttribute("duid", data['duid'])

        if data.has_key('item_id'):
            op = 'edit'
            # 実際はC++のsetDhcpClient関数にデータとidを渡す
            elems = self._getElements(elems[0], "client")
            elems[0].parentNode.replaceChild(client,elems[int(data['item_id'])])
        else:
            op = 'add'
            items = self.getDhcpClientListv6()
            if len(items) > MAX_COMMON_CLIENT:
                return 423
            # 実際はC++のsetDhcpClient関数にデータを渡す
            elems[0].appendChild(client)
        logDic['duid'] = data['duid']

        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        # ログ出力
        service = 'dhcpv6'
        section = 'client'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def setDhcpClientList(self, operation, aLowerList = [], aList = []):
        # リスト内重複チェック
        clientList = []
        for i in aLowerList:
            if i in clientList:
                raise ValueError("csv duplicate mac address [%s]" % i)
            else:
                clientList.append(i)
        operation = int(operation)
        if operation ==  OPCODE_REPLACE:
            self.delDhcpClient("all")
        if operation ==  OPCODE_DELETE:
            delitems = []
            try:
                items = self.getDhcpClientList()
            except TypeError, e:
                pass
            for x in range(len(items)):
                for y in range(len(clientList)):
                    if items[x]['mac'] == clientList[y]:
                        delitems.append(items[x]['id'])
            delitems.sort(reverse=True)
            for i in range(len(delitems)):
                self.delDhcpClient(str(delitems[i]))
        else:
            if operation == OPCODE_ADD_DIFFERENCE:
                for i in clientList:
                    self.setDhcpClient(i)
            else:
                for i in clientList:
                    dict = {}
                    dict['mac'] = i
                    result = self.setDhcpClient(dict)
                    if result == 422:
                        raise ValueError("duplicate mac address [%s]" % i)

    def setDhcpClientListv6(self, operation, aLowerList = [], aList = []):
        # リスト内重複チェック
        clientList = []
        for i in aLowerList:
            if i in clientList:
                raise ValueError("csv duplicate mac address [%s]" % i)
            else:
                clientList.append(i)
        operation = int(operation)
        if operation ==  OPCODE_REPLACE:
            self.delDhcpClientv6("all")
        if operation ==  OPCODE_DELETE:
            delitems = []
            try:
                items = self.getDhcpClientListv6()
            except TypeError, e:
                pass
            for x in range(len(items)):
                for y in range(len(clientList)):
                    if items[x]['duid'] == clientList[y]:
                        delitems.append(items[x]['id'])
            delitems.sort(reverse=True)
            for i in range(len(delitems)):
                self.delDhcpClientv6(str(delitems[i]))
        else:
            if operation == OPCODE_ADD_DIFFERENCE:
                for i in clientList:
                    self.setDhcpClientv6(i)
            else:
                for i in clientList:
                    dict = {}
                    dict['duid'] = i
                    result = self.setDhcpClientv6(dict)
                    if result == 422:
                        raise ValueError("duplicate duid [%s]" % i)

    def delDhcpClient(self, id):
        try:
            items = self.getDhcpClientList()
        except TypeError, e:
            pass

        # xmlファイル内を参照 C++に移行した場合記述を削除する#
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "clientList")

        logDic = []
        if id == "all":
            op = "all_delete"
            # 実際はC++のdelDhcpScope関数に引数「all」を渡す #
            elems[0].parentNode.removeChild(elems[0])
        else:
            op = "delete"
            list = id.split(",")
            list.sort(reverse=True)
            for i in range(len(list)):
                items = self.getDhcpClient(list[i])
                logDic.append({'mac': items['mac']})
            # 実際はC++のdelDhcpScope関数にlistを渡す #
            elems = self._getElements(elems[0], "client")
            for i in range(len(list)):
                elems[0].parentNode.removeChild(elems[int(list[i])])

        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        service = 'dhcp'
        section = 'client'
        for i in range(len(logDic)):
            self.syslog.SendLog(service, section, op, logDic[i], "info")
        return 'success'

    def delDhcpClientv6(self, id):
        try:
            items = self.getDhcpClientListv6()
        except TypeError, e:
            pass

        # xmlファイル内を参照 C++に移行した場合記述を削除する#
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcpv6")
        elems = self._getElements(elems[0], "clientList")

        logDic = []
        if id == "all":
            op = "all_delete"
            # 実際はC++のdelDhcpScope関数に引数「all」を渡す #
            elems[0].parentNode.removeChild(elems[0])
        else:
            op = "delete"
            list = id.split(",")
            list.sort(reverse=True)
            for i in range(len(list)):
                items = self.getDhcpClientv6(list[i])
                logDic.append({'duid': items['duid']})
            # 実際はC++のdelDhcpScope関数にlistを渡す #
            elems = self._getElements(elems[0], "client")
            for i in range(len(list)):
                elems[0].parentNode.removeChild(elems[int(list[i])])

        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        service = 'dhcpv6'
        section = 'client'
        for i in range(len(logDic)):
            self.syslog.SendLog(service, section, op, logDic[i], "info")
        return 'success'

    def getDhcpClientList(self,data={}):
        # この関数の処理は全てC++に置き換える必要があります
        items = {}
        items['data'] = []
        dic_list = []
        try:
            start=data.get('start', 0)
            limit=data.get('limit', None)
            if data.has_key('condition'):
                start=0
                limit=None
            dic_list = ch.getAttrDicList(["haconfig", "dhcp", "clientList"],
                "client",
                start,
                limit)
        except ValueError:
            return items['data']
        if (data.has_key('condition')):
            for elem in dic_list:
                total = 0
                if elem.get('mac').find(data['condition']) != -1:
                    items['data'].append({
                        'mac':elem.get('mac'),
                        'id':id
                    })
                    total += 1
                id += 1
            items['total'] = str(total)
        else:
            items.['data'] = items.['data'] 
            items['total'] = len(items.['data'])
        return items

    def getDhcpClientListv6(self,data={}):
        # この関数の処理は全てC++に置き換える必要があります
        items = {}
        items['data'] = []
        try:
            elems = self._getElements(self.doc, "haconfig", True)
            elems = self._getElements(elems[0], "dhcpv6", True)
            elems = self._getElements(elems[0], "clientList", True)
            elems = self._getElements(elems[0], "client", True)
        except ValueError:
            return items['data']
        id=0
        if (data.has_key('condition')):
            for elem in elems:
                total = 0
                if elem.getAttribute('duid').find(data['condition']) != -1:
                    items['data'].append({
                        'duid':elem.getAttribute('duid'),
                        'id':id
                    })
                    total += 1
                id += 1
            items['total'] = str(total)
        elif(data.has_key('start')):
            for elem in elems:
                if id >= int(data['start']) and id < int(data['start']) + int(data['limit']):
                    items['data'].append({
                        'duid':elem.getAttribute('duid'),
                        'id':id
                    })
                id += 1
            items['total'] = str(id)
        else:
            for elem in elems:
                items['data'].append({
                        'duid':elem.getAttribute('duid'),
                        'id':id
                    })
                id += 1
            return items['data']
        return items

    def getDhcpClient(self, getid):
        # この関数の処理は全てC++に置き換える必要があります
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp", True)
        elems = self._getElements(elems[0], "clientList", True)
        elems = self._getElements(elems[0], "client", True)
        id=0
        for elem in elems:
            if id == int(getid):
                items = {
                   'mac':elem.getAttribute('mac'),
                   'id':id
                }
            id += 1
        return items

    def getDhcpClientv6(self, getid):
        # この関数の処理は全てC++に置き換える必要があります
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcpv6", True)
        elems = self._getElements(elems[0], "clientList", True)
        elems = self._getElements(elems[0], "client", True)
        id=0
        for elem in elems:
            if id == int(getid):
                items = {
                   'duid':elem.getAttribute('duid'),
                   'id':id
                }
            id += 1
        return items

    def setDhcpHostList(self, operation, aList = []):
        # リスト内重複チェック
        name_list = []
        fixed_address_list = []

        hosts = self.getDhcpHostList();
        for host_dic in hosts:
            name_list.append( host_dic['name'] )
            fixed_address_list.append( host_dic['fixed_address'] )

        name_duplication = False
        fixed_address_duplication = False
        duplication_ids = []
        diff_list = []

        for i, dic in enumerate(aList):
            name_d = False
            fixed_address_d = False
            if dic["host_name"] in name_list:
                name_duplication = True
                name_d = True
            else:
                name_list.append(dic["host_name"])

            if dic["fixed_address"] in fixed_address_list:
                fixed_address_duplication = True
                fixed_address_d = True
            else:
                fixed_address_list.append(dic["fixed_address"])
            if name_d and fixed_address_d:
                for host_dic in hosts:
                    if host_dic['name'] == dic["host_name"]:
                        duplication_ids.append(host_dic['id'])
            else:
                diff_list.append(dic)

        operation = int(operation)
        if operation ==  OPCODE_REPLACE:
            name_duplication = False
            fixed_address_duplication = False
            self.delDhcpHost("all")
        if operation ==  OPCODE_DELETE:
            duplication_ids.sort()
            duplication_ids.reverse()
            for i in range(len(duplication_ids)):
                self.delDhcpHost(str(duplication_ids[i]))
        else:
            if operation == OPCODE_ADD_DIFFERENCE:
                for i in diff_list:
                    self.setDhcpHost(i)
            else:
                for i in aList:
                    result = self.setDhcpHost(i)
                    if result != 'success':
                        raise ValueError(i)

    def setDhcpHost(self, data):
        error_code = []
        # ValidChecker はここで実行
        if not IsGoodHostName(data['host_name']):
            error_code.append(41)
        if not is_address(data['fixed_address']):
            error_code.append(42)
        if not IsMacAddress(data['hardware']):
            error_code.append(43)
        if error_code != []:
            return error_code
        # 仮重複チェック C++に以降
        items = []
        logDic = {}
        try:
            items = self.getDhcpHostList()
        except TypeError, e:
            pass
        for i in range(len(items)):
            if items[i]['name'] == data['host_name']:
                if data.has_key('item_id'):
                    if i != int(data['item_id']):
                        return 422
                else:
                    return 422
            if items[i]['fixed_address'] == data['fixed_address']:
                if data.has_key('item_id'):
                    if i != int(data['item_id']):
                        return 423
                else:
                    return 423
        # xmlファイル内を参照 C++に移行した場合記述を削除する
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "hostList")
        host = self.doc.createElement("host")
        host.setAttribute("name", data['host_name'])
        host.setAttribute("fixed_address", data['fixed_address'])
        host.setAttribute("hardware", data['hardware'])

        if data.has_key('item_id'):
            op = 'edit'
            # 実際はC++のsetDhcpHost関数にデータとidを渡す
            elems = self._getElements(elems[0], "host")
            elems[0].parentNode.replaceChild(host,elems[int(data['item_id'])])
        else:
            op = 'add'
            items = self.getDhcpHostList()
            if len(items) > MAX_COMMON_CLIENT:
                return 423
            # 実際はC++のsetDhcpHost関数にデータを渡す
            elems[0].appendChild(host)
        logDic['name'] = data['host_name']
        logDic['fixed_address'] = data['fixed_address']
        logDic['hardware'] = data['hardware']

        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        # ログ出力
        service = 'dhcp'
        section = 'host'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def getDhcpHostList(self,data={}):
        # この関数の処理は全てC++に置き換える必要があります
        items = {}
        items['data'] = []
        try:
            elems = self._getElements(self.doc, "haconfig", True)
            elems = self._getElements(elems[0], "dhcp", True)
            elems = self._getElements(elems[0], "hostList", True)
            elems = self._getElements(elems[0], "host", True)
        except ValueError:
            return items['data']
        id=0
        if data.has_key('condition'):
            for elem in elems:
                total = 0
                if elem.getAttribute('host').find(data['condition']) != -1:
                    items['data'].append({
                            'name':elem.getAttribute('name'),
                            'fixed_address':elem.getAttribute('fixed_address'),
                            'hardware':elem.getAttribute('hardware'),
                            'id':id
                        })
                    total += 1
                id += 1
            items['total'] = str(total)
        elif(data.has_key('start')):
            for elem in elems:
                if id >= int(data['start']) and id < int(data['start']) + int(data['limit']):
                    items['data'].append({
                        'name':elem.getAttribute('name'),
                        'fixed_address':elem.getAttribute('fixed_address'),
                        'hardware':elem.getAttribute('hardware'),
                        'id':str(id)
                    })
                id += 1
            items['total'] = str(id)
        else:
            for elem in elems:
                items['data'].append({
                    'name':elem.getAttribute('name'),
                    'fixed_address':elem.getAttribute('fixed_address'),
                    'hardware':elem.getAttribute('hardware'),
                    'id':str(id)
                })
                id += 1
            return items['data']
        return items

    def getDhcpHost(self, getid):
        # この関数の処理は全てC++に置き換える必要があります
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp", True)
        elems = self._getElements(elems[0], "hostList", True)
        elems = self._getElements(elems[0], "host", True)
        id=0
        for elem in elems:
            if id == int(getid):
                items = {
                    'name':elem.getAttribute('name')
                    , 'fixed_address':elem.getAttribute('fixed_address')
                    , 'hardware':elem.getAttribute('hardware')
                    , 'id':id
                }
            id += 1
        return items

    def delDhcpHost(self, id):
        try:
            items = self.getDhcpHostList()
        except TypeError, e:
            pass

        # xmlファイル内を参照 C++に移行した場合記述を削除する#
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "hostList")

        logDic = []
        if id == "all":
            op = "all_delete"
            # 実際はC++のdelDhcpHost関数に引数「all」を渡す #
            elems[0].parentNode.removeChild(elems[0])
        else:
            op = "delete"
            list = id.split(",")
            list.sort(reverse=True)
            for i in range(len(list)):
                items = self.getDhcpHost(list[i])
                logDic.append({'host_name': items['name']})
            # 実際はC++のdelDhcpHost関数にlistを渡す #
            elems = self._getElements(elems[0], "host")
            for i in range(len(list)):
                elems[0].parentNode.removeChild(elems[int(list[i])])

        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        service = 'dhcp'
        section = 'host'
        for i in range(len(logDic)):
            self.syslog.SendLog(service, section, op, logDic[i], "info")
        return 'success'

    def setDhcpScope(self, data):
        error_code = []
        ## ValidChecker はここで実行
        if not is_address(data['network']):
            error_code.append(41)
        if not IsSubnetMask(data['subnetmask']):
            error_code.append(42)
        if not IsNullOrGoodIpAddresses(data['router']):
            error_code.append(43)
        if not IsNullOrGoodZoneName(data['domain']):
            error_code.append(44)
        if not IsNullOrGoodIpAddresses(data['dns']):
            error_code.append(45)
        try:
            if int(data['default_lease_time']) > 4294967295:
                error_code.append(51)
        except ValueError:
                error_code.append(51)
        try:
            if int(data['max_lease_time']) > 4294967295:
                error_code.append(52)
        except ValueError:
            error_code.append(52)
        if data['miss_nap_access'] == '':
            if data.has_key('item_id'):
                item = self.getDhcpScope(data['item_id'])
                data['miss_nap_access'] = item['miss_nap_access']
            else:
                data['miss_nap_access'] = 'allow'
        try:
            if int(data['ip_user_rate']) > 100:
               error_code.append(56)
        except ValueError:
            error_code.append(56)
        ######### ここから ###############
        ## 仮チェック
        items = []
        try:
            items = self.getDhcpScopeList()
        except TypeError, e:
            pass
        for i in range(len(items)):
            if items[i]['network'] == data['network']:
                if data.has_key('item_id'):
                    if i != int(data['item_id']):
                        return 422
                else:
                    return 422
        ## 仮チェック ここまで
        logDic = {}
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "scopeList")

        scope = self.doc.createElement("scope")
        scope.setAttribute("network", data['network'])
        scope.setAttribute("subnetmask", data['subnetmask'])
        scope.setAttribute("router", data['router'])
        scope.setAttribute("domain", data['domain'])
        scope.setAttribute("dns", data['dns'])

        option = self.doc.createElement("option")
        option.setAttribute('default_lease_time', data['default_lease_time'])
        option.setAttribute('max_lease_time', data['max_lease_time'])
        option.setAttribute('ping_check', data['ping_check'])
        option.setAttribute('nap', data['nap'])
        option.setAttribute('miss_nap_access', data['miss_nap_access'])
        option.setAttribute('use_ddns', data['use_ddns'])
        option.setAttribute('client_allow_deny', data['client_allow_deny'])
        option.setAttribute('client_type', data['client_type'])

        mail = self.doc.createElement("mail")
        mail.setAttribute('use_mail_alert', data['use_mail_alert'])
        mail.setAttribute('ip_user_rate', data['ip_user_rate'])

        if data.has_key('item_id'):
            op = 'edit'
            scope.appendChild(option)
            scope.appendChild(mail)
            elems = self._getElements(elems[0], "scope")
            elems[0].parentNode.replaceChild(scope,elems[int(data['item_id'])])
        else:
            ## レンジの ValidChecker はここで実行
            op = 'add'
            if not is_null_or_address(data['start_range']):
                error_code.append(47)
            if not is_null_or_address(data['end_range']):
                error_code.append(48)
            if not is_null_or_address(data['exclude_start_range']):
                error_code.append(49)
            if not is_null_or_address(data['exclude_end_range']):
                error_code.append(50)
            scope.appendChild(option)
            scope.appendChild(mail)
            elems[0].appendChild(scope)
        logDic['network'] = data['network']
        logDic['subnetmask'] = data['subnetmask']
        logDic['router'] = data['router']
        logDic['domain'] = data['domain']
        logDic['dns'] = data['dns']

        if error_code != []:
            return error_code
        else:
            if (IP(data['network']).int() & IP(data['subnetmask']).int() != IP(data['network']).int()):
                error_code.append(46)
                return error_code

        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()
        ######### ここまでが本来はC++ ##########
        service = 'dhcp'
        section = 'scope'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def getDhcpScopeList(self,data={}):
        # この関数の処理は全てC++に置き換える必要があります
        items = {}
        items['data'] = []
        try:
            elems = self._getElements(self.doc, "haconfig", True)
            elems = self._getElements(elems[0], "dhcp", True)
            elems = self._getElements(elems[0], "scopeList", True)
            elems = self._getElements(elems[0], "scope", True)
        except ValueError:
            return items['data']
        id=0
        if (data.has_key('condition')):
            for elem in elems:
                total = 0
                try:
                    rangelist = self._getElements(elem, "rangeList", True)
                    range = self._getElements(rangelist[0], "range", True)
                except ValueError, e:
                    disable = "(disable)"
                if elem.getAttribute('network').find(data['condition']) != -1:
                    items['data'].append({
                        'network':elem.getAttribute('network')+disable,
                        'id':id
                    })
                    total += 1
                id += 1
            items['total'] = str(total)
        elif(data.has_key('start')):
            for elem in elems:
                disable = ""
                try:
                    rangelist = self._getElements(elem, "rangeList", True)
                    range = self._getElements(rangelist[0], "range", True)
                except ValueError, e:
                    disable = "(disable)"
                if id >= int(data['start']) and id < int(data['start']) + int(data['limit']):
                    items['data'].append({
                        'network':elem.getAttribute('network')+disable,
                        'id':id
                    })
                id += 1
            items['total'] = str(id)
        else:
            for elem in elems:
                items['data'].append({
                    'network':elem.getAttribute('network'),
                    'id':id
                })
                id += 1
            return items['data']
        return items

    def getDhcpScope(self, data):
        # この関数の処理は全てC++に置き換える必要があります
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp", True)
        elems = self._getElements(elems[0], "scopeList", True)
        elems = self._getElements(elems[0], "scope", True)
        id=0
        for elem in elems:
            if id == int(data['scope_id']):
                option = self._getElements(elem, "option", True)
                mail = self._getElements(elem, "mail", True)
                items = {
                    'network':elem.getAttribute('network')
                    , 'subnetmask':elem.getAttribute('subnetmask')
                    , 'router':elem.getAttribute('router')
                    , 'domain':elem.getAttribute('domain')
                    , 'dns':elem.getAttribute('dns')
                    , 'default_lease_time':option[0].getAttribute('default_lease_time')
                    , 'max_lease_time':option[0].getAttribute('max_lease_time')
                    , 'ping_check':option[0].getAttribute('ping_check')
                    , 'nap':option[0].getAttribute('nap')
                    , 'miss_nap_access':option[0].getAttribute('miss_nap_access')
                    , 'use_ddns':option[0].getAttribute('use_ddns')
                    , 'client_allow_deny':option[0].getAttribute('client_allow_deny')
                    , 'client_type':option[0].getAttribute('client_type')
                    , 'use_mail_alert':mail[0].getAttribute('use_mail_alert')
                    , 'ip_user_rate':mail[0].getAttribute('ip_user_rate')
                    , 'id':id
                }
            id += 1
        return items

    def delDhcpScope(self, id):
        try:
            items = self.getDhcpClientList()
        except TypeError, e:
            pass

        # xmlファイル内を参照 C++に移行した場合記述を削除する#
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "scopeList")

        logDic = []
        if id == "all":
            op = "all_delete"
            # 実際はC++のdelDhcpScope関数に引数「all」を渡す #
            elems[0].parentNode.removeChild(elems[0])
        else:
            op = "delete"
            list = id.split(",")
            list.sort(reverse=True)
            for i in range(len(list)):
                items = self.getDhcpScope(list[i])
                logDic.append({'network': items['network']})
            # 実際はC++のdelDhcpScope関数にlistを渡す #
            elems = self._getElements(elems[0], "scope")
            for i in range(len(list)):
                elems[0].parentNode.removeChild(elems[int(list[i])])

        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()

        service = 'dhcp'
        section = 'scope'
        for i in range(len(logDic)):
            self.syslog.SendLog(service, section, op, logDic[i], "info")
        return 'success'

    def setDhcpRange(self, data):
        error_code = []
        if not is_address(data['start']):
            error_code.append(41)
        if not is_address(data['end']):
            error_code.append(42)
        if not is_null_or_address(data['exclude_start']):
            error_code.append(43)
        if not is_null_or_address(data['exclude_end']):
            error_code.append(44)
        if error_code != []:
            return error_code
        ######### スコープ範囲内チェック ###############
        scope = self.getDhcpScope(data)
        ######### レンジ重複チェック ###############
        ######### 除外レンジチェック ###############
        ## チェック ここまで
        logDic = {}
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "scopeList")
        elems = self._getElements(elems[0], "scope")
        elems = self._getElements(elems[int(data['scope_id'])], "rangeList")
        logDic['start'] = data['start']
        logDic['end'] = data['end']
        logDic['exclude_start'] = data['exclude_start']
        logDic['exclude_end'] = data['exclude_end']

        range = self.doc.createElement("range")
        range.setAttribute("start", data['start'])
        range.setAttribute("end", data['end'])
        range.setAttribute("exclude_start", data['exclude_start'])
        range.setAttribute("exclude_end", data['exclude_end'])

        if data.has_key('item_id'):
            op = 'edit'
            elems = self._getElements(elems[0], "range")
            elems[0].parentNode.replaceChild(range,elems[int(data['item_id'])])
        else:
            op = 'add'
            elems[0].appendChild(range)

        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()
        ######### ここまでが本来はC++ ##########
        service = 'dhcp'
        section = 'scope.range'
        self.syslog.SendLog(service, section, op, logDic, "info")
        return 'success'

    def getDhcpRangeList(self,data={}):
        # この関数の処理は全てC++に置き換える必要があります
        items = {}
        items['data'] = []
        try:
            elems = self._getElements(self.doc, "haconfig", True)
            elems = self._getElements(elems[0], "dhcp", True)
            elems = self._getElements(elems[0], "scopeList", True)
            elems = self._getElements(elems[0], "scope", True)
            elems = self._getElements(elems[int(data['scope_id'])], "rangeList", True)
            elems = self._getElements(elems[0], "range", True)
        except ValueError:
            return items['data']
        id=0
        if(data.has_key('start')):
            for elem in elems:
                if id >= int(data['start']) and id < int(data['start']) + int(data['limit']):
                    items['data'].append({
                        'range':elem.getAttribute('start') + ' - ' + elem.getAttribute('end'),
                        'exclude_range':elem.getAttribute('exclude_start') + ' - ' + elem.getAttribute('exclude_end'),
                        'id':id
                    })
                id += 1
            items['total'] = str(id)
        else:
            for elem in elems:
                items['data'].append({
                    'start':elem.getAttribute('start'),
                    'end':elem.getAttribute('end'),
                    'id':id
                })
                id += 1
            return items['data']
        return items

    def getDhcpRange(self, data):
        # この関数の処理は全てC++に置き換える必要があります
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp", True)
        elems = self._getElements(elems[0], "scopeList", True)
        elems = self._getElements(elems[0], "scope", True)
        elems = self._getElements(elems[int(data['scope_id'])], "rangeList", True)
        elems = self._getElements(elems[0], "range", True)
        id=0
        for elem in elems:
            if id == int(data['item_id']):
                items = {
                    'start':elem.getAttribute('start')
                    , 'end':elem.getAttribute('end')
                    , 'exclude_start':elem.getAttribute('exclude_start')
                    , 'exclude_end':elem.getAttribute('exclude_end')
                    , 'id':id
                }
            id += 1
        return items

    def delDhcpRange(self, data):
        try:
            items = self.getDhcpClientList()
        except TypeError, e:
            pass
        # xmlファイル内を参照 C++に移行した場合記述を削除する#
        elems = self._getElements(self.doc, "haconfig", True)
        elems = self._getElements(elems[0], "dhcp")
        elems = self._getElements(elems[0], "scopeList")
        elems = self._getElements(elems[0], "scope", True)
        elems = self._getElements(elems[int(data['scope_id'])], "rangeList", True)
        logDic = []
        op = "delete"
        list = data['item_id'].split(",")
        list.sort(reverse=True)
        for i in range(len(list)):
            items = self.getDhcpRange({'item_id':list[i],'scope_id':data['scope_id']})
            logDic.append({'range': items['start']+'-'+items['end']})
        # 実際はC++のdelDhcpRange関数にlistを渡す #
        elems = self._getElements(elems[0], "range")
        for i in range(len(list)):
            elems[0].parentNode.removeChild(elems[int(list[i])])
        # xmlファイルの書き出し C++に移行した場合記述を削除する
        f = open(self.filename, "w")
        self.doc.writexml(f, encoding='utf-8')
        f.close()
        service = 'dhcp'
        section = 'scope.range'
        for i in range(len(logDic)):
            self.syslog.SendLog(service, section, op, logDic[i], "info")
        return 'success'

    # ro がFalseの場合は読み込もうとしたElementが無い場合
    # Elementを新しく生成する
    def _getElements(self, elem, tagname, ro = False):
        if len(elem.getElementsByTagName(tagname)) <= 0:
            if ro:
                raise ValueError
            else:
               child = self.doc.createElement(tagname)
               elem.appendChild(child)
        return elem.getElementsByTagName(tagname)

"""
if len(sys.argv) > 1:
    config = ConfigManager(sys.argv[1])
else:
    print "Please input filename"
    sys.exit(1)

config.setDhcpScope("192.168.2.0", "255.255.255.0")
print config.getDhcpScopeList()
"""
