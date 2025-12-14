# E-Book Search with Custom Analyzers


## Milestones:
- Milestone 1 - Project description
    
    A search engine for e-books using Elasticsearch. It features custom text analyzers (with stemming and synonyms) to dramatically improve search relevance beyond simple keyword matching. Kibana is used to visualize the dataset's content and validate the custom text analysis.

- Milestone 2 - List of use cases
	- UC1: Ingest e-book metadata (title, author, language, published year, genres, synopsis, file URL)
	- UC2: Define and update custom analyzers (stemming, stopwords, synonyms) for English and additional languages
	- UC3: Index e-books into Elasticsearch with the active analyzer set
	- UC4: Reindex existing content when analyzer configuration changes
	- UC5: Full-text search by keyword/phrase with relevance boosting (title > synopsis > tags)
	- UC6: Faceted filtering (language, genre, year range, author) on search results
	- UC7: Pagination and sorting of search results (relevance, newest, oldest)
	- UC8: Suggest/autocomplete as user types (prefix and typo-tolerant where analyzer allows)
	- UC9: Highlight matched terms (synonym- and stem-aware) in results
	- UC10: Retrieve full e-book metadata and download link by ID
	- UC11: Track search queries and clicks for analytics
	- UC12: Visualize indexed corpus and analyzer behavior in Kibana (tokenization, synonyms, char filters)
	- UC13: Health check and monitoring endpoints for Elasticsearch cluster and API service
- Milestone 3 - Rest API  - SWAGGER UI
- Milestone 4 - Elastic Maping
- Milestone 5 - Implementation
- Milestone 6 - Postman Testing
