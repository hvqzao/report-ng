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


from util import yaml_load, UnsortableOrderedDict
import util
from openxml import Openxml
from pseudohtml import InlineHtmlParser, HtmlParser
from scan import Scan
import mangle

from lxml import etree
import yaml, json
import os
import os.path
from cgi import escape
#import base64
#import docx

import copy
from datetime import datetime

docx = None


class Report(object):
    class ns:
        w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        c = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
        r = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        a = 'http://schemas.openxmlformats.org/package/2006/relationships'
        pkg = 'http://schemas.microsoft.com/office/2006/xmlPackage'

    severity = UnsortableOrderedDict([
        ('Critical', 4),
        ('High', 3),
        ('Medium', 2),
        ('Low', 1),
        ('Informational', 0),
        ('Best Practices', -1)
    ])

    _template_filename = None
    #_docx = None
    _xml = None
    _struct = []
    _skel = UnsortableOrderedDict()
    _content_filename = None
    _content_yaml = None
    _content = None
    _meta = None
    _kb_filename = None
    _kb_type = None
    _kb = None
    _nmap = None
    _nmap_filenames = []
    _openxml = None
    _html_parser = None
    _ihtml_parser = None
    scan = None
    template_cleanup_required = None
    #__vulnparam_highlighting = True
    #__truncate = True
    _pPr_annotation = False
    chartIterator = 0

    def __init__(self):
        self._meta_init()

    def _cleanup(self):
        #if self._docx:
        #   del self._docx
        #self._docx = None
        if self._xml:
            del self._xml
        self._xml = None
        if self._openxml:
            del self._openxml
        self._openxml = None
        if self._html_parser:
            del self._html_parser
        self._html_parser = None
        if self._ihtml_parser:
            del self._ihtml_parser
        self._ihtml_parser = None
        if self._struct:
            del self._struct
        self._struct = []
        if self._skel:
            del self._skel
        self._skel = UnsortableOrderedDict()
        if self._content:
            del self._content
        self._content = None
        if self._meta:
            del self._meta
        self._meta_init()
        if self._kb:
            del self._kb
        self._kb = None
        if self._nmap:
            del self._nmap
        self._nmap = None
    @staticmethod
    def _dump_json(target):
        return json.dumps(target, indent=2, ensure_ascii=False)  #.decode('utf-8')

    def _dump_yaml(self, target):
        return yaml.dump(target, default_flow_style=False, allow_unicode=True).decode('utf-8')

    def _reserved(self, value):
        if value[-1][-1] in ['?', '!']:
            return True
        severity_keys = map(lambda x: self._severity_tag(x), self.severity.keys())
        if value == ['Findings', 'Chart']:
            return True
        if value[0] == 'Findings' and value[1] in severity_keys:
            return True
        if value[0] == 'Summary' and value[1] in severity_keys:
            return True
        if value == ['Finding']:
            return True
        #severity_keys_q = map(lambda x: self._severity_tag(x)+'?', self.severity.keys())
        #if value[0] == 'Finding' and value[1] in severity_keys_q:
        #    return True
        return False

    def _xml_val(self, children):
        return ''.join(map(lambda x: x.text, etree.ETXPath('.//{%s}t' % self.ns.w)(children[0])))

    def _template_parse(self, clean=False):
        summary_fields = []
        for alias in etree.ETXPath('//{%s}alias' % self.ns.w)(self._xml):
            value = alias.attrib['{%s}val' % self.ns.w].split('.')
            sdt = alias.getparent().getparent()
            children = etree.ETXPath('./{%s}sdtContent' % self.ns.w)(sdt)[0].getchildren()
            reserved = self._reserved(value)
            #print ['-','+'][int(reserved)], value
            self._struct += [[value, sdt, children]]
            #print value, reserved
            if not reserved:
                skel = self._skel
                for i in range(len(value)):
                    if value[i] not in skel.keys():
                        skel[value[i]] = UnsortableOrderedDict()
                        if value == ['Finding'] or i == len(value) - 1 and len(children) == 1 and children[0].tag == '{%s}tr' % self.ns.w:
                            skel[value[i]] = [UnsortableOrderedDict()]
                    skel = skel[value[i]]
                    if isinstance(skel, list):
                        skel = skel[0]
                del skel
            else:
                if len(value) == 3 and value[0] == 'Summary'\
                        and value[1] in map(lambda x: self._severity_tag(x),
                                            self.severity.keys()) and value[2] not in ['Finding']:
                    if value[2][-1] != '#' and value[2] not in summary_fields:
                        summary_fields += [value[2]]

        def leaf(skel):
            for i in skel.keys():
                if isinstance(skel[i], list):
                    leaf(skel[i][0])
                if isinstance(skel[i], UnsortableOrderedDict):
                    if not skel[i].keys():
                        skel[i] = ''
                    else:
                        leaf(skel[i])

        leaf(self._skel)
        if not clean:
            for i in self._struct:
                if self._skel.has_key(i[0][0]):
                    x = self._skel[i[0][0]]
                    for j in i[0][1:]:
                        if isinstance(x, list):
                            x = x[0]
                        if j in x:
                            if x[j] == '':
                                x[j] = self._xml_val(i[2])
                            else:
                                x = x[j]
                        else:
                            continue
        self._skel['Findings'] = [UnsortableOrderedDict()]
        for i in ['Name', 'Severity']:
            i_struct = filter(lambda x: x[0] == ['Finding', i], self._struct)
            if not clean and len(i_struct):
                self._skel['Findings'][0][i] = self._xml_val(i_struct[0][2])
            else:
                self._skel['Findings'][0][i] = ''
            del i_struct
            if i in self._skel['Finding']:
                del self._skel['Finding'][i]
        if summary_fields:
            self._skel['Findings'][0]['Summary'] = UnsortableOrderedDict()
            for i in summary_fields:
                if not clean:
                    self._skel['Findings'][0]['Summary'][i] = self._xml_val(
                        filter(lambda x: len(x[0]) > 2 and x[0][0] == 'Summary' and x[0][2] == i, self._struct)[0][2])
                else:
                    self._skel['Findings'][0]['Summary'][i] = ''
        for i in self._skel['Finding'].keys():
            self._skel['Findings'][0][i] = self._skel['Finding'][i]
            del self._skel['Finding'][i]
        del self._skel['Finding']

    def template_dump_json(self):
        return self._dump_json(self._skel)

    def template_dump_yaml(self):
        return self._dump_yaml(self._skel)

    def template_dump_struct(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        #pp.pprint(self._struct)
        #pp.pprint(map(lambda x: [x[0], map(lambda y: y.tag[y.tag.index('}') + 1:], x[2])], self._struct))
        return pp.pformat(map(lambda x: [x[0], map(lambda y: y.tag[y.tag.index('}') + 1:], x[2])], self._struct))

    def template_reload(self, clean=False):
        self._cleanup()
        self._xml = etree.parse(self._template_filename)
        self._openxml = Openxml(self._xml)
        self._html_parser = etree.XMLParser(target=HtmlParser(self._openxml), resolve_entities=False)
        self._ihtml_parser = etree.XMLParser(target=InlineHtmlParser(self._openxml), resolve_entities=False)
        self._template_parse(clean=clean)
        self._content_parse(self._skel)  # TODO added - test if ok
        self.template_cleanup_required = False
        return self

    def template_load_xml(self, filename, clean=False):
        self._template_filename = filename
        return self.template_reload(clean=clean)

    def is_template_with_nmap(self):
        return 'OpenPorts' in self._skel

    #def template_load_docx(self, filename, clean=False):
    #   self._docx = docx.Document(docx=filename)
    #   self._xml = self._docx._document_part._element
    #   self._template_parse(clean=clean)
    #   return self
    def save_report_xml(self, filename):
        if self._xml:
            self._xml.write(filename, xml_declaration=True, encoding='UTF-8')
            #if not self._docx:
            #    self._xml.write (filename, xml_declaration=True, encoding='UTF-8')
            #else:
            #    raise Exception ('docx templates must be saved as docx!')
        else:
            raise Exception('no template loaded!')

    def _meta_init(self):
        self._meta = UnsortableOrderedDict([('Findings', []), ('KB', []), ('Data', UnsortableOrderedDict())])

    def _content_parse(self, meta):
        self._content = meta.copy()
        self._meta_init()
        #self._meta['Findings'] = meta['Findings']
        #self._meta['Meta'] = UnsortableOrderedDict()
        #self._meta['Meta']['Findings'] = UnsortableOrderedDict()
        #for i in self.severity.keys():
        #    self._meta['Meta']['Findings'][i] = len (filter (lambda x: x['Severity'] == i, self._meta['Findings']))
        #del meta['Findings']
        self._meta['Data'] = meta.copy()
        #self._meta['Findings'] = self._meta['Data']['Findings'][:]
        if 'Findings' in self._meta['Data']:
            self._meta['Findings'] = filter(lambda x: x['Severity'] in self.severity.keys(), self._meta['Data']['Findings'])
            del self._meta['Data']['Findings']
        if self._kb:
            self._kb_meta_update()
        return self

    def content_reload(self):
        if self._content_yaml:
            self._content_parse(yaml_load(open(self._content_filename).read(), yaml.SafeLoader, UnsortableOrderedDict))
        else:
            self._content_parse(json.loads(open(self._content_filename).read().decode('utf-8-sig'),
                                           object_pairs_hook=UnsortableOrderedDict))
        return self

    def content_refresh(self):
        self._content_parse(self._content)

    def content_load_yaml(self, filename):
        self._content_filename = filename
        self._content_yaml = True
        return self.content_reload()

    def content_load_json(self, filename):
        self._content_filename = filename
        self._content_yaml = False
        return self.content_reload()

    def content_dump_json(self):
        return self._dump_json(self._content)

    def content_dump_yaml(self):
        return self._dump_yaml(self._content)

    def meta_dump_json(self):
        return self._dump_json(self._meta)

    def meta_dump_yaml(self):
        return self._dump_yaml(self._meta)

    @staticmethod
    def _v(struct, path):
        for i in path:
            struct = struct[i]
        return struct

    @staticmethod
    def _p(struct, path):
        for i in path[:-1]:
            if i not in struct:
                return None
            struct = struct[i]
        return struct

    def _xml_block_aliases(self, block):
        aliases = map(lambda x: UnsortableOrderedDict(
            [('struct', x.attrib['{%s}val' % self.ns.w].split('.')), ('sdt', x.getparent().getparent())]),
                      etree.ETXPath('.//{%s}alias' % self.ns.w)(block))
        for i in range(len(aliases)):
            aliases[i]['children'] = etree.ETXPath('./{%s}sdtContent' % self.ns.w)(aliases[i]['sdt'])[0].getchildren()
        return aliases

    #def _xml_sdt_single (self, value, sdt, children):
    #    if children[0].tag in ['{%s}p' % self.ns.w, '{%s}r' % self.ns.w, '{%s}tc' % self.ns.w]:
    #        tag = etree.ETXPath ('.//{%s}t' % self.ns.w) (children[0])
    #        tag[0].text = unicode(value)
    #        parent = sdt.getparent()
    #        parent.replace(sdt, children[0])
    #        del tag
    @staticmethod
    def _is_html(value):
        preamble = '<html>'
        try:
            return unicode(value).strip().lower()[:len(preamble)] == preamble
        except:
            return str(value).strip().lower()[:len(preamble)] == preamble

    @staticmethod
    def _is_ihtml(value):
        preamble = '<ihtml>'
        try:
            return unicode(value).strip().lower()[:len(preamble)] == preamble
        except:
            return str(value).strip().lower()[:len(preamble)] == preamble

    def _xml_sdt_single(self, value, sdt, children, struct=None):
        #print children
        #if struct:
        #    print struct
        p_r = filter(lambda x: x.tag in ['{%s}p' % self.ns.w, '{%s}r' % self.ns.w], children)
        tc = filter(lambda x: x.tag in ['{%s}tc' % self.ns.w], children)
        p_r_tc = p_r + tc
        if len(p_r_tc):
            #print '-'
            '''
            if self._is_html(value):
                self._openxml.set_sdt_cursor(cursor=sdt)
                self._openxml.parse(value, self._html_parser)
                self._openxml.remove_sdt_cursor()
            elif self._is_ihtml(value):
                self._openxml.set_sdt_cursor(cursor=sdt)
                self._openxml.parse(value, self._ihtml_parser)
                self._openxml.remove_sdt_cursor()
            '''
            if not util.binary(value) and (self._is_html(value) or self._is_ihtml(value)):
                block = etree.Element('Summary')
                for i in children:
                    block.append(etree.fromstring(etree.tostring(i)))
                if self._pPr_annotation == True:
                    pPr = None
                if len(tc):
                    _tc = filter(lambda x: x.tag in ['{%s}tc' % self.ns.w], block.getchildren())
                    _p_r = filter(lambda x: x.tag in ['{%s}p' % self.ns.w, '{%s}r' % self.ns.w], _tc[0])
                    cursor = _p_r[0]
                else:
                    _p_r = filter(lambda x: x.tag in ['{%s}p' % self.ns.w, '{%s}r' % self.ns.w], block.getchildren())
                    if self._pPr_annotation == True:
                        # try to get the formatting (pPr)
                        _p = filter(lambda x: x.tag in ['{%s}p' % self.ns.w], block.getchildren())
                        if len(_p) > 0:
                            pPrs = etree.ETXPath('./{%s}pPr' % self.ns.w)(_p[0])
                            if len(pPrs) > 0:
                                pPr = pPrs[0]
                                #print etree.tostring(pPr)
                        del _p
                    cursor = _p_r[0]
                self._openxml.set_sdt_cursor(cursor=cursor)
                self._openxml.parse(value, [self._html_parser, self._ihtml_parser][self._is_ihtml(value)])
                self._openxml.remove_sdt_cursor()
                parent = sdt.getparent()
                for i in block.getchildren():
                    if self._pPr_annotation == True and pPr != None and i.tag in ['{%s}p' % self.ns.w] and len(filter(lambda x: x.tag in ['{%s}pPr' % self.ns.w], i.getchildren())) == 0:
                        i.insert(0, etree.fromstring(etree.tostring(pPr)))
                    parent.insert(parent.index(sdt), i)
                parent.remove(sdt)
            else:
                if util.binary(value):
                    value = util.binary_safe(value)
                values = unicode(value).split('\n')
                build = []
                for v in values:
                    block = etree.fromstring(etree.tostring(p_r_tc[0]))
                    tags = etree.ETXPath('.//{%s}t' % self.ns.w)(block)
                    if len(tags) > 0:
                        tags[0].text = util.xml_valid_unicode(v)
                        for tag in tags[1:]:
                            tag_parent = tag.getparent()
                            tag_parent.remove(tag)
                            del tag_parent                        
                    build += [block]
                    del tags, block
                parent = sdt.getparent()
                for i in build:
                    parent.insert(parent.index(sdt), i)
                parent.remove(sdt)
                del build
            return True
        else:
            return False

    @staticmethod
    def surround(text, search, tag, inline=True):
        text = escape(text)
        start = text.find('&amp;'+search+'=')
        if start != -1:
            start += 5
        else:
            start = text.find(search+'=')
        if start == -1:
            return text
        else:
            walk = text[start+len(search)+1:]
            end = walk.find('&amp;')
            if end == -1:
                return '<'+['','i'][inline]+'html>'+text[:start]+'<'+tag+'>'+text[start:]+'</'+tag+'>'+'</'+['','i'][inline]+'html>'
            else:
                return '<'+['','i'][inline]+'html>'+text[:start]+'<'+tag+'>'+text[start:start+len(search)+1+end]+'</'+tag+'>'+text[start+len(search)+1+end:]+'</'+['','i'][inline]+'html>'
            return text

    def _xml_apply_data(self, struct, value, sdt, children):
        #print '*',struct, value
        if not children:
            return
        if not self._xml_sdt_single(value, sdt, children, struct=struct) and children[0].tag in ['{%s}tr' % self.ns.w]:
            #print '+',struct
            build = []
            for row in value:
                #print type(row), row
                if isinstance(row, str) or isinstance(row, unicode):
                    continue
                block = etree.fromstring(etree.tostring(children[0]))
                aliases = self._xml_block_aliases(block)
                for col in row:
                    #print 'x', col
                    alias_match_q = filter(lambda x: x['struct'] == struct + [str(col)+'?'], aliases)
                    if alias_match_q:
                        #print 'q'
                        if row[col]:
                            self._xml_sdt_replace(alias_match_q[0]['sdt'], alias_match_q[0]['children'])
                        else:
                            self._xml_sdt_remove(alias_match_q[0]['sdt'])
                    del alias_match_q
                    alias_match = filter(lambda x: x['struct'] == struct + [str(col)], aliases)
                    if not alias_match:
                        continue
                    alias = alias_match[0]

                    tags = etree.ETXPath('.//{%s}t' % self.ns.w)(alias['children'][0])
                    if len(tags) > 0:
                        val = row[col]
                        #if struct == ['Finding', 'Occurrences'] and 'Method' in row and 'VulnParam' in row and row['VulnParam']:
                        if struct == ['Finding', 'Occurrences'] and 'Method' in row:
                            if col == 'Post' and '\n' in val and not self._is_html(val) and not self._is_ihtml(val):
                                # highlighting could be added here as well I suppose
                                val = '<html>'+val.replace('\n','<br/>\n')+'</html>'
                            else:
                                if col == 'Post' and row['Method'] == 'POST':
                                    if self.__truncate:
                                        val = mangle.http_param_truncate(val)
                                if col == 'Location' and row['Method'] == 'GET' or col == 'Post' and row['Method'] == 'POST':
                                    if self.__vulnparam_highlighting and 'VulnParam' in row and row['VulnParam']:
                                        val = self.surround(val,row['VulnParam'],'red')
                        if self._is_html(val):
                            self._openxml.set_sdt_cursor(cursor=tags[0])
                            self._openxml.parse(val, self._html_parser)
                            self._openxml.remove_sdt_cursor()
                        elif self._is_ihtml(val):
                            self._openxml.set_sdt_cursor(cursor=tags[0])
                            self._openxml.parse(val, self._ihtml_parser)
                            self._openxml.remove_sdt_cursor()
                        elif isinstance(val, list):
                            pass # TODO
                            #print struct+[str(col)], val
                            self._xml_apply_data(struct+[str(col)], val, alias['sdt'], alias['children'])
                        elif val == None:
                            tags[0].text = ''
                        else:
                            #tags[0].text = unicode(val)
                            tags[0].text = util.xml_valid_unicode(val)
                        for tag in tags[1:]:
                            tag_parent = tag.getparent()
                            tag_parent.remove(tag)
                            del tag_parent                        
                        parent = alias['sdt'].getparent()
                        if parent != None:
                            parent.replace(alias['sdt'], alias['children'][0])
                    del alias_match, alias
                build += [block]
                del aliases, block
            parent = sdt.getparent()
            for i in build:
                parent.insert(parent.index(sdt), i)
            parent.remove(sdt)
            del build
            #print
        #struct_q = struct[:]
        #struct_q[-1] += '?'
        #if self
        #print struct

    def _xml_sdt_replace (self, sdt, children):
        parent = sdt.getparent()
        if parent != None:
            for i in children:
                parent.insert(parent.index(sdt), i)
            parent.remove(sdt)

    def _xml_sdt_remove (self, sdt):
        parent = sdt.getparent()
        if parent != None:
            parent.remove(sdt)

    @staticmethod
    def _severity_tag(severity):
        if severity == 'Best Practices':
            return 'BestPractices'
        else:
            return severity

    @staticmethod
    def _kb_val(finding_val, kb_val):
        #if not kb_val:
        #    return finding_val
        #if not finding_val:
        #    return kb_val
        #return finding_val+'\n'+kb_val
        if finding_val:
            return finding_val
        elif kb_val:
            return kb_val
        else:
            return ''

    ''' get knowledgebase item for given finding [name, severity] '''
    def _kb_match(self, name, severity, knowledgebase):
        kb = None
        if self._kb:
            kb_match = filter(lambda x: x['Name'] == name and x['Severity'] == severity, knowledgebase)
            if kb_match:
                kb = kb_match[0]
            del kb_match
            if kb == None:
                # find matching alias, if such exist
                #kb_match_aliases = filter(lambda x: 'Aliases' in x and name in x['Aliases'].split('\n') and x['Severity'] == severity, knowledgebase)
                kb_match_aliases = filter(lambda x: 'Aliases' in x and unicode(name).replace(u'\u200b','').lower() in x['Aliases'].lower().split('\n'), knowledgebase)
                #for i in map(lambda x: x['Aliases'].split('\n'), knowledgebase):
                #    print [name], unicode(name).replace(u'\u200b','') in i, i
                #print name, kb_match_aliases != []
                if kb_match_aliases:
                    kb = kb_match_aliases[0]
                del kb_match_aliases
        return kb

    def remove_kb(self):
        self._kb_filename = None
        self._kb_type = None
        if self._kb:
            del self._kb
        self._kb = None
        self._meta['KB'] = []

    ''' replaces kb updates during report generation '''
    def merge_kb(self):
        if self._kb == None or self._kb.keys() == []:
            return
        
        #self._content
        #self._kb
        #print self._dump_yaml(self._kb)
    
        def submerge(block, knowledge, path):
            for node in block:
                if path == [] and node in ['Name', 'Severity']:
                    continue
                if isinstance(block[node], dict) and knowledge.has_key(node):
                    #print len(path)*2*' ', node + ':'
                    submerge(block[node], knowledge[node], path + [node])
                    continue
                #print len(path)*2*' ', node + ':', type(finding[node])
                if not filter(lambda x: isinstance(block[node], x), [list, dict]):
                    if block[node] != None and len(block[node].strip()) == 0 and knowledge.has_key(node):
                        block[node] = knowledge[node]
            
        knowledgebase = self._kb[self._kb.keys()[0]][:]
        #print self._dump_yaml(kb)
        if self._content != None and isinstance(self._content, dict) and self._content.has_key('Findings'):
            for finding in self._content['Findings']:
                kb = self._kb_match(finding['Name'], finding['Severity'], knowledgebase)
                if kb != None:
                    submerge(finding, kb, [])
                #print self._dump_yaml(self._content)
                del kb
        return self._content
    
    def _xml_apply_findings(self):
        finding_struct = filter(lambda x: x[0] == ['Finding'], self._struct) #the whole Finding object in Word template (including Factors/Description etc.)
        #print map(lambda x: x['Name'], self._meta['Findings'])
        findings = self._meta['Findings']
        for severity in self.severity.keys():
            severity_tag = self._severity_tag(severity)
            severity_findings = filter(lambda x: x['Severity'] in severity, findings)
            findings_placeholder_row = filter(lambda x: x[0] == ['Findings', severity_tag], self._struct)
            if len(findings_placeholder_row):
                findings_placeholder = findings_placeholder_row[0][1]
                findings_placeholder_parent = findings_placeholder.getparent()
            summary_struct = filter(lambda x: x[0] == ['Summary', severity_tag], self._struct)
            #print summary_struct
            if summary_struct:
                summary_placeholder = summary_struct[0][1]
                summary_placeholder_parent = summary_placeholder.getparent()
                #print summary_placeholder
                #print summary_placeholder_parent
            for finding in severity_findings:
                #print '[*]',finding['Name']
                #print finding
                kb = self._kb_match(finding['Name'], finding['Severity'], self._meta['KB'])
                #print '?',kb != None
                # Build Finding xml block
                block = etree.Element('Finding')
                for i in finding_struct[0][2]:
                    block.append(etree.fromstring(etree.tostring(i)))
                aliases = self._xml_block_aliases(block)
                aliases_abs = map(lambda x: '.'.join(x['struct']), aliases)
                for i in aliases:
                    alias_abs = '.'.join(i['struct'])
                    #print ' ',alias_abs
                    # handle aliases ending with ! (acts as "if not", eg. Finding.Node not set or set to '')

                    #if alias_abs[-1] == '!' and len(i['struct'][1:]) == 1:
                    #    needle = i['struct'][-1][:-1]
                    #    if not finding.has_key(needle) or not len(finding[needle]):
                    #        self._xml_sdt_replace(i['sdt'], i['children'])
                    #    else:
                    #        self._xml_sdt_remove(i['sdt'])
                    #    del needle
                    #    continue

                    # instead of above, should handle Finding.root and Finding.[...].child elements
                    if alias_abs[-1] == '!' and len(i['struct'][1:]) >= 1:
                        #print i['struct']
                        val = finding
                        for j in i['struct'][1:][:-1] + [i['struct'][-1][:-1]]:
                            if val.has_key(j):
                                val = val[j]
                                #print 'o', val
                            else:
                                val = None
                                break
                        if val != None and len(val) > 0:
                            self._xml_sdt_remove(i['sdt'])
                        else:
                            self._xml_sdt_replace(i['sdt'], i['children'])
                        continue

                    if alias_abs[-1] == '?':
                        # is this finding.[severity]? -> if yes, replace content, otherwise delete me
                        if i['struct'][-1] in map(lambda x: self._severity_tag(x)+'?', self.severity.keys()):
                            if i['struct'][-1] == severity_tag+'?':
                                factorsArr = [1,1,1,1]

                                if 'Factors' in finding:
                                    factors = finding['Factors']

                                    factorsArr = map(lambda x: x if ("" + x).isdigit() else 1, [
                                        factors['Impact']['Business'],
                                        factors['Impact']['Technical'],
                                        factors['Likelihood']['Vulnerability'],
                                        factors['Likelihood']['ThreatAgent']
                                    ])
                                # if it's not a chart, then simply replace. otherwise apply to a chart
                                if not map(lambda x: etree.ETXPath('.//{%s}chart' % self.ns.c)(x), i['children'])[0]:
                                    self._xml_sdt_replace(i['sdt'], i['children'])
                                else:
                                    self._xml_apply_chart([[i['struct'], i['sdt'], i['children']]], factorsArr)
                                #self._xml_sdt_replace(i['sdt'], i['children'])
                                #print '+', finding['Name'], finding['Severity']
                            else:
                                self._xml_sdt_remove(i['sdt'])
                                #print '-', finding['Name'], finding['Severity']
                        else:
                        #    # is this finding.[key_not_found]? -> if yes, delete me
                        #    #print '?', alias_abs
                            val = finding
                            for j in i['struct'][1:][:-1] + [i['struct'][-1][:-1]]:
                                if isinstance(val, list):
                                    if not self._check_list_for_key(val, j):
                                        val = None
                                        break
                                elif val.has_key(j):
                                    val = val[j]
                                    #print 'o', val
                                else:
                                    val = None
                                    break

                            if val == None or len(val) == 0:
                                self._xml_sdt_remove(i['sdt'])
                    else:
                        # TODO recent fixes
                        #print 's',i['struct']
                        #if self._p(finding, i['struct'][1:]) == None:
                        #    print 'x',None
                        #    continue
                        if self._p(finding, i['struct'][1:]) != None and not isinstance(self._p(finding, i['struct'][1:]), list) and i['struct'][1:][-1] in self._p(finding, i['struct'][1:]):
                            #if self._p (finding, i['struct'][1:]).has_key(i['struct'][1:][-1]):
                            finding_val = self._v(finding, i['struct'][1:])
                        else:
                            finding_val = ''
                        kb_val = None
                        #print ' ', i['struct'], kb != None
                        if kb:
                            if i['struct'] not in [['Finding', 'Name'], ['Finding', 'Severity']]:
                                kb_p = self._p(kb, i['struct'][1:])
                                if kb_p and kb_p.has_key(i['struct'][1:][-1]):
                                    kb_val = self._v(kb, i['struct'][1:])
                                del kb_p
                        #self._xml_sdt_single (self._kb_val (finding_val, kb_val), i['sdt'], i['children'])
                        ultimate_val = self._kb_val(finding_val, kb_val)
                        #print '+', alias_abs
                        #print '=',ultimate_val
                        #print i['struct'], ultimate_val, i['sdt']
                        self._xml_apply_data(i['struct'], ultimate_val, i['sdt'], i['children'])
                        #print finding['Name'], i['struct']
                        alias_search = i['struct'][:]
                        alias_search[-1] += '?'
                        alias_search_matched = filter(lambda x: x['struct'] == alias_search, aliases)
                        if alias_search_matched: # and not isinstance(ultimate_val, list):
                            #print alias_search_matched[0]['struct']
                            #print ' ',alias_search, alias_search_matched, bool(ultimate_val)
                            # value present? -> leave contents, otherwise delete me
                            if ultimate_val:
                                self._xml_sdt_replace(alias_search_matched[0]['sdt'], alias_search_matched[0]['children'])
                            else:
                                self._xml_sdt_remove(alias_search_matched[0]['sdt'])
                        del alias_search_matched
                        del kb_val, finding_val, ultimate_val
                    del alias_abs
                # Insert Finding
                if len(findings_placeholder_row) > 0:
                    for i in block.getchildren():
                        findings_placeholder_parent.insert(findings_placeholder_parent.index(findings_placeholder), i)
                del block, aliases, aliases_abs
                # Summary row
                if summary_struct:
                    # Build a summary row xml block
                    block = etree.Element('Summary')
                    for i in summary_struct[0][2]:
                        block.append(etree.fromstring(etree.tostring(i)))
                    aliases = self._xml_block_aliases(block)
                    for i in aliases:
                        #print '+',i['struct']
                        if i['struct'] == ['Summary', severity_tag, 'Finding']:
                            self._xml_sdt_single(finding['Name'], i['sdt'], i['children'])
                        elif i['struct'][-1][-1] == '#':
                            i_hash = i['struct'][:]
                            i_hash[-1] = i_hash[-1][:-1]
                            if i_hash[2:][0] in finding:
                                i_hash_count = len(self._v(finding, i_hash[2:])) or 1
                            else:
                                i_hash_count = 1
                            self._xml_sdt_single(i_hash_count, i['sdt'], i['children'])
                            del i_hash
                        else:
                            #print finding
                            if 'Summary' in finding and i['struct'][2] in finding['Summary']:
                                finding_val = finding['Summary'][i['struct'][2]]
                            elif finding.has_key(i['struct'][2]):
                                finding_val = finding[i['struct'][2]]
                            else:
                                finding_val = ''
                            kb_val = None
                            if kb:
                                if 'Summary' in kb and i['struct'][2] in kb['Summary']:
                                    kb_val = kb['Summary'][i['struct'][2]]
                            self._xml_sdt_single(self._kb_val(finding_val, kb_val), i['sdt'], i['children'])
                            del kb_val, finding_val
                    for i in block.getchildren():
                        summary_placeholder_parent.insert(summary_placeholder_parent.index(summary_placeholder), i)
                    del block, aliases
                del kb
            if findings_placeholder_row:
                if summary_struct:
                    summary_placeholder_parent.remove(summary_placeholder)
                if len(severity_findings) > 0:
                    findings_placeholder_parent.remove(findings_placeholder)
                else:
                    if len(findings_placeholder_row):
                        if self._xml_val(findings_placeholder_row[0][2]).strip() != '':
                            self._xml_sdt_replace(findings_placeholder, findings_placeholder_row[0][2])
                        else:
                            self._xml_sdt_remove(findings_placeholder)
                del findings_placeholder, findings_placeholder_parent
            del findings_placeholder_row
            if summary_struct:
                del summary_placeholder, summary_placeholder_parent
            del severity_findings, summary_struct
        # Remove Finding template
        template = finding_struct[0][1]
        template_parent = template.getparent()
        template_parent.remove(template)
        del template_parent, template

    def _check_list_for_key(self, target_list, key):
        for obj in target_list:
            if isinstance(obj, list):
                return False
            
            if not obj.has_key(key):
                return False
        
        return True
    # Generate Chart
    def _xml_apply_chart(self, chart_struct, values):
        #if not self._docx:
        #...
        #else:
        #   #>>> a = docx.Document(docx='d3.docx')
        #   #>>> p=a._package
        #   chart_rid = reduce(lambda x,y: x+y, map(lambda x: etree.ETXPath ('.//{%s}chart' % self.ns.c) (x), chart_struct[0][2]))[0].attrib['{%s}id' % self.ns.r]
        #   chart_part = filter (lambda x: chart_rid in x and x[chart_rid].reltype == 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart', map (lambda x: x.rels, self._docx._package.parts))[0][chart_rid].target_part.package#._element #.package.main_document._element
        #   print chart_part
        #   #chart = etree.ETXPath ('.//{%s}chart' % self.ns.c) (chart_part)[0]
        #   #chart_num = etree.ETXPath('//{%s}val/{%s}numRef/{%s}f' % ((self.ns.c,)*3)) (chart)[0]
        #   #print chart_num
        #chart_rid = etree.ETXPath ('.//{%s}chart' % self.ns.c) (chart_struct[0][2][0])[0].attrib['{%s}id' % self.ns.r]
        #chart_struct = copy.deepcopy(chart_structOrg)
       # structOrgParent = chart_structOrg.getparent()
       # structOrgParent.append(chart_struct)
        chart = \
            reduce(lambda x, y: x + y,
                   map(lambda x: etree.ETXPath('.//{%s}chart' % self.ns.c)(x), chart_struct[0][2]))[0]
        chart_rid = chart.attrib['{%s}id' % self.ns.r]

        # iterator used for identifying copies of charts
        self.chartIterator += 1
        chartNewId = chart_rid + 'copy' + str(self.chartIterator)

        chart.attrib['{%s}id' % self.ns.r] = chartNewId

        # charts/chart.xml
        chart_rel = filter(lambda x: x.attrib['Id'] == chart_rid and x.attrib[
            'Type'] == 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart',
                                      etree.ETXPath('//{%s}Relationship' % self.ns.a)(self._xml))[0]

        chart_rel_target = chart_rel.attrib['Target']
        chart_rel_targetCopy = 'copy' + str(self.chartIterator) + chart_rel_target
        chart_relCopy = copy.deepcopy(chart_rel)
        chart_relCopy.attrib['Id'] = chartNewId
        chart_relCopy.attrib['Target'] = chart_rel_targetCopy
        chart_relParent = chart_rel.getparent()
        chart_relParent.append(chart_relCopy)

        #print chart_rel_target
        chart_part = filter(lambda x: x.attrib['{%s}name' % self.ns.pkg] == '/word/%s' % chart_rel_target,
                            etree.ETXPath('/{%s}package/{%s}part' % ((self.ns.pkg,) * 2))(self._xml))[0]
        
        chart_partCopy = copy.deepcopy(chart_part)
        chart_partCopy.attrib['{%s}name' % self.ns.pkg] = '/word/%s' % chart_rel_targetCopy
        chart_partParent = chart_part.getparent()
        chart_partParent.append(chart_partCopy)

        # <pkg:part pkg:name="/word/charts/chart5.xml" pkg:contentType="

        # /word/charts/_rels/chart1.xml.rels
        rels_part_name = "/word/" + chart_rel_target.replace("/", "/_rels/") + ".rels"
        rels_part_nameCopy = "/word/" + chart_rel_targetCopy.replace("/", "/_rels/") + ".rels"

        rels_part = filter(lambda x: x.attrib['{%s}name' % self.ns.pkg] == rels_part_name,
                            etree.ETXPath('/{%s}package/{%s}part' % ((self.ns.pkg,) * 2))(self._xml))[0]

        rels_partCopy = copy.deepcopy(rels_part)
        rels_partCopy.attrib['{%s}name' % self.ns.pkg] = rels_part_nameCopy
        rels_partCopy_rels = etree.ETXPath('//{%s}Relationship' % self.ns.a)(rels_partCopy)
       # rels_partCopy_drawing = rels_partCopy_rels[0]
        #rels_partCopy_worksheet = rels_partCopy_rels[1]

        
        def copyRelPackages(relationship):
             # the original drawing name used for the chart
            relationshipName = relationship.attrib["Target"]
            relationshipCopyName = relationshipName.replace("../", "../copy" + str(self.chartIterator))
            relationship.attrib["Target"] = relationshipCopyName

            pkgName = relationshipName.replace("../", "/word/")
            pkgCopyName = relationshipCopyName.replace("../", "/word/")
            pkg = filter(lambda x: x.attrib['{%s}name' % self.ns.pkg] == pkgName,
                                etree.ETXPath('/{%s}package/{%s}part' % ((self.ns.pkg,) * 2))(self._xml))[0]
            
            pkgCopy = copy.deepcopy(pkg)
            pkgCopy.attrib['{%s}name' % self.ns.pkg] = pkgCopyName
            pkgParent = pkg.getparent()
            pkgParent.append(pkgCopy)
        
        [copyRelPackages(rel) for rel in rels_partCopy_rels]

        rels_partParent = rels_part.getparent()
        rels_partParent.append(rels_partCopy)

        chart = etree.ETXPath('.//{%s}chart' % self.ns.c)(chart_partCopy)[0]
        #print etree.ETXPath('.//{%s}t' % 'http://schemas.openxmlformats.org/drawingml/2006/main')(chart)[0].text
        chart_num = etree.ETXPath('.//{%s}val/{%s}numRef/{%s}f' % ((self.ns.c,) * 3))(chart)[0]
        chart_values = etree.ETXPath('.//{%s}v' % self.ns.c)(chart_num.getparent().getparent())
        for i in range(len(chart_values)):
            if len(values) > i and values[i]:
                chart_values[i].text = str(values[i])
            else:
                chart_values[i].text = '0'
        #self._xml_sdt_replace(chart_struct['sdt'], chart_struct['children'])
        chart_parent = chart_struct[0][1].getparent()
        chart_parent.replace(chart_struct[0][1], chart_struct[0][2][0])

    def _set_document_name(self, test_type, test_name):
        pkg = filter(lambda x: x.attrib['{%s}name' % self.ns.pkg] == '/docProps/core.xml',
                                etree.ETXPath('/{%s}package/{%s}part' % ((self.ns.pkg,) * 2))(self._xml))[0]
        coreProperties = etree.ETXPath('.//{%s}coreProperties/{%s}title' \
            % ('http://schemas.openxmlformats.org/package/2006/metadata/core-properties', 'http://purl.org/dc/elements/1.1/'))(pkg)[0]
        coreProperties.text = '%s - %s' % (test_type, test_name)

    def xml_apply_meta(self, vulnparam_highlighting=True, truncation=True, pPr_annotation=True):

        # merge kb before generate
        self.merge_kb()
        
        self.template_cleanup_required = True
        self.__vulnparam_highlighting = vulnparam_highlighting
        self.__truncate = truncation
        self._pPr_annotation = pPr_annotation
        # change dir (for the purpose of images handling relatively to template path)
        pwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(self._template_filename))) #abspath needed for CLI
        # apply
        self._apply_scan()

        # find conditional root elements and make them dictionaries
        cond = dict()
        for i in filter(lambda x: len(x[0]) == 1 and x[0][-1][-1] == '?', self._struct):
            cond[i[0][-1][:-1]] = []
        #print cond
        # find if-not-exists
        notx = dict()
        for i in filter(lambda x: len(x[0]) == 1 and x[0][-1][-1] == '!', self._struct):
            notx[i[0][-1][:-1]] = []
        # process Data.*
        #for i in self._struct:
        def dict_count(block, key, fallback=1):
            if key in block:
                return len(block[key]) or fallback
            else:
                return fallback
        for i in filter(lambda x: x[0][-1][-1] not in ['?', '!'], self._struct):
            p = self._p(self._meta['Data'], i[0])
            #if p is not None and i[0] != ['Finding']:
            #    match_q = i[0][:]
            #    match_q[-1] += '?'
            #    print '?',i[0], p, len(filter(lambda x: x[0] == match_q, self._struct))
            if p is not None and not isinstance(p, list) and i[0][-1] in p:
                #print '+',i[0]
                val = self._v(self._meta['Data'], i[0])
                #print i[0], bool(val)
                if i[0][0] in cond.keys() and bool(val):
                    cond[i[0][0]] += [i[0]]
                if i[0][0] in notx.keys() and bool(val):
                    notx[i[0][0]] += [i[0]]
                if val == None:
                    val = ''
                self._xml_apply_data(i[0], val, i[1], i[2])
                # handle conditional sub elements 
                i_search = i[0][:]
                i_search[-1] = i_search[-1]+'?'
                i_search_match = filter(lambda x: i_search == x[0], self._struct)
                for match in i_search_match:
                    #print i_search, i_search_match
                    if val:
                        self._xml_sdt_replace(match[1], match[2])
                    else:
                        self._xml_sdt_remove(match[1])
                del i_search_match
                # handle if-not-exists sub elements 
                x_search = i[0][:]
                x_search[-1] = x_search[-1]+'!'
                x_search_match = filter(lambda x: x_search == x[0], self._struct)
                for match in x_search_match:
                    #print x_search, x_search_match
                    if val:
                        self._xml_sdt_remove(match[1])
                    else:
                        self._xml_sdt_replace(match[1], match[2])
                del x_search_match

                
        # if conditional root element does not have any members with values, remove them
        #print cond
        for i in cond.keys():
            i_struct = filter(lambda x: x[0] == [i+'?'], self._struct)
            if len(cond[i]):
                self._xml_sdt_replace(i_struct[0][1], i_struct[0][2])
            else:
                self._xml_sdt_remove(i_struct[0][1])
            del i_struct

        # if if-not-exists root element does not have any members with values, remove them
        #print notx
        for i in notx.keys():
            x_struct = filter(lambda x: x[0] == [i+'!'], self._struct)
            if len(cond[i]):
                self._xml_sdt_remove(x_struct[0][1])
            else:
                self._xml_sdt_replace(x_struct[0][1], x_struct[0][2])
            del x_struct

        # Findings
        self._xml_apply_findings()
        # Findings.Chart
        chart_struct = filter(lambda x: x[0] == ['Findings', 'Chart'], self._struct)
        if chart_struct:
            findings_by_severity_map = map(lambda x: x['Severity'], self._meta['Findings'])
            findings_by_severity = map(lambda x: len(filter(lambda y: x == y, findings_by_severity_map)), self.severity.keys())
            self._xml_apply_chart(chart_struct, findings_by_severity)
        del chart_struct
        # Findings.VolumeChart
        chart_struct = filter(lambda x: x[0] == ['Findings', 'VolumeChart'], self._struct)
        if chart_struct:
            findings_by_volume_map = map(lambda x: [x['Severity'], dict_count(x, 'Occurrences', fallback=1)], self._meta['Findings'])
            findings_by_volume = map(lambda z: reduce(lambda x,y: x+y, map(lambda x: x[1], filter(lambda x: x[0] == z, findings_by_volume_map))+[0]), self.severity.keys())
            self._xml_apply_chart(chart_struct, findings_by_volume)
        del chart_struct
        # handle conditionals for missing tags definition in content
        for i in filter(lambda x: len(x[0]) > 1 and x[0][0] not in ['Finding', 'Findings'] and x[0][-1][-1] == '?', self._struct):
            i_match_search = i[0][:]
            i_match_search[-1] = i_match_search[-1][:-1]
            i_match = filter(lambda x: x[0] == i_match_search, self._struct)
            self._xml_sdt_remove(i[1])
            del i_match
        # sdt cleanup
        for alias in etree.ETXPath('//{%s}alias' % self.ns.w)(self._xml):
            value = alias.attrib['{%s}val' % self.ns.w].split('.')
            sdt = alias.getparent().getparent()
            children = etree.ETXPath('./{%s}sdtContent' % self.ns.w)(sdt)[0].getchildren()
            self._xml_sdt_replace(sdt, children)

        if 'Test' in self._meta['Data']:
            test_type = self._meta['Data']['Test']['Type'] if 'Type' in self._meta['Data']['Test'] else 'Test'
            test_name = self._meta['Data']['Test']['Name'] if 'Name' in self._meta['Data']['Test'] else 'Application'

            self._set_document_name(test_type, test_name)
        # restore path
        os.chdir(pwd)

        self.remove_kb()

    def _kb_meta_update(self):
        if 'KB' in self._kb:
            self._meta['KB'] = self._kb['KB'][:]
        elif 'Findings' in self._kb:
            self._meta['KB'] = self._kb['Findings'][:]
        else:
            raise Exception('Knowledge base file must be have KB or Findings section!')

    def _kb_load_csv(self, filename):
        import csv
        def transcode(file, decode='cp1250', encode='utf-8'):
            for line in file:
                yield line.decode(decode).encode(encode)
        data = []
        with open(filename, 'rb') as csvfile:

            # CSV Reader - make it compatible with Polish regional settings. To adjust English settings:
            #     open Control Panel, Region and Language, Additional settings... List separator: ";"

            for row in csv.reader(transcode(csvfile), delimiter=';', quotechar='"'):
                data += [row]
        columns = data[0]
        rows = data[1:]
        results = []
        for row in rows:
            item = UnsortableOrderedDict()
            for col in range(len(columns)):
                value = unicode(row[col].decode('utf-8'))
                colname = columns[col]
                if colname == 'Vulnerability Name':
                    colname = 'Name'
                if colname == 'Vulnerability Aliases':
                    colname = 'Aliases'
                if colname in ['Modified By', 'Item Type', 'Path']:
                    continue
                #if colname == 'Name':
                #    print '[+]', value
                colname = unicode(colname.decode('utf-8')).replace(' ','').replace('\'','')
                value = filter(lambda x: x not in [u'\xa0', u'\x3f'], value)
                if colname == 'Aliases':
                    #value = '\n'.join(filter(lambda x: len(x) > 0, map(lambda x: ''.join(filter(lambda y: y not in [u'\xa0', u'\x3f'], list(x))), value.split('\n'))))
                    value = '\n'.join(filter(lambda x: len(x.strip()) > 0, value.split('\n')))
                colname_tree = colname.split('.')
                if len(colname_tree) > 1:
                    node = item
                    for colname_node in colname_tree[:-1]:
                        if colname_node not in item or not isinstance(item, UnsortableOrderedDict):
                            item[colname_node] = UnsortableOrderedDict()
                        node = item[colname_node]
                    node[colname_tree[-1]] = value
                else:
                    item[colname] = value
            results += [item]
        return UnsortableOrderedDict([('KB',results,)])
        
    def kb_reload(self):
        if self._kb_type == 'yaml':
            self._kb = yaml_load(open(self._kb_filename).read(), yaml.SafeLoader, UnsortableOrderedDict)
        elif self._kb_type == 'json':
            self._kb = json.loads(open(self._kb_filename).read().decode('utf-8-sig'),
                                  object_pairs_hook=UnsortableOrderedDict)
        else:
            self._kb = self._kb_load_csv(self._kb_filename)
        self._kb_meta_update()

    def kb_load_yaml(self, filename):
        self._kb_filename = filename
        self._kb_type = 'yaml'
        self.kb_reload()
        
    def kb_load_json(self, filename):
        self._kb_filename = filename
        self._kb_type = 'json'
        self.kb_reload()
        
    def kb_load_csv(self, filename):
        self._kb_filename = filename
        self._kb_type = 'csv'
        self.kb_reload()

    def kb_dump_json(self):
        return self._dump_json(self._kb)

    def kb_dump_yaml(self):
        return self._dump_yaml(self._kb)

    def nmap_load_xml(self, filename):
        self._nmap_filenames.append(filename)
        return self.nmap_reload()

    def nmap_remove(self):
        self._nmap = None
        self._nmap_filenames = []
        self._meta['Data']['OpenPorts'] = None

    def nmap_reload(self):
        self._nmap = ""
        
        if not hasattr(self, '_nmap_filenames') or len(self._nmap_filenames) == 0:
            return False

        def append_to_nmap(text):
            self._nmap += text + "\n"

        for filename in self._nmap_filenames:
            with open(filename) as fd:
                try:
                    doc = etree.fromstring(fd.read())
                except etree.XMLSyntaxError:
                    self.nmap_remove()
                    #raise Exception('Error while parsing XML!')
                    return False

                date, params = None, None

                for x in doc.xpath("//nmaprun"):
                    date = datetime.fromtimestamp(float(x.attrib['start']))
                    parameters = ' '.join(x.attrib['args'].split(' ')[1:])

                for x in doc.xpath("//host"):
                    for addr in x.xpath("address[@addrtype!='mac']/@addr"):
                        h_host = "Open ports on host {}:".format(addr)
                        append_to_nmap(h_host)
                        append_to_nmap("-" * len(h_host))

                    ports = []
                    for open_p in x.xpath("ports/port[state[@state='open']]"):
                        ports.append("{port}/{proto}".format(
                                port=open_p.attrib['portid'],
                                proto=open_p.attrib['protocol'].upper()))

                    append_to_nmap("\n".join(ports))

                    append_to_nmap("")

                append_to_nmap("Scan date: " + str(date))

            append_to_nmap("")
        self._nmap = unicode(self._nmap)
        self._apply_nmap_scan()
        return True

    def _apply_nmap_scan(self):
        self._meta['Data']['OpenPorts'] = self._nmap

    def nmap_dump(self):
        return self._nmap

    def _apply_scan(self):
        if self.scan:
            self._meta['Findings'] += self.scan.findings()
            self._meta['Findings'].sort(key=lambda x: x['Severity'], reverse=True)

    def merge_scan(self, scan):
        if 'Findings' not in self._content:
            # create empty self._content['Findings'] list
            self._content['Findings'] = []
        # if self._content len == 0
        if len(self._content['Findings']) == 0:
            # just copy scan['Findings']
            #self._content['Findings'] = scan._scan['Findings'][:]
            self._content['Findings'] = scan['Findings'][:]
        else:
            # for each finding in scan['Findings']
            #for finding in scan._scan['Findings']:
            for finding in scan['Findings']:
                # if name and severity matches:
                finding_match = filter(lambda x: x['Name'] == finding['Name'] and x['Severity'] == finding['Severity'], self._content['Findings'])
                if finding_match:
                    # add occurrences (if not duplicated)
                    for occurrence in finding['Occurrences']:
                        occurrence_match = filter(lambda x: x == occurrence, finding_match[0]['Occurrences'])
                        if not occurrence_match:
                            finding_match[0]['Occurrences'] += [occurrence]
                else:
                    # otherwise copy whole finding
                    self._content['Findings'] += [finding]
                del finding_match
        # filter out self._content['Findings'] where severity == ''
        self._content['Findings'] = filter(lambda x: x['Severity'] != '' , self._content['Findings'])
        if len(self._content['Findings']) == 0:
            del self._content['Findings']


