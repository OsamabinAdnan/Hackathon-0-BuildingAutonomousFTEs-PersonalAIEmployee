"""
LinkedIn Auto-Poster - Automated LinkedIn posting for business/sales.

This module provides automated LinkedIn posting capabilities:
- Scheduled business posts
- Engagement tracking
- Post templates
- Content suggestions

Usage:
    # Post directly
    python -m integrations.linkedin_poster --post "Excited to announce..."

    # Post from template
    python -m integrations.linkedin_poster --template product_launch --product "AI Assistant"

    # Schedule post (via external scheduler)
    python -m integrations.linkedin_poster --post "..." --schedule
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('integrations.linkedin_poster')


class LinkedInPoster:
    """
    LinkedIn Auto-Poster for business/sales posts.

    Provides automated posting with templates and scheduling support.
    """

    # Post templates
    TEMPLATES = {
        'product_launch': """
🚀 Excited to announce {product}!

{description}

This is a game-changer for {target_audience}.

Key features:
{features}

Learn more: {link}

#Innovation #Tech #ProductLaunch
        """.strip(),

        'milestone': """
🎉 Milestone Alert!

We've reached {milestone}!

This wouldn't be possible without:
✅ Our amazing team
✅ Our supportive customers
✅ Our partners

Thank you for being part of this journey!

#Growth #Success #ThankYou
        """.strip(),

        'tip': """
💡 {tip_title}

{tip_content}

What's your take? Share your thoughts below!

#Tips #{industry} #ProfessionalDevelopment
        """.strip(),

        'industry_news': """
📰 Industry Update: {news_title}

{news_summary}

My take: {my_take}

What do you think about this development?

#IndustryNews #{industry} #Trends
        """.strip(),

        'team_announcement': """
👥 Team Update!

{announcement}

We're growing! If you're passionate about {focus_area}, we'd love to hear from you.

#Hiring #Team #Careers
        """.strip(),

        'customer_success': """
⭐ Customer Success Story

{customer_name} achieved {achievement} using {product}!

"{testimonial}"

Results:
{results}

#CustomerSuccess #CaseStudy #Results
        """.strip(),

        'weekly_update': """
📊 Weekly Update - {week_ending}

Highlights:
{highlights}

Looking ahead: {next_week_goals}

