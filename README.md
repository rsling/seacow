# SeaCOW, the COW wrapper for the Manatee library

![Sample dependency graph image](https://raw.githubusercontent.com/rsling/seacow/master/samples/sample.png)

## Note: Because of the additional processing of query results in SeaCOW, it is significantly slower that NoSketchEngine or corpquery. This cannot be avoided unless you drop the extra processing, which is the whole point of having SeaCOW in the first place. Please do not file bug reports or complaints about the speed penalty involved in using SeaCOW. It is designed primarily for running unattended queries on a server with built-in processing, filtering, etc. If you are a Python wizard, you are invited to help us make the additional processing more efficient, of course.

## Features

- SeaCOW is a class-based rewrite of the old ManaCOW project.
- It uses an efficient Bloom filter for deduplication.
- It does not create huge memory structures but processes concordances on the fly.
- If you want custom processing, create an implementation of the Processor class.
- Included are two processors: ConcordanceWriter and   DependencyBuilder.

## Installation

We currently do not support or recommend installing it. In any case, you need a running Manatee with corpora, and you have to make the SeaCOW Python files visible to your own code.

Get an account on https://www.webcorpora.org/ to use SeaCOW with COW.

## Use

For each Processor class, there is a straightforward and annotated demo in the samnples folder!

1. Create a `SeaCOW.Query` object.
2. Set the relevant attributes, including search string (see below).
3. Create an object of a descendant class of `SeaCOW.Processor` and set its attributes.
4. Set the processor as the processor attribute of the query object.
5. Call the query's `run()` method.

**NOTE! This is currently Python 2.7 only. Please get in contact with us if you need Python 3, and we will asssist you in creating a Python 3 version.**

## Functions

```python
cow_region_to_conc(region, attrs = True)
```

Formats a Manatee region (as returned within Query objects and passed to Processor objects) to a usable structure. Decodes UTF-8. Set `attrs` to `True` if your concordance contains no structures and only one positional attribute (pure token stream).

## Classes

### Query

```python
Query(object)
```

Performs queries and pipes the data into a processor.


#### Notes on using `Nonprocessor` instances with `Query`!

If you pass an instance of `Nonprocessor` as the processor attribute, `Query` will call the `prepare()` and `finalise()` methods as usual. However, the stream returned by Manatee will not be processed and the `process()` method is not called once. Except for `corpus` and `string` you don't need to set any attributes. Even `container` can be left unset.

Using a `Nonprocessor` is intended for those who only want to read the `count` attribute after Manatee has executed the query (like Manatee's own `corpquery -n`).


#### Attributes

* ```corpus``` The string which identifies the corpus (lower case), such as `'decow16a-nano'`.
* ```attributes``` A list of attributes of tokens to be exported, such as `['word', 'tag', 'lemma', 'depind', 'dephd', 'deprel']`.
* ```structures``` A list of structures to be exported, such as `['s', 'nx']`.
* ```references``` A list of reference attributes to be exported, such as `['doc.id', 'doc.url', 's.idx']`.
* ```container``` The container structure to be exported, such as `'s'`
* ```string``` The query string, such as `'[lemma="Chuzpe"]'`
* ```max_hits``` The maximum number of hits to be exported.
* ```random_subset``` A float between 0 and 1 representing the proportion of hits to be exported (chosen randomly).
* ```context_left``` The number of `container` structures to be exported to the left of the matching one.
* ```context_right``` The number of `container` structures to be exported to the right of the matching one.
* ```processor``` The processor object which takes care of the returned results.


#### Methods

```set_deduplication(self, off = False)```

Enable or disable deduplication of concordances based on a bloom filter. Call without argument to activate filter.

```run(self)```

Execute the query and process the results after everything has been set up.

### Processor

```python
Processor(object)
```

The 'abstract' class from which processors should be derived.

#### Methods (You must override all of these.)

* `__init__(self)` Standard init.
* `prepare(self, query)` Code executed before the query results are processed.
* `finalise(self, query)` Code executed after the query results are processed.
* `process(self, query, region, meta, match_offset, match_length)` This is the callback called for each hit returned for the query. `query` is the query object. `region` is the Manatee region which should always be processed with `cow_region_to_conc`. `meta` is a list of all meta information for the hit (reference attributes; look in `query.references` for what they are). `match_offset` and `match_length` locate the actual matching structure in `region`.



### ConcordanceLoader


```python
ConcordanceLoader(Processor)
```

A Processor which loads a concordance in a Pytho list. Each element represents one hit and is organised as a dictionary. The keys are `meta` (meta data as requested in setting up Query) , `left` (left context), `match` (matching region), `right`  (right context). The three lastmentioned members are lists of strings and dictionaries. Structural markers like <s> are always a encoded as strings. Tokens are either a string (attributes concatenated) or a dictionaries. See `full_structure`.



#### Attributes

* `full_structure` If `True`, then each token in the matching region and the context will also be a dictionary with annotation names as keys and corresponding values (token, lemma, POS tag, etc.). Else everything will be flattened into one string with the pipes symbol |. Default is `False`.




### ConcordanceWriter


```python
ConcordanceWriter(Processor)
```

A Processor which writes results of a query into a nicely fromatted CSV file (or to the terminal).

#### Attributes

* `filename` Set this to save a CSV file. If `None`, output is on stdout.


### DependencyBuilder

```python
DependencyBuilder(Processor)
```

A Processor which re-creates dependency information contained in COW corpora and represents it as trees (in [anytree](https://pypi.python.org/pypi/anytree) format). This is a base class which only writes trees to the terminal, stores them as JSON, or draws Graphviz graphs to DOT or PNG files. Intended for refinement in custom classes.

#### Attributes

* `column_index` The 0-based index into the attribute list, locating the dependency index (see in `Query.attributes` where you specified something like `'depind'`).
* `column_head` The 0-based index into the attribute list, locating the dependency head index (see in `Query.attributes` where you specified something like `'dephd'`).
* `column_relation` The 0-based index into the attribute list, locating the dependency relation (see in `Query.attributes` where you specified something like `'deprel'`).
* `column_token` The 0-based index into the attribute list, locating the token (see in `Query.attributes` where you specified something like `'word'`).
* `fileprefix` The path prefix defining the location where the (potentially many) data files will be saved.
* `savejson` Set `True` to export full JSON for dependency trees (including meta data). One large file.
* `saveimage` Set to `'dot'` to export Graphviz DOT files, `'png'` to export PNG files, `None` to export no graphics files of dependency trees. **ATTENTION! Creates one file per hit!**
* `printtrees` Set to `True` to output ASCII renderings of trees at the terminal while processing.
* `imagemetaid1` The 0-based index of the hit's `meta` attribute which will be used to create graphics file names, first part. Recommended: `doc.id`. See `Query.references` for where you put the reference attributes in the list.
* `imagemetaid2` The 0-based index of the hit's `meta` attribute which will be used to create graphics file names, second part. Recommended: `s.idx`. See `Query.references` for where you put the reference attributes in the list. **NOTE: `imagemetaid2` is not required. However, if you only use a document identifier, subsequent sentences will overwrite those from the document already written.**


### Nonprocessor

```python
Nonprocessor(Processor)
```

A Processor which does nothing. All four functions simply call `pass`. Use this to read Query.count after executing a query if you just need query result counts. See Query() documentation about the implications.

