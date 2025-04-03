# Generating a Tapis Benchmark

The goal within this directory is to generate a benchmark for the Tapis project. Our approach will be to use a 
LLMs enhanced with LLMs to generate the benchmark. We will use these inputs to the RAG application:

- Tapis readthedocs contenst, as a single pds (see the `source` directory)
- Tapis Open API specs for each API, as a single text file (see the `live-docs` directory)
- An initial set of examples written by hand (see the `benchmark` directory)

In the future, we could also add additional inputs, such as: 
- Test suite code 
- Tutorials (as a pdf)


