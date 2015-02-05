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
import copy

from util import yaml_load, UnsortableOrderedDict
import mangle

class Scan(object):
    # _xml
    # _scan
    # _filename

    def _webinspect_import(self):
        from webinspect import webinspect_import

        self._scan = webinspect_import(self._xml)

    def _burp_import(self):
        from burp import burp_import

        self._scan = burp_import(self._xml)

    def __init__(self, filename):
        self._filename = filename
        json_ext = '.json'
        yaml_ext = '.yaml'
        if filename[-len(json_ext):] == json_ext:
            self._scan = json.loads(open(filename).read().decode('utf-8-sig'), object_pairs_hook=UnsortableOrderedDict)
        elif filename[-len(yaml_ext):] == yaml_ext:
            self._scan = yaml_load(open(filename).read(), yaml.SafeLoader, UnsortableOrderedDict)
        else:
            # xml
            #self._xml = etree.parse(filename)
            etree_parser = etree.XMLParser(huge_tree=True)
            self._xml = etree.parse(filename, parser=etree_parser)
            root = self._xml.getroot()
            if root.tag == 'Sessions':
                self._webinspect_import()
            elif root.tag == 'issues':
                self._burp_import()
            else:
                raise Exception('Unknown scan format!')

    def modify(self, truncate=True):
        if not truncate:
            return self._scan
        scan = copy.deepcopy(self._scan)
        if 'Findings' in scan:
            for finding in scan['Findings']:
                if 'Occurrences' in finding:
                    for occurrence in finding['Occurrences']:
                        if 'Post' in occurrence:
                            occurrence['Post'] = mangle.http_param_truncate(occurrence['Post'])
        return scan

    def dump_json(self, truncate=True):
        return json.dumps(self.modify(truncate=truncate), indent=2, ensure_ascii=False)  #.decode('utf-8')

    def dump_yaml(self, truncate=True):
        return yaml.dump(self.modify(truncate=truncate), default_flow_style=False, allow_unicode=True).decode('utf-8')

    def findings(self):
        return self._scan['Findings']


if __name__ == '__main__':
    pass

    #scan = Scan('../workbench/webin.xml')
    '''
    # XMLSyntaxError: xmlSAX2Characters: huge text node, line 353377, column 10000871
    line = 353377
    column = 10000871
    line = open('../workbench/webin.xml').read().split('\n')[line]
    print 'line length:', len(line)
    block = 100
    index = 0
    while index < len(line):
        row = line[index:index+block]
        if filter(lambda x: x in row, ['<','>']):
            print index, row
        index += block
    print
    '''
    
    #scan = Scan('../examples/tmp/b-webinspect.xml')
    #print scan.dump_yaml()
    #scan = Scan('../../c-webinspect.xml')
    #print scan.modify(True)['Findings'][0]['Occurrences'][0]['Post']#.keys()
    #print scan.modify(True)['Findings'][0]['Occurrences'][0].keys()
    #print scan.dump_yaml()
    #for i in scan._scan['Findings']:
    #    print i['Name']
