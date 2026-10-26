#!/usr/bin/env python3
"""The Job schema — one normalized shape every source produces."""


def job(id, title, company, location, url, date="", source="", description=""):
    """Build a normalized job dict.

    Fields:
      id          unique, source-namespaced (e.g. "linkedin:123", "gh:acme:45")
      title       job title
      company     employer name
      location    free-text location
      url         link to the posting
      date        "YYYY-MM-DD" when known, else ""
      source      which connector produced it (e.g. "linkedin", "greenhouse")
      description full text when available (used by keyword filtering)
    """
    return {
        "id": str(id),
        "title": title or "",
        "company": company or "",
        "location": location or "",
        "url": url or "",
        "date": date or "",
        "source": source or "",
        "description": description or "",
    }
