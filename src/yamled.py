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

from resources.yamled import icon


class YamledWindow(wx.Frame):

    #parent
    #icon
    ##gray
    ##white
    #splitter
    #left
    #tree
    #item_height
    #stack
    #t
    #n
    #stack_sizer
    ##scroll_spin

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
                    
    def __init__(self, parent=None, title='', yaml=None, size=(800, 600,), *args, **kwargs):
        wx.Frame.__init__(self, parent, title='Yamled', size=size, *args, **kwargs)
        self.parent = parent
        # icon
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
        #menu_file.AppendSeparator()
        menu_file.Append(wx.ID_EXIT, 'E&xit\tCtrl+Q', 'Exit application')
        self.Bind(wx.EVT_MENU, self.__Exit, id=wx.ID_EXIT)
        menu.Append(menu_file, '&File')
        self.SetMenuBar(menu)
        # Layout
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        #def splitter_dclick(e):
        #    e.Veto()
        #self.Bind(wx.EVT_SPLITTER_DCLICK, splitter_dclick, self.splitter)
        self.splitter.SetMinimumPaneSize(80)
        #self.gray = self.splitter.GetBackgroundColour()
        self.left = wx.Panel(self.splitter, style=wx.BORDER_SIMPLE)
        self.tree = wx.TreeCtrl(self.left, style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_MULTIPLE|wx.BORDER_NONE)
        #self.scroll_spin = False
        def splitter_repaint(e):
            self.__tree_adjust()
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
        node = self.tree.AppendItem(self.root, '')
        self.item_height = self.tree.GetBoundingRect(node)[-1]-1
        self.tree.Delete(node)
        del node
        # tree popupmenu
        self.tree_popupmenu = wx.Menu()
        self.tree_popupmenu_delnode = self.tree_popupmenu.Append(-1, 'Delete node')
        self.Bind(wx.EVT_MENU, self.__tree_OnPopupMenu_DelNode, self.tree_popupmenu_delnode)
        #for i in 'one two three four five'.split():
        #    item = self.tree_popupmenu.Append(-1, i)
        #    self.Bind(wx.EVT_MENU, self.__tree_OnPopupMenuItem, item)
        self.tree.Bind(wx.EVT_CONTEXT_MENU, self.__tree_OnPopupMenu)
        def tree_empty_popupmenu(e):
            if self.tree.GetCount() == 0:
                self.__tree_OnPopupMenu(e)
        self.tree.Bind(wx.EVT_RIGHT_DOWN, tree_empty_popupmenu)
        #for i in range(50):
        #    self.n += [self.tree.AppendItem(self.root, str(i+1))]
        #    ctrl = self.yTextCtrl(self.stack, self, size=(-1, self.item_height), style=wx.BORDER_NONE)
        #    self.stack_sizer.Add(ctrl, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        #    ctrl.SetValue(str(i+1))
        #    self.t += [ctrl]
        #    del ctrl
        #self.AppendNode('abc','def',dict(a=2))
        #self.AppendNode('cgi','har',dict(a='frai'))
        for i in range(1,50):
            self.AppendNode(str(i),str(i))
        self.Load(yaml)
        #self.tree.ExpandAll()
        # show
        self.CenterOnScreen()
        self.Show()
        self.SetMinSize(tuple(map(lambda x: x*2/3, self.GetSize())))
        self.Bind(wx.EVT_SIZE, self.__OnResize, self)
        self.Bind(wx.EVT_PAINT, self.__OnRepaint, self)
        #self.__tree_adjust()
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

    def Load(self, yaml):
        if yaml == None:
            return
        pass
    
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

    #def __tree_OnPopupMenuItem(self, e):
    #    item = self.tree_popupmenu.FindItemById(e.GetId())
    #    text = item.GetText()
    #    wx.MessageBox("You selected item '%s'" % text)

    def __tree_OnPopupMenu_DelNode(self, e):
        pass

    def __tree_OnPopupMenu(self, e):
        #self.tree_popupmenu_delnode.SetText('Delete nodes')
        pos = e.GetPosition()
        if self.tree.GetCount() == 0:
            pos += self.splitter.GetScreenPosition()
        pos = self.tree.ScreenToClient(pos)
        self.tree.PopupMenu(self.tree_popupmenu, pos)
    
    def __tree_OnScroll(self, e):
        #if self.scroll_spin == True:
        #    self.scroll_spin = False
        #    return
        pos = self.tree.GetScrollPos(wx.VERTICAL)
        self.stack.Scroll((-1, pos))

    def __stack_OnScroll(self, e):
        pos = self.stack.GetScrollPos(wx.VERTICAL)
        if pos < len(self.n):
            #self.scroll_spin = True
            self.tree.ScrollTo(self.n[pos])
       
    def __tree_adjust(self):
        self.tree.SetSize((self.left.GetSize()[0]+35, self.stack.GetSize()[1]))
        self.__stack_OnScroll(None)
        
    def __OnResize(self, e):
        self.__tree_adjust()
        e.Skip()

    def __OnRepaint(self, e):
        self.__tree_adjust()

    def __Exit(self, e):
        self.Close()

if __name__ == '__main__':
    wx_app = wx.App(redirect=True) # redirect in wxpython 3.0 defaults to False
    YamledWindow()
    wx_app.MainLoop()
