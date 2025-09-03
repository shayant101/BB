'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useEffect, useRef } from 'react';
import styles from './landing.module.css';

export default function HomePage() {
  const router = useRouter();
  const navbarRef = useRef(null);
  const videoRef = useRef(null);

  useEffect(() => {
    // Navbar scroll effect
    const handleScroll = () => {
      if (navbarRef.current) {
        if (window.scrollY > 50) {
          navbarRef.current.classList.add(styles.scrolled);
        } else {
          navbarRef.current.classList.remove(styles.scrolled);
        }
      }
    };

    // Video controls functionality
    const setupVideoControls = () => {
      const playPauseBtn = document.getElementById('playPauseBtn');
      const muteBtn = document.getElementById('muteBtn');
      const video = videoRef.current;

      if (playPauseBtn && video) {
        playPauseBtn.addEventListener('click', () => {
          if (video.paused) {
            video.play();
            playPauseBtn.innerHTML = `
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
              </svg>
            `;
          } else {
            video.pause();
            playPauseBtn.innerHTML = `
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
            `;
          }
        });
      }

      if (muteBtn && video) {
        muteBtn.addEventListener('click', () => {
          video.muted = !video.muted;
          muteBtn.innerHTML = video.muted ? `
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
            </svg>
          ` : `
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
          `;
        });
      }
    };

    window.addEventListener('scroll', handleScroll);
    setupVideoControls();

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <div className={styles.landingPage}>
      {/* Modern Transparent Navbar */}
      <nav ref={navbarRef} className={styles.floatingNavbar}>
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
          <Link href="/login" className={styles.navLoginBtn}>
            Log In
          </Link>
        </div>
      </nav>

      {/* Cinematic Hero Section with Background Video */}
      <section className={styles.heroSectionCinematic} id="home">
        {/* Background Video */}
        <div className={styles.videoBackground}>
          <video
            ref={videoRef}
            className={styles.backgroundVideo}
            autoPlay
            loop
            muted
            playsInline
            poster="https://images.unsplash.com/photo-1559329007-40df8a9345d8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1920&q=80"
          >
            <source src="/Realistic_Video_Generation_Request.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          
          {/* Gradient Overlay */}
          <div className={styles.videoOverlay}></div>
        </div>

        {/* Video Controls */}
        <div className={styles.videoControls}>
          <button className={styles.controlBtn} id="playPauseBtn">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>
          <button className={styles.controlBtn} id="muteBtn">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
          </button>
        </div>

        {/* Hero Content Overlay */}
        <div className={styles.heroContentOverlay}>
          <div className={styles.container}>
            <div className={styles.heroTextContainer}>
              <div className={styles.heroGlassCard}>
                <h1 className={styles.heroTitle}>
                  The Future of Restaurant Ordering
                </h1>
                <p className={styles.heroSubtitle}>
                  Streamline your supply chain with BistroBoard's intelligent ordering platform.
                  Connect with trusted vendors, compare prices, and manage inventory—all in one place.
                </p>
                <div className={styles.heroButtons}>
                  <Link href="/sign-up" className={`${styles.btn} ${styles.btnPrimary}`}>
                    Start Free Trial
                  </Link>
                  <Link href="#features" className={`${styles.btn} ${styles.btnSecondary}`}>
                    Watch Demo
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Modern Features Section */}
      <section className={styles.featuresSection} id="features">
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Why Choose BistroBoard?</h2>
          <p className={styles.sectionSubtitle}>
            Discover how our cutting-edge platform transforms restaurant operations with intelligent automation and seamless vendor connections.
          </p>
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

      {/* Experience Section */}
      <section className={styles.imageGridSection} id="about">
        <div className={styles.container}>
          <h2 className={styles.experienceTitle}>From Kitchen to Supplier — Streamline Every Step</h2>
          <p className={styles.experienceSubtitle}>
            See how restaurant professionals use BistroBoard to transform their ordering workflow,
            connect with trusted suppliers, and maintain the highest quality standards.
          </p>
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
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.modernFooter} id="contact">
        <div className={styles.container}>
          <div className={styles.footerContent}>
            <div className={styles.footerBrand}>
              <h3>BistroBoard</h3>
              <p>Revolutionizing restaurant operations with intelligent ordering solutions that connect kitchens to suppliers seamlessly.</p>
              <p className={styles.footerTagline}>Your Restaurant's Ordering Hub</p>
            </div>
            <div className={styles.footerColumn}>
              <h4>Company</h4>
              <a href="#about">About Us</a>
              <a href="#careers">Careers</a>
              <a href="#contact">Contact</a>
              <a href="#press">Press Kit</a>
            </div>
            <div className={styles.footerColumn}>
              <h4>Support</h4>
              <a href="#help">Help Center</a>
              <a href="#privacy">Privacy Policy</a>
              <a href="#terms">Terms of Service</a>
              <a href="#api">API Docs</a>
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
            <p>&copy; 2024 BistroBoard — Your Restaurant's Ordering Hub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}