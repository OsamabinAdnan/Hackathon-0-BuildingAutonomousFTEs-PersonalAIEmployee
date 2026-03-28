"""
Direct Executor - Fallback executor for MCP actions.

This module provides a fallback mechanism for executing external actions
when the MCP server is unavailable or fails. Used as a safety net.

Primary path: Claude Code → MCP Server
Fallback: Claude Code → Direct Executor (if MCP fails)

Usage:
    from mcp_server.direct_executor import DirectExecutor

    executor = DirectExecutor()

    # Send email (fallback if MCP fails)
    result = await executor.send_email(
        to="recipient@example.com",
        subject="Test",
        body="Hello!"
    )

    # Send WhatsApp
    result = executor.send_whatsapp(
        contact="John Doe",
        message="Hello from AI Employee!"
    )

    # Post to LinkedIn
    result = await executor.post_linkedin(
        text="Excited to share this update!"
    )
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger('mcp_server.direct_executor')


class DirectExecutor:
    """
    Direct executor for MCP actions (fallback mode).

    Provides simple methods for executing external actions when
    the MCP server is unavailable or fails.
    """

    def __init__(self, vault_path: str = './AI_Employee_Vault_FTE'):
        """
        Initialize the direct executor.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = vault_path
        self._email_service = None
        self._whatsapp_service = None
        self._linkedin_service = None
        logger.info('Direct Executor initialized (fallback mode)')

    @property
    def email_service(self):
        """Get email service lazily."""
        if self._email_service is None:
            from .email_service import EmailService
            self._email_service = EmailService(vault_path=self.vault_path)
        return self._email_service

    @property
    def whatsapp_service(self):
        """Get WhatsApp service lazily."""
        if self._whatsapp_service is None:
            from .whatsapp_service import WhatsAppService
            self._whatsapp_service = WhatsAppService(vault_path=self.vault_path)
        return self._whatsapp_service

    @property
    def linkedin_service(self):
        """Get LinkedIn service lazily."""
        if self._linkedin_service is None:
            from .linkedin_service import LinkedInService
            self._linkedin_service = LinkedInService(vault_path=self.vault_path)
        return self._linkedin_service

    # ========================================
    # Email Actions
    # ========================================

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        """
        Send an email (fallback method).

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: Optional CC (comma-separated)
            bcc: Optional BCC (comma-separated)
            html: Whether body is HTML

        Returns:
            Result dict with success status
        """
        logger.info(f"[FALLBACK] Sending email to: {to}")

        cc_list = [e.strip() for e in cc.split(',')] if cc else None
        bcc_list = [e.strip() for e in bcc.split(',')] if bcc else None

        try:
            result = await self.email_service.send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc_list,
                bcc=bcc_list,
                html=html
            )

            if result.get('success'):
                logger.info(f"[FALLBACK] Email sent successfully to {to}")
            else:
                logger.error(f"[FALLBACK] Failed to send email: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"[FALLBACK] Email execution error: {e}")
            return {'success': False, 'error': str(e), 'fallback': True}

    async def create_email_draft(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> Dict[str, Any]:
        """
        Create an email draft (fallback method).

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether body is HTML

        Returns:
            Result dict with draft ID
        """
        logger.info(f"[FALLBACK] Creating draft to: {to}")

        try:
            result = await self.email_service.create_draft(
                to=to,
                subject=subject,
                body=body,
                html=html
            )
            return result
        except Exception as e:
            logger.error(f"[FALLBACK] Draft creation error: {e}")
            return {'success': False, 'error': str(e), 'fallback': True}

    # ========================================
    # WhatsApp Actions
    # ========================================

    def send_whatsapp(
        self,
        contact: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message (fallback method).

        Args:
            contact: Contact name or phone number
            message: Message text

        Returns:
            Result dict with success status
        """
        logger.info(f"[FALLBACK] Sending WhatsApp to: {contact}")

        try:
            result = self.whatsapp_service.send_message(
                contact=contact,
                message=message
            )

            if result.get('success'):
                logger.info(f"[FALLBACK] WhatsApp sent successfully to {contact}")
            else:
                logger.error(f"[FALLBACK] Failed to send WhatsApp: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"[FALLBACK] WhatsApp execution error: {e}")
            return {'success': False, 'error': str(e), 'fallback': True}

    # ========================================
    # LinkedIn Actions
    # ========================================

    async def post_linkedin(
        self,
        text: str,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """
        Post to LinkedIn (fallback method).

        Args:
            text: Post text content
            visibility: "PUBLIC" or "CONNECTIONS"

        Returns:
            Result dict with post ID
        """
        logger.info(f"[FALLBACK] Posting to LinkedIn: {text[:50]}...")

        try:
            result = await self.linkedin_service.post_share(
                text=text,
                visibility=visibility
            )

            if result.get('success'):
                logger.info(f"[FALLBACK] LinkedIn post created successfully")
            else:
                logger.error(f"[FALLBACK] Failed to post to LinkedIn: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"[FALLBACK] LinkedIn post error: {e}")
            return {'success': False, 'error': str(e), 'fallback': True}

    async def post_linkedin_organization(
        self,
        text: str,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """
        Post to LinkedIn on behalf of organization (fallback method).

        Args:
            text: Post text content
            visibility: "PUBLIC" or "CONNECTIONS"

        Returns:
            Result dict with post ID
        """
        logger.info(f"[FALLBACK] Posting to LinkedIn organization")

        try:
            result = await self.linkedin_service.post_organization_share(
                text=text,
                visibility=visibility
            )
            return result
        except Exception as e:
            logger.error(f"[FALLBACK] LinkedIn org post error: {e}")
            return {'success': False, 'error': str(e), 'fallback': True}

    async def send_linkedin_message(
        self,
        user_urn: str,
        message: str,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a LinkedIn message (fallback method).

        Args:
            user_urn: Recipient URN
            message: Message text
            subject: Optional subject

        Returns:
            Result dict with success status
        """
        logger.info(f"[FALLBACK] Sending LinkedIn message to: {user_urn}")

        try:
            result = await self.linkedin_service.send_message(
                recipient_urn=user_urn,
                message=message,
                subject=subject
            )
            return result
        except Exception as e:
            logger.error(f"[FALLBACK] LinkedIn message error: {e}")
            return {'success': False, 'error': str(e), 'fallback': True}

    async def get_linkedin_profile(self) -> Dict[str, Any]:
        """
        Get LinkedIn profile (fallback method).

        Returns:
            Result dict with profile data
        """
        try:
            return await self.linkedin_service.get_profile()
        except Exception as e:
            logger.error(f"[FALLBACK] Get profile error: {e}")
            return {'success': False, 'error': str(e), 'fallback': True}

    # ========================================
    # Utility Methods
    # ========================================

    def check_services(self) -> Dict[str, bool]:
        """
        Check which services are available.

        Returns:
            Dict with service availability status
        """
        status = {}

        # Check email service
        try:
            import os
            from pathlib import Path
            token_path = os.getenv('GMAIL_TOKEN_PATH', './credentials/gmail_token.json')
            if not Path(token_path).is_absolute():
                token_path = str(Path(self.vault_path).parent / token_path)
            status['email'] = Path(token_path).exists()
        except Exception:
            status['email'] = False

        # Check WhatsApp service
        try:
            session_path = os.getenv('WHATSAPP_SESSION_PATH', './sessions/whatsapp')
            if not Path(session_path).is_absolute():
                session_path = str(Path(self.vault_path).parent / session_path)
            status['whatsapp'] = Path(session_path).exists()
        except Exception:
            status['whatsapp'] = False

        # Check LinkedIn service
        status['linkedin'] = bool(os.getenv('LINKEDIN_ACCESS_TOKEN'))

        return status
