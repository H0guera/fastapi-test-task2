import sqlalchemy as sa

from test_app.settings import settings

meta = sa.MetaData(naming_convention=settings.naming_conventions)
