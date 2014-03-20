import os
from setuptools import setup

base = os.path.normpath(os.path.dirname(__file__))
os.chdir(base)

userjs = __import__('userjs')
description = userjs.__doc__.strip()

if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = description

version = userjs.__version__

setup(
    name='django-userjs',
    version=version,
    packages=['userjs'],
    install_requires=['six'],
    include_package_data=True,
    license='BSD',
    description=description,
    long_description=README,
    url='https://github.com/tweekmonster/django-userjs',
    author='Tommy Allen',
    author_email='tommy@tweek.us',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)
