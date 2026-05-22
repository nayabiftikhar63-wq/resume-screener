"""Aggregates every route module so ``app.main`` can include them in one go."""

from . import applications, emails, jobs, screening, stats

__all__ = ["applications", "emails", "jobs", "screening", "stats"]
