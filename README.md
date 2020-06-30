# text-mining-project
Project in Text Mining course (TDDE16) at Linköping University winter 2019/2020.

## Word Embedding Bias
Word embeddings is a technique in NLP and text mining to represent words in order to be able to compare words based on similarity. The word embeddings are trained on large data sets with text written by humans. Therefore, the bias we have and include in our writings will be transferred to the word embeddings. 

This project looks at what biases there are in the swedish word embeddings [*Swectors*](https://www.ida.liu.se/divisions/hcs/nlplab/swectors/) based on text from Göteborgsposten. They are also compared with another set of word embeddings that are trained on data from two swedish discussion forums, *Familjeliv* and *Flashback*. The data is obtained from (Språkbanken)[https://spraakbanken.gu.se/swe].


## Installing
1. Install Python 3.6 or greater, 64 bit version.

2. In the folder containing this project, create a virtual environment to protect your own configurations by running `python -m venv env`

3. Activate the virtual environment by running `env\Scripts\activate` for Windows, and `source env/bin/activate` for Linux. Make sure you do all following installations within the virutal environment, marked by `(env)` in the beginning of the terminal prompt.

    1. (To disable the virtual environment when you are finished, run `deactivate`)

4. Run `python -m pip install --upgrade pip` to update pip to newest version.

5. Install jupyter. For Linux, run `python3 -m pip install jupyter`. For Windows, run `python -m pip install jupyter`.

6. Run `pip install --upgrade setuptools` to update setuptools.

7. Install Pandas by running `python -m pip install pandas`

8. Start the notebook by running `jupyter notebook word-embedding-bias.ipynb`.



