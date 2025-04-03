Overview
========

Goal: Poetry env that can generate pdf from RST
Followed: https://sphinx-test-docs.readthedocs.io

Setup
=====
In addition to installing the poetry package in the pwd, also installed the following:

```
sudo apt install texlive-latex-base
sudo apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
sudo apt install latexmk
```


Usage
=====
First, check that building the source works by executing (from docs_2_pdf directory):

```
  make html
```

With the poetry environment activated, from the docs_2_pdf directory, execute:

```
  make latexpdf
```

to generate the pdf file. The file tapis2pdf.pdf resides in the build/latext folder. 
