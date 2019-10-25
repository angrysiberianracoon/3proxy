#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    3Proxy server management for Docker installation
#
#    Copyright (C) 2019 Angry Siberian Racoon <angrysiberianracoon@gmail.com>
#
#    https://github.com/angrysiberianracoon/3proxy
#
#    This software is licensed under the MIT
#    License: https://github.com/angrysiberianracoon/3proxy/master/LICENSE

import json
import collections
import subprocess
import os
import sys
import re
import shutil
import re
import gettext
import struct


class Config:
    def __init__(self, filename):
        self.filename = filename

        with open(self.filename, 'r') as f:
            self.v = json.load(f, object_pairs_hook=collections.OrderedDict)

    def __getitem__(self, section):
        return self.v[section]

    def has(self, section, key):
        return key in self.v[section].keys()

    def update(self, section, key, value):
        self.v[section][key] = value
        self.save()

    def remove(self, section, key):
        del self.v[section][key]
        self.save()


    def save(self):
        open(self.filename, 'wb').write(json.dumps(
            self.v, ensure_ascii=False, indent=4).encode('utf8'))


class OutFormat:
    def __init__(self):
        pass

    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    GREEN = '\033[92m'
    LINK = '\33[33m'
    MENU = '\033[94m'
    BOLD = '\033[1m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'

    @staticmethod
    def clear_screen():
        print(chr(27) + "[2J")

    @staticmethod
    def clear_line():
        print(OutFormat.CURSOR_UP_ONE +
              OutFormat.ERASE_LINE + OutFormat.CURSOR_UP_ONE)

    @staticmethod
    def trim(value):
            return re.sub(r'\s+', ' ', value)

    @staticmethod
    def line_dashed():
        print(OutFormat.GREEN +
            '-----------------------------------------------------' + OutFormat.ENDC)

    @staticmethod
    def line_menu():
        print(OutFormat.MENU + '=============================' + OutFormat.ENDC)

    @staticmethod
    def bold(value):
        return OutFormat.BOLD + value + OutFormat.ENDC

    @staticmethod
    def yellow(value):
        return OutFormat.YELLOW + value + OutFormat.ENDC

    @staticmethod
    def link(value):
        return OutFormat.LINK + value + OutFormat.ENDC

    @staticmethod
    def alert(value):
        print('\n[ ' + OutFormat.BOLD + OutFormat.YELLOW +
            value + OutFormat.ENDC + ' ]')

    @staticmethod
    def header(value):
        print('\n\n' + OutFormat.bold(value))
        OutFormat.line()

    @staticmethod
    def logo():
        OutFormat.clear_screen()
        print(OutFormat.BOLD + ' _______________             ____  __')
        print(' __|__  /__  __ \\______________  |/ /____  __')
        print(' ___/_ <__  /_/ /_  ___/  __ \\_    /__  / / /')
        print(' ____/ /_  ____/_  /   / /_/ /    | _  /_/ /')
        print(' /____/ /_/     /_/    \\____//_/|_| _\\__, /')
        print('                                    /____/' + OutFormat.ENDC)


    @staticmethod
    def line():
        print (OutFormat.GREEN + '─────────────────────────────────────────────────────' + OutFormat.ENDC)

def lang_init(lang_code):
    path = sys.argv[0]
    path = os.path.join(os.path.dirname(path), 'lang')

    lang = gettext.translation('3proxy', path, [lang_code], fallback="en")
    return lang.gettext


def silent_run(command, show_output=False):
    if show_output:
        subprocess.check_call(command, shell=True)
    else:
        subprocess.check_call(command, shell=True, stdout=open(os.devnull, 'wb'))


def select_lang():
    locale_list = conf['lang']['list']
    locale_select = menu(locale_list.values())
    locale = locale_list.keys()[locale_select - 1]

    conf.update('lang', 'current', locale)

    return lang_init(locale)


def replace_in_file(file_name, find_text, replace_text):
    f_read = open(file_name, 'r')
    read_data = f_read.read()
    f_read.close()

    content = read_data.replace(find_text, replace_text)

    f_write = open(file_name, 'w')
    f_write.write(content)
    f_write.close()

def insert_in_file(file_name, value):
    with open(file_name, 'a') as the_file:
        the_file.write(value + '\n')


def get_from_file(file_name, key_word):
    with open(file_name, 'r') as f:
        for line in f:
            if key_word in line:
                return line
        return ''

