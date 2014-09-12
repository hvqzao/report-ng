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


from util import UnsortableOrderedDict
#import zlib
import base64
from lxml import etree
from lxml.html import soupparser
import re
import mangle


def fine_tune(content, section_name):
    if filter(lambda x: x == content[:len(x)], ['<html>', '<ihtml>']):
        content = re.sub('<br\/>(<br\/>)+', '<br/>', content)
        content = re.sub('(\s|\t|\n)+', ' ', content)
        content = re.sub('\s?<br\/>\s?', '<br/>', content)
        content = re.sub('^<html><br\/>', '<html>', content)
    content = re.sub('^<html\/>', '', content)
    content = content.strip()
    #print content
    #print
    return content

def burp_import(xml):
    # Burp Suite Pro (1.6beta2 / 1.6.01 used)
    issues_list = []
    issues = xml.xpath('/issues/issue')
    for issue in issues:
        full_host = issue.xpath('./host')[0].text
        scheme_split = full_host.split('://')
        scheme = scheme_split[0]
        full_host_parts = scheme_split[1].split(':')
        host = full_host_parts[0]
        if len(full_host_parts) > 1:
            port = int(full_host_parts[-1])
        elif scheme.lower() == 'https':
            port = 443
        else:
            port = 80
        # remove port if not needed
        if scheme.lower() == 'http' and port == 80:
            port = ''
        if scheme.lower() == 'https' and port == 443:
            port = ''
        del scheme_split, full_host_parts
        request_element = issue.xpath('./requestresponse/request')
        if request_element:
            request = base64.b64decode(request_element[0].text).replace('\r','')
            method = request_element[0].attrib['method']
            if method == 'POST':
                post = request.split('\n')[-1]
            else:
                post = ''
        else:
            request = ''
            method = None
            post = ''
        response_element = issue.xpath('./requestresponse/response')
        if response_element:
            response = base64.b64decode(response_element[0].text).replace('\r','')
        else:
            response = ''
            method = None
        status_parts = response.split('\n')[0].split(' ')
        if response_element:
            status_code, status_description = (int(status_parts[1]), ' '.join(status_parts[2:]))
        else:
            status_code, status_description = (None, None)
        del status_parts
        location = ' '.join(request.split('\n')[0].split(' ')[1:-1])
        vulnparam = issue.xpath('./location')[0].text[len(issue.xpath('./path')[0].text):]
        if vulnparam:
            vulnparam = vulnparam[2:-1-10]
            if ' ' in vulnparam:
                vulnparam = ''
        severity = issue.xpath('./severity')[0].text
        if severity == 'Information':
            severity = 'Informational'
        severity_id = ['Informational', 'Low', 'Medium', 'High'].index(severity)
        #confidence = issue.xpath('./confidence')[0].text
        name = issue.xpath('./name')[0].text
        vuln_id = issue.xpath('./type')[0].text
        issue_background = issue.xpath('./issueBackground')[0].text
        issue_detail_element = issue.xpath('./issueDetail')
        if issue_detail_element:
            issue_detail = issue_detail_element[0].text
        else:
            issue_detail = ''
        remediation_background_element = issue.xpath('./remediationBackground')
        if remediation_background_element:
            remediation_background = remediation_background_element[0].text
        else:
            remediation_background = ''
        report_sections = UnsortableOrderedDict([
            ['issueBackground', etree.tostring(soupparser.fromstring(issue_background))],
            ['issueDetail', etree.tostring(soupparser.fromstring(issue_detail))],
            ['remediationBackground', etree.tostring(soupparser.fromstring(remediation_background))],
        ])
        for i in report_sections:
            report_sections[i] = fine_tune(report_sections[i], i)
        issues_list += [UnsortableOrderedDict([
            ['Severity', severity],
            ['severity_id', severity_id],
            ['Name', name],
            ['vuln_id', vuln_id],
            ['Scheme', scheme],
            ['Host', host],
            ['Port', port],
            ['Method', method],
            ['Location', location],
            ['Post', post],
            ['VulnParam', vulnparam],
            ['Example', UnsortableOrderedDict([('VulnParam',vulnparam,),('Request',mangle.request_tune(request),),('Response',mangle.response_tune(response),)])],
            #['Request', base64.b64encode (zlib.compress (request.encode('utf-8')))],
            #['Response', base64.b64encode (zlib.compress (response.encode('utf-8')))],
            ['StatusCode', status_code],
            ['StatusDescription', status_description],
            #['Classifications', map(lambda x: UnsortableOrderedDict([['Name', x[3]], ['URL', x[2]]]), classifications)],
            ['ReportSections', UnsortableOrderedDict(
                map(lambda x: [x.replace(' ', ''), report_sections[x]], report_sections.keys()))],
        ])]
    findings = []
    for vuln_id in sorted(set(map(lambda x: int(x['vuln_id']), issues_list))):
        issue = UnsortableOrderedDict()
        for i in filter(lambda x: int(x['vuln_id']) == vuln_id, issues_list):
            for j in ['Severity', 'severity_id', 'Name', 'ReportSections', 'Example']:  #, 'Classifications'
                if j not in issue:
                    issue[j] = i[j]
                    #else:
                    #    if issue[j] != i[j]:
                    #        print j
            for j in ['Occurrences']:
                if j not in issue:
                    issue[j] = []
                v = UnsortableOrderedDict()
                for k in ['Scheme', 'Host', 'Port', 'Method', 'Location', 'Post', 'VulnParam', 'StatusCode', 'StatusDescription']:
                    v[k] = i[k]
                #for k in ['Request','Response']:
                #    v[k] = i[k]                        
                issue[j] += [v]
        findings += [issue]
    findings.sort(key=lambda x: x['severity_id'], reverse=True)
    for i in findings:
        del i['severity_id']
    return UnsortableOrderedDict([['Findings', findings], ])

if __name__ == '__main__':
    pass

    import yaml
    from lxml import etree
    xml = etree.parse('../examples/tmp/b-burp.xml')
    scan = burp_import(xml)
    sample = scan['Findings'][-2]
    print yaml.dump(sample, default_flow_style=False, allow_unicode=True).decode('utf-8')
