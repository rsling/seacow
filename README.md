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

## Documentation

### Functions

```python
cow_region_to_conc(region, attrs = True)
```

Formats a Manatee region (as returned within Query objects and passed to Processor objects) to a usable structure. Decodes UTF-8.

* `attrs` Set this to `True` if your concordance contains no structures and only one positional attribute (pure token stream).

### Classes

```Query(object)```

Performs queries and pipes the data into a processor.

```Processor(object)```

The 'abstract' class from which processors should be derived.

```ConcordanceWriter(Processor)```

A Processor which writes results of a query into a nicely fromatted CSV file (or to the terminal).

```DependencyBuilder(Processor)```

A Processor which re-creates dependency information contained in COW corpora and represents it as trees (in [anytree](https://pypi.python.org/pypi/anytree) format).

This is a base class which only writes trees to the terminal, stores them as JSON, or draws Graphviz graphs to DOT or PNG files. Intended for refinement in custom classes.
