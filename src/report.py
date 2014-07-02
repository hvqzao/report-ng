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


from util import yaml_load, UnsortableOrderedDict
from openxml import Openxml
from pseudohtml import InlineHtmlParser, HtmlParser
from scan import Scan

from lxml import etree
import yaml, json
import os
import os.path
#import docx
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
    _kb_yaml = None
    _kb = None
    _openxml = None
    _html_parser = None
    _ihtml_parser = None
    scan = None

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
        if self._kb:  # TODO ?
            del self._kb
        self._kb = None

    @staticmethod
    def _dump_json(target):
        return json.dumps(target, indent=2, ensure_ascii=False)  #.decode('utf-8')

    def _dump_yaml(self, target):
        return yaml.dump(target, default_flow_style=False, allow_unicode=True).decode('utf-8')

    def _reserved(self, value):
        if value[-1][-1] == '?':
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
        return ' '.join(map(lambda x: x.text, etree.ETXPath('.//{%s}t' % self.ns.w)(children[0])))

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
                        if value == ['Finding'] or i == len(value) - 1 and len(children) == 1 and children[
                            0].tag == '{%s}tr' % self.ns.w:
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
            if not clean:
                self._skel['Findings'][0][i] = self._xml_val(
                    filter(lambda x: x[0] == ['Finding', i], self._struct)[0][2])
            else:
                self._skel['Findings'][0][i] = ''
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
        #print self._skel

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

    def _template_reload(self, clean=False):
        self._cleanup()
        self._xml = etree.parse(self._template_filename)
        self._openxml = Openxml(self._xml)
        self._html_parser = etree.XMLParser(target=HtmlParser(self._openxml), resolve_entities=False)
        self._ihtml_parser = etree.XMLParser(target=InlineHtmlParser(self._openxml), resolve_entities=False)
        self._template_parse(clean=clean)
        self._content_parse(self._skel)  # TODO added - test if ok
        return self

    def template_load_xml(self, filename, clean=False):
        self._template_filename = filename
        return self._template_reload(clean=clean)

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

    def _content_reload(self):
        if self._content_yaml:
            self._content_parse(yaml_load(open(self._content_filename).read(), yaml.SafeLoader, UnsortableOrderedDict))
        else:
            self._content_parse(json.loads(open(self._content_filename).read().decode('utf-8-sig'),
                                           object_pairs_hook=UnsortableOrderedDict))
        return self

    def content_load_yaml(self, filename):
        self._content_filename = filename
        self._content_yaml = True
        return self._content_reload()

    def content_load_json(self, filename):
        self._content_filename = filename
        self._content_yaml = False
        return self._content_reload()

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
        return unicode(value).strip().lower()[:len(preamble)] == preamble

    @staticmethod
    def _is_ihtml(value):
        preamble = '<ihtml>'
        return unicode(value).strip().lower()[:len(preamble)] == preamble

    def _xml_sdt_single(self, value, sdt, children):
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
            if self._is_html(value) or self._is_ihtml(value):
                block = etree.Element('Summary')
                for i in children:
                    block.append(etree.fromstring(etree.tostring(i)))
                if len(tc):
                    _tc = filter(lambda x: x.tag in ['{%s}tc' % self.ns.w], block.getchildren())
                    _p_r = filter(lambda x: x.tag in ['{%s}p' % self.ns.w, '{%s}r' % self.ns.w], _tc[0])
                    cursor = _p_r[0]
                else:
                    _p_r = filter(lambda x: x.tag in ['{%s}p' % self.ns.w, '{%s}r' % self.ns.w], block.getchildren())
                    cursor = _p_r[0]
                self._openxml.set_sdt_cursor(cursor=cursor)
                self._openxml.parse(value, [self._html_parser, self._ihtml_parser][self._is_ihtml(value)])
                self._openxml.remove_sdt_cursor()
                parent = sdt.getparent()
                for i in block.getchildren():
                    parent.insert(parent.index(sdt), i)
                parent.remove(sdt)                    
            else:
                values = unicode(value).split('\n')
                build = []
                for v in values:
                    block = etree.fromstring(etree.tostring(p_r_tc[0]))
                    tag = etree.ETXPath('.//{%s}t' % self.ns.w)(block)
                    tag[0].text = unicode(v)
                    build += [block]
                    del tag, block
                parent = sdt.getparent()
                for i in build:
                    parent.insert(parent.index(sdt), i)
                parent.remove(sdt)
                del build
            return True
        else:
            return False

    def _xml_apply_data(self, struct, value, sdt, children):
        #print '*',struct#, value
        if not children:
            return
        if not self._xml_sdt_single(value, sdt, children) and children[0].tag in ['{%s}tr' % self.ns.w]:
            #print '+',struct
            build = []
            for row in value:
                block = etree.fromstring(etree.tostring(children[0]))
                aliases = self._xml_block_aliases(block)
                #print '-',row
                for col in row:
                    alias_match_q = filter(lambda x: x['struct'] == struct + [str(col)+'?'], aliases)
                    if alias_match_q:
                        if row[col]:
                            self._xml_sdt_replace(alias_match_q[0]['sdt'], alias_match_q[0]['children'])
                        else:
                            self._xml_sdt_remove(alias_match_q[0]['sdt'])
                    del alias_match_q
                    alias_match = filter(lambda x: x['struct'] == struct + [str(col)], aliases)
                    if not alias_match:
                        continue
                    alias = alias_match[0]
                    tag = etree.ETXPath('.//{%s}t' % self.ns.w)(alias['children'][0])
                    if self._is_html(row[col]):
                        self._openxml.set_sdt_cursor(cursor=tag[0])
                        self._openxml.parse(row[col], self._html_parser)
                        self._openxml.remove_sdt_cursor()
                    elif self._is_ihtml(row[col]):
                        self._openxml.set_sdt_cursor(cursor=tag[0])
                        self._openxml.parse(row[col], self._ihtml_parser)
                        self._openxml.remove_sdt_cursor()
                    else:
                        tag[0].text = unicode(row[col])
                    parent = alias['sdt'].getparent()
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
        for i in children:
            parent.insert(parent.index(sdt), i)
        parent.remove(sdt)

    def _xml_sdt_remove (self, sdt):
        parent = sdt.getparent()
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

    def _xml_apply_findings(self):
        finding_struct = filter(lambda x: x[0] == ['Finding'], self._struct)
        #print map(lambda x: x['Name'], self._meta['Findings'])
        findings = self._meta['Findings']
        for severity in self.severity.keys():
            severity_tag = self._severity_tag(severity)
            severity_findings = filter(lambda x: x['Severity'] in severity, findings)
            findings_placeholder = filter(lambda x: x[0] == ['Findings', severity_tag], self._struct)[0][1]
            findings_placeholder_parent = findings_placeholder.getparent()
            summary_struct = filter(lambda x: x[0] == ['Summary', severity_tag], self._struct)
            #print summary_struct
            if summary_struct:
                summary_placeholder = summary_struct[0][1]
                summary_placeholder_parent = summary_placeholder.getparent()
                #print summary_placeholder
                #print summary_placeholder_parent
            for finding in severity_findings:
                kb = None
                if self._kb:
                    kb_match = filter(lambda x: x['Name'] == finding['Name'] and x['Severity'] == finding['Severity'],
                                      self._meta['KB'])
                    if kb_match:
                        kb = kb_match[0]
                    del kb_match
                # Build Finding xml block
                block = etree.Element('Finding')
                for i in finding_struct[0][2]:
                    block.append(etree.fromstring(etree.tostring(i)))
                aliases = self._xml_block_aliases(block)
                aliases_abs = map(lambda x: '.'.join(x['struct']), aliases)
                for i in aliases:
                    alias_abs = '.'.join(i['struct'])
                    #print alias_abs
                    if alias_abs[-1] == '?':
                        # is this finding.[severity]? -> if yes, replace content, otherwise delete me
                        if i['struct'][-1] in  map(lambda x: self._severity_tag(x)+'?', self.severity.keys()):
                            if i['struct'][-1] == severity_tag+'?':
                                self._xml_sdt_replace(i['sdt'], i['children'])
                                #print '+', finding['Name'], finding['Severity']
                            else:
                                self._xml_sdt_remove(i['sdt'])
                                #print '-', finding['Name'], finding['Severity']
                        # commented out because might have kb value
                        #else:
                        #    # is this finding.[key_not_found]? -> if yes, delete me
                        #    #print '?', alias_abs
                        #    alias_search = i['struct'][:]
                        #    alias_search[-1] = alias_search[-1][:-1]
                        #    if not filter(lambda x: x['struct'] == alias_search, aliases):
                        #        self._xml_sdt_remove(i['sdt'])
                        #    #del alias_search
                    else:
                        # TODO recent fixes
                        #print i['struct']
                        if self._p(finding, i['struct'][1:]) == None:
                            continue
                        if not isinstance(self._p(finding, i['struct'][1:]), list) and i['struct'][1:][-1] in self._p(finding, i['struct'][1:]):
                            #if self._p (finding, i['struct'][1:]).has_key(i['struct'][1:][-1]):
                            finding_val = self._v(finding, i['struct'][1:])
                        else:
                            finding_val = ''
                        kb_val = None
                        if kb:
                            if i['struct'] not in [['Finding', 'Name'], ['Finding', 'Severity']]:
                                kb_p = self._p(kb, i['struct'][1:])
                                if kb_p and kb_p.has_key(i['struct'][1:][-1]):
                                    kb_val = self._v(kb, i['struct'][1:])
                                del kb_p
                        #self._xml_sdt_single (self._kb_val (finding_val, kb_val), i['sdt'], i['children'])
                        ultimate_val = self._kb_val(finding_val, kb_val)
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
                            self._xml_sdt_single(len(self._v(finding, i_hash[2:])), i['sdt'], i['children'])
                            del i_hash
                        else:
                            if 'Summary' in finding and i['struct'][2] in finding['Summary']:
                                finding_val = finding['Summary'][i['struct'][2]]
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
            if summary_struct:
                summary_placeholder_parent.remove(summary_placeholder)
            findings_placeholder_parent.remove(findings_placeholder)
            del findings_placeholder, findings_placeholder_parent
            if summary_struct:
                del summary_placeholder, summary_placeholder_parent
            del severity_findings, summary_struct
        # Remove Finding template
        template = finding_struct[0][1]
        template_parent = template.getparent()
        template_parent.remove(template)
        del template_parent, template

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
        chart_rid = \
            reduce(lambda x, y: x + y,
                   map(lambda x: etree.ETXPath('.//{%s}chart' % self.ns.c)(x), chart_struct[0][2]))[
                0].attrib['{%s}id' % self.ns.r]
        #print chart_rid
        chart_rel_target = filter(lambda x: x['Id'] == chart_rid and x[
            'Type'] == 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart',
                                  map(lambda x: x.attrib,
                                      etree.ETXPath('//{%s}Relationship' % self.ns.a)(self._xml)))[0]['Target']
        #print chart_rel_target
        chart_part = filter(lambda x: x.attrib['{%s}name' % self.ns.pkg] == '/word/%s' % chart_rel_target,
                            etree.ETXPath('/{%s}package/{%s}part' % ((self.ns.pkg,) * 2))(self._xml))[0]
        chart = etree.ETXPath('.//{%s}chart' % self.ns.c)(chart_part)[0]
        #print etree.ETXPath('.//{%s}t' % 'http://schemas.openxmlformats.org/drawingml/2006/main')(chart)[0].text
        chart_num = etree.ETXPath('.//{%s}val/{%s}numRef/{%s}f' % ((self.ns.c,) * 3))(chart)[0]
        chart_values = etree.ETXPath('.//{%s}v' % self.ns.c)(chart_num.getparent().getparent())
        for i in range(len(chart_values)):
            if values[i]:
                chart_values[i].text = str(values[i])
            else:
                chart_values[i].text = '0'
        chart_parent = chart_struct[0][1].getparent()
        chart_parent.replace(chart_struct[0][1], chart_struct[0][2][0])

    def xml_apply_meta(self):
        # change dir (for the purpose of images handling relatively to template path)
        pwd = os.getcwd()
        os.chdir(os.path.dirname(self._template_filename))
        # apply
        self._apply_scan()
        # find conditional root elements and make them dictionaries
        root = dict()
        for i in filter(lambda x: len(x[0]) == 1 and x[0][-1][-1] == '?', self._struct):
            root[i[0][-1][:-1]] = []
        #print root
        # process Data.*
        #for i in self._struct:
        for i in filter(lambda x: x[0][-1][-1] != '?', self._struct):
            p = self._p(self._meta['Data'], i[0])
            #if p is not None and i[0] != ['Finding']:
            #    match_q = i[0][:]
            #    match_q[-1] += '?'
            #    print '?',i[0], p, len(filter(lambda x: x[0] == match_q, self._struct))
            if p is not None and not isinstance(p, list) and i[0][-1] in p:
                #print '+',i[0]
                val = self._v(self._meta['Data'], i[0])
                #print i[0], bool(val)
                if i[0][0] in root.keys() and bool(val):
                    root[i[0][0]] += [i[0]]
                self._xml_apply_data(i[0], val, i[1], i[2])
        # if conditional root element does not have any members with values, remove them
        #print root
        for i in root.keys():
            i_struct = filter(lambda x: x[0] == [i+'?'], self._struct)
            if len(root[i]):
                self._xml_sdt_replace(i_struct[0][1], i_struct[0][2])
            else:
                self._xml_sdt_remove(i_struct[0][1])
            del i_struct
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
            findings_by_volume_map = map(lambda x: [x['Severity'], len(x['Occurrences'])], self._meta['Findings'])
            findings_by_volume = map(lambda z: reduce(lambda x,y: x+y, map(lambda x: x[1], filter(lambda x: x[0] == z, findings_by_volume_map))+[0]), self.severity.keys())
            self._xml_apply_chart(chart_struct, findings_by_volume)
        del chart_struct
        # restore path
        os.chdir(pwd)

    def _kb_meta_update(self):
        if 'KB' in self._kb:
            self._meta['KB'] = self._kb['KB'][:]
        elif 'Findings' in self._kb:
            self._meta['KB'] = self._kb['Findings'][:]
        else:
            raise Exception('Knowledge base file must be have KB or Findings section!')

    def kb_load_yaml(self, filename):
        self._kb_filename = filename
        self._kb_yaml = True
        self._kb = yaml_load(open(self._kb_filename).read(), yaml.SafeLoader, UnsortableOrderedDict)
        self._kb_meta_update()

    def kb_load_json(self, filename):
        self._kb_filename = filename
        self._kb_yaml = False
        self._kb = json.loads(open(self._kb_filename).read().decode('utf-8-sig'),
                              object_pairs_hook=UnsortableOrderedDict)
        self._kb_meta_update()

    def kb_dump_json(self):
        return self._dump_json(self._kb)

    def kb_dump_yaml(self):
        return self._dump_yaml(self._kb)

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
            self._content['Findings'] = scan._scan['Findings'][:]
        else:
            # for each finding in scan['Findings']
            for finding in scan._scan['Findings']:
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

    '''
    report = Report()
    #report.template_load_xml('../examples/example-2-webinspect-report-template.xml', clean=True)
    report.template_load_xml('../examples/example-2-scan-report-template.xml', clean=True)
    #print report.template_dump_yaml()
    report.content_load_yaml ('../examples/example-2-content.yaml')
    report.kb_load_yaml('../examples/example-2-kb.yaml')
    scan = Scan('../examples/tmp/b-webinspect.xml')
    #report.scan = scan
    #print report.content_dump_yaml()
    #print report.scan.dump_yaml()
    #print report._content
    #print scan._scan['Findings']
    report.merge_scan(scan)
    print report._content
    #report.scan = Scan('../examples/tmp/b-webinspect.yaml')
    #report.scan = Scan('../examples/tmp/b-burp.xml')
    #report.scan = Scan('../examples/tmp/b-burp.yaml')
    #report.scan = Scan('../examples/tmp/a-webinspect-http.xml')
    #report.scan = Scan('../examples/tmp/z-webinspect.xml')
    #report.scan = Scan('../examples/tmp/c-webinspect.yaml')
    #print map(lambda x: x['Name'], report.scan._scan['Findings'])
    #print report.scan.dump_yaml()
    #report.xml_apply_meta()
    #print report.meta_dump_yaml()
    #report.save_report_xml('../examples/tmp/output.xml')
    #report.save_report_xml('../examples/tmp/output-2.xml')
    #print 'end.'
    '''
    
    '''
    report = Report()
    report.template_load_xml ('../examples/example-1-content-report-template.xml')
    #report._template_reload(clean=True)
    #print report.template_dump_struct()
    #print report.template_dump_yaml()
    report.content_load_yaml ('../examples/example-1-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../examples/tmp/output.xml')
    '''
    
    '''
    report = Report()
    report.scan = Scan('../examples/tmp/b-burp.xml')
    print report.scan.dump_yaml()
    '''

    '''
    report = Report()
    report.template_load_xml ('../examples/example-1-content-report-template.xml')
    #print report.template_dump_struct()
    report.content_load_yaml ('../examples/example-1-content.yaml')
    report.xml_apply_meta()
    report.save_report_xml('../examples/tmp/output.xml')
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
    #report._template_reload(clean=True)
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
    scan = Scan('../examples/tmp/test-case-example-2-merge-1.yaml')
    report.merge_scan(scan)
    scan = Scan('../examples/tmp/test-case-example-2-merge-2.yaml')
    report.merge_scan(scan)
    scan = Scan('../examples/tmp/test-case-example-2-merge-3.yaml')
    report.merge_scan(scan)
    scan = Scan('../examples/tmp/test-case-example-2-merge-4.yaml')
    report.merge_scan(scan)
    print report.content_dump_yaml()
    '''
