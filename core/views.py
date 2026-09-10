from django.http import JsonResponse, HttpResponse
from django.shortcuts import render


def home(request):
    """Page d'accueil minimale."""
    html = """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>School Management</title>
  <style>
    body{font-family:system-ui,sans-serif;max-width:720px;margin:3rem auto;padding:0 1rem;color:#222}
    h1{color:#2c5282}
    code{background:#f4f4f4;padding:2px 6px;border-radius:4px}
    ul{line-height:1.8}
    .ok{color:#16a34a;font-weight:600}
  </style>
</head>
<body>
  <h1>🏫 School Management</h1>
  <p class="ok">✅ L'application tourne correctement sur Render.</p>
  <ul>
    <li><a href="/admin/">Administration Django</a> (/admin/)</li>
    <li><a href="/health/">Health check</a> (/health/)</li>
    <li><a href="/api/">API REST</a> (/api/)</li>
  </ul>
  <p>Pour configurer: définissez les variables d'environnement
     <code>SECRET_KEY</code>, <code>DATABASE_URL</code> (PostgreSQL Render),
     et passez <code>DEBUG=False</code> en production.</p>
</body>
</html>"""
    return HttpResponse(html)


def health(request):
    """Health check pour Render."""
    return JsonResponse({
        "status": "ok",
        "service": "school-management",
    })


def api_root(request):
    return JsonResponse({
        "service": "school-management",
        "version": "1.0",
        "endpoints": {
            "health": "/api/health/",
            "admin": "/admin/",
        },
    })
