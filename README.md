<img src="thumbnail.png" alt="thumbnail" width="300"/>

# Ocean Biogeochemistry Cookbook

[![nightly-build](https://github.com/ProjectPythia/cookbook-template/actions/workflows/nightly-build.yaml/badge.svg)](https://github.com/ProjectPythia/cookbook-template/actions/workflows/nightly-build.yaml)
[![Binder](https://binder.projectpythia.org/badge_logo.svg)](https://binder.projectpythia.org/v2/gh/ProjectPythia/cookbook-template/main?labpath=notebooks)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12557199.svg)](https://doi.org/10.5281/zenodo.12557199)

This Project Pythia Cookbook covers working with various sources of ocean biogeochemistry data, including Community Earth System Model (CESM) output and observational data.

## Motivation

You'll get a brief introduction to some metrics important to ocean biogeochemistry, from physical quantities like temperature to biological quantities like plankton biomass. You'll learn some of the data science techniques used to work with this information, and see the relationship between modeled and observational estimates.

## Authors

[Lev Romashkov](https://github.com/rmshkv), [Kristen Krumhardt](https://github.com/kristenkrumhardt)

### Contributors

<a href="https://github.com/rmshkv/ocean-bgc-cookbook/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=rmshkv/ocean-bgc-cookbook" />
</a>

## Structure

### Intro

Learn how to read in the main CESM dataset that we'll be working with, and make a few simple maps.

### Nutrients

Explore the distribution of several nutrients in the ocean with maps and vertical profiles, and compare to observational data.

### Plankton

Explore the distribution of the phytoplankton and zooplankton functional types represented in CESM, and compare to observational data.

## Running the Notebooks

You can either run the notebooks using [Binder](https://binder.projectpythia.org/) or on your local machine.

### Running on Binder

The simplest way to interact with a Jupyter Notebook is through
[Binder](https://binder.projectpythia.org/), which enables the execution of a
[Jupyter Book](https://jupyterbook.org) in the cloud. The details of how this works are not
important for now. All you need to know is how to launch a Pythia
Cookbooks chapter via Binder. Simply navigate your mouse to
the top right corner of the book chapter you are viewing and click
on the rocket ship icon, (see figure below), and be sure to select
“launch Binder”. After a moment you should be presented with a
notebook that you can interact with. I.e. you’ll be able to execute
and even change the example programs. You’ll see that the code cells
have no output at first, until you execute them by pressing
{kbd}`Shift`\+{kbd}`Enter`. Complete details on how to interact with
a live Jupyter notebook are described in [Getting Started with
Jupyter](https://foundations.projectpythia.org/foundations/getting-started-jupyter.html).

### Running on Your Own Machine

If you are interested in running this material locally on your computer, you will need to follow this workflow:

1. Clone the `https://github.com/ProjectPythia/ocean-bgc-cookbook` repository:

   ```bash
    git clone https://github.com/ProjectPythia/cookbook-example.git
   ```

1. Move into the `ocean-bgc-cookbook` directory
   ```bash
   cd ocean-bgc-cookbook
   ```
1. Create and activate your conda environment from the `environment.yml` file
   ```bash
   conda env create -f environment.yml
   conda activate ocean-bgc-cookbook-dev
   ```
1. Move into the `notebooks` directory and start up Jupyterlab
   ```bash
   cd notebooks/
   jupyter lab
   ```
