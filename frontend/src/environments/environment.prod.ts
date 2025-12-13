// Production environment configuration
// The API URL should be set via Netlify environment variables
export const environment = {
  production: true,
  // Replace this with your production API URL
  // This can be configured in Netlify's environment variables as VITE_API_URL
  apiUrl: (typeof window !== 'undefined' && (window as any).ENV?.API_URL) ||
          'https://your-api-domain.com/api'
};
