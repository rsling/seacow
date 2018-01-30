# SeacCOW, the COW wrapper for the Manatee library

![Sample dependency graph image](https://raw.githubusercontent.com/rsling/seacow/master/sample.png)

## Features

- SeaCOW is a class-based rewrite of the old ManaCOW project.
- It uses an efficient Bloom filter for deduplication.
- It does not create huge memory structures but processes
  concordances on the fly.
- If you want custom processing, create an implementation
  of the Processor class.
- Included are two processors: ConcordanceWriter and 
  DependencyTreeMaker.

## Installation

We currently do not support or recommend installing it. In any case, you need a running Manatee with corpora, and you have to make the SeaCOW Python files visible to your own code.

Get an account on https://www.webcorpora.org/ to use SeaCOW with COW.

## Use

1. Create a SeaCOW.Query object.
2. Set the relevant attributes, including search string.
3. Create a descendant of SeaCOW.Processor and set its attributes.
4. Set the processor as the processor attribute of the query object.
5. Call the query's run method.

## Functions

```python
cow_region_to_conc(region, attrs = True)
```

Formats a Manatee region (as returned within Query objects and passed to Processor objects) to a usable structure. Decodes UTF-8.

* `attrs` Set this to `True` if your concordance contains no structures and only one positional attribute (pure token stream).

## Classes

### Query

Performs queries and pipes the data into a processor.

#### Attributes

* ```corpus``` The string which identifies the corpus (lower case), such as `'decow16a-nano'`.
* ```attributes``` A list of attributes of tokens to be exported, such as `['token', 'tag', 'lemma']`.
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

The 'abstract' class from which processors should be derived.


### ConcordanceWriter

A Processor which writes results of a query into a nicely fromatted CSV file (or to the terminal).


### DependencyBuilder

A Processor which re-creates dependency information contained in COW corpora and represents it as trees (in [anytree](https://pypi.python.org/pypi/anytree) format).

This is a base class which only writes trees to the terminal, stores them as JSON, or draws Graphviz graphs to DOT or PNG files. Intended for refinement in custom classes.
