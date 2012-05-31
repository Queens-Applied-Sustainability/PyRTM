import threading
import subprocess


class FortranNamelist(dict):
    """Dict that returns a Fortran Namelist when stringified.
    
    Integers, floats, strings, and 1-dimensional arrays (lists or tupples, or,
    more accurately, any non-string itterable) should work as expected.
    
    This class currently can only handle one NAMELIST block for the file,
    despite the NAMELIST specification's ability to handle multiple blocks. Its
    name must be passed to the constructor.
    
    Use instances of this class like any other dict to hold stuff, and then just
    cast the object to a string to get the Fortran NAMELIST version out.
    
    This code works with a Fortran script that I compiled with gfortran. I
    could not find the actual fortran specifications for NAMELIST formatting
    anywhere, so your mileage may varry. If you know of these specs, please
    contact me -- uniphil@gmail.com.
    """
    entry_delimiter = ',\n '
    def __init__(self, block):
        super(FortranNamelist, self).__init__()
        self.header = block
    
    def __str__(self):
        from collections import Iterable
        out = '$' + self.header + '\n '
        #FIXME break the generator out into a loop. this is nuts.
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
    """
    Crazy magical python
    """
    def __get__(self, obj, objtype=None):
        return super(group_property, self).__get__(obj.config, objtype)

    def __set__(self, obj, value):
        super(group_property, self).__set__(obj.config, value)

    def __delete__(self, obj):
        return super(group_property, self).__del__(obj.config)


def config_meta(classname, parents, attrs):
    """
    Make this class do cool stuff.
    
    Adapted from suggestions I recieved on StackOverflow, see
    http://stackoverflow.com/a/10746986/1299695.
    
    Still not perfect; working on it.
    """
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
    

def underline(string):
    return '\n %s\n %s' % (string, '-'*len(string))


def popenAndCall(onExit, *popenArgs, **popenKWArgs):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that 
    would give to subprocess.Popen.
    """
    def runInThread(onExit, popenArgs, popenKWArgs):
        proc = subprocess.Popen(*popenArgs, **popenKWArgs)
        proc.wait()
        onExit()
        return
    thread = threading.Thread(target=runInThread, args=(onExit, popenArgs, popenKWArgs))
    thread.start()
    # returns immediately after the thread starts
    return thread