#WeeklyUpdate #Progress #Goals
        """.strip(),
    }

    def __init__(self, vault_path: str = './AI_Employee_Vault_FTE'):
        """
        Initialize the LinkedIn poster.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.posts_dir = self.vault_path / 'LinkedIn_Posts'
        self.analytics_dir = self.posts_dir / 'analytics'

        # Ensure directories exist
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        # LinkedIn service
        self._linkedin_service = None

        # Dry run mode
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

        # Organization ID for company posts
        self.org_id = os.getenv('LINKEDIN_ORG_ID')

        logger.info(f'LinkedIn Poster initialized')
        logger.info(f'  Posts directory: {self.posts_dir}')
        logger.info(f'  Organization ID: {self.org_id or "Not set"}')

    @property
    def linkedin_service(self):
        """Get LinkedIn service lazily."""
        if self._linkedin_service is None:
            from mcp_server.linkedin_service import LinkedInService
            self._linkedin_service = LinkedInService(vault_path=str(self.vault_path))
        return self._linkedin_service

    def list_templates(self) -> List[str]:
        """Get list of available templates."""
        return list(self.TEMPLATES.keys())

    def get_template(self, template_name: str) -> Optional[str]:
        """
        Get a template by name.

        Args:
            template_name: Name of the template

        Returns:
            Template string or None if not found
        """
        return self.TEMPLATES.get(template_name)

    def fill_template(self, template_name: str, **kwargs) -> str:
        """
        Fill a template with provided values.

        Args:
            template_name: Name of the template
            **kwargs: Values to fill in the template

        Returns:
            Filled template string
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        # Fill in the template
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required field for template: {e}")

    async def post(
        self,
        text: str,
        visibility: str = "PUBLIC",
        as_organization: bool = False
    ) -> Dict[str, Any]:
        """
        Post to LinkedIn.

        Args:
            text: Post text content
            visibility: Post visibility ("PUBLIC" or "CONNECTIONS")
            as_organization: Post as organization instead of personal

        Returns:
            Result dict with success status and post ID
        """
        logger.info(f"Posting to LinkedIn...")
        logger.info(f"  Visibility: {visibility}")
        logger.info(f"  As organization: {as_organization}")

        # Determine which service method to use
        if as_organization:
            if not self.org_id:
                logger.error("Organization ID not configured")
                return {'success': False, 'error': 'Organization ID not configured'}
            result = await self.linkedin_service.post_organization_share(
                text=text,
                visibility=visibility
            )
        else:
            result = await self.linkedin_service.post_share(
                text=text,
                visibility=visibility
            )

        # Save post record
        if result.get('success') or self.dry_run:
            self._save_post_record(text, result, as_organization)

        return result

    async def post_from_template(
        self,
        template_name: str,
        as_organization: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post using a template.

        Args:
            template_name: Name of the template
            as_organization: Post as organization
            **kwargs: Values for the template

        Returns:
            Result dict with success status
        """
        # Fill template
        text = self.fill_template(template_name, **kwargs)
        logger.info(f"Using template: {template_name}")

        # Post
        return await self.post(text, as_organization=as_organization)

    def _save_post_record(
        self,
        text: str,
        result: Dict[str, Any],
        as_organization: bool
    ):
        """
        Save a record of the posted content.

        Args:
            text: Post text
            result: Result from posting
            as_organization: Whether posted as organization
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'POST_{timestamp}.md'
        filepath = self.posts_dir / filename

        content = f'''---
type: linkedin_post
created: {datetime.now().isoformat()}
post_id: {result.get('post_id', 'N/A')}
as_organization: {as_organization}
success: {result.get('success', False)}
dry_run: {result.get('dry_run', False)}
---

# LinkedIn Post

## Post Details
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Post ID:** {result.get('post_id', 'N/A')}
- **As Organization:** {as_organization}
- **Status:** {'Dry Run' if result.get('dry_run') else ('Success' if result.get('success') else 'Failed')}

## Content

{text}

## Analytics
_Post analytics will be updated here after 24 hours_

---
*Auto-generated by LinkedIn Poster*
'''

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Post record saved: {filepath}")

    def get_post_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get history of posted content.

        Args:
            limit: Maximum number of posts to return

        Returns:
            List of post records
        """
        posts = []
        for post_file in sorted(self.posts_dir.glob('POST_*.md'), reverse=True)[:limit]:
            try:
                content = post_file.read_text(encoding='utf-8')
                # Parse frontmatter
                if '---' in content:
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        import re
                        frontmatter = parts[1]
                        # Extract fields
                        post = {
                            'file': post_file.name,
                            'created': re.search(r'created:\s*(.+)', frontmatter).group(1) if re.search(r'created:\s*(.+)', frontmatter) else None,
                            'post_id': re.search(r'post_id:\s*(.+)', frontmatter).group(1) if re.search(r'post_id:\s*(.+)', frontmatter) else None,
                            'success': 'true' in (re.search(r'success:\s*(.+)', frontmatter).group(1) if re.search(r'success:\s*(.+)', frontmatter) else 'false').lower(),
                        }
                        posts.append(post)
            except Exception as e:
                logger.debug(f"Error reading post file {post_file}: {e}")

        return posts

    def suggest_content(self, category: str = 'general') -> List[str]:
        """
        Suggest content ideas for posting.

        Args:
            category: Content category

        Returns:
            List of content suggestions
        """
        suggestions = {
            'general': [
                "Share a recent win or achievement",
                "Post a tip or insight from your work",
                "Highlight a team member's contribution",
                "Share industry news with your perspective",
                "Ask a thought-provoking question",
            ],
            'sales': [
                "Share a customer success story",
                "Post about a product feature",
                "Highlight a problem you solve",
                "Share a case study or testimonial",
                "Announce a new offering",
            ],
            'thought_leadership': [
                "Share your prediction for the industry",
                "Post a contrarian viewpoint",
                "Share lessons from a recent challenge",
                "Offer advice for professionals in your field",
                "Share a framework or methodology",
            ],
            'engagement': [
                "Ask a poll question",
                "Share a controversial opinion (respectfully)",
                "Post a 'day in the life' update",
                "Share something you've learned recently",
                "Celebrate a milestone",
            ],
        }

        return suggestions.get(category, suggestions['general'])


