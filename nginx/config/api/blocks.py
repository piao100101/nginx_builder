
from .base import Base
from .options import AttrDict, AttrList, KeyOption, KeyValueOption, KeyMultiValueOption,KeyValuesMultilines

# from helpers import duplicate_options

class Block(Base):
    """ A block represent a named section of an Nginx config, such as 'http', 'server' or 'location'

    Using this object is as simple as providing a name and any sections or options,
    which can be other Block objects or option objects.

    Example::

        >>> from nginx.config.api import Block
        >>> http = Block('http', option='value')
        >>> print(http)

            http {
                option value;
            }


    """
    def __init__(self, name,order_args=None,*sections, **options):
        """ Creates a block.
        
        Sections should be config objects such as Block or EmptyBlock,
        Options can be any key/value pair (such as worker_connections=512, etc)

        :param name str: The name of the block.
        """
        self.name = name
        self.order_args = order_args
        self.sections = AttrList(self)
        self.options = AttrDict(self)
        self._set_directives(order_args,*sections, **options)

    @property
    def _directives(self):
        
        if isinstance(self.sections, tuple):
           dirs = self._dump_options() + list(self.sections)
        else:
           dirs = self._dump_options() + self.sections.values()
        return [directive for directive in dirs if directive is not self]

    def _set_directives(self,order_args, *sections, **options):
        if order_args:
            self.sections = sections
        else:
            for section in sections:
                self.sections.append(section)
        
      
        for key, value in options.items():
            self.options[key]=value
          


    def _build_options(self, key, value):
        if isinstance(value, Block):
            option = value
        elif isinstance(value, list):
            option = KeyValuesMultilines(key, value)
        elif value is None or value == '':
            option = KeyOption(key)
        else:
            if isinstance(value, str) and ' ' in value:
                option = KeyMultiValueOption(key, value=value.split())
            else:
                option = KeyValueOption(key, value=value)
                
        return option

    def _dump_options(self):
        
            return [self._build_options(key, value) for key, value in self.options.items()]

    def __repr__(self):
        directives = self._directives
        for directive in directives:
            
            if directive is not self:
                directive._indent_level = self._indent_level + 1

        return '\n{indent}{name}{{{directives}\n{indent}}}'.format(
            name='{0} '.format(self.name),
            directives=''.join([repr(e) for e in directives]),
            indent=self._get_indent(),
        )


class EmptyBlock(Block):
    """ An unnamed block of options and/or sections.

    Empty blocks are useful for representing groups of options.

    For example, you can use them to represent options with non-unique keys:

    Example::

        >>> from nginx.config.helpers import duplicate_options
        >>> dupes = duplicate_options('key', ['value', 'other_value', 'third_value'])
        >>> type(dupes)
        nginx.config.api.blocks.EmptyBlock
        >>> print(dupes)

        key third_value;
        key value;
        key other_value;


    """
    def __init__(self, order_args=None,*sections, **options):
        """ Create an EmptyBlock. """
      
        self.sections = AttrList(self)
        self.options = AttrDict(self)

        self._set_directives(order_args,*sections, **options)

    def __repr__(self):
        directives = self._directives

        for directive in directives:
            directive._indent_level = self._indent_level

        return ''.join([repr(o) for o in directives])


class Location(Block):
    """ A Location is just a named block with "location" prefixed """
    def __init__(self, location, *args, **kwargs):
        super(Location, self).__init__('location {0}'.format(location), *args, **kwargs)

class Map(Block):
    """ A map is just a named block with "map" prefixed """
    def __init__(self, mapping, *args, **kwargs):
        super(Map, self).__init__('map {0}'.format(mapping), *args, **kwargs)
