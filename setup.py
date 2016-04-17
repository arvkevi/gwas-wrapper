# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(name='gwas_wrapper',
	  version='0.1',
	  description='Python wrapper for interacting with the NHGRI-EBI GWAS Catalog',
	  license='MIT',
	  keywords=['gwas', 'genomics', 'snp', 'bioinformatics'],
	  classifiers=[
		'Programming Language :: Python :: 2.7',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
		],
	  author='Kevin Arvai',
	  author_email='arvkevi@gmail.com',
	  download_url = 'https://github.com/arvkevi/gwas_wrapper/tarball/0.1',
	  url = 'https://github.com/arvkevi/gwas_wrapper',
	  packages=['gwas_wrapper'],
	  zip_safe=False)
