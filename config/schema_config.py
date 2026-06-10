# =============================================================================
# Keys used by the recommender's return-dict shape.
#
# Historically these were IMDB CSV column names. The app is now live on TMDB and
# no longer reads a dataset, but these three keys are the agreed contract between
# `core/movie_recommender.py` (producer) and `crew/crew.py` / `graph/nodes.py`
# (consumers), so they are kept as a single source of truth.
# =============================================================================

COL_TITLE    = "Series_Title"
COL_RATING   = "IMDB_Rating"
COL_DIRECTOR = "Director"
