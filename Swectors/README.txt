Word Vectors from Swedish News Text
Marco Kuhlmann <marco.kuhlmann@liu.se>

This directory contains a word2vec (skip-gram) model trained on 200k
tokens of Swedish news text taken from the newspaper Göteborgsposten
(2001–2013).  It was produced as follows:

1. Download the GP raw data (xml.bz2 files) from Språkbanken. Note
that we do not use the data from 1994.

2. Put the xml.bz2 files into their own directory:

% mkdir raw
% mv *.xml.bz2 raw
% cd raw

3. Run the following to create a large text file with everything:

% python3 ../bw_extract.py raw.txt

4. Run the postprocess script to only keep lowercased alphabetical
tokens:

% python3 ../postprocess.py < raw.txt > gp-2001-2013.txt

5. Train a default skipgram model and save the result in the binary
format:

% word2vec -train gp-2001-2013.txt -output ../gp-2001-2013.bin -binary 1 -cbow 0
