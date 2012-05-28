
class FortranNamelist(dict):
    """Dict that returns a Fortran Namelist when stringified.
    
    There's an initial header thing which has a purpose, but this class
    just accepts one, passed as a constructor. KISS.
    """
    entry_delimiter = ',\n '
    def __init__(self, block):
        super(FortranNamelist, self).__init__()
        self.header = block
    
    def __str__(self):
        from collections import Iterable
        out = '$' + self.header + '\n '
        out += self.entry_delimiter.join(
            '%s = %s' % (key,
                value if not isinstance(value, Iterable) or
                    isinstance(value, str)
                else ', '.join(map(str, value)))
            for key, value in self.items()
        )
        out += '\n$END'
        return out
    
    def __repr__(self):
        return 'Fortran Namelist dict thing - ' + self.header


class group_property(property):
    def __get__(self, obj, objtype=None):
        return super(group_property, self).__get__(obj.config, objtype)

    def __set__(self, obj, value):
        super(group_property, self).__set__(obj.config, value)

    def __delete__(self, obj):
        return super(group_property, self).__del__(obj.config)


def config_meta(classname, parents, attrs):
    defaults = {}
    groups = {}
    newattrs = {'defaults':defaults, 'groups':groups}
    for name, value in attrs.items():
        if name.startswith('__'):
            newattrs[name] = value
        elif isinstance(value, type):
            groups[name] = value
        else:
            defaults[name] = value
    def init(self):
        for name, value in defaults.items():
            self.__dict__[name] = value
        for name, value in groups.items():
            group = value()
            group.config = self
            self.__dict__[name] = group
    newattrs['__init__'] = init
    return type(classname, parents, newattrs)


class Conf(object):
    def __repr__(self):
        return str(self.__dict__)


def instantiator(cls):
    return cls()
