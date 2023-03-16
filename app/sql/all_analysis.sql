
-- month-on-month-traffic
select p.website, pt.month, pt.year, pt.traffic
from page p
join page_scrape ps on ps.page_id = p.id
join page_traffic pt on pt.scrape_id = ps.id
order by p.website, pt.year asc, pt.month asc;

