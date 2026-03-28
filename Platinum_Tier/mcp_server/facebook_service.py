"""
Facebook Service - Connect to Facebook via Graph API.

This service provides Facebook capabilities:
- Post to Facebook Page
- Send/receive messages
- Get insights/analytics

Usage:
    from mcp_server.facebook_service import FacebookService
    
    service = FacebookService(
        app_id="your_app_id",
        app_secret="your_app_secret",
        access_token="your_access_token",
        page_id="your_page_id"
    )
    
    # Post to Facebook
    result = await service.post_facebook(
        message="Hello from AI Employee!",
        image_url="https://example.com/image.jpg"
    )
"""

import logging
import os
import urllib.request
import urllib.error
import json
from typing import Optional, Dict, Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('mcp_server.facebook')


class FacebookService:
    """
    Facebook service using Graph API.
    
    Provides posting and messaging capabilities via Facebook Page.
    """

    API_BASE = 'https://graph.facebook.com/v18.0'

    def __init__(
        self,
        app_id: str = None,
        app_secret: str = None,
        access_token: str = None,
        page_id: str = None
    ):
        """
        Initialize Facebook service.

        Args:
            app_id: Facebook App ID
            app_secret: Facebook App Secret
            access_token: Page Access Token
            page_id: Facebook Page ID
        """
        self.app_id = app_id or os.getenv('FACEBOOK_APP_ID')
        self.app_secret = app_secret or os.getenv('FACEBOOK_APP_SECRET')
        self.access_token = access_token or os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = page_id or os.getenv('FACEBOOK_PAGE_ID')
        
        # Dry run mode
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        
        logger.info(f'Facebook Service initialized')
        logger.info(f'  App ID: {self.app_id or "Not set"}')
        logger.info(f'  Page ID: {self.page_id or "Not set"}')
        logger.info(f'  Access Token: {"Configured" if self.access_token else "Not set"}')
        logger.info(f'  Dry Run: {self.dry_run}')

    def _check_credentials(self) -> bool:
        """Check if credentials are configured."""
        if not self.access_token:
            logger.error('Facebook access token not configured')
            logger.error('Set FACEBOOK_ACCESS_TOKEN in .env file')
            return False
        if not self.page_id:
            logger.error('Facebook Page ID not configured')
            logger.error('Set FACEBOOK_PAGE_ID in .env file')
            return False
        return True

    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict] = None,
        use_access_token: bool = True
    ) -> Dict[str, Any]:
        """
        Make request to Facebook Graph API.

        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request body
            use_access_token: Include access token in request

        Returns:
            JSON response or error dict
        """
        if use_access_token and self.access_token:
            separator = '&' if '?' in endpoint else '?'
            endpoint = f"{endpoint}{separator}access_token={self.access_token}"

        url = f'{self.API_BASE}/{endpoint}'

        try:
            if data and method.upper() == 'POST':
                body = urllib.parse.urlencode(data).encode('utf-8')
                req = urllib.request.Request(url, data=body, method=method)
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            else:
                req = urllib.request.Request(url, method=method)

            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            logger.error(f'Facebook API error: {e.code} - {error_body}')
            try:
                error_data = json.loads(error_body)
                return {'error': f'HTTP {e.code}: {error_data.get("error", {}).get("message", e.reason)}'}
            except:
                return {'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            logger.error(f'Facebook API request failed: {e}')
            return {'error': str(e)}

    async def post_facebook(
        self,
        message: str,
        image_url: Optional[str] = None,
        link: Optional[str] = None,
        scheduled_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post to Facebook Page.

        Args:
            message: Post text content
            image_url: Optional image URL
            link: Optional link to share
            scheduled_time: Optional scheduled publish time (ISO 8601)

        Returns:
            Dict with post_id and status
        """
        # Import audit logger
        from audit.logger import get_audit_logger
        audit_logger = get_audit_logger()
        
        if self.dry_run:
            logger.info(f'[DRY RUN] Would post to Facebook: {message[:50]}...')
            audit_logger.log_facebook_post(
                post_id='DRY_RUN',
                message=message,
                status='success',
                error=None
            )
            return {
                'success': True,
                'dry_run': True,
                'message': message[:50],
                'page_id': self.page_id
            }

        if not self._check_credentials():
            audit_logger.log_facebook_post(
                post_id='FAILED',
                message=message,
                status='error',
                error='Credentials not configured'
            )
            return {'success': False, 'error': 'Credentials not configured'}

        try:
            endpoint = f'/{self.page_id}/feed'
            
            data = {
                'message': message
            }

            if image_url:
                data['link'] = image_url
            
            if link:
                data['link'] = link
            
            if scheduled_time:
                data['published'] = 'false'
                data['scheduled_publish_time'] = scheduled_time

            result = self._make_request(endpoint, method='POST', data=data)

            if 'error' in result:
                audit_logger.log_facebook_post(
                    post_id='ERROR',
                    message=message,
                    status='error',
                    error=result['error']
                )
                return {'success': False, 'error': result['error']}

            logger.info(f'Facebook post created: {result.get("id")}')
            
            # Log to audit
            audit_logger.log_facebook_post(
                post_id=result.get('id', 'UNKNOWN'),
                message=message,
                status='success',
                error=None
            )
            
            return {
                'success': True,
                'post_id': result.get('id'),
                'page_id': self.page_id
            }

        except Exception as e:
            logger.error(f'Failed to post to Facebook: {e}')
            audit_logger.log_facebook_post(
                post_id='ERROR',
                message=message,
                status='error',
                error=str(e)
            )
            return {'success': False, 'error': str(e)}

    async def post_photo(
        self,
        photo_url: str,
        message: str = None
    ) -> Dict[str, Any]:
        """
        Post a photo to Facebook Page.

        Args:
            photo_url: URL of the photo
            message: Optional caption

        Returns:
            Dict with post_id and status
        """
        if self.dry_run:
            logger.info(f'[DRY RUN] Would post photo to Facebook: {photo_url}')
            return {'success': True, 'dry_run': True, 'photo_url': photo_url}

        if not self._check_credentials():
            return {'success': False, 'error': 'Credentials not configured'}

        try:
            endpoint = f'/{self.page_id}/photos'
            
            data = {
                'url': photo_url
            }
            
            if message:
                data['message'] = message

            result = self._make_request(endpoint, method='POST', data=data)

            if 'error' in result:
                return {'success': False, 'error': result['error']}

            logger.info(f'Facebook photo post created: {result.get("id")}')
            return {
                'success': True,
                'post_id': result.get('id'),
                'photo_id': result.get('id')
            }

        except Exception as e:
            logger.error(f'Failed to post photo to Facebook: {e}')
            return {'success': False, 'error': str(e)}

    async def send_facebook_message(
        self,
        recipient_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a message via Facebook Page Messenger.

        Args:
            recipient_id: Recipient's Facebook user ID
            message: Message text

        Returns:
            Dict with status
        """
        if self.dry_run:
            logger.info(f'[DRY RUN] Would send Facebook message to {recipient_id}')
            return {
                'success': True,
                'dry_run': True,
                'recipient': recipient_id
            }

        if not self._check_credentials():
            return {'success': False, 'error': 'Credentials not configured'}

        try:
            # Use Send API
            endpoint = f'/me/messages'
            
            data = {
                'recipient': json.dumps({'id': recipient_id}),
                'message': json.dumps({'text': message}),
                'messaging_type': 'RESPONSE'
            }

            result = self._make_request(endpoint, method='POST', data=data)

            if 'error' in result:
                return {'success': False, 'error': result['error']}

            logger.info(f'Facebook message sent to {recipient_id}')
            return {
                'success': True,
                'message_id': result.get('message_id')
            }

        except Exception as e:
            logger.error(f'Failed to send Facebook message: {e}')
            return {'success': False, 'error': str(e)}

    async def get_facebook_insights(
        self,
        metric: str = 'page_impressions_unique',
        period: str = 'day'
    ) -> Dict[str, Any]:
        """
        Get Facebook Page insights/analytics.

        Args:
            metric: Metric to fetch (e.g., page_impressions_unique, page_engaged_users)
            period: Time period (day, week, month, lifetime)

        Returns:
            Dict with insights data
        """
        if self.dry_run:
            return {
                'success': True,
                'dry_run': True,
                'insights': {metric: 0}
            }

        if not self._check_credentials():
            return {'success': False, 'error': 'Credentials not configured'}

        try:
            endpoint = f'/{self.page_id}/insights'
            
            params = {
                'metric': metric,
                'period': period
            }

            result = self._make_request(endpoint, method='GET', data=params)

            if 'error' in result:
                return {'success': False, 'error': result['error']}

            # Parse insights
            insights_data = {}
            if 'data' in result:
                for item in result['data']:
                    insights_data[item['name']] = item['values']

            logger.info(f'Facebook insights retrieved')
            return {
                'success': True,
                'insights': insights_data,
                'page_id': self.page_id
            }

        except Exception as e:
            logger.error(f'Failed to get Facebook insights: {e}')
            return {'success': False, 'error': str(e)}

    async def get_page_info(self) -> Dict[str, Any]:
        """
        Get Facebook Page information.

        Returns:
            Dict with page info
        """
        if self.dry_run:
            return {
                'success': True,
                'dry_run': True,
                'page': {'name': 'Test Page', 'id': self.page_id}
            }

        if not self._check_credentials():
            return {'success': False, 'error': 'Credentials not configured'}

        try:
            endpoint = f'/{self.page_id}'
            
            params = {
                'fields': 'id,name,about,followers_count,likes,website'
            }

            result = self._make_request(endpoint, method='GET', data=params)

            if 'error' in result:
                return {'success': False, 'error': result['error']}

            return {
                'success': True,
                'page': result
            }

        except Exception as e:
            logger.error(f'Failed to get page info: {e}')
            return {'success': False, 'error': str(e)}

    async def get_posts(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent posts from Facebook Page.

        Args:
            limit: Number of posts to retrieve

        Returns:
            Dict with posts list
        """
        if self.dry_run:
            return {'success': True, 'dry_run': True, 'posts': []}

        if not self._check_credentials():
            return {'success': False, 'error': 'Credentials not configured'}

        try:
            endpoint = f'/{self.page_id}/feed'
            
            params = {
                'limit': limit
            }

            result = self._make_request(endpoint, method='GET', data=params)

            if 'error' in result:
                return {'success': False, 'error': result['error']}

            posts = result.get('data', [])
            
            return {
                'success': True,
                'posts': posts,
                'count': len(posts)
            }

        except Exception as e:
            logger.error(f'Failed to get posts: {e}')
            return {'success': False, 'error': str(e)}
