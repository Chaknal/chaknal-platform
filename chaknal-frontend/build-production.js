#!/usr/bin/env node

// Custom build script for production that handles ESLint warnings
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Building Chaknal Frontend for Production...');

try {
  // Set environment variables
  process.env.REACT_APP_API_BASE_URL = 'https://chaknal-backend-container.azurewebsites.net';
  process.env.REACT_APP_ENVIRONMENT = 'production';
  process.env.CI = 'false';
  process.env.GENERATE_SOURCEMAP = 'false';
  
  // Run the build with warnings as non-errors
  console.log('📦 Running React build...');
  execSync('ESLINT_NO_DEV_ERRORS=true npm run build', { 
    stdio: 'inherit',
    cwd: __dirname,
    env: {
      ...process.env,
      CI: 'false',
      GENERATE_SOURCEMAP: 'false',
      ESLINT_NO_DEV_ERRORS: 'true'
    }
  });
  
  console.log('✅ Frontend build completed successfully!');
  
} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}
