import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TimeMachine Web UI',
  description: 'Branch Testing for LangGraph Agents - Modern AI Development Tools',
  keywords: 'LangGraph, AI, TimeMachine, Branch Testing, Agent Development',
  authors: [{ name: 'TimeMachine Team' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link 
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" 
          rel="stylesheet" 
        />
      </head>
      <body className="min-h-screen text-gray-200 antialiased overflow-x-hidden font-medium">
        <div className="fixed inset-0 bg-[linear-gradient(135deg,_rgba(3,4,9,1),_rgba(15,23,42,1))] pointer-events-none" />
        <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top_left,_rgba(107,114,128,0.04),_transparent_60%)] pointer-events-none" />
        <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_rgba(107,114,128,0.03),_transparent_70%)] pointer-events-none" />
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  );
}
