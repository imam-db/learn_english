import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'English Learning Platform',
  description: 'Bank Soal + Buku Digital Bahasa Inggris - Learn English with interactive lessons and practice questions',
  keywords: ['english learning', 'bahasa inggris', 'grammar', 'vocabulary', 'reading', 'indonesia'],
  authors: [{ name: 'English Learning Platform Team' }],
  creator: 'English Learning Platform',
  publisher: 'English Learning Platform',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  manifest: '/manifest.json',
  themeColor: '#3B82F6',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className={inter.className}>
        <div id="root">
          {children}
        </div>
      </body>
    </html>
  );
}