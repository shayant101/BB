import './globals.css'
import { CartProvider } from '../src/context/CartContext';

export const metadata = {
  title: 'BistroBoard - Restaurant Supplier Management',
  description: 'Streamline your restaurant-supplier ordering process',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-gray-50 min-h-screen" suppressHydrationWarning={true}>
        <CartProvider>
          {children}
        </CartProvider>
      </body>
    </html>
  )
}