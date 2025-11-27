FROM postgres:15

ENV POSTGRES_USER=scraper \
    POSTGRES_PASSWORD=scraper \
    POSTGRES_DB=scraper

COPY db/migrations /docker-entrypoint-initdb.d

