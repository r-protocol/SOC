// Environment configuration
const env = {
  // Use environment variable or fallback to localhost
  API_BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:5000'
};

export default env;
