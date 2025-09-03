'use client';

import { useRouter } from 'next/navigation';
import styles from './login.module.css';

export default function LoginPage() {
  const router = useRouter();

  return (
    <div className={styles.loginPage}>
      <div className="min-h-screen flex">
        {/* Left Side - Branding */}
        <div className={`hidden lg:flex lg:w-1/2 ${styles.brandingSection}`}>
          <div className={styles.brandingOverlay}></div>
          <div className={styles.brandingContent}>
            <div className="mb-8">
              <h1 className={styles.brandingTitle}>BistroBoard</h1>
              <p className={styles.brandingSubtitle}>
                Streamline your restaurant-supplier relationships with modern order management.
              </p>
            </div>
            <div className={styles.featuresList}>
              <div className={styles.featureItem}>
                <svg className={styles.featureIcon} fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                </svg>
                <span>Real-time order tracking</span>
              </div>
              <div className={styles.featureItem}>
                <svg className={styles.featureIcon} fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                </svg>
                <span>Seamless communication</span>
              </div>
              <div className={styles.featureItem}>
                <svg className={styles.featureIcon} fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                </svg>
                <span>Professional order management</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Sign In Options */}
        <div className={`w-full lg:w-1/2 ${styles.formSection}`}>
          <div className={styles.formContainer}>
            <div className={`${styles.mobileHeader} lg:hidden`}>
              <h1 className={styles.mobileTitle}>BistroBoard</h1>
              <p className={styles.mobileSubtitle}>Restaurant-Supplier Management</p>
            </div>

            <div className={styles.loginCard}>
              <div className={styles.formHeader}>
                <h2 className={styles.formTitle}>Welcome to BistroBoard</h2>
                <p className={styles.formSubtitle}>Sign in to manage your restaurant or supplier business</p>
              </div>

              <div className={styles.buttonContainer}>
                {/* Sign In Button */}
                <button
                  onClick={() => router.push('/sign-in')}
                  className={styles.primaryButton}
                >
                  Sign In
                </button>

                <div className={styles.divider}>
                  <div className={styles.dividerLine}>
                    <div className={styles.dividerBorder} />
                  </div>
                  <div className={styles.dividerText}>
                    <span className={styles.dividerLabel}>New to BistroBoard?</span>
                  </div>
                </div>

                <button
                  onClick={() => router.push('/sign-up')}
                  className={styles.secondaryButton}
                >
                  Create Account
                </button>

                {/* Admin Command Center Button */}
                <div className={styles.divider}>
                  <div className={styles.dividerLine}>
                    <div className={styles.dividerBorder} />
                  </div>
                  <div className={styles.dividerText}>
                    <span className={styles.dividerLabel}>Admin Access</span>
                  </div>
                </div>

                <button
                  onClick={() => router.push('/backend-login')}
                  className={styles.adminButton}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd" />
                  </svg>
                  <span>🛡️ Admin Command Center</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}