async def main_async():
    """Async main entry point."""
    parser = argparse.ArgumentParser(
        description='LinkedIn Auto-Poster - Automated LinkedIn posting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Post directly
    python -m integrations.linkedin_poster --post "Excited to share..."

    # Post from template
    python -m integrations.linkedin_poster --template tip --tip-title "Productivity Hack" --tip-content "..."

    # Post as organization
    python -m integrations.linkedin_poster --post "Company update" --org

    # List templates
    python -m integrations.linkedin_poster --list-templates

    # Get content suggestions
    python -m integrations.linkedin_poster --suggest sales
        """
    )

    parser.add_argument(
        '--vault-path',
        type=str,
        default='./AI_Employee_Vault_FTE',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--post',
        type=str,
        help='Post text content'
    )
    parser.add_argument(
        '--template',
        type=str,
        help='Template name to use'
    )
    parser.add_argument(
        '--org',
        action='store_true',
        help='Post as organization'
    )
    parser.add_argument(
        '--visibility',
        type=str,
        default='PUBLIC',
        choices=['PUBLIC', 'CONNECTIONS'],
        help='Post visibility'
    )
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='List available templates'
    )
    parser.add_argument(
        '--suggest',
        type=str,
        nargs='?',
        const='general',
        help='Get content suggestions (optional category)'
    )
    parser.add_argument(
        '--history',
        action='store_true',
        help='Show post history'
    )

    # Template-specific arguments (will be passed to template)
    args, template_args = parser.parse_known_args()

    poster = LinkedInPoster(vault_path=args.vault_path)

    # Handle list templates
    if args.list_templates:
        print("\nAvailable Templates:")
        print("=" * 50)
        for name in poster.list_templates():
            print(f"  - {name}")
        print("\nUse --template <name> with required arguments")
        return

    # Handle suggestions
    if args.suggest is not None:
        suggestions = poster.suggest_content(args.suggest)
        print(f"\nContent Suggestions ({args.suggest}):")
        print("=" * 50)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        print("")
        return

    # Handle history
    if args.history:
        history = poster.get_post_history()
        print("\nPost History:")
        print("=" * 50)
        for post in history:
            print(f"  - {post.get('created', 'Unknown')}: {post.get('post_id', 'N/A')} ({'Success' if post.get('success') else 'Failed'})")
        print("")
        return

    # Handle direct post
    if args.post:
        result = await poster.post(
            text=args.post,
            visibility=args.visibility,
            as_organization=args.org
        )

        if result.get('success'):
            if result.get('dry_run'):
                print("[DRY RUN] Post would be created")
            else:
                print(f"Post created successfully! ID: {result.get('post_id', 'N/A')}")
        else:
            print(f"Failed to post: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        return

    # Handle template post
    if args.template:
        # Parse template arguments
        template_kwargs = {}
        for arg in template_args:
            if arg.startswith('--'):
                key_value = arg[2:].split('=', 1)
                if len(key_value) == 2:
                    template_kwargs[key_value[0]] = key_value[1]
                else:
                    # Next arg is the value
                    continue

        # Also check remaining args
        i = 0
        while i < len(template_args):
            arg = template_args[i]
            if arg.startswith('--') and '=' not in arg:
                key = arg[2:]
                if i + 1 < len(template_args) and not template_args[i + 1].startswith('--'):
                    template_kwargs[key] = template_args[i + 1]
                    i += 2
                    continue
            i += 1

        try:
            result = await poster.post_from_template(
                template_name=args.template,
                as_organization=args.org,
                **template_kwargs
            )

            if result.get('success'):
                if result.get('dry_run'):
                    print("[DRY RUN] Post would be created from template")
                else:
                    print(f"Post created from template! ID: {result.get('post_id', 'N/A')}")
            else:
                print(f"Failed to post: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        return

    # No action specified
    parser.print_help()


def main():
    """Main entry point."""
    import asyncio
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
