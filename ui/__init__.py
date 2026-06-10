"""CineLex AI — Streamlit UI package.

The web front-end is split into small, single-responsibility modules:

    ui/
      app.py            # main() — orchestrates the page
      config.py         # constants (API URL, page config, suggestions)
      state.py          # session-state initialisation
      api_client.py     # all HTTP calls to the FastAPI backend
      styles.py         # injects assets/styles.css
      search_handler.py # glue between UI events, the API and session state
      assets/           # styles.css
      components/        # sidebar / hero / search / suggestions / results

The repository root keeps a thin ``streamlit_app.py`` launcher so existing
Docker, docker-compose and Kubernetes references continue to work.
"""
