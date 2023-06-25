from setuptools import setup
import labedf
with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()
LONG_DESCRIPTION = readme
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
setup(
    name="labedf",
    author="sn-10",
    url="https://github.com/s-n-1-0/labedf.py",
    download_url="https://github.com/s-n-1-0/labedf.py",
    version=labedf.__version__,
    description="Merge the lab.js csv file and the edf file.",
    install_requires=[
        "pyedflib>=0.1.30",
        "labcsv>=1.0.4",
        "numpy>=1.22.4"
        ],
    packages=["labedf","labedf.utilities"],
    license="MIT",
    keywords= ["labjs","lab.js"],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown"
)