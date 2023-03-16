# Specter Take Home Engineering Challenge
---

This repository is for completing the engineering challenge given to me by Specter for the Senior Data Engineer role. I have chosen
architect my solution as a microservice based on Flask and SQLAlchemy. The answers to the questions in the challenge doc can be found
in `QUESTIONS.md`.


## Setup

I have chosen to use [Poetry](https://python-poetry.org/) for this project. To install all of the dependancies:

```
poetry install
```

Once poetry has been installed the virtual environment can be activated using:
```
poetry shell
```

The final step is to initialise the DB tables using:
```
flask cli create_tables
```

This project has been formatted using [Black](https://pypi.org/project/black/) and checked with 
[MyPy](https://mypy.readthedocs.io/en/stable/) to ensure type safety.

## Implementation
---

I have chosen to approach this challenge by creating the barebones framework for a web scraping micro service, where a cron worker
would trigger one/many of the CLI commands for scraping, ingesting, or summarising data. I went with this approach so that I could 
implement all of the steps presented in the challenge as separate steps that could be tested. With the flow being broken up into 
smaller units of work, validaton and error control could be implemented during each unit of work to make an overall data pipleine 
and workflow more resilient. 

To parse all of the local files:
```
flask cli scrape parse_all_pages
```

This command will scrape all of the pages saved locally in `app/local/scraped_pages` for the required data in the first step of the
challenge, before outputing the contents of each of the pages to a single CSV stored in `app/local/input`.  

To parse input directory for all files from SimilarWeb:
```
flask cli ingest load_all_similar_web
```

To produce the summary statistics and graphs:
```
flask cli summary analysis_all
```

For the challenge I have failed to scrape the Ranking Data for each of the pages after coming across a number of issues and running 
out of time. I had attempted to first scrape it through selecting the correct CSS tags like the other graphs and found that they were
not present. My next step after being pointed in the right direction was to attempt to scrape the Highcharts from their JavaScript. 
This attempt also failed because I suspect that the charts are being rendered server side, and only the SVG is being sent to the front 
end. I validated some of this by checking the current live site from SimiliarWeb and also could not locate the charts in the JavaScript.

I was in the process of investigating parsing the raw SVG data but simply ran out of time and when balanced against properly documenting
my work and pressing on with attempting to parse the data I have chosen to document my process in this README instead.

## Tests
---

I have implemented a limited number of tests, only covering the two known variations of data scraped from similar web due to time
but I would have liked to have refactored my code more to make it testable. The tests can be run with:

```
pytest
```

