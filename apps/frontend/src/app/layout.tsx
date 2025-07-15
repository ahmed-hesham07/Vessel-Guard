import './globals.css'
import { Inter } from 'next/font/google'
import { AuthProvider } from '@/contexts/auth-context'
import { Providers } from '@/app/providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Vessel Guard - Engineering Compliance Platform',
  description: 'Professional vessel inspection and compliance management system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <AuthProvider>
            {children}
          </AuthProvider>
        </Providers>
      </body>
    </html>
  )
}