from distutils.core import setup

with open('README.rst') as description:
    long_description = description.read()

setup(
    name='django-bitmask-field',
    version='0.1.3',
    author='Rinat Khabibiev',
    author_email='srenskiy@gmail.com',
    py_modules=['django_bitmask_field'],
    url='https://github.com/renskiy/django-bitmask-field',
    license='MIT',
    description='BitmaskField implementation for Django ORM',
    long_description=long_description,
    install_requires=[
        'six>=1.16.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Operating System :: OS Independent',
        'Topic :: Database',
    ],
)
