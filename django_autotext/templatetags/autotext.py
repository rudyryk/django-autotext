# -*- coding: utf-8 -*-

import re
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django_autotext import formatter

AUTOTEXT_EXPAND_OPEN = getattr(settings, 'AUTOTEXT_EXPAND_OPEN', '(+++')
AUTOTEXT_EXPAND_CLOSE = getattr(settings, 'AUTOTEXT_EXPAND_CLOSE', ')')

def do_autotext(parser, token):
    """
    Block tag for 
    
    Examples
    --------
    
        {# full text #}
        {% autotext %}{{ content }}{% endautotext %}
        
        {# shorten text with read more link #}
        {% autotext %}{{ content }}{% expandlink %}<a href="[expand url]">{{ expandlink }}</a>{% autotext %}
    
    """
    endtoken = 'end%s' % list(token.split_contents())[0]
    expandtoken = 'expandlink'
    nodelist = parser.parse((expandtoken, endtoken,))
    token = parser.next_token()
    if token.contents == expandtoken:
        bits = token.split_contents()
        nodelist_expand = parser.parse((endtoken,))
        parser.delete_first_token()
    else:
        nodelist_expand = None
    return AutotextNode(nodelist, nodelist_expand)

class AutotextNode(template.Node):
    def __init__(self, nodelist, nodelist_expand=None):
        self.nodelist = nodelist
        self.nodelist_expand = nodelist_expand
    
    def filter_cut_mark(self, context, output):
        """
        Remove 'read more' mark from output, replace by link
        if self.nodelist_expand is defined.
        """
        split_start = output.find(AUTOTEXT_EXPAND_OPEN)
        split_end = output.find(AUTOTEXT_EXPAND_CLOSE, split_start)
        if split_start >= 0 and split_end >= 0:
            shorted = output[:split_start]
            if self.nodelist_expand is None:
                output = shorted + output[split_end+1:]
            else:
                context.update({'expandlink': output[split_start+len(AUTOTEXT_EXPAND_OPEN):split_end]})
                output = shorted + self.nodelist_expand.render(context)
                context.pop()
        return output
    
    def render(self, context):
        autoescape_ = context.autoescape
        context.autoescape = False
        
        output = self.filter_cut_mark(context, self.nodelist.render(context))
        output = mark_safe(formatter.run(output, context))
        
        context.autoescape = autoescape_
        
        return output

register = template.Library()

register.tag('autotext', do_autotext)