import './globals.css'
import AuthInitializer from '../src/components/AuthInitializer';

export const metadata = {
  title: 'BistroBoard - Restaurant Supplier Management',
  description: 'Streamline your restaurant-supplier ordering process',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <AuthInitializer />
        {children}
      </body>
    </html>
  )
}