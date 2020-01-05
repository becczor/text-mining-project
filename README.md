# text-mining-project
Project in Text Mining course (TDDE16) at Linköping University winter 2019/2020

## Installing
1. Install Python 3.5 or greater, 64 bit version.

2. In the folder containing this project, create a virtual environment to protect your own configurations by running `python -m venv env`

3. Activate the virtual environment by running `env\Scripts\activate` for Windows, and `source env/bin/activate` for Linux. Make sure you do all following installations within the virutal environment, marked by `(env)` in the beginning of the terminal prompt.

    1. (To disable the virtual environment when you are finished, run `deactivate`)

4. Run `python -m pip install --upgrade pip` to update pip to newest version.

5. Install jupyter. For Linux, run `python3 -m pip install jupyter`. For Windows, run `python -m pip install jupyter`.

6. Run `pip install --upgrade setuptools` to update setuptools.

7. If you do not have "Microsoft Visual C++ 2015 Build Tools", download it here: http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe.)[http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe.]. Avaliable under "Tools for Visual Studio" further down on the page. If you don't know if you have it or not, you will notice it if the next step works or not :).

8. Install SpaCy. For Windows, run `pip install -U spacy`.

9. Start the notebook by running `jupyter notebook word-embedding-bias.ipynb`.



