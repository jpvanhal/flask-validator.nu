# -*- coding: utf-8 -*-
"""
    flaskext.validatornu
    ~~~~~~~~~~~~~~~~~~~~

    Adds automatic HTML5 validation to Flask with the help of the Validator.nu_ 
    service.
    
    .. _Validator.nu: http://validator.nu/

    :copyright: (c) 2011 by Janne Vanhala.
    :license: BSD, see LICENSE for more details.
"""
import gzip
import StringIO

from flask import json, request, url_for
from httplib2 import Http
from jinja2 import Environment, PackageLoader
from werkzeug import url_encode

from flaskext.validatornu.views import module
from flaskext.validatornu.pygmentsext import PygmentsExtension


class ValidationMessage(object):
    def __init__(self, data):
        self.data = data

    @property
    def type(self):
        if 'subType' in self.data:
            return self.data['subType']
        else:
            return self.data['type']

    @property
    def is_error(self):
        return self.type == 'error'

    @property
    def is_warning(self):
        return self.type == 'warning'


class ValidatorServiceConnectionRefused(Exception):
    def __init__(self, url):
        message = 'Could not connect to the validation service at %s' % url
        Exception.__init__(self, message)


class ValidatorNu(object):
    DEFAULT_AUTOMATIC_VALIDATION = True
    DEFAULT_CONTENT_TYPES = ('text/html', 'application/xml+xhtml')
    DEFAULT_SERVICE_URL = 'http://localhost:8888'

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

        self._jinja_env = Environment(
            autoescape=True, 
            extensions=[PygmentsExtension],
            loader=PackageLoader(__name__, 'templates')
        )

    def init_app(self, app):
        self.app = app

        app.config.setdefault('VALIDATOR_NU_AUTOMATIC_VALIDATION',
                              self.DEFAULT_AUTOMATIC_VALIDATION)
        app.config.setdefault('VALIDATOR_NU_CONTENT_TYPES',
                              self.DEFAULT_CONTENT_TYPES)
        app.config.setdefault('VALIDATOR_NU_SERVICE_URL',
                              self.DEFAULT_SERVICE_URL)

        if app.config['VALIDATOR_NU_AUTOMATIC_VALIDATION']:
            app.register_module(module, url_prefix='/_validator.nu')
            app.after_request(self.after_request)

    def _render_template(self, template_name, **context):
        template = self._jinja_env.get_template(template_name)
        return template.render(**context)
        
    def _should_validate(self, response):
        return response.mimetype in self.app.config['VALIDATOR_NU_CONTENT_TYPES']

    def _filter_validator_messages(self, messages):
        return [message for message in messages if message.is_error or 
                                                   message.is_warning]

    def validate(self, document, content_type='text/html', encoding='utf8'):
        headers = {
            'Content-Type': content_type,
            'Content-Encoding': 'gzip'
        }
        params = {
            'out': 'json', 
            'encoding': encoding
        }
        url = '%s?%s' % (self.app.config['VALIDATOR_NU_SERVICE_URL'],
                         url_encode(params))

        stream = StringIO.StringIO()
        gzipper = gzip.GzipFile(fileobj=stream, mode='wb')
        gzipper.write(document)
        gzipper.close()
        body = stream.getvalue()

        http = Http()
        try:
            response, content = http.request(url, method='POST', body=body, 
                                             headers=headers)
        except AttributeError:
            # httplib2 raises AttributeError if server refuses the connection:
            # http://code.google.com/p/httplib2/issues/detail?id=62
            raise ValidatorServiceConnectionRefused(
                self.app.config['VALIDATOR_NU_SERVICE_URL'])

        result = json.loads(content)
        messages = [ValidationMessage(message) for message in result['messages']]
        
        return self._filter_validator_messages(messages)

    def validate_response(self, response):
        if not self._should_validate(response):
            return []

        return self.validate(document=response.data,
                             content_type=response.mimetype,
                             encoding=response.mimetype_params['charset'])

    def after_request(self, response):
        messages = self.validate_response(response)
        
        if not messages:
            return response
        
        num_errors = sum(1 for message in messages if message.is_error)
        num_warnings = sum(1 for message in messages if message.is_warning)

        return self.app.make_response(self._render_template('base.html',
            messages=messages, num_errors=num_errors, num_warnings=num_warnings,
            url=request.url, source=response.data, url_for=url_for))
