# gwas_wrapper
`gwas_wrapper` is a lightweight Python wrapper designed to interact with the [GWAS Catalog](https://www.ebi.ac.uk/gwas/home) API.  As mentioned on their [help page](https://www.ebi.ac.uk/gwas/docs/programmatic-access), the GWAS Catalog API is under active development and no official documentation yet exists.  There are two intended purpose for `gwas_wrapper`:

   1.  Quick and flexible (programmatic) access to SNP (single nucleotide polymorphism) associations.
   2.  Format the results in a easily accessible object for downstream use. (to be used by other bioinformatics tools)

## Installation
Install with pip:
```sh
pip install gwas_wrapper
```

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
#### snp_list
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


## batch_search
The GWAS Catalog does not allow users to search for multiple SNPs in one query.
The following functionality assumes the user has a list of rsIDs.

The input to `batch_search` should be a python list or the path to a file
conatining 'newline-separated' rsIDs. (Example file: `snp_batch.txt`)

```python
#snps = '/path/to/snp_batch.txt'
snps = ['rs2497938', 'rs6047844']
batch_results = GWAS().batch_search(snps, pvalfilter='5e-10')
```
Again, I thought it was important to expose the rsID, so `batch_results`
is a dictionary. Keys are the rsIDs from the input, and values are lists
of association objects returned from the search.

```python
batch_results['rs2497938']

[{'_version_': 1531851937000980481,
  'ancestralGroups': ['European'],
  'ancestryLinks': ['initial|Germany,Greece,Iceland,Netherlands,Switzerland,U.K.,Australia|European|12806'],
  'author': ['Li R'],
  ...
```

### batch_enrichment
To get the number of types of associations for each rsID individually
as well as the batch as a whole, pass the object returned from 
`batch_search` to `batch_enrichment`.

```python
batch_assoc_count, snp_assoc_count = GWAS().batch_enrichment(batch_results)
```

`batch_assoc_count` is a `Counter()` object that spans the the entire batch, 
while `snp_assoc_count` is a dictionary with association counts by
individual rsID.

```python
print batch_assoc_count

Counter({'alopecia, androgenetic': 6,
         'alopecia, androgenic': 6,
         'alopecia, male pattern': 6,
         'androgenic alopecia': 6,
         'male pattern baldness': 6,
         'male-pattern baldness': 6})

print snp_assoc_count['rs2180439']  

Counter({'alopecia, androgenetic': 2,
         'alopecia, androgenic': 2,
         'alopecia, male pattern': 2,
         'androgenic alopecia': 2,
         'male pattern baldness': 2,
         'male-pattern baldness': 2})
```

In this example, with the search term `"baldness"`, `batch_assoc_count` reveals
that these SNPs are only associated with hair loss.  `snp_assoc_count['rs2180439']`
shows that there is more than one study or assocation where that SNP was linked to 
hair loss.

In a more impure example:

```python
snps = ['rs3803662', 'rs2981582', 'rs2735839', 'rs2788612']
batch_results = GWAS().batch_search(snps)

batch_assoc_count, snp_assoc_count = GWAS().batch_enrichment(batch_results)
print batch_assoc_count

Counter({'BREAST NEOPL': 9,
         'Breast Cancer': 9,
         'Breast Neoplasm': 9,
         'Breast Tumor': 9,
         'CA - Carcinoma of breast': 9,
         'Cancer of Breast': 9,
         'Cancer of Prostate': 2,
         'Cancer of the Breast': 9,
         'Cancer of the Prostate': 2,
         ...
```
There are some SNPs associated with breast cancer and some associated with prostate cancer.

## TODO
### Filters
1. Currently orfilter only selects snp associations with the exact value.  
   Test how to filter <, > or an explict range (min,max).
2. Test date filter
3. Test beta filter

### Other query types
1. By Study
2. By Gene

## Citation
Welter D, MacArthur J, Morales J, Burdett T, Hall P, Junkins H, Klemm A,
    Flicek P, Manolio T, Hindorff L, and Parkinson H.
    The NHGRI GWAS Catalog, a curated resource of SNP-trait associations.
    Nucleic Acids Research, 2014, Vol. 42 (Database issue): D1001-D1006.