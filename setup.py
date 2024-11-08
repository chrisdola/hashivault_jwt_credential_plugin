#!/usr/bin/env python

from setuptools import setup

requirements = ["jwt"]  # add Python dependencies here
# e.g., requirements = ["PyYAML"]

setup(
    name='hashivault_jwt_credential_plugin',
    version='0.6',
    author='Chris LaMendola',
    author_email='clamendola1992@gmail.com',
    description='',
    long_description='',
    license='Apache License 2.0',
    keywords='ansible',
    url='https://github.com/chrisdola/hashivault_jwt_credential_plugin',
    packages=['hashivault_jwt_credential_plugin'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[],
    install_requires=requirements,
    entry_points = {
        'awx.credential_plugins': [
            'hashivault_jwt_credential_plugin = hashivault_jwt_credential_plugin:hashivault_jwt_credential_plugin',
        ]
    }
)
