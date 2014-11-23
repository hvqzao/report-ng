# -*- coding: utf-8 -*-
# Yamled
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
import wx.lib.scrolledpanel as sp
import base64
import cStringIO
import yaml

from util import yaml_load, UnsortableOrderedDict
import util
from resources.yamled import icon
from version import Version


class YamledWindow(wx.Frame):

    #parent
    #icon
    ##gray
    ##white
    #menu_file_save_as
    #splitter
    #left
    #tree
    #item_height
    #stack
    #t
    #n
    #d
    #r
    #stack_sizer
    SPACER = '      '

    class yTextCtrl(wx.TextCtrl):

        def __init__(self, parent, frame, *args, **kwargs):
            self.frame = frame
            wx.TextCtrl.__init__(self, parent, *args, **kwargs)
            self.SetEditable(False)
            self.Bind(wx.EVT_MOUSE_EVENTS, self.__OnMouseEvent)
            self.Bind(wx.EVT_SET_FOCUS, self.__OnSetFocus)
            self.Bind(wx.EVT_KILL_FOCUS, self.__OnKillFocus)
            self.Bind(wx.EVT_LEFT_UP, self.__OnLeftUp)

        def tree_highlight(self, eid):
            items = filter(lambda x: x.GetId() == eid, self.frame.t)
            if items:
                pos = self.frame.t.index(items[0])
                #self.frame.tree.SetFocusedItem(self.frame.n[pos])
                self.frame.tree.UnselectAll()
                self.frame.tree.SelectItem(self.frame.n[pos])
        
        def __OnMouseEvent(self, e):
            pass
            #if self.frame.FindFocus() != self and e.Moving():
            #    self.SetCursor(wx.STANDARD_CURSOR)
                
        def __OnSetFocus(self, e):
            if not self.IsEditable():
                self.Navigate(wx.NavigationKeyEvent.IsForward)
            else:
                self.tree_highlight(e.GetId())
                e.Skip()
            
        def __OnKillFocus(self, e):
            self.SetEditable(False)
            e.Skip()

        def __OnLeftUp(self, e):
            focused = self.frame.FindFocus()
            if focused == self:
                pass
            elif type(focused) == type(self):
                self.SetFocus()
                self.frame.tree.UnselectAll()
            else:
                self.SetEditable(True)
                self.SetFocus()
                self.SetInsertionPointEnd()
            e.Skip()
                    
    def __init__(self, parent=None, title='', content=None, size=(800, 600,), *args, **kwargs):
        wx.Frame.__init__(self, parent, title='Yamled', size=size, *args, **kwargs)
        self.parent = parent
        self.application = Version()
        # icon
        myStream = cStringIO.StringIO(base64.b64decode(icon))
        myImage = wx.ImageFromStream(myStream)
        myBitmap = wx.BitmapFromImage(myImage)
        self.icon = wx.EmptyIcon()
        self.icon.CopyFromBitmap(myBitmap)
        self.SetIcon(self.icon)
        # tree image list
        #self.tree_image_list = wx.ImageList(16, 16)
        #self.dotlist = self.tree_image_list.Add(wx.Image('resources/dotlist.png', wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
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
        #menu_file_close = menu_file.Append(index.next(), '&Close')
        #self.Bind(wx.EVT_MENU, self.File_Close, id=index.current)
        self.menu_file_save_as = menu_file.Append(index.next(), '&Save As...')
        self.menu_file_save_as.Enable(False)
        self.Bind(wx.EVT_MENU, self.File_Save_As, id=index.current)
        menu_file.AppendSeparator()
        menu_file.Append(wx.ID_EXIT, 'E&xit\tCtrl+Q', 'Exit application')
        self.Bind(wx.EVT_MENU, self.__Exit, id=wx.ID_EXIT)
        menu.Append(menu_file, '&File')
        menu_help = wx.Menu()
        menu_help.Append(wx.ID_ABOUT, '&About')
        self.Bind(wx.EVT_MENU, self.About, id=wx.ID_ABOUT)
        menu.Append(menu_help, '&Help')
        self.SetMenuBar(menu)
        # Layout
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        #def splitter_dclick(e):
        #    e.Veto()
        #self.Bind(wx.EVT_SPLITTER_DCLICK, splitter_dclick, self.splitter)
        self.splitter.SetMinimumPaneSize(200)
        #self.gray = self.splitter.GetBackgroundColour()
        self.left = wx.Panel(self.splitter, style=wx.BORDER_SIMPLE)
        self.tree = wx.TreeCtrl(self.left, style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_MULTIPLE|wx.BORDER_NONE) #|wx.TR_NO_LINES
        #self.tree.AssignImageList(self.tree_image_list)
        def splitter_repaint(e):
            self._tree_adjust()
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, splitter_repaint, self.splitter)
        #self.splitter.Bind(wx.EVT_PAINT, splitter_repaint)
        #self.white = self.tree.GetBackgroundColour()
        #print self.stack.GetBackgroundColour() --> (240, 240, 240, 255)
        self.stack = sp.ScrolledPanel(self.splitter, style=wx.BORDER_SIMPLE)
        self.stack_sizer = wx.BoxSizer(wx.VERTICAL)
        self.stack.SetSizer(self.stack_sizer)
        self.stack.Layout()
        self.stack.SetupScrolling(scroll_x=False)
        self.stack_sizer.Fit(self.stack)
        self.splitter.SplitVertically(self.left, self.stack, 300)
        self.root = self.tree.AddRoot('')
        self.n=[]
        self.t=[]
        self.d=[]
        self.r=[]
        node = self.tree.AppendItem(self.root, '')
        self.item_height = self.tree.GetBoundingRect(node)[-1]-1
        self.tree.Delete(node)
        del node
        # tree popupmenu
        self.tree_popupmenu = wx.Menu()
        self.tree_popupmenu_delnode = self.tree_popupmenu.Append(-1, 'Delete node')
        self.Bind(wx.EVT_MENU, self.__tree_OnPopupMenu_DelNode, self.tree_popupmenu_delnode)
        self.tree_popupmenu.AppendSeparator()
        tree_popupmenu_collapse_all = self.tree_popupmenu.Append(-1, 'Collapse all')
        self.Bind(wx.EVT_MENU, self.__tree_OnPopupMenu_CollapseAll, tree_popupmenu_collapse_all)
        tree_popupmenu_expand_all = self.tree_popupmenu.Append(-1, 'Expand all')
        self.Bind(wx.EVT_MENU, self.__tree_OnPopupMenu_ExpandAll, tree_popupmenu_expand_all)
        self.tree.Bind(wx.EVT_CONTEXT_MENU, self.__tree_OnPopupMenu)
        def tree_empty_OnPopupMenu(e):
            if self.tree.GetCount() == 0:
                self.__tree_OnPopupMenu(e)
        self.tree.Bind(wx.EVT_RIGHT_DOWN, tree_empty_OnPopupMenu)
        #for i in range(50):
        #    self.n += [self.tree.AppendItem(self.root, str(i+1))]
        #    ctrl = self.yTextCtrl(self.stack, self, size=(-1, self.item_height), style=wx.BORDER_NONE)
        #    self.stack_sizer.Add(ctrl, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        #    ctrl.SetValue(str(i+1))
        #    self.t += [ctrl]
        #    del ctrl
        #self.AppendNode('abc','def',dict(a=2))
        #self.AppendNode('cgi','har',dict(a='frai'))
        #for i in range(1,50):
        #    self.AppendNode(str(i),str(i))
        if content != None:
            self.Load(content)
        self.tree.ExpandAll()
        #self._stack_adjust()
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.__tree_OnCollapse)
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.__tree_OnExpand)
        # show
        #self.SetDoubleBuffered(True)
        self.CenterOnScreen()
        self.Show()
        self.SetMinSize(tuple(map(lambda x: x*2/3, self.GetSize())))
        self.Bind(wx.EVT_SIZE, self.__OnResize, self)
        self.Bind(wx.EVT_PAINT, self.__OnRepaint, self)
        #self._tree_adjust()
        self.stack.SetScrollRate(16, self.item_height)
        self.tree.Bind(wx.EVT_PAINT, self.__tree_OnScroll)
        self.stack.Bind(wx.EVT_PAINT, self.__stack_OnScroll)
        #self.stack.Bind(wx.EVT_SCROLLWIN, self.__stack_OnScroll)
        def stack_focus_release(e):
            self.SetFocus()
            self.tree.UnselectAll()
        self.stack.Bind(wx.EVT_LEFT_UP, stack_focus_release)
        #self.t[2].Hide()
        #self.stack.Layout()
        #self.t[2].Show()
        #self.stack.Layout()
        #self.t[12].SetBackgroundColour(self.white)
        self.splitter.SetDoubleBuffered(True)
        #self.stack.SetBackgroundColour((240,255,255,255))
        #self.Extract()
            
    def Extract(self):
        #print
        #for i in range(len(self.n)):
        #    print self.tree.GetItemText(self.n[i]),  self.tree.ItemHasChildren(self.n[i]), self.d[i], isinstance(self.d[i], list)
        #print
        root = self.tree.GetRootItem()
        def walk(parent, listmode=False):
            stack = []
            struct = UnsortableOrderedDict()
            (item, cookie) = self.tree.GetFirstChild(parent)
            while item:
                name = self.tree.GetItemText(item)
                if name[:len(self.SPACER)] == self.SPACER:
                    name = name[len(self.SPACER):-1]
                else:
                    name = name[:-1]
                data = self.GetData(item)
                if self.tree.ItemHasChildren(item):
                    result = walk(item, isinstance(data, list))
                    if listmode:
                        struct[name] = data
                        for i in result.keys():
                            struct[i] = result[i]
                        stack += [struct]
                        struct = UnsortableOrderedDict()
                    else:
                        struct[name] = result
                else:
                    struct[name] = self.GetData(item)
                (item, cookie) = self.tree.GetNextChild(item, cookie)
            if listmode:
                return stack
            else:
                return struct
        #print walk(root)
        return walk(root)
    
    def Load(self, content):
        if content == None:
            return
        if isinstance(content, UnsortableOrderedDict):
            data = content
        else:
            data = yaml_load(open(content).read(), yaml.SafeLoader, UnsortableOrderedDict)
        #print data
        def walk(data, parent=None):
            if isinstance(data, UnsortableOrderedDict):
                for i in data:
                    item = self.AppendNode(i+':', '', None, parent)
                    if parent != None:
                        self.SetData(parent, UnsortableOrderedDict())
                    walk(data[i], item)
            elif isinstance(data, list):
                if isinstance(data[0], UnsortableOrderedDict):
                    keys = data[0].keys()
                    self.SetData(parent, keys)
                    for i in data:
                        if i.keys() != keys:
                            raise Exception('List keys differ!')
                        list_item = self.AppendNode(self.SPACER+keys[0]+':', '', None, parent)
                        #self.tree.SetPyData(list_item, None)
                        #self.tree.SetItemImage(list_item, self.dotlist) #, wx.TreeItemIcon_Normal)
                        walk(i[keys[0]], list_item)
                        for j in keys[1:]:
                            item = self.AppendNode(j+':', '', None, list_item)
                            walk(i[j], item)
            else:
                if parent != None:
                    self.SetValue(parent, data)
                    self.SetData(parent, data)
        walk(data)
        self.menu_file_save_as.Enable(True)

    def SetData(self, item, data):
        pos = self.n.index(item)
        self.d[pos] = data

    def SetValue(self, item, value):
        pos = self.n.index(item)
        if util.binary(value):
            value = util.binary_safe(value)
        value = unicode(value).split('\n')
        value = value[0]+['',' [...]'][len(value) > 1]
        self.t[pos].SetValue(unicode(value).split('\n')[0])

    def GetData(self, item):
        pos = self.n.index(item)
        return self.d[pos]
    
    def AppendNode(self, name, value, data=None, parent=None):
        if parent == None:
            parent = self.root
        item = self.tree.AppendItem(parent, name)
        self.n += [item]
        ctrl = self.yTextCtrl(self.stack, self, size=(-1, self.item_height), style=wx.BORDER_NONE)
        self.stack_sizer.Add(ctrl, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ctrl.SetValue(value)
        self.t += [ctrl]
        self.d += [data]
        self.r += [True]
        return item

    def DeleteNode(self, item):
        while self.tree.ItemHasChildren(item):
            (child, cookie) = self.tree.GetFirstChild(item)
            self.DeleteNode(child)
        pos = self.n.index(item)
        self.stack_sizer.Hide(self.t[pos])
        self.stack_sizer.Remove(self.t[pos])
        self.tree.Delete(self.n[pos])
        del self.n[pos]
        del self.t[pos]
        del self.d[pos]
        del self.r[pos]

    def _stack_adjust(self):
        # recalc items visiblity
        for i in range(len(self.n)):
            path = []
            item = self.n[i]
            while item != self.root:
                item = self.tree.GetItemParent(item)
                path += [item]
            self.r[i] = not bool(filter(lambda x: not self.tree.IsExpanded(x), path[:-1]))
            # update stack textctrls visibility
            if self.r[i]:
                self.t[i].Show()
            else:
                self.t[i].Hide()
        # update stack layout and height
        self.stack.Layout()
        self.stack.SetVirtualSize((-1, self.item_height*(len(filter(lambda x: x, self.r))-0)-0))
        #self.tree.Layout()
        
    def __tree_OnCollapse(self, e):
        #print e.GetItem()
        self._stack_adjust()

    def __tree_OnExpand(self, e):
        #print e.GetItem()
        self._stack_adjust()

    def __tree_OnPopupMenu_DelNode(self, e):
        for i in self.tree.GetSelections():
            self.DeleteNode(i)
        self._stack_adjust()

    def __tree_OnPopupMenu_CollapseAll(self, e):
        self.tree.CollapseAll()
        self._stack_adjust()

    def __tree_OnPopupMenu_ExpandAll(self, e):
        self.tree.ExpandAll()
        self._stack_adjust()

    def __tree_OnPopupMenu(self, e):
        if len(self.tree.GetSelections()) > 0:
            self.tree_popupmenu_delnode.Enable(True)
            if len(self.tree.GetSelections()) > 1:
                self.tree_popupmenu_delnode.SetText('Delete nodes')
            else:
                self.tree_popupmenu_delnode.SetText('Delete node')
        else:
            self.tree_popupmenu_delnode.SetText('Delete node')
            self.tree_popupmenu_delnode.Enable(False)
        #self.tree_popupmenu_delnode.Enable(False)
        pos = e.GetPosition()
        if self.tree.GetCount() == 0:
            pos += self.splitter.GetScreenPosition()
        pos = self.tree.ScreenToClient(pos)
        self.tree.PopupMenu(self.tree_popupmenu, pos)
    
    def __tree_OnScroll(self, e):
        pos = self.tree.GetScrollPos(wx.VERTICAL)
        self.stack.Scroll((-1, pos))

    def __stack_OnScroll(self, e):
        pos = self.stack.GetScrollPos(wx.VERTICAL)
        n_range = filter(lambda x: self.r[x], range(len(self.r)))
        if n_range:
            if pos in range(len(n_range)):
                self.tree.ScrollTo(self.n[n_range[pos]])
            else:
                self.tree.ScrollTo(self.n[n_range[0]])
        self.__tree_OnScroll(e)
        
    def _tree_adjust(self):
        self.tree.SetSize((self.left.GetSize()[0]+35, self.stack.GetSize()[1]))
        #self.__stack_OnScroll(None)
        
    def __OnResize(self, e):
        self._tree_adjust()
        for i in [False, True]:
            self.splitter.SetDoubleBuffered(i)
        e.Skip()

    def __OnRepaint(self, e):
        self._tree_adjust()

    def File_Close(self, e):
        pass

    def File_Save_As(self, e):
        openFileDialog = wx.FileDialog(self, 'Save Yaml As', '', '',
                                       'Yaml files (*.yaml)|*.yaml|All files (*.*)|*.*',
                                       wx.FD_SAVE | wx.wx.FD_OVERWRITE_PROMPT)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
        filename = openFileDialog.GetPath()
        h = open(filename, 'w')
        h.write(yaml.dump(self.Extract(), default_flow_style=False, allow_unicode=True).decode('utf-8').encode('utf-8'))
        h.close()

    def __Exit(self, e):
        self.Close()

    def About(self, e):
        dialog = wx.AboutDialogInfo()
        #dialog.SetIcon (wx.Icon('icon.ico', wx.BITMAP_TYPE_PNG))
        dialog.SetIcon(self.icon)
        #dialog.SetName(self.application.long_title+' - '+self.application.title)
        dialog.SetName('Yaml Editor - Yamled')
        dialog.SetVersion(self.application.version)
        dialog.SetCopyright(self.application.c)
        #dialog.SetDescription('\n'.join(map(lambda x: x[4:], self.application.about.split('\n')[1:][:-1])))
        dialog.SetDescription('Not yet functional')

        #dialog.SetWebSite(self.application.url)
        #dialog.SetLicence(self.application.license)
        wx.AboutBox(dialog)

def GUI():
    wx_app = wx.App(redirect=True) # redirect in wxpython 3.0 defaults to False
    #wx_app = wx.App(redirect=False)
    #YamledWindow(content='../../x.yaml')
    #YamledWindow(content='../../y.yaml')
    YamledWindow(content='../../z.yaml')
    #YamledWindow()
    wx_app.MainLoop()

if __name__ == '__main__':
    GUI()
