'use client';

import { useEffect } from 'react';
import { getAuthToken, setAuthToken } from '../lib/api';

export default function AuthInitializer() {
  useEffect(() => {
    console.log("--- AuthInitializer mounted, setting token ---");
    const token = getAuthToken();
    if (token) {
      setAuthToken(token);
    }
  }, []);

  return null;
}