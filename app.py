import warnings
from typing import Optional, List

import urllib3
from elasticsearch import Elasticsearch
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(
    title="📚 E-Book Search Engine",
    version="1.5.0",
    docs_url=None
)

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "bananana"),
    verify_certs=False
)


# Pydantic model for book data validation
class Book(BaseModel):
    title: str = Field(..., description="Book title", examples=["The Great Gatsby"])
    author: Optional[str] = Field(None, description="Author name", examples=["F. Scott Fitzgerald"])
    language: str = Field("en", description="Language code", examples=["en"])
    published_year: Optional[int] = Field(None, description="Year of publication", examples=[1925])
    genres: List[str] = Field(default_factory=list, description="List of genres", examples=[["Fiction", "Classic"]])
    synopsis: str = Field("", description="Book synopsis/description")
    tags: List[str] = Field(default_factory=list, description="Search tags",
                            examples=[["classic", "american literature"]])
    file_url: Optional[str] = Field(None, description="URL to book resource")


class BookResponse(BaseModel):
    success: bool
    message: str
    book_id: str


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    content = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title,
    ).body.decode("utf-8")

    custom_css = """
    <style>
        .swagger-ui .topbar { background-color: #2c3e50 !important; border-bottom: 3px solid #27ae60 !important; }
        .swagger-ui .info .title { color: #27ae60 !important; font-family: 'Trebuchet MS', sans-serif !important; }
        .swagger-ui .opblock.opblock-get { background: rgba(39, 174, 96, 0.05) !important; border-color: #27ae60 !important; }
        .swagger-ui .opblock.opblock-post { background: rgba(52, 152, 219, 0.05) !important; border-color: #3498db !important; }
        .swagger-ui .opblock.opblock-delete { background: rgba(231, 76, 60, 0.05) !important; border-color: #e74c3c !important; }
        .btn.execute { background-color: #27ae60 !important; color: white !important; }
    </style>
    """
    return HTMLResponse(content=content.replace("</head>", f"{custom_css}</head>"))


@app.get("/", tags=["info"])
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "📚 E-Book Search Engine API",
        "version": "1.5.0",
        "endpoints": {
            "/search": "Search for books",
            "/book": "Add a new book (POST) or get book by ID (GET)",
            "/book/{id}": "Delete a book by ID",
            "/docs": "API documentation"
        }
    }


@app.get("/search", tags=["searchServices"])
async def search_books(
        q: str = Query(..., description="Enter search term", examples=["gentleman"]),
        limit: int = Query(5, ge=1, le=50, description="Number of results to return")
):
    """Search for books using multi-field matching with custom analyzer"""
    query = {
        "size": limit,
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["title^3", "tags^2", "synopsis"]
            }
        },
        "_source": ["title", "author", "published_year", "genres", "synopsis", "language"],
        "highlight": {
            "fields": {
                "title": {},
                "synopsis": {}
            }
        }
    }
    try:
        res = es.search(index="ebooks", body=query)
        results = []
        for hit in res["hits"]["hits"]:
            result = hit["_source"]
            result["_id"] = hit["_id"]
            result["_score"] = hit["_score"]
            if "highlight" in hit:
                result["_highlight"] = hit["highlight"]
            results.append(result)
        return {
            "total": res["hits"]["total"]["value"],
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/book", tags=["bookManagement"], response_model=BookResponse)
async def add_book(book: Book = Body(..., examples=[{
    "title": "1984",
    "author": "George Orwell",
    "language": "en",
    "published_year": 1949,
    "genres": ["Dystopian", "Science Fiction", "Political Fiction"],
    "synopsis": "A dystopian social science fiction novel and cautionary tale about the dangers of totalitarianism.",
    "tags": ["dystopia", "surveillance", "totalitarianism", "classic"],
    "file_url": "https://openlibrary.org/works/OL1168007W"
}])):
    """Add a new book to the index"""
    try:
        # Generate document ID from title (you can also use UUID)
        import hashlib
        doc_id = hashlib.md5(book.title.encode()).hexdigest()[:12]

        # Index the document
        response = es.index(
            index="ebooks",
            id=doc_id,
            document=book.model_dump()
        )

        return BookResponse(
            success=True,
            message=f"Book '{book.title}' added successfully",
            book_id=doc_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add book: {str(e)}")


@app.get("/book/{book_id}", tags=["bookManagement"])
async def get_book(book_id: str):
    """Retrieve a specific book by ID"""
    try:
        result = es.get(index="ebooks", id=book_id)
        return {
            "id": result["_id"],
            "found": result["found"],
            "data": result["_source"]
        }
    except Exception as e:
        if "NotFoundError" in str(type(e).__name__):
            raise HTTPException(status_code=404, detail=f"Book with ID '{book_id}' not found")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve book: {str(e)}")


@app.delete("/book/{book_id}", tags=["bookManagement"])
async def delete_book(book_id: str):
    """Delete a book by ID"""
    try:
        result = es.delete(index="ebooks", id=book_id)
        return {
            "success": True,
            "message": f"Book with ID '{book_id}' deleted successfully",
            "result": result["result"]
        }
    except Exception as e:
        if "NotFoundError" in str(type(e).__name__):
            raise HTTPException(status_code=404, detail=f"Book with ID '{book_id}' not found")
        raise HTTPException(status_code=500, detail=f"Failed to delete book: {str(e)}")


@app.get("/stats", tags=["info"])
async def get_stats():
    """Get index statistics"""
    try:
        count = es.count(index="ebooks")
        health = es.cluster.health()
        return {
            "index": "ebooks",
            "document_count": count["count"],
            "cluster_status": health["status"],
            "number_of_nodes": health["number_of_nodes"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)