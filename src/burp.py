# report-ng
# Copyright (c) 2014-2017 Marcin Woloszyn (@hvqzao)
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
import zlib
import base64
from lxml import etree
#from lxml.html import soupparser
import re
import mangle

#from scan import add_extra_fields


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

def _extract_post(request, method):
    if method == 'POST':
        #post = request.split('\n')[-1]
        request_temp = request.replace('\r','')
        loc = request_temp.find('\n\n')
        if loc != -1:
            post = request_temp[loc:].strip()
        del request_temp
    else:
        post = ''
    return post

def burp_import(xml, requests_and_responses=False):
    # initially: Burp Suite Pro (1.6beta2 / 1.6.01 used), recently: 1.6.16
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
            post = _extract_post(request, method)
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
        status_code, status_description = (None, None)
        if response_element and len(status_parts) > 1:
            try:
                status_code, status_description = (int(status_parts[1]), ' '.join(status_parts[2:]))
            except:
                pass
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
        confidence = issue.xpath('./confidence')[0].text
        name = issue.xpath('./name')[0].text
        vuln_id = issue.xpath('./type')[0].text
        issue_background_element = issue.xpath('./issueBackground')
        if issue_background_element:
            issue_background = issue_background_element[0].text
        else:
            issue_background = ''
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
            ['issueBackground', mangle.soap_flatten(issue_background)],
            ['issueDetail', mangle.soap_flatten(issue_detail)],
            ['remediationBackground', mangle.soap_flatten(remediation_background)],
        ])
        #if 'Host header poisoning' in name:
        #if vuln_id == '134217728':
        #    print name
        for i in report_sections:
            report_sections[i] = fine_tune(report_sections[i], i)
        issues_item = [
            ['Severity', severity],
            ['severity_id', severity_id],
            ['Name', name],
            ['Confidence', confidence],
            ['vuln_id', vuln_id],
            ['Scheme', scheme],
            ['Host', host],
            ['Port', port],
            ['Method', method],
            ['Location', location],
            ['Post', post],
            ['VulnParam', vulnparam],
            ['Example', UnsortableOrderedDict([('VulnParam',vulnparam,),('Request',mangle.request_tune(request),),('Response',mangle.response_tune(response),)])],
        ]
        if requests_and_responses:
            issues_item += [
            #['Request', base64.b64encode (zlib.compress (request.encode('utf-8')))],
            #['Response', base64.b64encode (zlib.compress (response.encode('utf-8')))],
            ['Request', base64.b64encode (zlib.compress (request))],
            ['Response', base64.b64encode (zlib.compress (response))],
        ]
        issues_item += [
            ['StatusCode', status_code],
            ['StatusDescription', status_description],
            #['Classifications', map(lambda x: UnsortableOrderedDict([['Name', x[3]], ['URL', x[2]]]), classifications)],
            ['ReportSections', UnsortableOrderedDict(
                map(lambda x: [x.replace(' ', ''), report_sections[x]], report_sections.keys()))],
        ]
        issues_list += [UnsortableOrderedDict(issues_item)]
    findings = []
    for vuln_name in sorted(set(map(lambda x: x['Name'], issues_list))):
        issue = UnsortableOrderedDict()
        for i in filter(lambda x: x['Name'] == vuln_name, issues_list):
            for j in ['Name', 'Severity', 'severity_id', 'Confidence']:  #, 'Classifications'
                if j not in issue:
                    issue[j] = i[j]
            issue['Summary'] = UnsortableOrderedDict()
            issue['Summary']['Description'] = ''
            issue['Summary']['Recommendation'] = ''
            issue['Description'] = ''
            issue['Recommendation'] = ''
            for j in ['ReportSections', 'Example']:
                if j not in issue:
                    issue[j] = i[j]
            for j in ['Occurrences']:
                if j not in issue:
                    issue[j] = []
                v = UnsortableOrderedDict()
                for k in ['Scheme', 'Host', 'Port', 'Method', 'Location', 'Post', 'VulnParam', 'StatusCode', 'StatusDescription']:
                    v[k] = i[k]
                if requests_and_responses:
                    for k in ['Request','Response']:
                        v[k] = i[k]                        
                issue[j] += [v]
        findings += [issue]
    findings.sort(key=lambda x: x['severity_id'], reverse=True)
    for i in findings:
        del i['severity_id']
    #add_extra_fields(findings)
    return UnsortableOrderedDict([['Findings', findings], ])

def burp_items_import(xml, requests_and_responses=False):
    # Burp Pro (1.6.11)
    item_list = []
    items = xml.xpath('/items/item')
    for item in items:
        host = item.xpath('./host')[0].text
        method = item.xpath('./method')[0].text
        port = item.xpath('./port')[0].text
        location = item.xpath('./path')[0].text
        scheme = item.xpath('./protocol')[0].text
        #post = item.xpath('./post')[0].text
        request_element = item.xpath('./request')
        if 'base64' in request_element[0].attrib and request_element[0].attrib['base64'].lower() == 'true':
            request = base64.b64decode(request_element[0].text).replace('\r','')
        else:
            request = request_element[0].text.replace('\r','')
        post = _extract_post(request,method)
        response_element = item.xpath('./response')
        if response_element:
            if 'base64' in response_element[0].attrib and response_element[0].attrib['base64'].lower() == 'true':
                response = base64.b64decode(response_element[0].text).replace('\r','')
            else:
                response = response_element[0].text.replace('\r','')
            status_code = item.xpath('./status')[0].text
            status_description = ' '.join(response.split('\n')[0].split(' ')[2:])
        else:
            response = ''
            status_code = ''
            status_description = ''

        #print scheme,host,port,method,location,post,status_code,status_description
        #print request.split('\n')[:3]
        #print '-'
        #print response.split('\n')[:3]
        build = UnsortableOrderedDict()
        build['Scheme'] = scheme
        build['Host'] = host
        build['Port'] = port
        build['Method'] = method
        build['Location'] = location
        build['Post'] = post
        build['VulnParam'] = ''
        build['StatusCode'] = status_code
        build['StatusDescription'] = status_description
        if requests_and_responses:
            build['Request'] = base64.b64encode (zlib.compress (request))
            build['Response'] = base64.b64encode (zlib.compress (response))
        #build['Request'] = request
        #build['Response'] = response
        item_list += [build]
    return UnsortableOrderedDict([['Occurrences', item_list], ])

if __name__ == '__main__':
    pass

    import yaml
    from lxml import etree
    xml = etree.parse('../examples/example-2-scan-export-Burp (XSS only).xml')
    scan = burp_import(xml)
    print yaml.dump(scan)

    #import yaml
    #from lxml import etree
    #xml = etree.parse('../workbench/pb1/is.xml')
    #scan = burp_import(xml)
    #print yaml.dump(scan)

    #xml = etree.parse('../workbench/xss-2-intruder-items.xml')
    #scan = burp_items_import(xml)
    
    #for i in scan['Findings']:
    #    print i['Name']
    #sample = scan['Findings'][-2]
    #print yaml.dump(sample, default_flow_style=False, allow_unicode=True).decode('utf-8')
