"""
LinkedIn Service - Post to LinkedIn and send messages via API.

This service provides LinkedIn capabilities via the LinkedIn API.
Supports posting shares and sending messages.

Usage:
    from mcp_server.linkedin_service import LinkedInService

    service = LinkedInService()
    await service.post_share(
        text="Hello from AI Employee!",
        visibility="PUBLIC"
    )
"""

import json
import logging
import os
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('mcp_server.linkedin')


class LinkedInService:
    """
    LinkedIn service using LinkedIn API.

    Provides posting and messaging capabilities via LinkedIn API v2.
    """

    API_BASE = 'https://api.linkedin.com/v2'

    def __init__(self, vault_path: str = './AI_Employee_Vault_FTE'):
        """
        Initialize the LinkedIn service.

        Args:
            vault_path: Path to vault (unused, kept for consistency)
        """
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.refresh_token = os.getenv('LINKEDIN_REFRESH_TOKEN')
        self.org_id = os.getenv('LINKEDIN_ORG_ID')

        # Dry run mode
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

        logger.info(f'LinkedIn Service initialized')
        logger.info(f'  Access Token: {"Configured" if self.access_token else "Not set"}')
        logger.info(f'  Org ID: {self.org_id or "Not set"}')

    def _check_token(self) -> bool:
        """Check if access token is configured."""
        if not self.access_token:
            logger.error('LinkedIn access token not configured')
            logger.error('Set LINKEDIN_ACCESS_TOKEN in .env file')
            return False
        return True

    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to LinkedIn API.

        Args:
            endpoint: API endpoint (without base URL)
            method: HTTP method
            data: Request body data

        Returns:
            JSON response or error dict
        """
        if not self._check_token():
            return {'error': 'Access token not configured'}

        url = f'{self.API_BASE}/{endpoint}'

        try:
            req = urllib.request.Request(url, method=method)
            req.add_header('Authorization', f'Bearer {self.access_token}')
            req.add_header('X-Restli-Protocol-Version', '2.0.0')
            req.add_header('Content-Type', 'application/json')

            if data:
                body = json.dumps(data).encode('utf-8')
                response = urllib.request.urlopen(req, body, timeout=30)
            else:
                response = urllib.request.urlopen(req, timeout=30)

            return json.loads(response.read().decode('utf-8'))

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            logger.error(f'LinkedIn API error: {e.code} - {error_body}')
            return {'error': f'HTTP {e.code}: {e.reason}', 'details': error_body}
        except Exception as e:
            logger.error(f'LinkedIn API request failed: {e}')
            return {'error': str(e)}

    async def get_profile(self) -> dict:
        """
        Get current user's LinkedIn profile using OpenID Connect userinfo endpoint.

        Returns:
            Dict with profile data or error
        """
        if self.dry_run:
            return {'success': True, 'dry_run': True, 'profile': 'mock_profile'}

        # Use userinfo endpoint (OpenID Connect) which works with openid + profile scopes
        result = self._make_request('userinfo')

        if 'error' in result:
            logger.error(f"Failed to get profile from userinfo: {result['error']}")
            return {'success': False, 'error': result['error']}

        # Extract Member ID from 'sub' claim
        # The sub field contains the member ID in format like: urn:li:msn:XXXXXXXXXX
        # For posting, we need the person URN format: urn:li:person:XXXXXXXXXX
        sub_claim = result.get('sub', '')
        if not sub_claim:
            return {'success': False, 'error': 'No sub claim in userinfo response'}

        # If sub is already in urn:li:person: format, use as-is
        # Otherwise, extract member ID and construct proper URN
        if sub_claim.startswith('urn:li:person:'):
            member_urn = sub_claim
        elif sub_claim.startswith('urn:li:member:'):
            # Convert member format to person format
            member_id = sub_claim.replace('urn:li:member:', '')
            member_urn = f'urn:li:person:{member_id}'
        elif ':' in sub_claim:
            # If it contains other URN formats, extract the ID part
            parts = sub_claim.split(':')
            if len(parts) >= 3:
                member_id = parts[-1]
                member_urn = f'urn:li:person:{member_id}'
            else:
                # Assume it's just the member ID
                member_urn = f'urn:li:person:{sub_claim}'
        else:
            # Just the member ID, construct URN
            member_urn = f'urn:li:person:{sub_claim}'

        logger.info(f"Retrieved Member URN from userinfo: {member_urn}")

        return {
            'success': True,
            'profile': {
                'id': member_urn,
                'firstName': {'localized': {'en_US': result.get('given_name', 'User')}},
                'lastName': {'localized': {'en_US': result.get('family_name', '')}}
            }
        }

    async def post_share(
        self,
        text: str,
        visibility: str = 'PUBLIC',
        author_urn: Optional[str] = None
    ) -> dict:
        """
        Post a share (text post) to LinkedIn.

        Args:
            text: Post text content
            visibility: Post visibility ('PUBLIC' or 'CONNECTIONS')
            author_urn: Optional author URN (if not provided, uses userinfo to get member ID)

        Returns:
            Dict with success status and post ID or error
        """
        if self.dry_run:
            logger.info(f'[DRY RUN] Would post to LinkedIn: {text[:50]}...')
            return {'success': True, 'dry_run': True, 'text': text[:50]}

        if not self._check_token():
            return {'success': False, 'error': 'Access token not configured'}

        # Get author URN if not provided
        if not author_urn:
            profile = await self.get_profile()
            if not profile.get('success'):
                logger.error(f"Failed to get profile: {profile.get('error')}")
                return {'success': False, 'error': f"Cannot get member ID: {profile.get('error')}"}

            # Extract member ID from profile
            member_id = profile.get('profile', {}).get('id', '')
            if not member_id:
                return {'success': False, 'error': 'No member ID in profile'}

            # Member ID from userinfo has been converted to proper URN format: urn:li:person:XXXXXXX
            author_urn = member_id
            logger.info(f"Using author URN: {author_urn}")

        # Build post body
        post_data = {
            'author': author_urn,
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': text
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': visibility
            }
        }

        logger.info(f"Posting to LinkedIn with author: {author_urn}")

        # Post to LinkedIn
        result = self._make_request('ugcPosts', method='POST', data=post_data)

        if 'error' in result:
            logger.error(f"Failed to create post: {result['error']}")
            return {'success': False, 'error': result['error']}

        logger.info(f'LinkedIn post created successfully')
        return {
            'success': True,
            'post_id': result.get('id', 'unknown'),
            'visibility': visibility
        }

    async def post_organization_share(
        self,
        text: str,
        visibility: str = 'PUBLIC'
    ) -> dict:
        """
        Post a share on behalf of an organization.

        Args:
            text: Post text content
            visibility: Post visibility

        Returns:
            Dict with success status and post ID or error
        """
        if not self.org_id:
            return {'success': False, 'error': 'Organization ID not configured'}

        author_urn = f'urn:li:organization:{self.org_id}'
        return await self.post_share(text, visibility, author_urn)

    async def send_message(
        self,
        recipient_urn: str,
        message: str,
        subject: Optional[str] = None
    ) -> dict:
        """
        Send a LinkedIn message.

        Args:
            recipient_urn: Recipient's URN (e.g., 'urn:li:person:xxx')
            message: Message text
            subject: Optional message subject

        Returns:
            Dict with success status or error
        """
        if self.dry_run:
            logger.info(f'[DRY RUN] Would send LinkedIn message to: {recipient_urn}')
            return {'success': True, 'dry_run': True, 'recipient': recipient_urn}

        if not self._check_token():
            return {'success': False, 'error': 'Access token not configured'}

        # Get current user's URN
        profile = await self.get_profile()
        if not profile.get('success'):
            sender_urn = 'urn:li:person:me'
        else:
            profile_id = profile.get('profile', {}).get('id', 'me')
            sender_urn = f'urn:li:person:{profile_id}'

        # Build message body
        message_data = {
            'recipients': [recipient_urn],
            'subject': subject or 'Message from AI Employee',
            'body': message
        }

        # Send message
        result = self._make_request('messages', method='POST', data=message_data)

        if 'error' in result:
            return {'success': False, 'error': result['error']}

        logger.info(f'LinkedIn message sent to {recipient_urn}')
        return {
            'success': True,
            'recipient': recipient_urn
        }

    async def get_connections(self, start: int = 0, count: int = 10) -> dict:
        """
        Get LinkedIn connections.

        Args:
            start: Start index for pagination
            count: Number of connections to return

        Returns:
            Dict with connections list or error
        """
        if self.dry_run:
            return {'success': True, 'dry_run': True, 'connections': []}

        endpoint = f'connections?start={start}&count={count}'
        result = self._make_request(endpoint)

        if 'error' in result:
            return {'success': False, 'error': result['error']}

        return {'success': True, 'connections': result.get('elements', [])}
