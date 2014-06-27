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


from collections import OrderedDict
import yaml
import yaml.representer
import yaml.resolver


class UnsortableList(list):
    def sort(self, *args, **kwargs):
        pass


class UnsortableOrderedDict(OrderedDict):
    def items(self, *args, **kwargs):
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))


yaml.add_representer(UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)
yaml.add_representer(unicode, lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:str', value))


def yaml_load(stream, Loader=yaml.Loader, object_pairs_hook=UnsortableOrderedDict):
    class MyLoader(Loader):
        pass

    # use UnsortableOrderedDict
    MyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                             lambda loader, node: object_pairs_hook(loader.construct_pairs(node)))
    # treat str as unicode

    def construct_yaml_str(self, node):
        return self.construct_scalar(node)

    MyLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
    return yaml.load(stream, MyLoader)
