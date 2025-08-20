#!/usr/bin/env node

/**
 * BistroBoard Frontend Setup Validation Script
 * Run this before starting development to catch configuration issues early
 */

const fs = require('fs');
const path = require('path');
const axios = require('axios');

console.log('🔍 BistroBoard Frontend Setup Validation\n');

// Colors for console output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

function log(color, symbol, message) {
  console.log(`${colors[color]}${symbol} ${message}${colors.reset}`);
}

function success(message) { log('green', '✅', message); }
function error(message) { log('red', '❌', message); }
function warning(message) { log('yellow', '⚠️', message); }
function info(message) { log('blue', 'ℹ️', message); }

let hasErrors = false;
let hasWarnings = false;

// 1. Check Node.js version
function checkNodeVersion() {
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
  
  if (majorVersion >= 18) {
    success(`Node.js version: ${nodeVersion}`);
  } else {
    error(`Node.js version ${nodeVersion} is too old. Requires Node.js 18+`);
    hasErrors = true;
  }
}

// 2. Check package.json and dependencies
function checkPackageJson() {
  const packagePath = path.join(__dirname, '..', 'package.json');
  
  if (!fs.existsSync(packagePath)) {
    error('package.json not found');
    hasErrors = true;
    return;
  }
  
  success('package.json found');
  
  // Check if node_modules exists
  const nodeModulesPath = path.join(__dirname, '..', 'node_modules');
  if (!fs.existsSync(nodeModulesPath)) {
    error('node_modules not found. Run: npm install');
    hasErrors = true;
  } else {
    success('node_modules found');
  }
}

// 3. Check environment configuration
function checkEnvironment() {
  const envPath = path.join(__dirname, '..', '.env.local');
  
  if (!fs.existsSync(envPath)) {
    warning('.env.local not found. Using fallback configuration.');
    hasWarnings = true;
  } else {
    success('.env.local found');
    
    // Read and validate environment variables
    const envContent = fs.readFileSync(envPath, 'utf8');
    const apiUrlMatch = envContent.match(/NEXT_PUBLIC_API_URL=(.+)/);
    
    if (apiUrlMatch) {
      const apiUrl = apiUrlMatch[1].trim();
      if (apiUrl.endsWith('/api')) {
        success(`API URL configured: ${apiUrl}`);
      } else {
        warning(`API URL should end with '/api': ${apiUrl}`);
        hasWarnings = true;
      }
    } else {
      warning('NEXT_PUBLIC_API_URL not found in .env.local');
      hasWarnings = true;
    }
  }
}

// 4. Check Next.js configuration
function checkNextConfig() {
  const nextConfigPath = path.join(__dirname, '..', 'next.config.js');
  
  if (!fs.existsSync(nextConfigPath)) {
    error('next.config.js not found');
    hasErrors = true;
  } else {
    success('next.config.js found');
  }
}

// 5. Check critical files
function checkCriticalFiles() {
  const criticalFiles = [
    'app/layout.js',
    'app/page.js',
    'src/lib/api.js',
    'src/components/AuthInitializer.js',
    'src/context/CartContext.js'
  ];
  
  criticalFiles.forEach(file => {
    const filePath = path.join(__dirname, '..', file);
    if (fs.existsSync(filePath)) {
      success(`${file} found`);
    } else {
      error(`${file} missing`);
      hasErrors = true;
    }
  });
}

// 6. Check backend connectivity
async function checkBackendConnectivity() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  const healthUrl = apiUrl.replace('/api', '/health');
  
  try {
    info(`Checking backend connectivity: ${healthUrl}`);
    const response = await axios.get(healthUrl, { timeout: 5000 });
    success(`Backend server is running: ${response.data.status}`);
    
    if (response.data.database_status === 'connected') {
      success('Database connection verified');
    } else {
      warning('Database connection issue detected');
      hasWarnings = true;
    }
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      warning('Backend server not running. Start with: cd backend && python -m uvicorn app.main:app --reload --port 8000');
      hasWarnings = true;
    } else {
      error(`Backend connectivity check failed: ${error.message}`);
      hasWarnings = true;
    }
  }
}

// Main validation function
async function runValidation() {
  console.log('Running setup validation...\n');
  
  checkNodeVersion();
  checkPackageJson();
  checkEnvironment();
  checkNextConfig();
  checkCriticalFiles();
  await checkBackendConnectivity();
  
  console.log('\n' + '='.repeat(50));
  
  if (hasErrors) {
    error('Setup validation failed! Please fix the errors above before starting development.');
    process.exit(1);
  } else if (hasWarnings) {
    warning('Setup validation completed with warnings. Development may work but some features might be limited.');
    info('Consider addressing the warnings above for the best development experience.');
  } else {
    success('Setup validation passed! Ready for development.');
    info('Start development with: npm run dev');
  }
}

// Run validation
runValidation().catch(error => {
  error(`Validation script failed: ${error.message}`);
  process.exit(1);
});