def remove_from_file(file_name, key_word):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    with open(file_name, 'w') as f:
        for line in lines:
            if not line.strip('\n').startswith(key_word):
                f.write(line)


def menu(options, return_item=False, header=None):
    print ('\n')

    if header:
        print (OutFormat.bold(header))

    OutFormat.line_menu()
    for key, item in enumerate(options, start=1):
        print (' ' + str(key) + '. ' + item)

    if return_item:
        print (' 0. ' + return_item)

    OutFormat.line_menu()

    input_items = [str(index) for index in range(1, len(options) + 1)]

    if return_item:
        input_items.append("0")

    return int(confirmation(input_items))


def confirmation(options):
    while 1:
        value = raw_input().lower()
        OutFormat.clear_line()
        if value in options:
            return value


def user_input(promt, validator=None):
    OutFormat.header(promt)
    prev_novalid = False

    while 1:
        value = raw_input()

        if prev_novalid:
            OutFormat.clear_line()
            OutFormat.clear_line()

        prev_novalid = False

        OutFormat.clear_line()
        print (_('your input: [{value}]').format(value=OutFormat.yellow(value)))

        if validator is not None:
            validator_result = validator(value)

        if validator is None or validator_result is None:
            print (_('continue [y] / input again [n] ?'))

            if confirmation(['y', 'n']) == 'y':
                OutFormat.clear_line()
                return value

            OutFormat.clear_line()
            OutFormat.clear_line()

        else:
            prev_novalid = True
            print (validator_result + ', ' + _('try again') + ':')


def limit_validate(value):
    if value == '' or (value.isdigit()):
        return None
    else:
        return _('limit must be a number')

def port_validate(value):
    if value == '' or (value.isdigit() and 1024 <= int(value) <= 65535):
        return None
    else:
        return _('port must be in range 1024 - 65535')


def name_validate(value):
    reg = re.compile("^[A-Za-z0-9_.@-]+$")

    if not reg.match(value):
        return _('the name must contain only letters, numbers and symbols [_ - . @]')
    else:
        return None


def init_setting():
    proc = subprocess.Popen(['id', 'proxy3', '-u'], stdout=subprocess.PIPE)
    uid, err = proc.communicate()

    proc = subprocess.Popen(['id', 'proxy3', '-g'], stdout=subprocess.PIPE)
    gid, err = proc.communicate()

    shutil.copy('/data/configs/3proxy.cfg', '/etc/3proxy/3proxy.cfg')
    replace_in_file('/etc/3proxy/3proxy.cfg', '$GID', re.sub(r'\D', '', gid))
    replace_in_file('/etc/3proxy/3proxy.cfg', '$UID', re.sub(r'\D', '', uid))

    http_port = user_input(_('Enter port for HTTP proxy, (for ex. 3128)') + '\n' + _('or leave blank for disable') + ':', port_validate)

    if http_port != '':
        replace_in_file('/etc/3proxy/3proxy.cfg', '$HTTPPROXY', 'proxy -p' + http_port + ' -n')
    else:
        replace_in_file('/etc/3proxy/3proxy.cfg', '$HTTPPROXY', '')

    socks_port = user_input(_('Enter port for SOCKS 4/4.5/5 proxy, (for ex. 1080)') + '\n' + _('or leave blank for disable') + ':', port_validate)

    if socks_port != '':
        replace_in_file('/etc/3proxy/3proxy.cfg', '$SOCKSPROXY', 'socks -p' + socks_port)
    else:
        replace_in_file('/etc/3proxy/3proxy.cfg', '$SOCKSPROXY', '')

    restart_server()


def restart_server():
    print '\n' + OutFormat.bold(_('restart server') + '... '),
    sys.stdout.flush()
    silent_run('supervisorctl restart 3proxy')
    print OutFormat.bold(_('done'))


def get_last_counter_id():
    return conf['counters']['counterindex']


def set_last_counter_id(value):
    conf.update('counters', 'counterindex', value)


def add_client_limit(client_name, client_limit):
    counter_id = get_last_counter_id() + 1

    limit_string = 'countin {counter_id} D {client_limit} {client_name}'.format(counter_id=counter_id, client_name=client_name, client_limit=client_limit)
    insert_in_file('/etc/3proxy/limits', limit_string)

    set_last_counter_id(counter_id)


def get_client_limit(client_name):
    counter_line = get_from_file('/etc/3proxy/limits', ' ' + client_name)

    if '' == counter_line:
        return None

    counter_data = counter_line.split()

    return {'index': counter_data[1], 'limit': counter_data[3]}


