# Financial Mediator Frontend

This is the frontend component of the Financial Mediator application, built with React and TypeScript.

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page components
│   ├── services/       # API services and integrations
│   ├── utils/          # Utility functions
│   ├── assets/         # Static assets (images, fonts)
│   ├── styles/         # Global styles and themes
│   ├── hooks/          # Custom React hooks
│   └── config/         # Application configuration
├── public/             # Static files
└── tests/              # Test files
```

## Prerequisites

- Node.js 16+
- npm or yarn

## Installation

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

2. Create a `.env` file in the root directory:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_API_VERSION=v1
   ```

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### `npm test`

Launches the test runner in the interactive watch mode.

### `npm run build`

Builds the app for production to the `build` folder.

### `npm run eject`

Note: this is a one-way operation. Once you `eject`, you can't go back!

## Features

- Modern React with TypeScript
- Material-UI for components
- Redux Toolkit for state management
- React Router for routing
- Formik + Yup for form handling
- Chart.js for data visualization
- Responsive design
- API integration with backend
- Unit testing with Jest

## Development

1. Start the development server:
   ```bash
   npm start
   ```

2. Start the backend server:
   ```bash
   # In a separate terminal
   cd ../backend
   python manage.py runserver
   ```

3. The application will be available at http://localhost:3000

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
