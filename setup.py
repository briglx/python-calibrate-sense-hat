import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="calibrate-sense-hat",
    version="1.0.0",
    author="Brig Lamoreaux",
    author_email="brig@golamoreaux.com",
    description="Python module to calibrate the Raspberry Pi Sense HAT used in the Astro Pi mission",
    long_description=read('README.rst'),
    license="MIT",
    keywords=[
        "sense hat",
        "raspberrypi",
        "astro pi",
    ],
    url="https://github.com/briglx/python-calibrate-sense-hat",
    packages=find_packages(),
    package_data={
        "txt": ['calibrate_sense_hat_text.txt'],
        "png": ['calibrate_sense_hat_text.png']
    },
    include_package_data=True,
    install_requires=[
        "pillow",
        "numpy"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Education",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
    ],
)