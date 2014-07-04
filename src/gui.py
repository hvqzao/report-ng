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


import wx
import base64
import cStringIO

from resources.icon import icon
from report import Report
from scan import Scan
from version import Version


class GUI(Version):

    def MainWindow(self):
        self.__MainWindow(application=self)

    class __MainWindow(wx.Frame):

        # Variables set during __init__

        #report
        #application
        #scan
        #template
        #icon
        #menu_file_open_c
        #menu_file_open_k
        #menu_file_generate_c
        #menu_file_generate_k
        #menu_file_generate_r
        #menu_file_save_t
        #menu_file_save_c
        #menu_file_save_s
        #menu_file_save_k
        #menu_file_save_r
        #menu_view_c
        #menu_view_y
        #menu_view_j
        #menu_view_v
        #menu_tools_template_structure_preview
        #menu_tools_merge_scan_into_content
        #ctrl_st_t
        #ctrl_tc_t
        #ctrl_st_c
        #ctrl_tc_c
        #ctrl_st_s
        #ctrl_tc_s
        #ctrl_st_k
        #ctrl_tc_k
        #ctrl_st_r
        #ctrl_tc_r
        #color_tc_bg_e
        #color_tc_bg_d

        def __init__(self, application=None, parent=None, *args,
                     **kwargs):  #style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER

            #self.report = None
            self.report = Report()
            self.application = application
            self.scan = None
            wx.Frame.__init__(self, parent, title=self.application.title + ' ' + self.application.version, *args,
                              **kwargs)  #style=style
            self.Bind(wx.EVT_CLOSE, lambda x: self.Destroy())

            myStream = cStringIO.StringIO(base64.b64decode(icon))
            myImage = wx.ImageFromStream(myStream)
            myBitmap = wx.BitmapFromImage(myImage)
            self.icon = wx.EmptyIcon()
            self.icon.CopyFromBitmap(myBitmap)
            self.SetIcon(self.icon)

            # Menu arrangement

            menu = wx.MenuBar()

            class Index(object):
                def __init__(self, current):
                    self.__current = current - 1

                @property
                def current(self):
                    return self.__current

                @current.setter
                def current(self, x):
                    self.__current = x

                def next(self):
                    self.__current += 1
                    return self.__current

            index = Index(100)
            menu_file = wx.Menu()
            menu_file.Append(index.next(), 'Open Report &Template...')
            self.Bind(wx.EVT_MENU, self.Open_Template, id=index.current)
            self.menu_file_open_c = menu_file.Append(index.next(), 'Open &Content...')
            self.menu_file_open_c.Enable(False)
            self.Bind(wx.EVT_MENU, self.Open_Content, id=index.current)
            menu_file.Append(index.next(), 'Open &Scan...')
            self.Bind(wx.EVT_MENU, self.Open_Scan, id=index.current)
            self.menu_file_open_k = menu_file.Append(index.next(), 'Open &Knowledge Base...')
            self.menu_file_open_k.Enable(False)
            self.Bind(wx.EVT_MENU, self.Open_Knowledge_Base, id=index.current)
            #menu_file.AppendSeparator()
            #self.menu_file_generate_c = menu_file.Append(index.next(), '&Generate Content')
            #self.menu_file_generate_c.Enable(False)
            #self.Bind(wx.EVT_MENU, self.Generate_Content, id=index.current)
            #self.menu_file_generate_k = menu_file.Append(index.next(), 'G&enerate Knowledge Base')
            #self.menu_file_generate_k.Enable(False)
            #self.Bind(wx.EVT_MENU, self.Generate_Knowledge_Base, id=index.current)
            #self.menu_file_generate_r = menu_file.Append(index.next(), 'Ge&nerate Report')
            #self.menu_file_generate_r.Enable(False)
            #self.Bind(wx.EVT_MENU, self.Generate_Report, id=index.current)
            menu_file.AppendSeparator()
            self.menu_file_save_t = menu_file.Append(index.next(), '&Save Template As...')
            self.menu_file_save_t.Enable(False)
            self.Bind(wx.EVT_MENU, self.Save_Template_As, id=index.current)
            self.menu_file_save_c = menu_file.Append(index.next(), 'Sav&e Content As...')
            self.menu_file_save_c.Enable(False)
            self.Bind(wx.EVT_MENU, self.Save_Content_As, id=index.current)
            #self.menu_file_save_k = menu_file.Append(index.next(), 'S&ave Knowledge Base As...')
            #self.menu_file_save_k.Enable(False)
            #self.Bind(wx.EVT_MENU, self.Save_Knowledge_Base_As, id=index.current)
            self.menu_file_save_s = menu_file.Append(index.next(), 'Sa&ve Scan As...')
            self.menu_file_save_s.Enable(False)
            self.Bind(wx.EVT_MENU, self.Save_Scan_As, id=index.current)
            self.menu_file_save_r = menu_file.Append(index.next(), 'Save &Report As...')
            self.menu_file_save_r.Enable(False)
            self.Bind(wx.EVT_MENU, self.Save_Report_As, id=index.current)
            menu_file.AppendSeparator()
            menu_file.Append(wx.ID_EXIT, 'E&xit\tCtrl+Q', 'Exit application')
            self.Bind(wx.EVT_MENU, self.Exit, id=wx.ID_EXIT)
            menu.Append(menu_file, '&File')
            menu_view = wx.Menu()
            self.menu_view_c = menu_view.Append(index.next(), 'C&lean template', kind=wx.ITEM_CHECK)
            self.Bind(wx.EVT_MENU, self.Clean_template, id=index.current)
            self.menu_view_c.Check(True)
            menu_view.AppendSeparator()
            self.menu_view_y = menu_view.Append(index.next(), '&yaml', kind=wx.ITEM_RADIO)
            self.Bind(wx.EVT_MENU, self.Use_yaml, id=index.current)
            self.menu_view_j = menu_view.Append(index.next(), '&json', kind=wx.ITEM_RADIO)
            self.Bind(wx.EVT_MENU, self.Use_json, id=index.current)
            self.menu_view_y.Check(True)
            menu.Append(menu_view, '&View')
            menu_view.AppendSeparator()
            self.menu_view_v = menu_view.Append(index.next(), '&VulnParam highlighting', kind=wx.ITEM_CHECK)
            self.Bind(wx.EVT_MENU, self.VulnParam_highlighting, id=index.current)
            self.menu_view_v.Check(True)
            menu_tools = wx.Menu()
            self.menu_tools_template_structure_preview = menu_tools.Append(index.next(), 'Te&mplate structure preview')
            self.menu_tools_template_structure_preview.Enable(False)
            self.Bind(wx.EVT_MENU, self.Template_Structure_Preview, id=index.current)
            self.menu_tools_merge_scan_into_content = menu_tools.Append(index.next(), 'Mer&ge Scan into Content')
            self.menu_tools_merge_scan_into_content.Enable(False)
            self.Bind(wx.EVT_MENU, self.Merge_Scan_Into_Content, id=index.current)
            menu.Append(menu_tools, '&Tools')
            menu_help = wx.Menu()
            menu_help.Append(index.next(), '&Usage')
            self.Bind(wx.EVT_MENU, self.Usage, id=index.current)
            menu_help.Append(index.next(), '&Changelog')
            self.Bind(wx.EVT_MENU, self.Changelog, id=index.current)
            menu_help.AppendSeparator()
            menu_help.Append(wx.ID_ABOUT, '&About')
            self.Bind(wx.EVT_MENU, self.About, id=wx.ID_ABOUT)
            menu.Append(menu_help, '&Help')
            self.SetMenuBar(menu)

            # Frame layout arrangement

            class FileDropTarget(wx.FileDropTarget):
                def __init__(self, target, handler):
                    wx.FileDropTarget.__init__(self)
                    self.target = target
                    self.handler = handler

                def OnDropFiles(self, x, y, filenames):
                    self.handler(filenames)

            panel = wx.Panel(self)
            vbox = wx.BoxSizer(wx.VERTICAL)
            fgs = wx.FlexGridSizer(5, 2, 9, 25)

            # Template
            self.ctrl_st_t = wx.StaticText(panel, label='Template:')
            self.ctrl_st_t.Enable(False)
            self.ctrl_tc_t = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(200, 3 * 17,))

            def ctrl_tc_t_OnFocus(e):
                self.ctrl_tc_t.ShowNativeCaret(False)
                # for unknown reason this refuse to work in wxpython 3.0
                e.Skip()

            def ctrl_tc_t_OnDoubleclick(e):
                if self.ctrl_st_t.IsEnabled():
                    self.application.TextWindow(self, title='Template Preview', content=self.ctrl_tc_t.GetValue())
                e.Skip()

            self.ctrl_tc_t.Bind(wx.EVT_SET_FOCUS, ctrl_tc_t_OnFocus)
            self.ctrl_tc_t.Bind(wx.EVT_LEFT_DCLICK, ctrl_tc_t_OnDoubleclick)

            def ctrl_tc_t_OnDropFiles(filenames):
                if len(filenames) != 1:
                    wx.MessageBox('Single file is expected!', 'Error', wx.OK | wx.ICON_ERROR)
                    return
                self._open_template(filenames[0])

            ctrl_tc_t_dt = FileDropTarget(self.ctrl_tc_t, ctrl_tc_t_OnDropFiles)
            self.ctrl_tc_t.SetDropTarget(ctrl_tc_t_dt)
            fgs.AddMany([(self.ctrl_st_t, 1, wx.EXPAND), (self.ctrl_tc_t, 1, wx.EXPAND)])

            # Content
            self.ctrl_st_c = wx.StaticText(panel, label='Content:')
            self.ctrl_st_c.Enable(False)
            self.ctrl_tc_c = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(200, 3 * 17,))
            self.color_tc_bg_e = self.ctrl_tc_c.GetBackgroundColour()
            self.ctrl_tc_c.Enable(False)
            self.color_tc_bg_d = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
            self.ctrl_tc_c.SetBackgroundColour(self.color_tc_bg_d)

            def ctrl_tc_c_OnFocus(e):
                self.ctrl_tc_c.ShowNativeCaret(False)
                e.Skip()

            def ctrl_tc_c_OnDoubleclick(e):
                if self.ctrl_st_c.IsEnabled():
                    self.application.TextWindow(self, title='Content Preview', content=self.ctrl_tc_c.GetValue())
                e.Skip()

            self.ctrl_tc_c.Bind(wx.EVT_SET_FOCUS, ctrl_tc_c_OnFocus)
            self.ctrl_tc_c.Bind(wx.EVT_LEFT_DCLICK, ctrl_tc_c_OnDoubleclick)

            def ctrl_tc_c_OnDropFiles(filenames):
                if len(filenames) != 1:
                    wx.MessageBox('Single file is expected!', 'Error', wx.OK | wx.ICON_ERROR)
                    return
                self._open_content(filenames[0])

            ctrl_tc_c_dt = FileDropTarget(self.ctrl_tc_c, ctrl_tc_c_OnDropFiles)
            self.ctrl_tc_c.SetDropTarget(ctrl_tc_c_dt)
            fgs.AddMany([(self.ctrl_st_c, 1, wx.EXPAND), (self.ctrl_tc_c, 1, wx.EXPAND)])

            # Scan
            self.ctrl_st_s = wx.StaticText(panel, label='Scan:')
            self.ctrl_st_s.Enable(False)
            self.ctrl_tc_s = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(200, 3 * 17,))

            def ctrl_tc_s_OnFocus(e):
                self.ctrl_tc_s.ShowNativeCaret(False)
                e.Skip()

            def ctrl_tc_s_OnDoubleclick(e):
                if self.ctrl_st_s.IsEnabled():
                    self.application.TextWindow(self, title='Scan Preview', content=self.ctrl_tc_s.GetValue())
                e.Skip()

            self.ctrl_tc_s.Bind(wx.EVT_SET_FOCUS, ctrl_tc_s_OnFocus)
            self.ctrl_tc_s.Bind(wx.EVT_LEFT_DCLICK, ctrl_tc_s_OnDoubleclick)

            def ctrl_tc_s_OnDropFiles(filenames):
                if len(filenames) != 1:
                    wx.MessageBox('Single file is expected!', 'Error', wx.OK | wx.ICON_ERROR)
                    return
                self._open_scan(filenames[0])

            ctrl_tc_s_dt = FileDropTarget(self.ctrl_tc_s, ctrl_tc_s_OnDropFiles)
            self.ctrl_tc_s.SetDropTarget(ctrl_tc_s_dt)
            fgs.AddMany([(self.ctrl_st_s, 1, wx.EXPAND), (self.ctrl_tc_s, 1, wx.EXPAND)])

            # Knowledge Base
            self.ctrl_st_k = wx.StaticText(panel, label='Knowledge Base:')
            self.ctrl_st_k.Enable(False)
            self.ctrl_tc_k = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(200, 3 * 17,))
            self.ctrl_tc_k.Enable(False)
            self.ctrl_tc_k.SetBackgroundColour(self.color_tc_bg_d)

            def ctrl_tc_k_OnFocus(e):
                self.ctrl_tc_k.ShowNativeCaret(False)
                e.Skip()

            def ctrl_tc_k_OnDoubleclick(e):
                if self.ctrl_st_k.IsEnabled():
                    self.application.TextWindow(self, title='KB Preview', content=self.ctrl_tc_k.GetValue())
                e.Skip()

            self.ctrl_tc_k.Bind(wx.EVT_SET_FOCUS, ctrl_tc_k_OnFocus)
            self.ctrl_tc_k.Bind(wx.EVT_LEFT_DCLICK, ctrl_tc_k_OnDoubleclick)

            def ctrl_tc_k_OnDropFiles(filenames):
                if len(filenames) != 1:
                    wx.MessageBox('Single file is expected!', 'Error', wx.OK | wx.ICON_ERROR)
                    return
                self._open_kb(filenames[0])

            ctrl_tc_k_dt = FileDropTarget(self.ctrl_tc_k, ctrl_tc_k_OnDropFiles)
            self.ctrl_tc_k.SetDropTarget(ctrl_tc_k_dt)
            fgs.AddMany([(self.ctrl_st_k, 1, wx.EXPAND), (self.ctrl_tc_k, 1, wx.EXPAND)])

            # Report
            #self.ctrl_st_r = wx.StaticText(panel, label='Report:')
            #self.ctrl_st_r.Enable (False)
            #self.ctrl_tc_r = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(200, 3*17,))
            #self.ctrl_tc_r.Enable(False)
            #self.ctrl_tc_r.SetBackgroundColour (self.color_tc_bg_d)
            #def ctrl_tc_r_OnFocus (e):
            #    self.ctrl_tc_r.ShowNativeCaret (False)
            #    e.Skip()
            #self.ctrl_tc_r.Bind (wx.EVT_SET_FOCUS, ctrl_tc_r_OnFocus)
            #fgs.AddMany ([(self.ctrl_st_r, 1, wx.EXPAND), (self.ctrl_tc_r, 1, wx.EXPAND)])

            fgs.AddGrowableRow(0, 1)
            fgs.AddGrowableRow(1, 1)
            fgs.AddGrowableRow(2, 1)
            fgs.AddGrowableRow(3, 1)
            #fgs.AddGrowableRow (4, 1)
            fgs.AddGrowableCol(1, 1)
            vbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
            #data = wx.TextCtrl(panel)
            #hbox1 = wx.BoxSizer (wx.HORIZONTAL)
            #hbox1.Add(data, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=10)
            #vbox.Add (hbox1, 0, wx.ALL|wx.EXPAND, 0)
            panel.SetSizer(vbox)
            vbox.Fit(self)
            self.SetMinSize(self.GetSize())
            #panel = wx.Panel (self)
            #vbox = wx.BoxSizer (wx.VERTICAL)
            #hbox1 = wx.BoxSizer (wx.HORIZONTAL)
            ##st1 = wx.StaticText (panel, wx.ID_ANY, label='Not yet ready')
            #st1 = wx.StaticText (panel, wx.ID_ANY, label='Template:', size=(100, -1,))
            #hbox1.Add (st1, 0, wx.ALL, 5)
            #tc1 = wx.TextCtrl (panel, wx.ID_ANY, size=(300, -1,))
            #hbox1.Add (tc1, 1, wx.ALL|wx.EXPAND, 0)
            #vbox.Add (hbox1, 0, wx.ALL|wx.EXPAND, 0)
            #hbox2 = wx.BoxSizer (wx.HORIZONTAL)
            #st2 = wx.StaticText (panel, wx.ID_ANY, label='Scan:', size=(100, -1,))
            #hbox2.Add (st2, 0, wx.ALL, 5)
            #tc2 = wx.TextCtrl (panel, wx.ID_ANY, size=(300, -1,))
            #hbox2.Add (tc2, 1, wx.ALL|wx.EXPAND, 0)
            #vbox.Add (hbox2, 0, wx.ALL|wx.EXPAND, 0)
            ##vbox.Add (hbox1, 0, wx.CENTER, 5)
            #panel.SetSizer (vbox)
            #vbox.Fit (self)
            self.Center()
            self.Show()
            #print 'loaded'

        def Exit(self, e):
            self.Close()

        def About(self, e):
            dialog = wx.AboutDialogInfo()
            #dialog.SetIcon (wx.Icon('icon.ico', wx.BITMAP_TYPE_PNG))
            dialog.SetIcon(self.icon)
            dialog.SetName(self.application.long_title+' - '+self.application.title)
            dialog.SetVersion(self.application.version)
            dialog.SetCopyright(self.application.c)
            dialog.SetDescription('\n'.join(map(lambda x: x[4:], self.application.about.split('\n')[1:][:-1])))
            
            dialog.SetWebSite(self.application.url)
            dialog.SetLicence(self.application.license)
            wx.AboutBox(dialog)

        def Template_Structure_Preview(self, e):
            self.application.TextWindow(self, title=self.Usage.__name__, content=self.report.template_dump_struct())

        def Usage(self, e):
            self.application.TextWindow(self, title=self.Usage.__name__, content='\n'.join(
                map(lambda x: x[4:], self.application.usage.split('\n')[1:][:-1])))

        def Changelog(self, e):
            self.application.TextWindow(self, title=self.Changelog.__name__, content='\n'.join(
                map(lambda x: x[4:], self.application.changelog.split('\n')[1:][:-1])))

        def Destroy(self):
            map(lambda x: x.Close(), filter(lambda x: isinstance(x, wx.Frame), self.GetChildren()))
            wx.WakeUpIdle()
            #print 'destroying MainWindow'
            super(wx.Frame, self).Destroy()

        def Open_Template(self, e):
            openFileDialog = wx.FileDialog(self, 'Open Template', '', '', 'XML files (*.xml)|*.xml|All files (*.*)|*.*',
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self._open_template(openFileDialog.GetPath())

        def _open_template(self, filename):
            self.ctrl_st_t.Enable(False)
            self.ctrl_tc_t.SetValue('')
            self.ctrl_st_c.Enable(False)
            self.ctrl_tc_c.SetValue('')
            self.menu_file_open_k.Enable(False)
            self.menu_file_save_t.Enable(False)
            self.menu_file_save_r.Enable(False)
            self.menu_tools_template_structure_preview.Enable(False)
            #if self.report:
            #    del self.report
            #self.report = Report()
            #print self.report._skel
            self.report.template_load_xml(filename, clean=self.menu_view_c.IsChecked())
            if self.menu_view_y.IsChecked():
                self.ctrl_tc_t.SetValue(self.report.template_dump_yaml())
            else:
                self.ctrl_tc_t.SetValue(self.report.template_dump_json())
            self.ctrl_st_t.Enable(True)
            self.ctrl_tc_c.Enable(True)
            self.ctrl_tc_c.SetBackgroundColour(self.color_tc_bg_e)
            self.ctrl_tc_k.Enable(True)
            self.ctrl_tc_k.SetBackgroundColour(self.color_tc_bg_e)
            self.menu_file_open_k.Enable(True)
            self.menu_file_open_c.Enable(True)
            self.menu_file_save_t.Enable(True)
            self.menu_tools_template_structure_preview.Enable(True)
            if self.scan:
                self.menu_file_save_r.Enable(True)

        def Open_Content(self, e):
            openFileDialog = wx.FileDialog(self, 'Open Content', '', '',
                                           'Content files (*.yaml; *.json)|*.yaml;*.json|All files (*.*)|*.*',
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self._open_content(openFileDialog.GetPath())

        def __show_content(self):
            if self.menu_view_y.IsChecked():
                self.ctrl_tc_c.SetValue(self.report.content_dump_yaml())
            else:
                self.ctrl_tc_c.SetValue(self.report.content_dump_json())

        def _open_content(self, filename):
            self.ctrl_st_c.Enable(False)
            json_ext = '.json'
            if filename[-len(json_ext):] == json_ext:
                self.report.content_load_json(filename)
            else:
                self.report.content_load_yaml(filename)
            self.__show_content()
            self.ctrl_st_c.Enable(True)
            self.menu_file_save_r.Enable(True)
            self.menu_file_save_c.Enable(True)
            if self.scan:
                self.menu_tools_merge_scan_into_content.Enable(True)

        def Open_Scan(self, e):
            openFileDialog = wx.FileDialog(self, 'Open Scan', '', '',
                                           'Scan files (*.xml; *.yaml; *.json)|*.xml;*.yaml;*.json|All files (*.*)|*.*',
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self._open_scan(openFileDialog.GetPath())

        def _open_scan(self, filename):
            self.menu_file_save_s.Enable(False)
            if self.scan is not None:
                del self.scan
            self.scan = Scan(filename)
            if self.menu_view_y.IsChecked():
                self.ctrl_tc_s.SetValue(self.scan.dump_yaml())
            else:
                self.ctrl_tc_s.SetValue(self.scan.dump_json())
            self.ctrl_st_s.Enable(True)
            self.menu_file_save_s.Enable(True)
            self.menu_file_save_r.Enable(True)
            if self.ctrl_st_c.IsEnabled():
                self.menu_tools_merge_scan_into_content.Enable(True)

        def Merge_Scan_Into_Content(self, e):
            self.report.merge_scan(self.scan)
            self.menu_file_save_s.Enable(False)
            del self.scan
            self.scan = None
            self.ctrl_tc_s.SetValue('')
            self.ctrl_st_s.Enable(False)
            self.menu_file_save_s.Enable(False)
            self.__show_content()
            self.menu_tools_merge_scan_into_content.Enable(False)

        #def Open_Knowledge_Base (self, e):
        #    pass
        #def Generate_Content (self, e):
        #    pass
        #def Generate_Knowledge_Base (self, e):
        #    pass
        #def Generate_Report (self, e):
        #    pass
        def Save_Template_As(self, e):
            openFileDialog = wx.FileDialog(self, 'Save Template As', '', '',
                                           'Content files (*.yaml; *.json)|*.yaml;*.json|All files (*.*)|*.*',
                                           wx.FD_SAVE | wx.wx.FD_OVERWRITE_PROMPT)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            json_ext = '.json'
            filename = openFileDialog.GetPath()
            h = open(filename, 'w')
            if filename[-len(json_ext):] == json_ext:
                h.write(self.report.template_dump_json())
            else:
                h.write(self.report.template_dump_yaml())
            h.close()

        def Save_Content_As(self, e):
            openFileDialog = wx.FileDialog(self, 'Save Content As', '', '',
                                           'Content files (*.yaml; *.json)|*.yaml;*.json|All files (*.*)|*.*',
                                           wx.FD_SAVE | wx.wx.FD_OVERWRITE_PROMPT)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            json_ext = '.json'
            filename = openFileDialog.GetPath()
            h = open(filename, 'w')
            if filename[-len(json_ext):] == json_ext:
                h.write(self.report.content_dump_json())
            else:
                h.write(self.report.content_dump_yaml())
            h.close()

        def Save_Scan_As(self, e):
            openFileDialog = wx.FileDialog(self, 'Save Scan As', '', '',
                                           'Content files (*.yaml; *.json)|*.yaml;*.json|All files (*.*)|*.*',
                                           wx.FD_SAVE | wx.wx.FD_OVERWRITE_PROMPT)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            json_ext = '.json'
            filename = openFileDialog.GetPath()
            h = open(filename, 'w')
            if filename[-len(json_ext):] == json_ext:
                h.write(self.scan.dump_json())
            else:
                h.write(self.scan.dump_yaml())
            h.close()

        #def Save_Knowledge_Base_As (self, e):
        #    pass
        def Save_Report_As(self, e):
            openFileDialog = wx.FileDialog(self, 'Save Report As', '', '',
                                           'XML files (*.xml)|*.xml|All files (*.*)|*.*',
                                           wx.FD_SAVE | wx.wx.FD_OVERWRITE_PROMPT)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = openFileDialog.GetPath()
            if filename == self.report._template_filename:
                wx.MessageBox('For safety reasons, template overwriting with generated report is not allowed!', 'Error',
                              wx.OK | wx.ICON_ERROR)
                return
            self.report.scan = self.scan
            self.report.xml_apply_meta()
            self.report.save_report_xml(filename)

        def Clean_template(self, e):
            if self.ctrl_st_t.IsEnabled():
                self.report._template_reload(clean=self.menu_view_c.IsChecked())
                if self.ctrl_st_c.IsEnabled():
                    self.report._content_reload()
                self._refresh()

        def _refresh(self):
            if self.menu_view_y.IsChecked():
                self._Use_yaml()
            else:
                self._Use_json()

        def _Use_yaml(self):
            if self.ctrl_st_t.IsEnabled():
                self.ctrl_tc_t.SetValue(self.report.template_dump_yaml())
            if self.ctrl_st_c.IsEnabled():
                self.ctrl_tc_c.SetValue(self.report.content_dump_yaml())
            if self.ctrl_st_s.IsEnabled():
                self.ctrl_tc_s.SetValue(self.scan.dump_yaml())

        def Use_yaml(self, e):
            self._Use_yaml()

        def _Use_json(self):
            if self.ctrl_st_t.IsEnabled():
                self.ctrl_tc_t.SetValue(self.report.template_dump_json())
            if self.ctrl_st_c.IsEnabled():
                self.ctrl_tc_c.SetValue(self.report.content_dump_json())
            if self.ctrl_st_s.IsEnabled():
                self.ctrl_tc_s.SetValue(self.scan.dump_json())

        def Use_json(self, e):
            self._Use_json()

        def VulnParam_highlighting(self, e):
            pass

        def Open_Knowledge_Base(self, e):
            openFileDialog = wx.FileDialog(self, 'Open Knowledge Base', '', '',
                                           'Knowledge Base files (*.yaml; *.json)|*.yaml;*.json|All files (*.*)|*.*',
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self._open_kb(openFileDialog.GetPath())

        def _open_kb(self, filename):
            self.ctrl_st_k.Enable(False)
            json_ext = '.json'
            if filename[-len(json_ext):] == json_ext:
                self.report.kb_load_json(filename)
            else:
                self.report.kb_load_yaml(filename)
            if self.menu_view_y.IsChecked():
                self.ctrl_tc_k.SetValue(self.report.kb_dump_yaml())
            else:
                self.ctrl_tc_k.SetValue(self.report.kb_dump_json())
            self.ctrl_st_k.Enable(True)
            #self.menu_file_save_k.Enable (True)
            self.menu_file_save_r.Enable(True)

    class TextWindow(wx.Frame):

        def __init__(self, parent, content='', size=(500, 600,), *args, **kwargs):
            if parent is not None:
                for title in ['title']:
                    if title in kwargs:
                        kwargs[title] = parent.application.title + ' - ' + kwargs[title]
            wx.Frame.__init__(self, parent, size=size, *args, **kwargs)
            if parent is not None:
                self.SetIcon(parent.icon)
            self.Bind(wx.EVT_CLOSE, lambda x: self.Destroy())
            tc = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

            def tc_OnFocus(e):
                tc.ShowNativeCaret(False)
                e.Skip()

            tc.Bind(wx.EVT_SET_FOCUS, tc_OnFocus)
            tc.SetValue(content)
            self.Center()
            self.Show()

        def Destroy(self):
            #print 'destroying TextWindow'
            super(wx.Frame, self).Destroy()

    def CLI(self):
        self.__CLI(application=self)
    
    class __CLI(wx.Frame):

        # application

        def __init__(self, application=None, *args, **kwargs):
            self.application = application
            wx.Frame.__init__(self, None, *args, **kwargs)
            self.Bind(wx.EVT_CLOSE, lambda x: self.Destroy())
            #self.Show()
            import sys

            def val (key):
                if key in sys.argv:
                    return sys.argv[sys.argv.index('-t')+1]
                else:
                    return None
                
            def is_yaml (filename):
                ext = '.yaml'
                return filename[-len(ext):] == ext
                
            template_file = val('-t')
            content_file = val('-c')
            kb_file = val('-k')
            scan_file = val('-s')
            report_file = val('-r')

            if template_file and report_file:
                report = Report()
                report.template_load_xml(template_file)
                if content_file:
                    if is_yaml(content_file):
                        report.content_load_yaml(content_file)
                    else:
                        report.content_load_json(content_file)
                if kb_file:
                    if is_yaml(kb_file):
                        report.kb_load_yaml(kb_file)
                    else:
                        report.kb_load_json(kb_file)
                if scan_file:
                    report.scan = Scan(scan_file)                
                report.xml_apply_meta(vulnparam_highlighting=self.report.self.menu_view_v.IsChecked())
                report.save_report_xml(report_file)
            else:
                print 'Usage: '
                print
                print '    '+self.application.title+'.exe'
                print '        start GUI application'
                print
                print '    '+self.application.title+'.exe -t template-file [-c content-file] [-k kb-file] [-s scan-file] -r report-file'
                print '        generate report'
                print
                print '    '+self.application.title+'.exe [any other arguments]'
                print '        display usage and exit'
            
            self.Close()

        def Destroy(self):
            #print 'destroying CLI'
            super(wx.Frame, self).Destroy()

    # GUI class

    def __init__(self):
        #wx_app = wx.App (redirect=False) # DEVELOPMENT
        wx_app = wx.App()
        #self.TextWindow(None, title='asdasd', content='bsdsdasd')
        import sys
        #sys.argv = [sys.argv[0], '--help']
        #sys.argv = [sys.argv[0], '-t', 'asdad']
        if len(sys.argv) > 1:
            self.CLI()
        else:
            self.MainWindow()
        wx_app.MainLoop()


if __name__ == '__main__':
    GUI()
