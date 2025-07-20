from src.app.db.views import router as db_router
from src.app.address.views import router as address_router
from src.app.auth.views import router as auth_router
from src.app.aulet.views import router as aulet_router
from src.app.tree.views import router as tree_router
from src.app.ticket.views import router as ticket_router
from src.app.pages.views import router as pages_router
from src.app.page_news.views import router as page_news_router
from src.app.page_popular_peoples.views import router as page_popular_peoples_router


def init_app(app):
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(address_router, prefix="/address", tags=["address"])
    app.include_router(tree_router, prefix="/tree", tags=["tree"])
    app.include_router(pages_router, prefix="/pages", tags=["pages"])
    app.include_router(page_news_router, prefix="/page_news", tags=["page_news"])
    app.include_router(page_popular_peoples_router, prefix="/page_popular_peoples", tags=["page_popular_peoples"])
    app.include_router(ticket_router, prefix="/ticket", tags=["ticket"])
    app.include_router(aulet_router, prefix="/aulet", tags=["menin-auletim"])
    app.include_router(db_router, prefix="/db", tags=["db"])
    return app

