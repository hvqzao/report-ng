# report-ng
# Copyright (c) 2015-2017 Marcin Woloszyn (@hvqzao)
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


import sys

from report import Report
from scan import Scan
from version import Version

class CLI(Version):

    def __init__(self):

        #def flagged (key):
        #    return key in sys.argv

        def value (key):
            if key in sys.argv:
                index = sys.argv.index(key)
                if len(sys.argv) > index + 1:
                    return sys.argv[index + 1]
            return None

        def values (key):
            if key in sys.argv:
                return map(lambda x: sys.argv[x + 1], filter(lambda x: x + 1 < len(sys.argv), filter(lambda x: sys.argv[x] == key, range(len(sys.argv)))))
            return None
        
        def is_csv (filename):
            ext = '.csv'
            return filename[-len(ext):] == ext

        def is_yaml (filename):
            ext = '.yaml'
            return filename[-len(ext):] == ext

        template_file = value('-t')
        content_file = value('-c')
        kb_file = value('-k')
        scan_files = values('-s')
        report_file = value('-r')
        output_file = value('-o')

        if template_file and report_file:
            report = Report()
            report.template_load_xml(template_file)
            if content_file:
                if is_yaml(content_file):
                    report.content_load_yaml(content_file)
                else:
                    report.content_load_json(content_file)
            for scan_file in scan_files:
                #report.scan = Scan(scan_file)
                scan = Scan(scan_file)
                report.merge_scan(scan.modify())
                report.content_refresh()
                del scan
            if kb_file:
                if is_csv(kb_file):
                    report.kb_load_csv(kb_file)
                elif is_yaml(kb_file):
                    report.kb_load_yaml(kb_file)
                else:
                    report.kb_load_json(kb_file)
            if output_file:
                json_ext = '.json'
                with open(output_file, 'w') as h:
                    if output_file[-len(json_ext):] == json_ext:
                        h.write(report.content_dump_json().encode('utf-8'))
                    else:
                        h.write(report.content_dump_yaml().encode('utf-8'))
                print 'Output content file saved.'
            report.xml_apply_meta()
            report.save_report_xml(report_file)
            print 'Report saved.'
        elif scan_files and output_file:
            if len(scan_files) > 1:
                print 'Only single scan-file can be provided!'
            else:
                scan = Scan(scan_files[0])
                json_ext = '.json'
                with open(output_file, 'w') as h:
                    if output_file[-len(json_ext):] == json_ext:
                        h.write(scan.dump_json().encode('utf-8'))
                    else:
                        h.write(scan.dump_yaml().encode('utf-8'))
                print 'Output scan file saved.'
        else:
            print 'Usage: '
            print
            print '    ' + self.title + '.exe -t template-file [-c content-file] [-k kb-file] [[-s scan-file] ...] -r output-report-file [-o output-content-file]'
            print '        generate report (and optionally - content as yaml / json)'
            print
            print '    ' + self.title + '.exe -s scan-file -o output-scan-file'
            print '        convert scan xml to yaml or json format (derived from output file extension)'
            print
            print '    ' + self.title + '.exe [--help]'
            print '        display usage and exit'


if __name__ == '__main__':
    #sys.argv += ['--help']
    #sys.argv += ['-t','aaa']
    #sys.argv = [sys.argv[0], '-t', 'asdad']
    CLI()
