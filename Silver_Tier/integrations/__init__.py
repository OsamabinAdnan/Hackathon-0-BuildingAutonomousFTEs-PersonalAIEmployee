"""
Integrations package for AI Employee (Silver Tier).

This package contains external integration modules for automated actions.

Available integrations:
- LinkedInPoster: Automated LinkedIn posting for business/sales

Usage:
    from integrations.linkedin_poster import LinkedInPoster

    poster = LinkedInPoster()
    await poster.post("Excited to share this update!")
"""

from .linkedin_poster import LinkedInPoster

__all__ = ['LinkedInPoster']
