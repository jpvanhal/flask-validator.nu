"""
Flask-Validator.nu
------------------

Adds automatic HTML5 validation to Flask with the help of the Validator.nu_ 
service.
    
Links
`````

* `documentation <http://packages.python.org/Flask-Validator.nu>`_
* `development version
  <http://github.com/jpvanhal/flask-validatornu/zipball/master#egg=Flask-Validator.nu-dev>`_

.. _Validator.nu: http://validator.nu/

"""
from setuptools import setup


setup(
    name='Flask-Validator.nu',
    version='0.1',
    url='https://github.com/jpvanhal/flask-validatornu',
    license='BSD',
    author='Janne Vanhala',
    author_email='janne.vanhala@gmail.com',
    description='Adds automatic HTML5 validation to Flask through Validator.nu',
    long_description=__doc__,
    packages=[
        'flaskext',
        'flaskext.validatornu',
    ],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'httplib2',
        'Pygments'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
