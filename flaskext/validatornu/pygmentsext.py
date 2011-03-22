# -*- coding: utf-8 -*-
"""
    flaskext.validatornu.pygmentsext
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds 'code' block to Jinja2_ that highlights code with the help of 
    Pygments_.
    
    .. _Jinja2: http://jinja.pocoo.org/
    .. _Pygments: http://pygments.org/

    :copyright: (c) 2011 by Janne Vanhala.
    :license: BSD, see LICENSE for more details.
"""
from jinja2 import nodes
from jinja2.ext import Extension
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter


class PygmentsExtension(Extension):
    tags = set(['code'])

    def __init__(self, environment):
        super(PygmentsExtension, self).__init__(environment)

    def parse(self, parser):
        # the first token is always 'code'
        lineno = parser.stream.next().lineno

        args = []
        language = parser.parse_expression()
        if language is not None:
            args.append(language)

        body = parser.parse_statements(['name:endcode'], drop_needle=True)

        return nodes.CallBlock(self.call_method('_highlight', args),
                               [], [], body).set_lineno(lineno)

    def _highlight(self, language, caller):
        code = caller()
        
        if language is None:
            lexer = guess_lexer(code)
        else:
            lexer = get_lexer_by_name(language)
        
        formatter = HtmlFormatter(linenos='inline', lineanchors='line')
        
        return highlight(code.unescape(), lexer, formatter)
