# Popular cities and local moments

Used when a local model is missing, quiet, or returns nothing.

- `popular_cities.csv` — watch cities and name aliases (so “Brooklyn” still finds New York).
- `popular_city_events.csv` — public festivals, neighborhood days, and seasonal windows. Prefer local moments people miss, not only Christmas, Thanksgiving, New Year, or Presidents’ Day.

Pipelines read **account places** when the traveler saved them. Empty slots use the built-in default cities.

Add a row to the events file:

`city,region,country,match_keys,months,name,kind,when,blurb`

- `match_keys` — lowercase aliases split by `|`
- `months` — `9` or `9,10`
- `kind` — `festival`, `culture`, `season`, or `community`
