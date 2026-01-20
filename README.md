# E-Book Search with Custom Analyzers

Username: elastic
Password: bananana

## Milestones:
- <b> Milestone 1 - Project description </b>
    
	An Elasticsearch-backed e-book index running in Docker (TLS + basic auth). A custom English analyzer (text_english) is defined with lowercase, asciifolding, English stopwords, stemming, and shingles to improve relevance. A 10k-record OpenLibrary dataset is harvested via get_books.py, mapped with mapping.json, bulk-loaded into the ebooks index, and explored via Kibana and Postman.

<br>

- <b> Milestone 2 - List of use cases </b>

	- UC1: Harvest open e-book metadata with get_books.py into NDJSON for bulk ingest.
	- UC2: Define and apply the custom text_english analyzer via mapping.json when creating the ebooks index.
	- UC3: Bulk load the generated dataset into Elasticsearch over HTTPS with auth.
	- UC4: Run relevance tests using multi_match queries (curl/Postman) on title, synopsis, and tags with stemming and shingles.
	- UC5: Inspect analyzer output with _analyze to validate tokenization/stemming for search quality.
	- UC6: Explore indexed data in Kibana (Discover, Lens) using the ebooks data view (no time field).
	- UC7: Retrieve individual documents by ID and basic counts/health from the secured cluster.
	- UC8: Highlight matched terms in search responses to verify analyzer impact.

<br>

- <b> Milestone 3 - Rest API  - SWAGGER UI </b>

Prerequisites - Make sure you have the required libraries installed:


pip install fastapi pydantic uvicorn elasticsearch


Run the application 

python app.py 


Open the Swagger UI on http://127.0.0.1:8000/docs

> *Note:* The engine has 2 inputs: word (search term) and limit (number of results).


#### Successful request example:


q: gentleman
limit: 50


Response:
json
[
  {
    "title": "A Gentleman in Moscow",
    "author": "Amor Towles",
    "published_year": 2016,
    "genres": ["Historical Fiction"],
    "synopsis": "A count is sentenced to house arrest in a luxury hotel.",
    "file_url": "[https://example.com/gentleman.pdf](https://example.com/gentleman.pdf)"
  }
]


#### Validation Error Example

To trigger the validation error open http://127.0.0.1:8000/search?q=books&limit=999 by giving a higher character limit on a query, the validation message will be 

json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": [
        "query",
        "limit"
      ],
      "msg": "Input should be less than or equal to 50",
      "input": "999",
      "ctx": {
        "le": 50
      }
    }
  ]
}


> *Note:* Validation errors for data types (like entering text into the limit field) cannot be triggered directly in the Swagger UI because it uses a *client-side validator* to block invalid requests before they reach the server.

<br>

- <b> Milestone 4 - Elastic Maping </b>

get_books.py gets the dataset and then is imported.


curl.exe -X PUT "http://localhost:9200/ebooks" -H "Content-Type: application/json" --data-binary '@mapping.json'



curl.exe -X POST "https://localhost:9200/ebooks/_bulk" --cacert "certs/ca/ca.crt" -u "elastic:bananana" -H "Content-Type: application/json" --data-binary "@dataset/books-openlibrary.jsonl"


<br>

- <b> Milestone 5 - Implementation </b>

Docker containers are configured and data is imported.

<i> To deploy: </i>


docker-compose up -d


<i> Enter on http://localhost:5601. Log in, go to Analytics and press on Discover. </i>

<br>

- <b> Milestone 6 - Postman Testing </b>

Functionality of querying ElasticSearch works

<i> Example of query "travel": </i>


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