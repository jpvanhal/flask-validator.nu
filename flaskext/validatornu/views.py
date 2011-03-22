# -*- coding: utf-8 -*-
"""
    flaskext.validatornu.views
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2011 by Janne Vanhala.
    :license: BSD, see LICENSE for more details.
"""
import os

from flask import Module
from flask.helpers import send_from_directory


module = Module(__name__, name='validatornu')
static_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), 'static'))


@module.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory(static_dir)