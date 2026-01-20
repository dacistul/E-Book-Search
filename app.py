import warnings

import urllib3
from elasticsearch import Elasticsearch
from fastapi import FastAPI, Query, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

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
        .btn.execute { background-color: #27ae60 !important; color: white !important; }
    </style>
    """
    return HTMLResponse(content=content.replace("</head>", f"{custom_css}</head>"))


@app.get("/search", tags=["Search Services"])
async def search_books(
        q: str = Query(..., description="Enter search term", examples=["gentleman"]),
        limit: int = Query(5, ge=1, le=50)
):
    query = {
        "size": limit,
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["title^3", "tags^2", "synopsis"]
            }
        }
    }
    try:
        res = es.search(index="ebooks", body=query)
        return [hit["_source"] for hit in res["hits"]["hits"]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)