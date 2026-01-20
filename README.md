# E-Book Search with Custom Analyzers

Username: elastic </br>
Password: bananana

## Milestones:
- <b> Milestone 1 - Project description </b>
    
	An Elasticsearch-backed e-book index running in Docker (TLS + basic auth). A custom English analyzer (`text_english`) is defined with lowercase, asciifolding, English stopwords, stemming, and shingles to improve relevance. A 10k-record OpenLibrary dataset is harvested via `get_books.py`, mapped with `mapping.json`, bulk-loaded into the `ebooks` index, and explored via Kibana and Postman.

<br>

- <b> Milestone 2 - List of use cases </b>

	- UC1: Harvest open e-book metadata with `get_books.py` into NDJSON for bulk ingest.
	- UC2: Define and apply the custom `text_english` analyzer via `mapping.json` when creating the `ebooks` index.
	- UC3: Bulk load the generated dataset into Elasticsearch over HTTPS with auth.
	- UC4: Run relevance tests using `multi_match` queries (curl/Postman) on `title`, `synopsis`, and `tags` with stemming and shingles.
	- UC5: Inspect analyzer output with `_analyze` to validate tokenization/stemming for search quality.
	- UC6: Explore indexed data in Kibana (Discover, Lens) using the `ebooks` data view (no time field).
	- UC7: Retrieve individual documents by ID and basic counts/health from the secured cluster.
	- UC8: Highlight matched terms in search responses to verify analyzer impact.

<br>

- <b> Milestone 3 - Rest API  - SWAGGER UI </b>

<br>

- <b> Milestone 4 - Elastic Maping </b>

get_books.py gets the dataset and then is imported.

```
curl.exe -X PUT "http://localhost:9200/ebooks" -H "Content-Type: application/json" --data-binary '@mapping.json'
```

```
curl.exe -X POST "https://localhost:9200/ebooks/_bulk" --cacert "certs/ca/ca.crt" -u "elastic:bananana" -H "Content-Type: application/json" --data-binary "@dataset/books-openlibrary.jsonl"
```

<br>

- <b> Milestone 5 - Implementation </b>

Docker containers are configured and data is imported.

<i> To deploy: </i>
```
docker-compose up -d
```
<i> Enter on http://localhost:5601. Log in, go to Analytics and press on Discover. </i>

<br>

- <b> Milestone 6 - Postman Testing </b>

Functionality of querying ElasticSearch works

<i> Example of query "travel": </i>
```
GET: https://localhost:9200/ebooks/_search
Header: Content-Type:application/json
Body:
{
  "query": {
    "multi_match": {
      "query": "travel",
      "fields": ["title", "synopsis", "tags"]
    }
  },
  "_source": ["title", "author", "published_year"],
  "highlight": {
    "fields": {
      "title": {},
      "synopsis": {}
    }
  },
  "size": 10
}
```
