# Wasar
# Copyright (c) 2014 Marcin Woloszyn (@hvqzao)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import json, yaml
from lxml import etree

from util import yaml_load, UnsortableOrderedDict


class Scan(object):
    # _xml
    # _scan

    def _webinspect_import(self):
        from webinspect import webinspect_import

        self._scan = webinspect_import(self._xml)

    def _burp_import(self):
        from burp import burp_import

        self._scan = burp_import(self._xml)

    def __init__(self, filename):
        json_ext = '.json'
        yaml_ext = '.yaml'
        if filename[-len(json_ext):] == json_ext:
            self._scan = json.loads(open(filename).read().decode('utf-8-sig'), object_pairs_hook=UnsortableOrderedDict)
        elif filename[-len(yaml_ext):] == yaml_ext:
            self._scan = yaml_load(open(filename).read(), yaml.SafeLoader, UnsortableOrderedDict)
        else:
            # xml
            self._xml = etree.parse(filename)
            root = self._xml.getroot()
            if root.tag == 'Sessions':
                self._webinspect_import()
            elif root.tag == 'issues':
                self._burp_import()
            else:
                raise Exception('Unknown scan format!')

    def dump_json(self):
        return json.dumps(self._scan, indent=2, ensure_ascii=False)  #.decode('utf-8')

    def dump_yaml(self):
        return yaml.dump(self._scan, default_flow_style=False, allow_unicode=True).decode('utf-8')

    def findings(self):
        return self._scan['Findings']


if __name__ == '__main__':
    pass
    '''
    scan = Scan('d8-webinspect-scan.xml')
    scan = Scan('d8-burp-scan.xml')
    print scan.dump_yaml()
    '''
