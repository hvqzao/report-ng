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


from cgi import escape


class InlineHtmlParser(object):
    #_href

    def __init__(self, openxml):
        self._o = openxml
        self.reset()

    def reset(self):
        self._href = None

    def start(self, tag, attrib):
        handled = False
        if tag == 'b':
            self._o.set_style(bold=True)
        if tag == 'i':
            self._o.set_style(italic=True)
        if tag in ['r', 'red']:
            self._o.set_style(color='red')
        if tag in ['y', 'yellow']:
            self._o.set_style(highlight='yellow')
        if tag in ['rw', 'redwhite']:
            self._o.set_style(highlight='redwhite')
        if tag == 'a' and 'href' in attrib:
            self._href = attrib['href']
        if tag == 'font':
            if 'face' in attrib:
                self._o.set_style(font=attrib['face'])
            if 'size' in attrib:
                self._o.set_style(size=int(float(attrib['size']) * 2))
        if tag in ['b', 'i', 'r', 'red', 'y', 'yellow', 'rw', 'redwhite', 'ihtml', 'a', 'font']:
            handled = True

    def end(self, tag):
        handled = False
        if tag == 'b':
            self._o.set_style(bold=False)
        if tag == 'i':
            self._o.set_style(italic=False)
        if tag in ['r', 'red']:
            self._o.set_style(color=None)
        if tag in ['y', 'yellow']:
            self._o.set_style(highlight=None)
        if tag in ['rw', 'redwhite']:
            self._o.set_style(highlight=None)
        if tag == 'a':
            self._href = None
        if tag == 'font':
            self._o.set_style(font=None, size=None)
        if tag in ['b', 'i', 'r', 'red', 'y', 'yellow', 'rw', 'redwhite', 'ihtml', 'a', 'font']:
            handled = True

    def data(self, data):
        if self._href:
            self._o.append(self._o.h(escape(data), href=self._href))
        else:
            self._o.append(self._o.r(escape(data)))

    def close(self):
        self.reset()


class HtmlParser(object):
    #_numered
    #_href

    def __init__(self, openxml):
        self._o = openxml
        self.reset()

    def reset(self):
        self._numbered = False
        self._href = None

    def start(self, tag, attrib):
        handled = False
        if tag == 'b':
            self._o.set_style(bold=True)
        if tag == 'i':
            self._o.set_style(italic=True)
        if tag in ['r', 'red']:
            self._o.set_style(color='red')
        if tag in ['y', 'yellow']:
            self._o.set_style(highlight='yellow')
        if tag in ['rw', 'redwhite']:
            self._o.set_style(highlight='redwhite')
        if tag in ['ul', 'ol', 'xl', 'li', 'img']:
            if self._o.seq_len():
                self._o.p(self._o.seq_end())
        if tag == 'ul':
            self._numbered = False
        if tag == 'ol':
            self._o.ol_reset()
            self._numbered = True
        if tag == 'a' and 'href' in attrib:
            self._href = attrib['href']
        if tag == 'font':
            if 'face' in attrib:
                self._o.set_style(font=attrib['face'])
            if 'size' in attrib:
                self._o.set_style(size=int(float(attrib['size']) * 2))
        if tag == 'img':
            args = dict(name=attrib['src'])
            if 'alt' in attrib:
                args['descr'] = attrib['alt']
            if 'width' in attrib:
                args['cap'] = int(attrib['width'])
            self._o.picture(attrib['src'], **args)
        if tag in ['b', 'i', 'r', 'red', 'y', 'yellow', 'rw', 'redwhite', 'html', 'br', 'ul', 'ol', 'li', 'xl', 'a', 'font',
                   'img']:
            handled = True
        #print ['?','*'][handled],'start %s %r' % (tag, dict(attrib))

    def end(self, tag):
        handled = False
        if tag == 'b':
            self._o.set_style(bold=False)
        if tag == 'i':
            self._o.set_style(italic=False)
        if tag in ['r', 'red']:
            self._o.set_style(color=None)
        if tag in ['y', 'yellow']:
            self._o.set_style(highlight=None)
        if tag in ['rw', 'redwhite']:
            self._o.set_style(highlight=None)
        if tag == 'br':
            self._o.p(self._o.seq_end())
        if tag == 'li':
            if self._numbered:
                self._o.ol(self._o.seq_end())
            else:
                self._o.ul(self._o.seq_end())
        if tag == 'xl':
            self._o.xl(self._o.seq_end())
        if tag == 'a':
            self._href = None
        if tag == 'font':
            self._o.set_style(font=None, size=None)
        if tag in ['b', 'i', 'r', 'red', 'y', 'yellow', 'rw', 'redwhite', 'html', 'br', 'ul', 'ol', 'li', 'xl', 'a', 'font',
                   'img']:
            handled = True
        #print ['?','*'][handled],'end %s' % tag

    def data(self, data):
        #print ' ','data %r' % data
        #print ' ','data', data
        if self._href:
            self._o.seq_append(self._o.h(escape(data), href=self._href))
        else:
            self._o.seq_append(self._o.r(escape(data)))

    #def comment(self, text):
    #    print ' ','comment %s' % text
    def close(self):
        #print ' ','close'
        if self._o.seq_len():
            self._o.p(self._o.seq_end())
        self.reset()
        #return 'closed!'


if __name__ == '__main__':
    pass
    '''
    # pseudo-html parser use
    html_parser = etree.XMLParser (target=HtmlParser (o), resolve_entities=False)
    data = open ('d7-input.txt').read() #.replace (chr(146),'\'')
    data = etree.tostring (soupparser.fromstring (data, features='html.parser'))[len('<html>'):-len('</html>')]
    o.set_sdt_cursor (title='Replace')
    for i in map (lambda x: '<html>'+x.replace('<br/><br/>','<br/>').replace('\n','<br/>').replace('<br/><br/>','<br/>')+'</html>', data.split('\n\n')): #[:1]
        #print i
        #etree.XML (i, html_parser)
        o.parse (i, html_parser)
    o.remove_sdt_cursor()

    xml.write ('d7-done.xml', xml_declaration=True, encoding='UTF-8')
    '''
