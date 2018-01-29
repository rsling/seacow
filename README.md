# seacow
SeaCOW wrapper by COW for the Manatee library

FEATURES

- SeaCOW is a class-based rewrite of the old ManaCOW project.
- It uses an efficient Bloom filter for deduplication.
- It does not create huge memory structures but processes
  concordances on the fly.
- If you want custom processing, create an implementation
  of the Processor class.
- Included are two processors: ConcordanceWriter and 
  DependencyTreeMaker.
