# Questions
---

These are my answers to the questions presented at the end of the document.

**Q:** *We run scrapes continuously, both on the same websites as data changes over time and on new websites that we find interesting. 
How would you monitor the activity of the scrapers to make sure they were functioning and functioning correctly?*

**A:** It depends on the architecture and how the scrapers are set up. If these were implemented like a traditional application server
then monitoring can be simple. Health check routes are a great way of ensuring that your service is running as expected, can access the
database it is operating with, and any connectivity with 3rd parties is successful. Services such Datadog and AWS Cloudwatch can be 
configured to monitor the health of scrapers.

I believe that monitoring the health of the scraper is a an different issue to ensuring the correctness of the data being consumed. To 
ensure that the scrapers are consuming the correct data I believe it is import to develop them in a defensive manner, where we treat 
all data consumed as hostile and requiring validation. With websites constantly changing and being iterated on, we shouldn't trust 
what is being scraped unless it meets some level of valiation before being entered into a data warehouse or database. By being defensive 
we can ensure that our core systems are accurate and prevent bad data from being entered into our systems. 

---

**Q:** *We join data from lots of sources and this can lead to sparsity in the data, often it’s a case of identifying when we are missing 
data and differentiating that from when data simply isn’t available. How could you determine missing data in a scalable way?*

**A:** Achieving scale is all about automation in my opinion, where at a very small scale it is possible to eye ball data to ensure it 
is consistent, therefore to automate this a defensive minded data pipline and workflow is required. I believe that when dealing with
data that can be inconsistent, there should be steps in the data pipeline to ensure that it looks how we understand it should look. I
believe it is also important to break up the workflow into small units of work so that if a fail occurs at any point finding the error
is much easier.

I was not able to fulyy demonstrate this is the challenge due to time constraints but I feel that the solution is archiected in a way
such that it show how we can unitise the process and test for data quality at each step. While scraping the actual data I decided not
to validate many inputs as I wanted the output CSV to closely match what the website actually showed. This is where I implemented the
first layer of validation, ensuring that the data I expected to be there was correct. I handled the inconsistent data differently,
electing to use a try/except handler for when we failed to parse the data and log the error.

The ingesting step validates data differently, using cattrs to structure the class and validate each of the inputs before it is initialised
as a attrs class. This allows us to be type safe during runtime, and preventing incorrect data loading. This ensures that all data saved 
to the database is in the correct shape.

---

**Q:** *We release data on a weekly cadence, as time goes on we query more data and it can take longer to scrape and process the data we 
need. How would you scale the system to do more work within a shorter period of time?*

**A:** I believe there isn't a one size fits all answer to this question, that a number of inputs are required, not just the cadence of
release and quantity of data. For example, for a large timeseries data set being stored in a traditional PostgreSQL database there are
a number of strategies to scale your system based on access patterns and volume. 

The first step would be to log query performance and to analyse the query plan of slow queries, which can show how data can be better 
organised and indexed once the access pattern is known. Depending on how the data is accessed it might change how we approach scaling a 
solution such as, view tables for common complex joins and queries, bulk actions and jobs in off peak hours to replicate tables and 
update views, and improvements to the data model to better optimise for how it is being accessed.

Once all of these avenues have been explored, it might be time to change the architecture of the product. This might be changing database
products to be something better suited for time series data and separating that part of the product, or moving to a data warehouse type
product like snow flake. All of these solutions are costly and take time to implement, so need to be balanced against the actual benefits
of scaling further. 

---

**Q:** *A recent change to the codebase has caused a feature to begin failing, the failure has made it’s way to production and needs to be 
resolved. What would you do to get the system back on track and reduce these sorts of incidents happening in future?*

**A:** I am a firm believer in failing forward, not rolling back, and patching the issue as quickly as possible. During the incident I think
communication is the most important factor to resolving it quicklym, both within the team and with externals such as management. A well
defined incident process such as, declaration of the incident, coordination in a public channel/venue, and resolving the isssue on a call
is better than rolling the change back. There are very few types of incident that should be solved with a rollback, a no blame culture 
within the team helps engineers to be empowered to actually fix the issue. 

The benefit from rolling forward without blame is that engineers don't fear releases and you keep team velocity. Small continuous delivery
stops large scale issues from happening when teams are confident in their systems and tools. A good CI/CD pipeline and well tested product
gives teams confidence to deploy quickly. Without this you can't have a culture of rolling forward during an incident, deploys will slow 
down fixes, teams will then group up releases, which leads to a higher probability of issues occuring in production. No one writes perfect
code, we should prepare for incidents and make resolving them as easy as possible.

