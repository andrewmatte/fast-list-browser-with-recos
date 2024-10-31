# fast-list-browser-with-recos
This is a demo for browsing lists quickly and easily, showing similar items.

The server is written with ntex, the best on techempower.com's benchmark #22 composite score. It uses a different repo I wrote for vector search to get the recommendations.

Word embeddings are way bigger than necessary these days (altough they are great for longer form content) so I PCA(10) the 1024-dim data to speed up search and reduce data size. That storage reduces from 246MB to less than 6MB. As well, I fetch data from GoogleTranslate but there has got to be a bug or something because the data is mostly bad. That's read only and so it's stored in a sqlite3 file with the en_words column indexed. It's about 175MB. The web server application is 9MB and the vector search DB is 13MB so all of it fits into a 512MB of RAM instance, which at current prices is $4/mo. I used sailfish to template data but now it's a bit of an artifact unless I add a route to get a specific word.

The vector search database is the https://github.com/mandrewstuart/nearest-neighbour-geo-search repo. I added a /get_by_id route that I haven't uploaded as of Halloween 2024.

Benchmarking the service locally, it returns the static content in about 1ms and the json endpoint in under 20ms, although on the cheapest instance that DigitalOcean offers at $4/mo, it's almost 100ms. Still using apache-benchmarking tools, I'm having increase the concurrent requests to 1000 for 5 seconds before I get any errors on the static content and 25 concurrent requests for 5 seconds on the json endpoint.

The single-page-app intentionally doesn't have any links, imports or images so that it all arrives in a single request.
