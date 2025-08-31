# Frontend - Next.js Application

English Learning Platform frontend built with Next.js, React, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3+
- **UI Components**: Headless UI / Radix UI
- **State Management**: Zustand / React Query
- **Forms**: React Hook Form with Zod validation
- **Testing**: Jest + React Testing Library + Playwright
- **PWA**: Next-PWA for offline capabilities

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # Reusable React components
│   │   ├── ui/           # Base UI components
│   │   ├── forms/        # Form components
│   │   └── layout/       # Layout components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utility libraries
│   ├── services/         # API services
│   ├── stores/           # State management
│   ├── types/            # TypeScript type definitions
│   └── utils/            # Utility functions
├── public/               # Static assets
├── tests/                # Test files
├── playwright.config.ts  # E2E test configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── next.config.js        # Next.js configuration
```

## Development Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   ```

4. **Access Application**
   - Development: http://localhost:3000
   - Storybook: http://localhost:6006

## Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler

# Testing
npm run test         # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run test:e2e     # Run E2E tests with Playwright

# Storybook
npm run storybook    # Start Storybook
npm run build-storybook  # Build Storybook
```

## Code Quality

```bash
# Format code
npm run format

# Lint and fix
npm run lint:fix

# Type checking
npm run type-check
```

## PWA Features

- **Offline Support**: Core lessons cached for offline access
- **Install Prompt**: Native app-like installation
- **Background Sync**: Queue actions when offline
- **Push Notifications**: Study reminders and achievements

## Performance Targets

- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms