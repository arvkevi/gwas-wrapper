# gwas_wrapper
`gwas_wrapper` is a lightweight Python wrapper designed to interact with the [GWAS Catalog](https://www.ebi.ac.uk/gwas/home) API.  As mentioned on their [help page](https://www.ebi.ac.uk/gwas/docs/programmatic-access), the GWAS Catalog API is under active development and no official documentation yet exists.  There are two intended purpose for `gwas_wrapper`:

   1.  Quick and flexible (programmatic) access to SNP (single nucleotide polymorphism) associations.
   2.  Format the results in a easily accessible object for downstream use. (to be used by other bioinformatics tools)

## Installation
Install using github:
```sh
git clone https://github.com/arvkevi/gwas_wrapper.git
cd gwas_wrapper
python setup.py install
```

## Usage
### search
Search for all SNP associations related to query term(s) with default filters:
```python
from gwas_wrapper import GWAS
raw_results = GWAS().search("baldness")
```

Add custom filters to the search with keyword arguments (available arguments and default values are in the search docstring):
```python
raw_results = GWAS().search("baldness", pvalfilter='5e-15')
```

`raw_results` is a nested dictionary, it contains one or more SNP association records.  However, each record has a varying number of keys, so there are a few parsing functions included to standardize the format.
### snp_list
To produce a list of tuples with the `("SNP rsID number", "risk allele")`:
```python
GWAS().snp_list(raw_results)
[('rs2497938', 'T'), ('rs6047844', 'T'), ('rs2497938', 'n/a'), ('rs2180439', '?'), ('rs2180439', 'C')]
```
Of note:

1. Two SNPs were repeated with differing risk alleles. (SNPs can have more than one risk allele assocaition)
2. `'n/a'` is used when no value was found in the GWAS Catalog, while `'?'` is when the GWAS study reported and "unknown risk allele".

### parse_snps
`parse_snps` reformats the `raw_results` into a nested dictionary, however, now the top level of the dictionary is a unique rsID and the second level is the risk allele.  This was done to expose the rsID as a unique element.

```python
{'rs2497938': {'T' {...},
              {'n/a' {...}
  },
{'rs6047844': ...
```

To return all the attributes for the snp associations in `raw_results` use `parse_type='all'`:
```python
parsed_results = GWAS().parse_snps(raw_results, parse_type='all')
print parsed_results

{ 'rs2180439': { '?': { '_version_': 1531216734768332800,
                        'ancestralGroups': ['European'],
                        'ancestryLinks': [ 'initial|NR|European|1198',
                                           'replication|NR|European|612'],
                        'author': ['Brockschmidt FF'],
                        'author_s': 'Brockschmidt FF',
                        ...

```
Alternatively, specify `parse_type='custom'`, which will read a list of attributes from the `custom_attr` keyword.
If a specified attribute does not exist, the function will create a key, value pair `custom_attr[i]: 'n/a'`.

```python
custom_results = GWAS().parse_snps(raw_results, parse_type='custom', custom_attr=['studyId', 'numberOfIndividuals', 'orPerCopyNum'])
print custom_results

{ 'rs2180439': { '?': { 'numberOfIndividuals': [1198, 612],
                        'orPerCopyNum': 2.08,
                        'studyId': '6515'},
                 'C': { 'numberOfIndividuals': [808, 553],
                        'orPerCopyNum': 1.82,
                        'studyId': '5266'}},
  'rs2497938': { 'T': { 'numberOfIndividuals': [12806],
                        'orPerCopyNum': 2.2,
                        'studyId': '6795'},
                 'n/a': { 'numberOfIndividuals': [1198, 612],
                          'orPerCopyNum': 6.5,
                          'studyId': '6515'}},
  'rs6047844': { 'T': { 'numberOfIndividuals': [12806],
                        'orPerCopyNum': 1.6,
                        'studyId': '6795'}}}
```
## TODO
### Filters
1. Currently orfilter only selects snp associations with the exact value.  Test how to filter <, > or an explict range (min,max).
2. Test date filter
3. Test beta filter

## Citation
Welter D, MacArthur J, Morales J, Burdett T, Hall P, Junkins H, Klemm A,
    Flicek P, Manolio T, Hindorff L, and Parkinson H.
    The NHGRI GWAS Catalog, a curated resource of SNP-trait associations.
    Nucleic Acids Research, 2014, Vol. 42 (Database issue): D1001-D1006.
