"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useCart } from '../../../src/context/CartContext';
import api from '../../../src/lib/api';

export default function VendorStorefront() {
  const [storefront, setStorefront] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { vendorId } = useParams();
  const { addToCart, cartItems } = useCart();

  useEffect(() => {
    if (vendorId) {
      const fetchStorefrontData = async () => {
        try {
          const [storefrontRes, productsRes] = await Promise.all([
            api.get(`/storefront/${vendorId}`),
            api.get(`/storefront/${vendorId}/products`)
          ]);
          const storefrontData = storefrontRes.data;
          const productsData = productsRes.data;
          setStorefront(storefrontData);
          setProducts(productsData);
        } catch (error) {
          console.error("Failed to fetch storefront data:", error);
        } finally {
          setLoading(false);
        }
      };
      fetchStorefrontData();
    }
  }, [vendorId]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!storefront) {
    return <div>Storefront not found.</div>;
  }

  return (
    <div style={{ 
        '--brand-primary': storefront.brand_colors?.primary || '#000',
        '--brand-secondary': storefront.brand_colors?.secondary || '#fff',
      }}
    >
      <header style={{ backgroundColor: 'var(--brand-primary)', color: 'var(--brand-secondary)', padding: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          {storefront.logo_url && <img src={storefront.logo_url} alt="logo" style={{ maxHeight: '80px' }} />}
          <h1>{storefront.tagline || `Welcome to Vendor ${vendorId}'s Store`}</h1>
          <p>{storefront.welcome_message}</p>
        </div>
        <div>
          Cart: {cartItems.length} items
        </div>
      </header>
      
      <main style={{ padding: '2rem' }}>
        <h2>Our Products</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
          {products.map(product => (
            <div key={product.product_id} style={{ border: '1px solid #ccc', padding: '1rem' }}>
              {product.images && product.images.length > 0 &&
                <img key={`${product.product_id}-image-0`} src={product.images[0]} alt={product.name} style={{ maxWidth: '100%', height: 'auto' }} />
              }
              <h3>{product.name}</h3>
              <p>{product.description}</p>
              <p>Price: ${product.price}</p>
              <button onClick={() => addToCart(product)} style={{ padding: '0.5rem', backgroundColor: 'var(--brand-primary)', color: 'var(--brand-secondary)', border: 'none', cursor: 'pointer' }}>
                Add to Cart
              </button>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}