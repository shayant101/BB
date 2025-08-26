import './globals.css'
import { ClerkProvider } from '@clerk/nextjs'
import { CartProvider } from '../src/context/CartContext';

export const metadata = {
  title: 'BistroBoard - Restaurant Supplier Management',
  description: 'Streamline your restaurant-supplier ordering process',
}

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className="bg-gray-50 min-h-screen">
          <CartProvider>
            {children}
          </CartProvider>
        </body>
      </html>
    </ClerkProvider>
  )
}