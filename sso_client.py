import os
import urllib.parse
import requests
import jwt
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from typing import Optional, Dict, Any


class StreamlitSSO:
    """
    A reusable Single Sign-On (SSO) client for Streamlit applications.
    Handles secure backend-to-backend token exchange, encrypted local session cookies,
    and Audience-based (aud) token isolation.
    """

    def __init__(self, audience: str, app_url: str, cookie_prefix: str):
        """
        Initialize the SSO Client for a specific application.

        :param audience: The exact app ID defined in the SSO's security.yaml (e.g., "media_intelligence")
        :param app_url: The full URL of this Streamlit app (e.g., "https://catalog.getlinko.com/media-intelligence")
        :param cookie_prefix: A unique string to isolate this app's cookies (e.g., "media_intel_")
        """
        self.audience = audience
        self.app_url = app_url
        self.cookie_prefix = cookie_prefix

        # Load security configuration from Environment Variables (Injected by AWS ECS).
        # No hardcoded fallbacks for secrets — missing vars crash loudly at startup,
        # which is far safer than silently running with a known default.
        self.sso_login_url = os.environ.get("SSO_LOGIN_URL", "https://login.getlinko.com/login")
        self.sso_exchange_url = os.environ.get("SSO_EXCHANGE_URL", "https://login.getlinko.com/api/exchange")

        self.internal_secret = os.environ.get("INTERNAL_SERVER_SECRET")
        if not self.internal_secret:
            raise RuntimeError("INTERNAL_SERVER_SECRET environment variable is not set.")

        self.jwt_secret = os.environ.get("JWT_SECRET")
        if not self.jwt_secret:
            raise RuntimeError("JWT_SECRET environment variable is not set.")

        self.cookie_password = os.environ.get("COOKIE_PASSWORD")
        if not self.cookie_password:
            raise RuntimeError("COOKIE_PASSWORD environment variable is not set.")

        # Initialize the Encrypted Cookie Manager.
        self.cookies = EncryptedCookieManager(prefix=self.cookie_prefix, password=self.cookie_password)
        if not self.cookies.ready():
            # Streamlit requires a fraction of a second to mount the cookies.
            # Halting execution here ensures the app doesn't crash on the first load.
            # NOTE: This rerun is exactly why we guard _exchange_code_for_token with
            # session_state below — without it, the exchange fires twice and the
            # backend correctly rejects the already-consumed one-time code.
            st.stop()

    def authenticate(self) -> Dict[str, Any]:
        """
        Main authentication flow.
        - If not authenticated, forces the browser to redirect to the central SSO login.
        - If authenticated, returns a dictionary with the user's email and Symfony roles.
        """
        # 1. SCENARIO A: Returning from the SSO Portal with a temporary exchange code.
        #    FIX: Guard with session_state so this only fires once per code, even if
        #    Streamlit reruns the script (e.g., during cookie manager initialization).
        if "code" in st.query_params and not st.session_state.get("_sso_exchange_done"):
            st.session_state["_sso_exchange_done"] = True
            self._exchange_code_for_token(st.query_params["code"])

        # 2. SCENARIO B: The user already has an active session cookie.
        session_token = self.cookies.get("session_token")
        if session_token:
            user_data = self._validate_token(session_token)
            if user_data:
                return user_data

        # 3. If no valid session is found, force redirection to the SSO Portal.
        self._redirect_to_login()

    def logout(self):
        """Destroys the local session cookie and reloads the application."""
        if "session_token" in self.cookies:
            del self.cookies["session_token"]
            self.cookies.save()
            st.rerun()

    # ==========================================
    # INTERNAL METHODS (Protected)
    # ==========================================

    def _exchange_code_for_token(self, exchange_code: str):
        """Secure backend-to-backend call to exchange a 30-sec code for a 12-hour JWT."""
        try:
            # Use data= (form-encoded) because the FastAPI endpoint declares its
            # parameters with Form(...), which requires application/x-www-form-urlencoded.
            # Using json= here would cause a 422 Unprocessable Entity on the other side.
            response = requests.post(
                self.sso_exchange_url,
                data={"code": exchange_code, "server_secret": self.internal_secret},
                timeout=5
            )

            if response.status_code == 200:
                real_jwt = response.json().get("access_token")

                # FIX: Guard against a 200 that returns an empty or malformed body.
                if not real_jwt:
                    st.error("SSO Error: Exchange endpoint returned 200 but 'access_token' was missing in the response.")
                    st.stop()

                # Save the real JWT in the encrypted browser cookie.
                self.cookies["session_token"] = real_jwt
                self.cookies.save()

                # Clear the query params so the 'code' disappears from the URL bar and history.
                st.query_params.clear()
                st.rerun()

            else:
                # FIX: Show the actual backend response so you know exactly what failed.
                st.error(f"SSO exchange failed [{response.status_code}]: {response.text}")
                st.stop()

        except requests.exceptions.RequestException as e:
            st.error(f"SSO Server unreachable. Please check network connectivity. Details: {e}")
            st.stop()

    def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decodes the JWT and explicitly checks the intended Audience and Expiration."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                audience=self.audience  # STRICT SECURITY: Rejects tokens generated for other apps.
            )

            return {
                "email": payload.get("sub"),
                "roles": payload.get("roles", [])
            }

        except (jwt.InvalidAudienceError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # If the token is manipulated, expired, or belongs to another app, destroy the session.
            del self.cookies["session_token"]
            self.cookies.save()
            return None

    def _redirect_to_login(self):
        """Safely encodes the return URL and redirects the browser to the SSO portal."""
        encoded_app_url = urllib.parse.quote(self.app_url, safe="")
        redirect_url = f"{self.sso_login_url}?redirect_url={encoded_app_url}"

        # Streamlit-native way to force a browser redirect.
        st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', unsafe_allow_html=True)
        st.stop()