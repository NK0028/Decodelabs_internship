import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Image Generation Studio | DecodeLabs Project 3',
  description: 'Multimodal AI Image Generation — DecodeLabs Internship by Naeem Khan',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}