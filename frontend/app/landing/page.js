'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import styles from './landing.module.css';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className={styles.landingPage}>
      {/* Floating Navbar */}
      <nav className={styles.floatingNavbar}>
        <div className={styles.navContainer}>
          <div className={styles.navBrand}>
            <h2>BistroBoard</h2>
          </div>
          <div className={styles.navLinks}>
            <a href="#home">Home</a>
            <a href="#features">Features</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
          </div>
          <Link href="/sign-in" className={styles.navLoginBtn}>
            Log In
          </Link>
        </div>
      </nav>

      {/* Modern Hero Section */}
      <section className={styles.heroSectionModern} id="home">
        <div className={styles.container}>
          <div className={`${styles.heroContent} ${styles.glassCard}`}>
            <h1>Your Restaurant's Ordering Hub</h1>
            <p>Streamline Supplies from All Your Favorite Vendors</p>
            <Link href="/sign-up" className={`${styles.btn} ${styles.btnCtaModern}`}>
              Get Started - It's Free!
            </Link>
          </div>
        </div>
      </section>

      {/* Modern Features Section */}
      <section className={styles.featuresSection} id="features">
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Why Choose BistroBoard?</h2>
          <div className={styles.featuresGridModern}>
            {/* Feature 1 */}
            <div className={`${styles.featureItemModern} ${styles.glassCard}`}>
              <div className={styles.iconWrapper}>
                <svg className={styles.featureIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12,6 12,12 16,14"/>
                </svg>
              </div>
              <h3>Save Time & Money</h3>
              <p>Streamline your ordering process and discover competitive pricing from multiple vendors.</p>
            </div>
            
            {/* Feature 2 */}
            <div className={`${styles.featureItemModern} ${styles.glassCard}`}>
              <div className={styles.iconWrapper}>
                <svg className={styles.featureIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="1" x2="12" y2="23"/>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
              </div>
              <h3>Smart Inventory Management</h3>
              <p>Track your supplies in real-time and never run out of essential ingredients again.</p>
            </div>
            
            {/* Feature 3 */}
            <div className={`${styles.featureItemModern} ${styles.glassCard}`}>
              <div className={styles.iconWrapper}>
                <svg className={styles.featureIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 3v18h18"/>
                  <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
                </svg>
              </div>
              <h3>Multiple Vendor Network</h3>
              <p>Access a wide network of trusted suppliers and compare prices effortlessly.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Image Grid Section */}
      <section className={styles.imageGridSection} id="about">
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Experience Professional Kitchen Management</h2>
          <div className={styles.imageGrid}>
            <div className={`${styles.imageCard} ${styles.glassCard}`}>
              <Image 
                src="https://images.unsplash.com/photo-1577219491135-ce391730fb2c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80" 
                alt="Professional Chef" 
                className={styles.gridImage}
                width={1000}
                height={250}
              />
              <div className={styles.imageOverlay}>
                <h3>Expert Chefs</h3>
                <p>Professional kitchen management</p>
              </div>
            </div>
            
            <div className={`${styles.imageCard} ${styles.glassCard}`}>
              <Image 
                src="https://images.unsplash.com/photo-1542838132-92c53300491e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80" 
                alt="Fresh Produce" 
                className={styles.gridImage}
                width={1000}
                height={250}
              />
              <div className={styles.imageOverlay}>
                <h3>Fresh Ingredients</h3>
                <p>Quality sourced produce</p>
              </div>
            </div>
            
            <div className={`${styles.imageCard} ${styles.glassCard}`}>
              <Image 
                src="https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80" 
                alt="Restaurant Kitchen" 
                className={styles.gridImage}
                width={1000}
                height={250}
              />
              <div className={styles.imageOverlay}>
                <h3>Modern Kitchen</h3>
                <p>State-of-the-art facilities</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.modernFooter} id="contact">
        <div className={styles.container}>
          <div className={styles.footerContent}>
            <div className={styles.footerBrand}>
              <h3>BistroBoard</h3>
              <p>Your Restaurant's Ordering Hub</p>
            </div>
            <div className={styles.footerLinks}>
              <div className={styles.footerColumn}>
                <h4>Company</h4>
                <a href="#about">About Us</a>
                <a href="#careers">Careers</a>
                <a href="#contact">Contact</a>
              </div>
              <div className={styles.footerColumn}>
                <h4>Support</h4>
                <a href="#help">Help Center</a>
                <a href="#privacy">Privacy Policy</a>
                <a href="#terms">Terms of Service</a>
              </div>
            </div>
            <div className={styles.footerSocial}>
              <h4>Follow Us</h4>
              <div className={styles.socialIcons}>
                <a href="#" className={styles.socialIcon}>
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                  </svg>
                </a>
                <a href="#" className={styles.socialIcon}>
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
                  </svg>
                </a>
                <a href="#" className={styles.socialIcon}>
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
              </div>
            </div>
          </div>
          <div className={styles.footerBottom}>
            <p>&copy; 2024 BistroBoard. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}