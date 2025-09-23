module.exports = {
  extends: [
    'react-app',
    'react-app/jest'
  ],
  rules: {
    // Allow unused variables in production builds
    'no-unused-vars': 'warn',
    // Allow missing dependencies in useEffect
    'react-hooks/exhaustive-deps': 'warn',
    // Allow missing default cases
    'default-case': 'warn'
  },
  env: {
    browser: true,
    es6: true,
    node: true
  }
};