if __name__ == '__main__':
    pass

    Scan('../workbench/burp-1/burp.xml')
    
    '''
    # Standard, demo operation (example with two scans and knowledge base)
    report = Report()
    report.template_load_xml('../examples/example-2A-scan-report-template.xml', clean=True)
    report.content_load_yaml('../examples/example-2B-content.yaml')
    #report.scan = Scan('../examples/example-2-scan-export-Burp.xml')
    scan = Scan('../examples/example-2C-scan-export-Burp.xml')
    report.merge_scan(scan.modify())
    report.content_refresh()
    scan2 = Scan('../examples/example-2C-scan-export-WebInspect.xml')
    report.merge_scan(scan2.modify())
    report.content_refresh()
    #report.kb_load_yaml('../examples/example-2D-kb.yaml')
    report.kb_load_csv('../examples/example-2D-kb.csv')
    report.merge_kb()
    report.xml_apply_meta()
    report.save_report_xml('../examples/\!.xml')
    '''

    '''
    # html-formatting-1
    report = Report()
    report.template_load_xml('../testcase/html-formatting-1/1-template.xml', clean=True)
    report.content_load_yaml('../testcase/html-formatting-1/2-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../testcase/html-formatting-1/!.xml')
    '''
    
    '''
    # conditional "if not" for non-finding root nodes
    report = Report()
    report.template_load_xml('../testcase/non-finding-if-not-1/1-template.xml', clean=True)
    report.content_load_yaml('../testcase/non-finding-if-not-1/2-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../testcase/non-finding-if-not-1/!.xml')
    '''
    
    '''
    report = Report()
    report.template_load_xml('../workbench/no-bestpractices-2/1.xml', clean=True)
    report.content_load_yaml('../workbench/no-bestpractices-2/2.yaml')
    report.xml_apply_meta()
    #report.save_report_xml('../workbench/no-bestpractices-2/!.xml')
    '''
    
    '''
    report = Report()
    report.template_load_xml('../workbench/merge-kb-fix-1/1.xml', clean=True)
    report.content_load_yaml('../workbench/merge-kb-fix-1/2.yaml')
    report.kb_load_csv('../workbench/merge-kb-fix-1/4.csv')
    report.merge_kb()
    #print '---'
    print report.content_dump_yaml()
    #report.xml_apply_meta()
    #report.save_report_xml('../workbench/merge-kb-fix-1/!.xml')
    '''

    #report = Report()
    #report.template_load_xml('../workbench/no-bestpractices-1/3.xml', clean=True)
    #report.content_load_yaml('../workbench/no-bestpractices-1/3.yaml')
    #report.xml_apply_meta()
    #report.save_report_xml('../workbench/no-bestpractices-1/!.xml')

    '''
    # conditional "if not" for Finding child nodes
    report = Report()
    report.template_load_xml('../testcase/if-not-2/1-template.xml', clean=True)
    report.content_load_yaml('../testcase/if-not-2/2-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../testcase/if-not-2/!.xml')
    '''

    '''
    # conditional "if not" for Finding root nodes
    report = Report()
    report.template_load_xml('../testcase/if-not-1/1-template.xml', clean=True)
    report.content_load_yaml('../testcase/if-not-1/2-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../testcase/if-not-1/!.xml')
    '''
    
    '''
    # conditional "if"
    report = Report()
    report.template_load_xml('../testcase/if-1/1-template.xml', clean=True)
    report.content_load_yaml('../testcase/if-1/2-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../testcase/if-1/!.xml')
    '''
    
    '''
    report = Report()
    report.template_load_xml('../workbench/1-template.xml', clean=True)
    report.content_load_yaml('../workbench/2-content.yaml')
    #scan = Scan('../workbench/3-scan.yaml')
    #scan.dump_yaml()
    #report.merge_scan(scan)
    report.kb_load_csv('../workbench/4-kb.csv')
    report.merge_kb()
    #print '---'
    print report.content_dump_yaml()
    #
    #print report._dump_yaml(report._content)
    #print report._dump_yaml(report._meta)
    #print report._dump_yaml(report._kb)
    #print report._kb['KB'][0]
    #print report.meta_dump_yaml()
    #print report.kb_dump_yaml()
    #report.xml_apply_meta()
    #report.save_report_xml('../workbench/!.xml')
    #print report.content_dump_yaml()
    '''
    
    '''
    report = Report()
    report.template_load_xml('../workbench/pd1/x.xml', clean=True)
    report.content_load_yaml('../workbench/pd1/x.yaml')
    report.xml_apply_meta()
    #report.save_report_xml('../workbench/pd1/!.xml')
    '''
    
    #report = Report()
    #report.template_load_xml('../workbench/pd1/x.xml', clean=True)
    #report.content_load_yaml('../workbench/pd1/y.yaml')
    #report.xml_apply_meta()
    #report.save_report_xml('../workbench/pd1/!!.xml')
    
    '''
    report = Report()
    #report.kb_load_yaml('../examples/example-2-kb.yaml')
    #print report._kb
    #report.kb_load_csv('../workbench/test-KB.csv')
    report.kb_load_csv('../workbench/KB.csv')
    #print report._kb['KB'][0]
    #print report.meta_dump_yaml()
    print report.kb_dump_yaml()
    '''

    #report = Report()
    #report.template_load_xml('../workbench/pb1/templ.xml', clean=True)
    #report.scan = Scan('../workbench/pb1/is.xml')
    #report.scan.dump_yaml()
    #report.xml_apply_meta()
    #report.save_report_xml('../workbench/pb1/!.xml')

    '''
    report = Report()
    #report.template_load_xml('../workbench/s/PT template v1.4.xml', clean=True)
    report.template_load_xml('../workbench/k/PT Polish template v1.0.xml', clean=True)
    #report.content_load_yaml('../workbench/s/x.yaml')
    report.content_load_yaml('../workbench/k/PT Polish content.yaml')
    #report.scan = Scan('../workbench/j/...yaml')
    #report.kb_load_csv('../workbench/j/KB_latest.csv')
    report.xml_apply_meta()
    report.save_report_xml('../workbench/k/!.xml')
    '''
    
    '''
    report = Report()
    report.template_load_xml('../workbench/p/templ.xml', clean=True)
    report.content_load_yaml ('../workbench/p/templ.yaml') 
    report.scan = Scan('../workbench/p/scan.yaml')
    report.kb_load_csv('../workbench/p/kb.csv')
    report.xml_apply_meta()
    report.save_report_xml('../workbench/p/!.xml')
    '''
    
    '''
    report = Report()
    report.kb_load_csv('../workbench/KB-1.csv')
    #print report.kb_dump_yaml()
    #print filter(lambda x: 'Hidden' in x['Name'], report._kb['KB'])
    for i in map(lambda x:x['Aliases'], report._kb['KB']):
        print i.split('\n')
        print

    #report.template_load_xml('../workbench/bug-01/template.xml', clean=True)
    #report.scan = Scan('../workbench/bug-01/burp scan bug.yaml')
    #report.xml_apply_meta()
    #report.save_report_xml('../workbench/bug-01/!.xml')
    '''

    '''
    report = Report()
    report.template_load_xml('../workbench/issue/a.xml', clean=True)
    report.content_load_yaml ('../workbench/issue/a.yaml') 
    report.scan = Scan('../workbench/issue/b.xml')
    #report.kb_load_csv('../workbench/issue/a.csv')
    report.xml_apply_meta()
    #report.save_report_xml('../workbench/issue/!.xml')
    '''

    #report = Report()
    #report.scan = Scan('../workbench/_prep-joined.yaml')
    
    '''
    # sample DS
    report = Report()
    report.template_load_xml('../workbench/s-template v1.0.xml', clean=True)
    report.content_load_yaml ('../workbench/s-template v1.0-content.yaml') 
    report.kb_load_csv('../workbench/KB.csv')
    report.scan = Scan('../workbench/b-webinspect.xml')
    report.xml_apply_meta()
    report.save_report_xml('../workbench/output-2.xml')
    '''
    
    '''
    report = Report()
    #report.template_load_xml('../workbench/example-2-webinspect-report-template.xml', clean=True)
    #report.template_load_xml('../workbench/example-2-scan-report-template.xml', clean=True)
    report.template_load_xml('../workbench/pt-template-v0.6-v0.2.xml', clean=False)
    #print report.template_dump_yaml()
    #report.content_load_yaml ('../workbench/example-2-content.yaml')
    #report.content_load_yaml ('../workbench/test-v0.3-content.yaml')
    report.content_load_yaml ('../workbench/pt-template-v0.6-v0.2-content.yaml')
    #report.kb_load_yaml('../examples/example-2-kb.yaml')
    #report.kb_load_csv('../workbench/Knowledge Base.csv')
    report.kb_load_csv('../workbench/KB.csv')
    #print report.kb_dump_yaml()
    #scan = Scan('../workbench/b-webinspect.xml')
    #scan= Scan('../workbench/b-burp.xml')
    #print scan.dump_yaml()
    #report.scan = scan
    #print report.content_dump_yaml()
    #print report.scan.dump_yaml()
    #print report._content
    #print scan._scan['Findings']
    #report.merge_scan(scan)
    #print report._content
    #report.scan = Scan('../workbench/b-webinspect.xml')
    #report.scan = Scan('../workbench/b-webinspect.yaml')
    #report.scan = Scan('../workbench/b-burp.xml')
    #report.scan = Scan('../workbench/b-burp.yaml')
    #report.scan = Scan('../workbench/a-webinspect-http.xml')
    #report.scan = Scan('../workbench/z-webinspect.xml')
    #report.scan = Scan('../workbench/c-webinspect.yaml')
    #print map(lambda x: x['Name'], report.scan._scan['Findings'])
    #print report.scan.dump_yaml()
    #report.xml_apply_meta(vulnparam_highlighting=False)
    report.xml_apply_meta()
    #print report.meta_dump_yaml()
    #report.save_report_xml('../workbench/output.xml')
    #report.save_report_xml('../workbench/output-2.xml')
    report.save_report_xml('../workbench/test-output.xml')
    #print 'end.'
    '''
    
    '''
    report = Report()
    report.template_load_xml ('../workbench/example-1-content-report-template.xml')
    #report.template_reload(clean=True)
    #print report.template_dump_struct()
    #print report.template_dump_yaml()
    report.content_load_yaml ('../workbench/example-1-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../workbench/output.xml')
    #report.template_reload(clean=True)
    #report.content_load_yaml ('../examples/example-1-content.yaml')
    #report.xml_apply_meta()
    #report.save_report_xml('../workbench/output.xml')
    '''
    
    '''
    report = Report()
    report.scan = Scan('../workbench/b-burp.xml')
    print report.scan.dump_yaml()
    '''

    '''
    report = Report()
    report.template_load_xml ('../examples/example-1-content-report-template.xml')
    #print report.template_dump_struct()
    report.content_load_yaml ('../examples/example-1-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../workbench/output.xml')
    '''
    
    '''
    report = Report()
    #report.template_load_xml('d4-example-report-template.xml', clean=True)
    #report.template_load_xml('d4-example-report-template.xml')
    #report.template_load_xml('d9-test-template.xml', clean=True)
    #report.template_load_xml('d9-test-template.xml')
    #report.template_load_xml('d9-simple-template.xml', clean=True)
    #report.template_load_xml('d9-simple-template.xml')
    report.template_load_xml('d9-webinspect-10-template.xml')
    #print report.template_dump_struct()
    #report.template_load_docx('d3.docx')
    #report.template_reload(clean=True)
    #print report.template_dump_json()
    #print report.template_dump_yaml()
    #print '---'
    ##report.content_load_yaml('d4-example-content.yaml')
    #report.content_load_yaml('d5-kb-content.yaml')
    #report.content_load_yaml('d9-test-content.yaml')
    #report.content_load_yaml('d9-simple-content.yaml')
    #report.kb_load_yaml('d5-kb.yaml')
    #print report.meta_dump_yaml()
    #print report.kb_dump_yaml()
    #print report.meta_dump_json()
    #report.scan = Scan('d8-webinspect-scan.xml')
    report.scan = Scan('d9-webinspect-10-scan.xml')
    #print report.scan.dump_yaml()
    #report._apply_scan()
    #print report.meta_dump_yaml()
    #report.content_load_json('d3.json')
    report.xml_apply_meta()
    report.save_report_xml('done.xml')
    '''

    '''
    # test: merge_scan
    report = Report()
    report.content_load_yaml('../examples/example-2-content.yaml')
    scan = Scan('../workbench/test-case-example-2-merge-1.yaml')
    report.merge_scan(scan)
    scan = Scan('../workbench/test-case-example-2-merge-2.yaml')
    report.merge_scan(scan)
    scan = Scan('../workbench/test-case-example-2-merge-3.yaml')
    report.merge_scan(scan)
    scan = Scan('../workbench/test-case-example-2-merge-4.yaml')
    report.merge_scan(scan)
    print report.content_dump_yaml()
    '''
