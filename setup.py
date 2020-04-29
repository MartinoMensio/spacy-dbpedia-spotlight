from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

def setup_package():
    setup(name="spacy_dbpedia_spotlight",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown')

if __name__ == "__main__":
    setup_package()