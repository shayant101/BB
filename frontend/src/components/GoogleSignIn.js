'use client';

import { useState, useEffect } from 'react';
import { authAPI, setAuthToken, setUser } from '../lib/api';

const GoogleSignIn = ({ onSuccess, onError, role = 'restaurant' }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [googleConfig, setGoogleConfig] = useState(null);

  useEffect(() => {
    // Load Google Identity Services script
    const loadGoogleScript = () => {
      if (window.google) {
        initializeGoogle();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initializeGoogle;
      document.head.appendChild(script);
    };

    const initializeGoogle = async () => {
      try {
        console.log('🔍 [DEBUG] Initializing Google Sign-In...');
        
        // Get Google OAuth configuration from backend
        const config = await authAPI.getGoogleConfig();
        console.log('🔍 [DEBUG] Google config received:', {
          hasClientId: !!config.client_id,
          clientIdLength: config.client_id?.length,
          redirectUri: config.redirect_uri
        });
        
        setGoogleConfig(config);

        // Validate client ID
        if (!config.client_id || config.client_id.includes('your_google_client_id')) {
          throw new Error('Google OAuth client ID not properly configured');
        }

        // Initialize Google Identity Services
        console.log('🔍 [DEBUG] Initializing Google Identity Services...');
        window.google.accounts.id.initialize({
          client_id: config.client_id,
          callback: handleGoogleResponse,
          auto_select: false,
          cancel_on_tap_outside: true,
        });

        // Try to render the Google Sign-In button with custom styling
        try {
          console.log('🔍 [DEBUG] Rendering Google Sign-In button...');
          window.google.accounts.id.renderButton(
            document.getElementById('google-signin-button'),
            {
              theme: 'outline',
              size: 'large',
              width: '100%',
              text: 'continue_with',
              shape: 'rectangular',
              logo_alignment: 'left',
            }
          );
          
          // Apply minimal CSS for sizing and positioning only
          setTimeout(() => {
            const googleButton = document.querySelector('#google-signin-button > div');
            if (googleButton) {
              googleButton.style.width = '100%';
              googleButton.style.height = '48px';
            }
          }, 100);
          
          console.log('🔍 [DEBUG] Google Sign-In button rendered successfully');
        } catch (renderError) {
          console.warn('⚠️ [DEBUG] Google button render failed:', renderError);
          // Show fallback button if Google button fails
          const fallbackButton = document.getElementById('fallback-google-button');
          if (fallbackButton) {
            fallbackButton.style.display = 'flex';
          }
        }
      } catch (error) {
        console.error('🚨 [DEBUG] Failed to initialize Google Sign-In:', error);
        
        // Show fallback button for configuration errors
        const fallbackButton = document.getElementById('fallback-google-button');
        if (fallbackButton) {
          fallbackButton.style.display = 'flex';
        }
        
        // Show user-friendly error message
        const errorMessage = error.message.includes('client ID')
          ? 'Google Sign-In is not configured properly. Please contact support.'
          : 'Failed to initialize Google Sign-In. Please try again or contact support.';
        
        onError?.(errorMessage);
      }
    };

    loadGoogleScript();
  }, []);

  const handleGoogleResponse = async (response) => {
    console.log('🔍 [DEBUG] handleGoogleResponse called with:', {
      hasCredential: !!response?.credential,
      credentialLength: response?.credential?.length,
      role: role,
      timestamp: new Date().toISOString()
    });
    
    setIsLoading(true);
    
    try {
      // Validate Google response
      if (!response || !response.credential) {
        throw new Error('Invalid Google response: missing credential');
      }
      
      console.log('🔍 [DEBUG] Calling authAPI.googleLogin with:', {
        credentialPresent: !!response.credential,
        role: role
      });
      
      // Send the credential to our backend
      const authResponse = await authAPI.googleLogin(response.credential, role);
      
      console.log('🔍 [DEBUG] Backend response received:', {
        hasResponse: !!authResponse,
        needsRoleSelection: authResponse?.needs_role_selection,
        hasAccessToken: !!authResponse?.access_token,
        hasUserId: !!authResponse?.user_id,
        hasRole: !!authResponse?.role,
        hasName: !!authResponse?.name,
        responseKeys: authResponse ? Object.keys(authResponse) : []
      });
      
      // Check if user needs role selection
      if (authResponse.needs_role_selection) {
        console.log('🔍 [DEBUG] User needs role selection, calling onSuccess with role selection data');
        // Pass the response to parent for role selection handling
        onSuccess?.({
          ...authResponse,
          credential: response.credential
        });
        return;
      }
      
      // Normal login flow - store token and user info
      if (authResponse.access_token) {
        console.log('🔍 [DEBUG] Storing auth token and user info');
        setAuthToken(authResponse.access_token);
        setUser({
          id: authResponse.user_id,
          role: authResponse.role,
          name: authResponse.name
        });
      } else {
        console.warn('⚠️ [DEBUG] No access_token in response, skipping token storage');
      }

      console.log('🔍 [DEBUG] Calling onSuccess with authResponse');
      onSuccess?.(authResponse);
    } catch (error) {
      console.error('🚨 [DEBUG] Google login error details:', {
        errorType: error.constructor.name,
        errorMessage: error.message,
        hasResponse: !!error.response,
        responseStatus: error.response?.status,
        responseData: error.response?.data,
        responseDataDetail: error.response?.data?.detail,
        fullError: error,
        stack: error.stack
      });
      
      // Safe error message extraction
      let errorMessage = 'Google login failed';
      try {
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.message) {
          errorMessage = error.message;
        }
      } catch (msgError) {
        console.error('🚨 [DEBUG] Error extracting error message:', msgError);
      }
      
      console.log('🔍 [DEBUG] Calling onError with message:', errorMessage);
      onError?.(errorMessage);
    } finally {
      console.log('🔍 [DEBUG] Setting isLoading to false');
      setIsLoading(false);
    }
  };

  const handleFallbackGoogleSignIn = () => {
    if (!window.google || !googleConfig) {
      onError?.('Google Sign-In not initialized');
      return;
    }

    // Use the prompt method as fallback
    try {
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // If prompt fails, show error message with instructions
          onError?.('Google Sign-In is not available. Please ensure this domain is authorized in Google Cloud Console.');
        }
      });
    } catch (error) {
      console.error('Fallback Google Sign-In failed:', error);
      onError?.('Google Sign-In failed. Please try again or contact support.');
    }
  };

  return (
    <div className="w-full">
      {isLoading && (
        <div className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-gray-50 text-gray-700 font-medium">
          <svg className="w-5 h-5 mr-3 animate-spin" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 3v3l4-4-4-4v3c-4.42 0-8 3.58-8 8s3.58 8 8 8c1.57 0 3.04-.46 4.28-1.26l-1.45-1.45C11.76 12.53 10.92 13 10 13c-1.65 0-3-1.35-3-3s1.35-3 3-3z"></path>
          </svg>
          Signing in with Google...
        </div>
      )}
      
      {!isLoading && (
        <>
          {/* Google's official button container */}
          <div
            id="google-signin-button"
            className="w-full"
            style={{ opacity: (!googleConfig) ? 0.5 : 1, pointerEvents: (!googleConfig) ? 'none' : 'auto' }}
          />
          
          {/* Fallback custom button - only shown if Google button fails to render */}
          <button
            type="button"
            onClick={handleFallbackGoogleSignIn}
            disabled={!googleConfig}
            className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-700 font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            id="fallback-google-button"
            style={{ display: 'none' }}
          >
            <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>
        </>
      )}
    </div>
  );
};

export default GoogleSignIn;