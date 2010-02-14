# -*- coding: utf-8 -*-

"""
Utilities for adding context depended "autotext" macros. Macros are
found in text by pattern { [macro_name args,kwargs] }.

Defining macro
--------------

    from django_autotext import formatter
    def username_macro(context, *args, **kwargs):
        return context['user'].username
    formatter.add_macro('username', username_macro)

Placing macro in text
---------------------

    1. Simple:
    
        Hi, { username }! You are on page { pagetitle }.
    
    2. With arguments:
    
        { feed url=http://somesite/rss/feed }
        { thumb w=300,h=400 }

Processing text
---------------

    from django_autotext import formatter
    formatter.run(text)

"""

import re

__all__ = ['add_macro', 'run']

def add_macro(name, processor):
    """
    Register new autotext macro.
    """
    _formatter.processors[name] = processor

def run(text, context={}):
    """
    Expand registered autotext macros.
    """
    return _formatter.run(text, context)

macro_re = re.compile(r'{([^}]+)}')
macro_args_re = re.compile(r'\s*[^=]+=')
space_re = re.compile(r'\s+')

class Formatter(object):
    """
    Autotext macros manager.
    """
    
    def __init__(self):
        self.processors = {}
    
    def run(self, text, context):
        """
        Process end expand defined macros.
        """
        new_lines = []
        for line in text.splitlines(True):
            matches = macro_re.finditer(line)
            (start, end) = (0, 0)
            for m in matches:
                end = m.start()
                new_lines.append(line[start:end] + self._expand_macro(m, context))
                start = m.end()
            new_lines.append(line[start:])
        return u''.join(new_lines)
    
    def _parse_macro_args(self, args):
        """
        Parse macro arguments.
        """
        largs, kwargs = [], {}
        if args:
            for arg in re.split(r'(?<!\\),', args):
                arg = arg.replace(r'\,', ',')
                m = macro_args_re.match(arg)
                if m:
                    kw = str(arg[:m.end()-1].strip())
                    kwargs[kw] = arg[m.end():]
                else:
                    largs.append(arg)
        return largs, kwargs
    
    def _expand_macro(self, match, context):
        """
        Expand matched macro if defined. If not defined, return
        unchanged (empty?).
        """
        content = space_re.split(match.group(1).strip(), 1)
        macro = content[0]
        if self.processors.has_key(macro):
            args, kwargs = self._parse_macro_args(len(content) > 1 and content[1] or '')
            return self.processors[macro](context, *args, **kwargs)
        return match.group(0)

_formatter = Formatter()
