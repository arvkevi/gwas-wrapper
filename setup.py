# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(name='gwas_wrapper',
	  version='0.1',
	  description='Python wrapper for interacting with the NHGRI-EBI GWAS Catalog',
	  url='http://github.com/arvkevi/gwas_wrapper',
	  license='MIT',
	  keywords='gwas genomics snp bioinformatics',
	  classifiers=[
		'Programming Language :: Python :: 2.7',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
		],
	  author='Kevin Arvai',
	  author_email='arvkevi@gmail.com',
	  packages=['gwas_wrapper'],
	  zip_safe=False)
