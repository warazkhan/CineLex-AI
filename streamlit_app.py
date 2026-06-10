"""Thin launcher for the CineLex AI Streamlit UI.

The actual UI lives in the ``ui/`` package (see ``ui/app.py``). This file is
kept at the repository root so existing run commands and deployment manifests
keep working:

    streamlit run streamlit_app.py

Referenced by docker-compose.yml, k8s/*/06-streamlit-deployment.yaml and the
README — do not rename without updating those.
"""
from ui.app import main

main()
