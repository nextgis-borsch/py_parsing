# -*- coding: utf-8 -*-

import sys
import os
import json

version = '0.0.0'
download_url = ''

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)
    name = data['info']['name']
    version_less_than = sys.argv[3]

    for version, i in reversed(data['releases'].items()):
        if version < version_less_than:
            index = len(i) - 1
            if i[index]['url'].endswith('tar.gz') or i[index]['url'].endswith('zip'):
                download_url = i[0]['url']
                date = i[index]['upload_time'].replace('T', ' ')
                break

    version_file_name = os.path.join(os.path.dirname(sys.argv[1]), 'version.str')
    version_file = open(version_file_name, 'w')
    pack_name = "{}-{}-{}".format(name, version, sys.argv[2])
    version_file.write("{}\n{}\n{}".format(version, date, pack_name))
    version_file.close()

print(download_url + ';' + version + ';' + pack_name)
