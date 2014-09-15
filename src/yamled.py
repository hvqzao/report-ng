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

from resources.yamled import icon


class YamledWindow(wx.Frame):

    #icon

    class YamlEdTree(wx.TreeCtrl):

        pass
        
    def __init__(self, parent=None, title='', yaml=None, size=(800, 600,), *args, **kwargs):
        wx.Frame.__init__(self, parent, title='Yamled', size=size, *args, **kwargs)

        myStream = cStringIO.StringIO(base64.b64decode(icon))
        myImage = wx.ImageFromStream(myStream)
        myBitmap = wx.BitmapFromImage(myImage)
        self.icon = wx.EmptyIcon()
        self.icon.CopyFromBitmap(myBitmap)
        self.SetIcon(self.icon)
        
        self.parent = parent
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.tree = self.YamlEdTree(splitter)
        pan2 = wx.Window(splitter) #style=wx.BORDER_SUNKEN
        box = wx.BoxSizer(wx.HORIZONTAL)
        t2 = wx.TextCtrl(pan2, style=wx.TE_MULTILINE|wx.TE_READONLY)
        box.Add(t2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND)
        pan2.SetSizer(box)
        box.Fit(pan2)
        splitter.SplitVertically(self.tree, pan2, 300)

        item_A = self.tree.AddRoot('A')
        item_AA = self.tree.AppendItem(item_A, 'AA')
        item_AAA =self.tree.AppendItem(item_AA, 'AAA')
        item_AB = self.tree.AppendItem(item_A, 'AB')
        self.tree.ExpandAll()
        
        self.CenterOnScreen()
        self.Show()

if __name__ == '__main__':
    wx_app = wx.App(redirect=True) # redirect in wxpython 3.0 defaults to False
    YamledWindow()
    wx_app.MainLoop()
