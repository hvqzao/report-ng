# report-ng
# Copyright (c) 2014-2015 Marcin Woloszyn (@hvqzao)
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


#from collections import OrderedDict
from lxml import etree
from lxml.html import soupparser
import base64


class Openxml(object):
    _listparagraph_style = '''

<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="paragraph" w:styleId="ListParagraph">
  <w:name w:val="List Paragraph"/>
  <w:basedOn w:val="Normal"/>
  <w:uiPriority w:val="34"/>
  <w:qFormat/>
  <w:rsid w:val="002C7152"/>
  <w:pPr>
    <w:ind w:left="720"/>
    <w:contextualSpacing/>
  </w:pPr>
</w:style>
'''
    _hyperlink_style = '''

<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="character" w:styleId="Hyperlink">
  <w:name w:val="Hyperlink"/>
  <w:basedOn w:val="DefaultParagraphFont"/>
  <w:uiPriority w:val="99"/>
  <w:unhideWhenUsed/>
  <w:rPr>
    <w:color w:val="0000FF" w:themeColor="hyperlink"/>
    <w:u w:val="single"/>
  </w:rPr>
</w:style>
'''
    _numbering_pkg = '''

<pkg:part xmlns:pkg="http://schemas.microsoft.com/office/2006/xmlPackage" pkg:name="/word/numbering.xml" pkg:contentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml">
  <pkg:xmlData>
    <w:numbering xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 wp14">
      <w:abstractNum w:abstractNumId="0">
        <w:multiLevelType w:val="hybridMultilevel"/>
        <w:lvl w:ilvl="0">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="&#xF0B7;"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="720" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="1" w:tentative="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="o"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="1440" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New" w:hint="default"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="2" w:tentative="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="&#xF0A7;"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="2160" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Wingdings" w:hAnsi="Wingdings" w:hint="default"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="3" w:tentative="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="&#xF0B7;"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="2880" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="4" w:tentative="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="o"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="3600" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New" w:hint="default"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="5" w:tentative="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="&#xF0A7;"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="4320" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Wingdings" w:hAnsi="Wingdings" w:hint="default"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="6" w:tentative="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="&#xF0B7;"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="5040" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="7" w:tentative="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="o"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="5760" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New" w:hint="default"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="8" w:tentative="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="bullet"/>
          <w:lvlText w:val="&#xF0A7;"/>
          <w:lvlJc w:val="left"/>
          <w:pPr>
            <w:ind w:left="6480" w:hanging="360"/>
          </w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="Wingdings" w:hAnsi="Wingdings" w:hint="default"/>
          </w:rPr>
        </w:lvl>
      </w:abstractNum>
      <w:num w:numId="1">
        <w:abstractNumId w:val="0"/>
      </w:num>
    </w:numbering>
  </pkg:xmlData>
</pkg:part>
'''
    _abstractNum_decimal = '''

<w:abstractNum xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:abstractNumId="2">
  <w:multiLevelType w:val="hybridMultilevel"/>
  <w:lvl w:ilvl="0">
    <w:start w:val="1"/>
    <w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%1."/>
    <w:lvlJc w:val="left"/>
    <w:pPr>
      <w:ind w:left="720" w:hanging="360"/>
    </w:pPr>
  </w:lvl>
  <w:lvl w:ilvl="1" w:tentative="1">
    <w:start w:val="1"/>
    <w:numFmt w:val="lowerLetter"/>
    <w:lvlText w:val="%2."/>
    <w:lvlJc w:val="left"/>
    <w:pPr>
      <w:ind w:left="1440" w:hanging="360"/>
    </w:pPr>
  </w:lvl>
  <w:lvl w:ilvl="2" w:tentative="1">
    <w:start w:val="1"/>
    <w:numFmt w:val="lowerRoman"/>
    <w:lvlText w:val="%3."/>
    <w:lvlJc w:val="right"/>
    <w:pPr>
      <w:ind w:left="2160" w:hanging="180"/>
    </w:pPr>
  </w:lvl>
  <w:lvl w:ilvl="3" w:tentative="1">
    <w:start w:val="1"/>
    <w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%4."/>
    <w:lvlJc w:val="left"/>
    <w:pPr>
      <w:ind w:left="2880" w:hanging="360"/>
    </w:pPr>
  </w:lvl>
  <w:lvl w:ilvl="4" w:tentative="1">
    <w:start w:val="1"/>
    <w:numFmt w:val="lowerLetter"/>
    <w:lvlText w:val="%5."/>
    <w:lvlJc w:val="left"/>
    <w:pPr>
      <w:ind w:left="3600" w:hanging="360"/>
    </w:pPr>
  </w:lvl>
  <w:lvl w:ilvl="5" w:tentative="1">
    <w:start w:val="1"/>
    <w:numFmt w:val="lowerRoman"/>
    <w:lvlText w:val="%6."/>
    <w:lvlJc w:val="right"/>
    <w:pPr>
      <w:ind w:left="4320" w:hanging="180"/>
    </w:pPr>
  </w:lvl>
  <w:lvl w:ilvl="6" w:tentative="1">
    <w:start w:val="1"/>
    <w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%7."/>
    <w:lvlJc w:val="left"/>
    <w:pPr>
      <w:ind w:left="5040" w:hanging="360"/>
    </w:pPr>
  </w:lvl>
  <w:lvl w:ilvl="7" w:tentative="1">
    <w:start w:val="1"/>
    <w:numFmt w:val="lowerLetter"/>
    <w:lvlText w:val="%8."/>
    <w:lvlJc w:val="left"/>
    <w:pPr>
      <w:ind w:left="5760" w:hanging="360"/>
    </w:pPr>
  </w:lvl>
  <w:lvl w:ilvl="8" w:tentative="1">
    <w:start w:val="1"/>
    <w:numFmt w:val="lowerRoman"/>
    <w:lvlText w:val="%9."/>
    <w:lvlJc w:val="right"/>
    <w:pPr>
      <w:ind w:left="6840" w:hanging="360"/>
    </w:pPr>
  </w:lvl>
</w:abstractNum>
'''

    class ns:  # openxml namespaces used
        w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        a = 'http://schemas.openxmlformats.org/package/2006/relationships'
        pkg = 'http://schemas.microsoft.com/office/2006/xmlPackage'
        wp = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'

    #_xml
    #_cursor
    #_relationships
    #_style
    #_bullet
    #_numbered
    #_seq

    _style_defaults = {
        'run': {
            'bold': False,
            'italic': False,
            'space': True,  # space preservation?
            'font': None,  # e.g. Consolas
            'size': None,  # 2x pt size
            'color': None,  # possible: red
            'highlight': None,  # possible: yellow, redwhite
            'href': None  # url
        }
    }

    def __init__(self, xml):
        self._xml = xml
        self._cursor = None
        # retrieve relationships
        self._relationships = filter(
            lambda x: x.getparent().getparent().attrib['{%s}name' % self.ns.pkg] == '/word/_rels/document.xml.rels',
            self._xml.xpath('/pkg:package/pkg:part/pkg:xmlData/a:Relationships',
                            namespaces=dict(pkg=self.ns.pkg, a=self.ns.a)))[0]
        # add numbering package and related relationship
        relationships = self.relationships()
        if not filter(lambda x: x[2] == 'numbering.xml', relationships):
            self._xml.getroot().append(etree.fromstring(self._numbering_pkg))
            self._relationships.append(etree.fromstring(
                '<Relationship xmlns="http://schemas.openxmlformats.org/package/2006/relationships" Id="rId' + str(
                    self.new_rel_id(
                        relationships)) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'))
        del relationships
        # update styles if required
        for styles in filter(
                lambda x: x.getparent().getparent().attrib['{%s}name' % self.ns.pkg] in ['/word/styles.xml',
                                                                                         '/word/stylesWithEffects.xml'],
                self._xml.xpath('//w:styles', namespaces=dict(w=self.ns.w))):
            styles_map = map(lambda x: x.attrib['{%s}styleId' % self.ns.w], styles.xpath('./w:style',
                                                                                         namespaces=dict(w=self.ns.w)))
            if 'ListParagraph' not in styles_map:
                styles.append(etree.fromstring(self._listparagraph_style))
            if 'Hyperlink' not in styles_map:
                styles.append(etree.fromstring(self._hyperlink_style))
        # ul will use it
        self._bullet = None
        self._numbered = None
        # misc
        self.reset_style()
        self.seq_start()

    def set_sdt_cursor(self, title=None, cursor=None):
        if cursor is None:
            result = map(lambda x: x.getparent().getparent(), filter(lambda x: x.attrib['{%s}val' % self.ns.w] == title,
                                                                     self._xml.xpath('//w:sdt/w:sdtPr/w:alias',
                                                                                     namespaces=dict(w=self.ns.w))))
            if result:
                self._cursor = result[0]
            else:
                self._cursor = None
        else:
            self._cursor = cursor
        return self._cursor

    def relationships(self):
        return map(lambda x: [x.attrib['Id'], x.attrib['Type'], x.attrib['Target']],
                   self._relationships.xpath('./a:Relationship', namespaces=dict(a=self.ns.a)))

    def new_rel_id(self, relationships=None):
        if relationships is None:
            relationships = self.relationships()
        return sorted(map(lambda x: int(x[0][3:]), relationships))[-1] + 1

    def _insert(self, children):
        if not isinstance(children, list):
            children = [children]
        p = self._cursor.getparent()
        for child in children:
            p.insert(p.index(self._cursor), child)
        return self

    def _replace(self, children):
        self._insert(children)
        return self.remove_sdt_cursor()

    def remove_sdt_cursor(self):
        p = self._cursor.getparent()
        p.remove(self._cursor)
        self._cursor = None
        return self

    def seq_start(self):
        self._seq = []

    def seq_append(self, children):
        if not isinstance(children, list):
            children = [children]
        self._seq += children

    def seq_end(self):
        seq = self._seq
        self._seq = []
        return seq

    def seq_len(self):
        return len(self._seq)

    def p(self, children):
        if not isinstance(children, list):
            children = [children]
        e = etree.fromstring('''

<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
</w:p>
''')
        for child in children:
            e.append(child)
        self.reset_run_style()
        self._insert(e)
        return e

    def append(self, children):
        self._insert(children)

    def reset_style(self):
        self._style = self._style_defaults.copy()

    def reset_run_style(self):
        self._style['run'] = self._style_defaults['run'].copy()

    def set_style(self, **params):
        for i in ['bold', 'italic', 'space', 'font', 'size', 'color', 'highlight', 'href']:
            if i in params:
                self._style['run'][i] = params[i]

    def _get_style(self, params):
        # volatile
        for i in ['bold']:
            if i in params:
                bold = params[i]
            else:
                bold = self._style['run'][i]
        for i in ['italic']:
            if i in params:
                italic = params[i]
            else:
                italic = self._style['run'][i]
        for i in ['space']:
            if i in params:
                space = params[i]
            else:
                space = self._style['run'][i]
        for i in ['font']:
            if i in params:
                font = params[i]
            else:
                font = self._style['run'][i]
        for i in ['size']:
            if i in params:
                size = params[i]
            else:
                size = self._style['run'][i]
        for i in ['color']:
            if i in params:
                color = params[i]
            else:
                color = self._style['run'][i]
        for i in ['highlight']:
            if i in params:
                highlight = params[i]
            else:
                highlight = self._style['run'][i]
        for i in ['href']:
            if i in params:
                href = params[i]
            else:
                href = self._style['run'][i]
        margins = [None, None]
        style_set = bold or italic or font != None or size != None or color != None or highlight != None or href != None
        return bold, italic, space, font, size, margins, color, highlight, href, style_set

    def get_style(self):
        return self._style

    def r(self, content, **params):
        bold, italic, space, font, size, margins, color, highlight, href, style_set = self._get_style(params)
        e = etree.fromstring('''

  <w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">''' + ['', '''
    <w:rPr>'''][style_set] + ['', '''
      <w:b />'''][bold] + ['', '''
      <w:i />'''][italic] + ['', '''
      <w:color w:val="FF0000" />'''][color == 'red'] + ['', '''
      <w:highlight w:val="yellow" />'''][highlight == 'yellow'] + ['', '''
      <w:color w:val="FFFFFF" w:themeColor="background1" />
      <w:highlight w:val="red" />'''][highlight == 'redwhite'] + ['', '''
      <w:rFonts w:ascii="''' + str(font) + '''" w:hAnsi="''' + str(font) + '''" w:cs="''' + str(font) + '''"/>'''][
            font is not None] + ['', '''
      <w:sz w:val="''' + str(size) + '''"/>'''][size is not None] + ['', '''
      <w:rStyle w:val="Hyperlink"/>'''][href is not None] + ['', '''
      <w:ind w:left="''' + str(margins[0]) + '''" w:hanging="''' + str(margins[1]) + '''"/>'''][
                                 margins != [None, None]] + ['', '''
    </w:rPr>'''][style_set] + '''
    <w:t''' + ['', ' xml:space="preserve"'][space] + '>' + content + '''</w:t>
  </w:r>
''')
        #print z
        #self._insert(e)
        return e

    def h(self, content, **params):
        self.set_style(href=params['href'])
        relationships = self.relationships()
        rel_id = self.new_rel_id(relationships)
        self._relationships.append(etree.fromstring(
            '<Relationship xmlns="http://schemas.openxmlformats.org/package/2006/relationships" Id="rId' + str(
                rel_id) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="' +
            self._style['run']['href'] + '" TargetMode="External"/>'))
        e = etree.fromstring('''

      <w:hyperlink xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:id="rId''' + str(
            rel_id) + '''" w:history="1">
      </w:hyperlink>
''')
        e.append(self.r(content, **params))
        self._style['run']['href'] = None
        #self._insert(e)
        return e

    def ul(self, children):
        if self._bullet is None:
            bullet_abstractNums = map(lambda x: x.attrib['{' + self.ns.w + '}abstractNumId'], list(set(
                map(lambda x: x.getparent().getparent(),
                    filter(lambda x: x.attrib['{' + self.ns.w + '}val'] == 'bullet',
                           self._xml.xpath('//w:numbering/w:abstractNum/w:lvl/w:numFmt',
                                           namespaces=dict(w=self.ns.w)))))))
            #print bullet_abstractNums
            numids_to_abstractNums = map(
                lambda x: [x.getparent().attrib['{' + self.ns.w + '}numId'], x.attrib['{' + self.ns.w + '}val']],
                self._xml.xpath('//w:numbering/w:num/w:abstractNumId', namespaces=dict(w=self.ns.w)))
            #print numids_to_abstractNums
            bullet_numids = map(lambda x: x[0], filter(lambda x: x[1] in bullet_abstractNums, numids_to_abstractNums))
            self._bullet = bullet_numids[0]
        e = self.p(children)
        e.insert(0, etree.fromstring('''

<w:pPr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:numPr>
    <w:ilvl w:val="0" />
    <w:numId w:val="''' + str(self._bullet) + '''" />
  </w:numPr>
</w:pPr>
'''))
        self._insert(e)
        return e

    def new_abstractNum(self):
        return sorted(map(lambda x: int(x.attrib['{' + self.ns.w + '}abstractNumId']), list(set(
            map(lambda x: x.getparent().getparent(),
                self._xml.xpath('//w:numbering/w:abstractNum/w:lvl/w:numFmt', namespaces=dict(w=self.ns.w)))))))[
                   -1] + 1, sorted(map(lambda x: int(x.getparent().attrib['{' + self.ns.w + '}numId']),
                                       self._xml.xpath('//w:numbering/w:num/w:abstractNumId',
                                                       namespaces=dict(w=self.ns.w))))[-1] + 1

    def ol_reset(self):
        abstractNum, num_id = self.new_abstractNum()
        num = etree.fromstring('''

<w:num w:numId="''' + str(num_id) + '''" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNumId w:val="''' + str(abstractNum) + '''" />
</w:num>
''')
        abstractNum_decimal = etree.fromstring(self._abstractNum_decimal)
        abstractNum_decimal.attrib['{' + self.ns.w + '}abstractNumId'] = str(abstractNum)
        numbering = self._xml.xpath('//w:numbering', namespaces=dict(w=self.ns.w))[0]
        numbering_num = numbering.xpath('./w:num', namespaces=dict(w=self.ns.w))[0]
        numbering.insert(numbering.index(numbering_num), abstractNum_decimal)
        numbering.append(num)
        self._numbered = (abstractNum, num_id)

    def ol(self, children, reset=False):
        if self._numbered == None or reset:
            self.ol_reset()
        abstractNum, num_id = self._numbered
        e = self.p(children)
        e.insert(0, etree.fromstring('''

<w:pPr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:numPr>
    <w:ilvl w:val="0" />
    <w:numId w:val="''' + str(num_id) + '''" />
  </w:numPr>
</w:pPr>
'''))
        self._insert(e)
        return e

    def xl(self, children):
        e = self.p(children)
        e.insert(0, etree.fromstring('''

<w:pPr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:pStyle w:val="ListParagraph" />
</w:pPr>
'''))
        self._insert(e)
        return e

    def picture(self, filename, name='', descr='', cap=627):
        # ext, content_type, relationships
        ext = filename.split('.')[-1]
        if ext == 'jpg':
            content_type = 'image/jpeg'
        else:
            content_type = 'image/' + ext
        relationships = self.relationships()
        # image_id, target
        for pattern in ['media/image']:
            images = sorted(map(lambda x: int(x[2][len(pattern):].split('.')[0]),
                                filter(lambda x: x[2][:len(pattern)] == pattern, relationships)))
            if len(images):
                image_id = images[-1] + 1
            else:
                image_id = 1
            del images
        target = 'image' + str(image_id) + '.' + ext
        # docPr_id
        docPr_ids = sorted(
            map(lambda x: int(x.attrib['id']), self._xml.xpath('//wp:docPr', namespaces=dict(wp=self.ns.wp))))
        if len(docPr_ids):
            docPr_id = docPr_ids[-1] + 1
        else:
            docPr_id = 1
        del docPr_ids
        # rel_id, ...
        rel_id = self.new_rel_id(relationships)
        self._relationships.append(etree.fromstring('<Relationship Id="rId' + str(
            rel_id) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/' + target + '" xmlns="http://schemas.openxmlformats.org/package/2006/relationships" />'))
        self._xml.getroot().append(etree.fromstring(
            '<pkg:part pkg:name="/word/media/' + target + '" pkg:contentType="' + content_type + '" pkg:compression="store" xmlns:pkg="http://schemas.microsoft.com/office/2006/xmlPackage"><pkg:binaryData>' + base64.b64encode(
                open(filename, 'rb').read()) + '</pkg:binaryData></pkg:part>'))
        from PIL import Image

        im = Image.open(filename)
        x, y = im.size
        if cap != None:
            if x > cap:
                y = int(round(float(cap * y) / x))
                x = cap
        x = str(x * 9525)
        y = str(y * 9525)
        e = etree.fromstring('''

<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:r>
    <w:rPr>
      <w:noProof/>
    </w:rPr>
    <w:drawing>
      <wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
        <wp:extent cx="''' + x + '''" cy="''' + y + '''"/>
        <wp:docPr id="''' + str(docPr_id) + '''" name="''' + name + '''" descr="''' + descr + '''"/>
        <wp:cNvGraphicFramePr>
          <a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>
        </wp:cNvGraphicFramePr>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="0" name="''' + name + '''" descr="''' + descr + '''"/>
                <pic:cNvPicPr>
                  <a:picLocks noChangeAspect="1" noChangeArrowheads="1"/>
                </pic:cNvPicPr>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="rId''' + str(
            rel_id) + '''"/>
                <a:srcRect/>
                <a:stretch>
                  <a:fillRect/>
                </a:stretch>
              </pic:blipFill>
              <pic:spPr bwMode="auto">
                <a:xfrm>
                  <a:off x="0" y="0"/>
                  <a:ext cx="''' + x + '''" cy="''' + y + '''"/>
                </a:xfrm>
                <a:prstGeom prst="rect">
                  <a:avLst/>
                </a:prstGeom>
                <a:noFill/>
                <a:ln>
                  <a:noFill/>
                </a:ln>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
''')
        self._insert(e)
        return e

    def parse(self, data, parser):
        # TODO, workaround for workbench/p/
        try:
            clean =  etree.tostring(soupparser.fromstring(data, features='html.parser'))
            #clean = clean.replace('<br/><br/>','<br/>') #.replace('\n','')
            #print clean
            pre_before = '<html><ihtml>'
            pre_remove = '<html>'
            #post_before = '</ihtml></html>'
            post_remove = '</html>'
            if clean[:len(pre_before)] == pre_before:
                clean = clean[len(pre_remove):-len(post_remove)]
            etree.XML(clean, parser)
        except:
            pass

if __name__ == '__main__':
    xml = etree.parse('d6-empty.xml')

    o = Openxml(xml)

    # example usage of tree building
    o.set_sdt_cursor(title='Replace')
    o.seq_start()
    o.seq_append([
        o.r('Contents under '),
        o.r('Pressure', highlight='redwhite'),
    ])
    o.p(o.seq_end())
    o.picture('xss1.png')
    o.picture('image-slider-4.jpg')
    o.picture('logo_sm_2.jpeg')
    o.p([
        o.r('We are in '),
        o.r('some', highlight='yellow', space=False),
        o.r(' paragraph with '),
        o.r('nasty', highlight='redwhite', space=False),
        o.r(' italic', italic=True),
        o.r(' and '),
        o.r(' bold', bold=True),
        o.r(' characters.', font='Consolas', size=22),
    ]),
    o.p([
        o.r('And now some '),
        o.h('link', href='http://www.onet.pl/'),
        o.r('.'),
    ])
    o.ul(o.r('unordered'))
    o.ol([
        o.r('ordered 1'),
    ])
    o.xl(o.r('test'))
    o.ol(o.r('ordered 1 again'))
    o.ol(o.r('ordered 2'), reset=True)
    #o.remove_sdt_cursor()

    xml.write('d7-done.xml', xml_declaration=True, encoding='UTF-8')
