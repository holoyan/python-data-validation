from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyva',
    packages=find_packages(),
    version='0.4',
    license='MIT',
    description='Simple and flexible python data validation library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Artak',
    author_email='artaksafaryanc@gmail.com',
    url='https://github.com/holoyan/python-data-validation',
    keywords=['data', 'validation', 'validator', 'data validator'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
