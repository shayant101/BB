# Frontend Troubleshooting Guide

## Issue: Next.js Development Server Not Starting or Extremely Slow Compilation

### Problem Description
During development, the Next.js frontend server may experience:
- Extremely long compilation times (5+ minutes)
- Server hanging during startup
- Port 3000 not responding despite process running
- Empty responses from localhost:3000

### Root Cause Analysis
The issue was caused by **corrupted build cache and node_modules** combined with **Next.js 15.4.6 + React 19.1.1 compatibility issues**:

1. **Corrupted Cache**: The `.next` build cache became corrupted, causing compilation to hang
2. **Node Modules Corruption**: Inconsistent dependency states in `node_modules`
3. **Package Lock Issues**: `package-lock.json` had conflicting dependency resolutions
4. **Version Compatibility**: Next.js 15 with React 19 has known performance issues in development mode

### Solution Steps

#### Step 1: Complete Clean Installation
```bash
cd "bistroboard 2/frontend"
rm -rf .next node_modules package-lock.json
npm install
```

#### Step 2: Use Turbo Mode for Faster Development
```bash
npm run dev -- --turbo
```

#### Step 3: Alternative - Use Standard Mode
```bash
npm run dev
```

### Diagnostic Commands

#### Check if Port is in Use
```bash
lsof -i :3000
```

#### Check Running Processes
```bash
ps aux | grep "next dev"
```

#### Test Server Response
```bash
curl -I http://localhost:3000
```

#### Kill Stuck Processes
```bash
pkill -f "next dev"
# or
kill <PID>
```

### Prevention Strategies

#### 1. Regular Cache Cleanup
Add to package.json scripts:
```json
{
  "scripts": {
    "clean": "rm -rf .next node_modules package-lock.json",
    "fresh-install": "npm run clean && npm install",
    "dev:clean": "npm run clean && npm install && npm run dev"
  }
}
```

#### 2. Use Turbo Mode by Default
Update package.json:
```json
{
  "scripts": {
    "dev": "next dev --turbo",
    "dev:standard": "next dev"
  }
}
```

#### 3. Environment Monitoring
Create a health check script:
```bash
#!/bin/bash
# health-check.sh
echo "Checking Next.js development environment..."
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"
echo "Next.js version: $(npx next --version)"
echo "Port 3000 status:"
lsof -i :3000 || echo "Port 3000 is free"
```

### Warning Signs to Watch For

1. **Compilation taking >30 seconds**
2. **Webpack cache errors in console**
3. **Memory usage >2GB for Next.js process**
4. **Multiple Next.js processes running simultaneously**

### Quick Recovery Commands

```bash
# Emergency reset
pkill -f "next dev"
cd "bistroboard 2/frontend"
rm -rf .next
npm run dev -- --turbo

# If still failing
rm -rf .next node_modules package-lock.json
npm install
npm run dev -- --turbo
```

### Version Compatibility Notes

#### Current Working Configuration
- Next.js: ^15.4.6
- React: ^19.1.1
- React-DOM: ^19.1.1
- @clerk/nextjs: ^6.31.3

#### Known Issues
- Next.js 15 + React 19 can have slow compilation in development
- Turbo mode significantly improves performance
- Clean installs resolve most caching issues

### Monitoring and Logging

#### Enable Verbose Logging
```bash
DEBUG=* npm run dev -- --turbo
```

#### Monitor Build Performance
```bash
npm run dev -- --turbo --profile
```

### Emergency Fallback

If all else fails, consider temporarily downgrading:
```json
{
  "dependencies": {
    "next": "^14.2.15",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@clerk/nextjs": "^5.7.1"
  }
}
```

Then run:
```bash
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

## Testing Checklist

After resolving frontend issues, verify:

- [ ] Frontend starts within 30 seconds
- [ ] http://localhost:3000 responds
- [ ] Hot reload works on file changes
- [ ] No console errors in browser
- [ ] Authentication flow works
- [ ] API calls to backend succeed
- [ ] All pages load correctly

## Contact Information

If issues persist, check:
1. System resources (RAM, CPU)
2. Node.js version compatibility
3. Network connectivity to localhost
4. Firewall/antivirus blocking ports
5. Other processes using port 3000

---
*Last Updated: 2025-08-26*
*Issue Resolution: Complete clean install + Turbo mode*