# CV Tailor Frontend

A modern React application for intelligently tailoring CVs to match job descriptions.

## Prerequisites

- Node.js 18+ (recommended: 20+)
- npm or yarn

## Installation

```bash
# Install dependencies
npm install
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Configure environment variables:
```env
VITE_API_URL=http://localhost:8000/api
```

## Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

Make sure your backend is running at `http://localhost:8000`

## Build for Production

```bash
npm run build
```

This creates an optimized `dist` folder ready for deployment.

## Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── api/
│   └── client.js        # API client with axios
├── components/
│   ├── Header.jsx       # Header component
│   ├── CVUploader.jsx   # CV upload interface
│   ├── JobDescriptionForm.jsx
│   ├── TailoringResults.jsx
│   ├── ATSScoreDisplay.jsx
│   └── ProtectedRoute.jsx
├── pages/
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   └── DashboardPage.jsx
├── stores/
│   ├── authStore.js     # Auth state (Zustand)
│   └── cvStore.js       # CV state (Zustand)
├── App.jsx              # Main app with routing
├── main.jsx             # Entry point
└── index.css            # Tailwind CSS
```

## Features

✅ User authentication (register, login, logout)
✅ CV file upload (PDF, DOCX)
✅ Job description analysis
✅ Intelligent CV tailoring
✅ ATS score calculation
✅ PDF download
✅ Responsive UI with Tailwind CSS

## Technologies

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000/api`

### JWT Authentication

- Access tokens are stored in localStorage
- Automatic token refresh on 401 errors
- Authorization header automatically added to requests

### API Client

Import API functions from `src/api/client.js`:

```javascript
import { authAPI, cvAPI, jobAPI, tailorAPI, pdfAPI } from './api/client'

// Example usage
const response = await authAPI.login(username, password)
const cvs = await cvAPI.list()
const result = await tailorAPI.tailor(cvFile, jobDescription)
```

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Then drag the dist folder to Netlify
```

### Manual Deployment

1. Build the project: `npm run build`
2. Upload the `dist` folder to your web server
3. Configure your backend API URL in production `.env`

## Troubleshooting

### API Connection Issues

- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `.env`
- Check browser console for CORS errors

### Build Errors

- Delete `node_modules` and reinstall: `npm install`
- Clear cache: `npm run build --force`

### Port Already in Use

Change port in `vite.config.js`:
```javascript
server: {
  port: 3001  // or any other port
}
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT

## Support

For issues or questions, refer to the backend documentation in the parent directory.
