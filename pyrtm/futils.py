
class FortranNamelist(dict):
    """Dict that returns a Fortran Namelist when stringified.
    
    There's an initial header thing which has a purpose, but this class
    just accepts one, passed as a constructor. KISS.
    """
    entry_delimiter = ',\n '
    def __init__(self, blah):
        self.header = blah
    
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
