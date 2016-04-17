# -*- coding: utf-8 -*-

import urlparse, types
from urllib import urlencode
from urllib2 import urlopen
import json

class GWAS(object):
    """
    A simple Python wrapper for the GWAS Catalog API.
    GWAS Catalog API:  https://www.ebi.ac.uk/gwas/home
    
    The GWAS Catalog API is currently under active development and there is
    no official documentation.
    
    If you use data from the GWAS Catalog, please follow citation guidelines:
    https://www.ebi.ac.uk/gwas/docs/about
    
    Welter D, MacArthur J, Morales J, Burdett T, Hall P, Junkins H, Klemm A,
    Flicek P, Manolio T, Hindorff L, and Parkinson H.
    The NHGRI GWAS Catalog, a curated resource of SNP-trait associations.
    Nucleic Acids Research, 2014, Vol. 42 (Database issue): D1001-D1006.
    """
    
    def __init__(self):
        
        BASE_URL = 'http://www.ebi.ac.uk/gwas/api/'
        self.BASE_URL = BASE_URL
        self.search_url = BASE_URL + 'search/moreresults'
    
    def search(self, query, **kwargs):
        """
        To get unfiltered snp associations in a raw json format:
        >>> from gwas_wrapper import GWAS
        >>> GWAS().search('baldness')
        
        **kwargs handles the additional filtering parameters:
        >>> GWAS().search('baldness', max_results=100, pvalfilter='5e-10')
        
        Default kwargs (other valid values):
        max_results= 600 (100)
        facet= 'association' 
        pvalfilter= '5e-8' ('5e-50')
        orfilter= '' (2.0)
        betafilter= '' 
        datefilter= ''
        sort= ''
        asc= ''
        
        The only facet that I have successfully returned results with is
        'association'.  I've also tried 'studies' and 'catalog traits'
        but without success.
        """
        
        query_params = (
            ('q', query),
            ('max', kwargs.pop('max_results', 600)),
            ('facet', kwargs.pop('facet', 'association')),
            ('pvalfilter', kwargs.pop('pvalfilter', '5e-8')),
            ('orfilter', kwargs.pop('orfilter', '')),
            ('betafilter', kwargs.pop('betafilter', '')),
            ('datefilter', kwargs.pop('datefilter', '')),
            ('sort', kwargs.pop('sort', '')),
            ('asc', kwargs.pop('asc', ''))
        )

        query_params = [(param[0], param[1].encode('utf-8')
                         if type(param[1]) is types.UnicodeType
                         else param[1]) for param in query_params]
                             
        query_string = urlencode(query_params)
        query_string = '{0}?{1}'.format(self.search_url, query_string)
        
        request = urlopen(query_string)
        results = request.read()
        
        return json.loads(results)
        
    def snp_list(self, raw_results):
        """
        Returns a list of tuples with the SNP rsID and the risk allele.
        >>> GWAS().snp_list(raw_results)
        [('rs2497938, 'T'), ('rs6047844', 'T'), ('rs2497938', 'n/a'), ...]
        """
        raw_results = self.byteify(raw_results)
        
        snp_list = []
        for snp in raw_results["response"]["docs"]:
            try:
                snp_list.append((snp["rsId"][0],
                                 snp["strongestAllele"][0].split('-')[1]))
            except IndexError:
                snp_list.append((snp["rsId"][0], 'n/a'))
    
        return snp_list
    
    def parse_snps(self, raw_results, **kwargs):
        """
        parse_snps() transforms the object returned from the search function
        into a more useable nested dictionary format.  The top level keys are
        rsIDs, the second level keys are the risk allele.
        
        The first argument, raw_results, is the object returned
        from the search function.
        
        The keyword argument, parse_type, must be one of two keyword arguments:
        'all', or 'custom'
        
        parse_type='all' retains all the original information
        >>> GWAS().parse_snps(raw_results, parse_type='all')
        
        'rs2497938': {  'T': {  '_version_': 1531216814503100416,
                                     'ancestralGroups': ['European'],
                                     'ancestryLinks': [  'initial|Germany,...],
                                     'author': ['Li R'],
                                     'author_s': 'Li R',
                                     ...
                            ...
        
        parse_type='custom' allows the user to pass a list of
        attributes to be included.  
        >>> GWAS().parse_snps(raw_results, parse_type='custom',
                             custom_attr=['orPerCopyNum', 'riskFrequency'])
        
        {'rs10502861': {'C': {'orPerCopyNum': 1.28, 'riskFrequency': '0.775'}},
         'rs1160312': {'A': {'orPerCopyNum': 1.6, 'riskFrequency': '0.43'}},
        """
        raw_results = self.byteify(raw_results)
        
        # default parse_type
        parse_type = kwargs.pop('parse_type', 'all')
        
        # default snp info for parse_type='custom'
        custom_attr = kwargs.pop('custom_attr',
                                 ['orPerCopyNum','riskFrequency'])
        
        # return nested dict
        snp_dict = {}
        for snpObj in raw_results["response"]["docs"]:
            try:
                rsID, ra = (str(snpObj["rsId"][0]),
                          str(snpObj["strongestAllele"][0].split('-')[1]))
            except IndexError:
                rsID, ra = (snpObj["rsId"][0], 'n/a')
            
            # top-level key is the rsID
            if rsID not in snp_dict:
                snp_dict[rsID] = {}
            
            # second-level key is the risk allele
            if parse_type == 'all':    
                snp_dict[rsID][ra] = snpObj
            
            elif parse_type == 'custom':
                snp_dict[rsID][ra] = {}
                for attr in custom_attr:
                    # assign attributes if present
                    if attr in snpObj:
                        snp_dict[rsID][ra][attr] = snpObj[attr]
                    # assign n/a if attribute not present
                    else:
                        snp_dict[rsID][ra][attr] = 'n/a'

        return snp_dict
    
    def byteify(self, inpt):
        """
        Helper function, recursively keeps elements as strings.
        """
        if isinstance(inpt, dict):
            return {self.byteify( key): self.byteify(value)
                    for key, value in inpt.iteritems()}
        elif isinstance(inpt, list):
            return [self.byteify(element) for element in inpt]
        elif isinstance(inpt, unicode):
            return inpt.encode('utf-8')
        else:
            return inpt