def add_client():
    client_name = user_input(_('Enter the user name') + ':', name_validate)
    user_list = conf['clients']

    if any(client_name in client for client in user_list):
        print (_('User [{user}] already exist').format(user=OutFormat.yellow(client_name)))
        return

    client_password = user_input((_('Enter the password for [{user}]') + '\n' + _('you can leave the field blank') + ':').format(user=OutFormat.yellow(client_name)))

    insert_in_file('/etc/3proxy/.proxyauth', client_name + ':CL:' + client_password)

    client_limit = user_input((_('Enter traffic limit (megabytes per day) for [{user}]') + '\n' + _('you can leave the field blank') + ':').format(user=OutFormat.yellow(client_name)), limit_validate)

    if client_limit <> 0 and client_limit <> '':
        add_client_limit(client_name, client_limit)

    if len(user_list) == 0:
        restart_server()

    conf.update('clients', str(len(user_list) + 1), client_name)


def view_client():
    user_list = conf['clients']

    if len(user_list) == 0:
        OutFormat.alert(_('No users'))
        return

    selected_user = menu(user_list.values(), '[ ' + _('back') + ' ]', _('Select user for view') + ':')

    if selected_user == 0:
        return

    user_key = str(user_list.keys()[selected_user - 1])
    user_name = user_list[user_key]

    user_line = get_from_file('/etc/3proxy/.proxyauth', user_name + ':CL:')
    user_array = user_line.split(':CL:')

    OutFormat.clear_line()
    OutFormat.clear_line()

    print('\n\n')

    print (_('Name') + ': ' + OutFormat.yellow(user_array[0]))
    print (_('Password') + ': ' + OutFormat.yellow(user_array[1]))

    print_client_stat(user_array[0])


def remove_client():
    user_list = conf['clients']

    if len(user_list) == 0:
        OutFormat.alert(_('No users'))
        return

    selected_user = menu(user_list.values(), '[ ' + _('back') + ' ]', _('Select user for view') + ':')

    if selected_user == 0:
        return

    user_key = str(user_list.keys()[selected_user - 1])
    user_name = user_list[user_key]

    remove_from_file('/etc/3proxy/.proxyauth', user_name + ':CL:')

    conf.remove('clients', str(user_key))


def print_proxy_config():
    http_proxy = get_from_file('/etc/3proxy/3proxy.cfg', 'proxy -p')
    socks_proxy = get_from_file('/etc/3proxy/3proxy.cfg', 'socks -p')

    if '' != http_proxy:
        print (_('Http port') + ': ' + OutFormat.yellow(http_proxy[8:-3]))

    if '' != socks_proxy:
        print (_('Socks port') + ': ' + OutFormat.yellow(socks_proxy[8:]))


def print_client_stat(client_name):
    client_limit = get_client_limit(client_name)

    if None == client_limit:
        print (_('No traffic restrictions'))
        return

    with open("/var/log/3proxy/3proxy.3cf", "rb") as binary_file:
        data = binary_file.read()
        traffic_data = []
        i = 4 * 4 #skip header

        while i < len(data):
            counter = data[i:i + 16]
            counter_data = struct.unpack('<IIII', counter)
            traffic_data.append(counter_data[0])

            i += 4 * 6

        print (_('Traffic limit') + ': ' + OutFormat.yellow(client_limit['limit']) + 'Mb')

        if int(client_limit['index']) - 1 >= len(traffic_data):
            print (_('No traffic used'))
            return

        traffic = traffic_data[int(client_limit['index']) - 1] / 1024 / 1024

        print (_('Used traffic') + ': ' + OutFormat.yellow(str(traffic)) + 'Mb')


conf = Config(os.path.dirname(os.path.realpath(__file__)) + '/3proxy.json')

if conf.has('lang', 'current'):
    _ = lang_init(conf['lang']['current'])
else:
    _ = select_lang()

OutFormat.logo()

if conf['counters']['init'] == 0:
    conf.update('counters', 'init', 1)
    init_setting()
    add_client()
else:
    print_proxy_config()

operation = None
while operation != 0:
    operation = menu([_('initial setup'), _('add user'), _('view users'), _('remove user'), _('select language')], _('exit'))

    if operation == 1:
        init_setting()
    elif operation == 2:
        add_client()
    elif operation == 3:
        view_client()
    elif operation == 4:
        remove_client()
    elif operation == 5:
        _ = select_lang()