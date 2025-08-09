"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useCart } from '../../../src/context/CartContext';
import api, { storefrontAPI } from '../../../src/lib/api';
import CartModal from '../../../src/components/CartModal';
import {
  ShoppingCartIcon,
  StarIcon,
  MapPinIcon,
  ClockIcon,
  PhoneIcon,
  EnvelopeIcon,
  BuildingStorefrontIcon,
  PhotoIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';

export default function VendorStorefront() {
  const [storefront, setStorefront] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [imageErrors, setImageErrors] = useState({});
  const [aiImages, setAiImages] = useState({});
  const [loadingImages, setLoadingImages] = useState({});
  const [isCartModalOpen, setIsCartModalOpen] = useState(false);
  const { vendorId } = useParams();
  const { addToCart, getCartItemCount } = useCart();

  useEffect(() => {
    if (vendorId && typeof vendorId === 'string' && vendorId !== 'undefined') {
      const fetchStorefrontData = async () => {
        try {
          const [storefrontRes, productsData] = await Promise.all([
            api.get(`/storefront/${vendorId}`),
            storefrontAPI.getVendorProducts(vendorId)
          ]);
          const storefrontData = storefrontRes.data;
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

  const handleImageError = (productId) => {
    setImageErrors(prev => ({ ...prev, [productId]: true }));
  };

  // Generate AI-based stock image using CORS-friendly sources
  const generateAIImage = async (productName, productId) => {
    if (aiImages[productId] || loadingImages[productId]) return;
    
    console.log(`Generating AI image for: ${productName} (ID: ${productId})`);
    setLoadingImages(prev => ({ ...prev, [productId]: true }));
    
    try {
      // Intelligent keyword extraction for food items
      const extractFoodKeywords = (name) => {
        const cleanName = name.toLowerCase().replace(/[^a-z0-9\s-]/g, '');
        
        // Common food descriptors to filter out (but keep for context)
        const descriptors = [
          'organic', 'fresh', 'wild', 'caught', 'free', 'range', 'grass', 'fed',
          'local', 'farm', 'raised', 'natural', 'premium', 'grade', 'choice',
          'prime', 'select', 'whole', 'half', 'quarter', 'sliced', 'diced',
          'chopped', 'ground', 'minced', 'frozen', 'canned', 'dried', 'smoked',
          'aged', 'mature', 'young', 'baby', 'jumbo', 'large', 'medium', 'small',
          'extra', 'super', 'giant', 'mini', 'bite', 'sized'
        ];
        
        // Units and preparations to filter out (but NOT food identifiers like 'steak', 'chops')
        const unitsAndPreps = [
          'lb', 'lbs', 'pound', 'pounds', 'oz', 'ounce', 'ounces', 'kg', 'gram', 'grams',
          'piece', 'pieces', 'each', 'per', 'pack', 'package', 'bag', 'box', 'bunch',
          'head', 'heads', 'fillet', 'fillets', 'roast', 'breast', 'thigh', 'wing', 'wings',
          'leg', 'legs', 'rack', 'strip', 'strips', 'cube', 'cubes', 'chunk', 'chunks',
          'loaf', 'loaves', 'standard', 'large', 'bulk'
        ];
        
        // Known food items (prioritized keywords)
        const foodItems = [
          // Proteins - Multi-word items first (more specific)
          'prime ribeye steak', 'ribeye steak', 'sirloin steak', 'ground beef', 'chicken breast',
          'salmon fillet', 'pork chop', 'lamb chop', 'lamb chops', 'beef brisket', 'pork shoulder',
          'chicken thigh', 'pork tenderloin', 'fresh scallops', 'fresh salmon fillet',
          // Proteins - Single words
          'salmon', 'tuna', 'cod', 'halibut', 'trout', 'bass', 'chicken', 'beef', 'pork',
          'lamb', 'turkey', 'duck', 'shrimp', 'crab', 'lobster', 'scallops', 'mussels',
          'sirloin', 'ribeye', 'tenderloin', 'brisket', 'ribs', 'steak',
          // Vegetables & Herbs
          'tomato', 'tomatoes', 'lettuce', 'spinach', 'kale', 'arugula', 'cabbage',
          'broccoli', 'cauliflower', 'carrot', 'carrots', 'celery', 'onion', 'onions',
          'garlic', 'potato', 'potatoes', 'sweet potato', 'yam', 'beet', 'beets',
          'radish', 'turnip', 'parsnip', 'asparagus', 'artichoke', 'avocado', 'avocados',
          'cucumber', 'zucchini', 'squash', 'pumpkin', 'eggplant', 'pepper', 'peppers',
          'mushroom', 'mushrooms', 'corn', 'peas', 'beans', 'lentils', 'chickpeas',
          'basil', 'parsley', 'cilantro', 'mint', 'oregano', 'thyme', 'rosemary', 'sage',
          'greens', 'mixed greens', 'salad greens', 'bell pepper', 'bell peppers',
          // Fruits
          'apple', 'apples', 'banana', 'bananas', 'orange', 'oranges', 'lemon', 'lemons',
          'lime', 'limes', 'grapefruit', 'strawberry', 'strawberries', 'blueberry', 'blueberries',
          'raspberry', 'raspberries', 'blackberry', 'blackberries', 'grape', 'grapes',
          'peach', 'peaches', 'pear', 'pears', 'plum', 'plums', 'cherry', 'cherries',
          'pineapple', 'mango', 'papaya', 'kiwi', 'melon', 'watermelon', 'cantaloupe',
          // Grains & Bread
          'bread', 'sourdough', 'baguette', 'croissant', 'bagel', 'muffin', 'rice',
          'quinoa', 'oats', 'barley', 'wheat', 'pasta', 'noodles',
          // Dairy
          'milk', 'cheese', 'butter', 'cream', 'yogurt', 'eggs',
          // Beverages
          'coffee', 'tea', 'beer', 'water', 'juice'
        ];
        
        const words = cleanName.split(/\s+/).filter(word => word.length > 1);
        
        console.log(`[AI IMAGE DEBUG] Processing "${name}": words = [${words.join(', ')}]`);
        
        // First, look for exact food item matches (prioritize multi-word items)
        // Check for 3-word combinations first
        for (let i = 0; i < words.length - 2; i++) {
          const threeWordCombo = `${words[i]} ${words[i + 1]} ${words[i + 2]}`;
          if (foodItems.includes(threeWordCombo)) {
            console.log(`[AI IMAGE DEBUG] Found 3-word match: "${threeWordCombo}"`);
            return threeWordCombo;
          }
        }
        
        // Then check for 2-word combinations
        for (let i = 0; i < words.length - 1; i++) {
          const twoWordCombo = `${words[i]} ${words[i + 1]}`;
          if (foodItems.includes(twoWordCombo)) {
            console.log(`[AI IMAGE DEBUG] Found 2-word match: "${twoWordCombo}"`);
            return twoWordCombo;
          }
        }
        
        // Then look for single food items
        for (const word of words) {
          if (foodItems.includes(word)) {
            console.log(`[AI IMAGE DEBUG] Found single word match: "${word}"`);
            return word;
          }
        }
        
        // If no exact match, find the most likely food word by filtering out descriptors
        const filteredWords = words.filter(word =>
          !descriptors.includes(word) &&
          !unitsAndPreps.includes(word) &&
          word.length > 2
        );
        
        console.log(`[AI IMAGE DEBUG] No exact match found. Filtered words: [${filteredWords.join(', ')}]`);
        
        // Return the first significant word, or fallback to first word
        const result = filteredWords[0] || words[0] || 'food';
        console.log(`[AI IMAGE DEBUG] Final result: "${result}"`);
        return result;
      };
      
      const mainFood = extractFoodKeywords(productName);
      console.log(`Extracted food keyword: "${mainFood}" from "${productName}"`);
      
      // Enhanced food image mapping with more comprehensive coverage
      const foodImageMap = {
        // Proteins - Multi-word items (more specific)
        'prime ribeye steak': 'https://images.unsplash.com/photo-1588347818133-38c4106c8f3b?w=400&h=300&fit=crop&crop=center',
        'ribeye steak': 'https://images.unsplash.com/photo-1588347818133-38c4106c8f3b?w=400&h=300&fit=crop&crop=center',
        'sirloin steak': 'https://images.unsplash.com/photo-1588347818133-38c4106c8f3b?w=400&h=300&fit=crop&crop=center',
        'ground beef': 'https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=400&h=300&fit=crop&crop=center',
        'chicken breast': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400&h=300&fit=crop&crop=center',
        'salmon fillet': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=300&fit=crop&crop=center',
        'fresh salmon fillet': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=300&fit=crop&crop=center',
        'pork chop': 'https://images.unsplash.com/photo-1602470520998-f4a52199a3d6?w=400&h=300&fit=crop&crop=center',
        'lamb chop': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop&crop=center',
        'lamb chops': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop&crop=center',
        'pork tenderloin': 'https://images.unsplash.com/photo-1602470520998-f4a52199a3d6?w=400&h=300&fit=crop&crop=center',
        'fresh scallops': 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=400&h=300&fit=crop&crop=center',
        
        // Proteins - Fish & Seafood
        'salmon': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=300&fit=crop&crop=center',
        'tuna': 'https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=400&h=300&fit=crop&crop=center',
        'cod': 'https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=400&h=300&fit=crop&crop=center',
        'shrimp': 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=400&h=300&fit=crop&crop=center',
        'crab': 'https://images.unsplash.com/photo-1558030006-450675393462?w=400&h=300&fit=crop&crop=center',
        'scallops': 'https://images.unsplash.com/photo-1559847844-d7b4ac2b7e8b?w=400&h=300&fit=crop&crop=center',
        
        // Proteins - Meat
        'beef': 'https://images.unsplash.com/photo-1588347818133-38c4106c8f3b?w=400&h=300&fit=crop&crop=center',
        'steak': 'https://images.unsplash.com/photo-1588347818133-38c4106c8f3b?w=400&h=300&fit=crop&crop=center',
        'sirloin': 'https://images.unsplash.com/photo-1588347818133-38c4106c8f3b?w=400&h=300&fit=crop&crop=center',
        'ribeye': 'https://images.unsplash.com/photo-1588347818133-38c4106c8f3b?w=400&h=300&fit=crop&crop=center',
        'chicken': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400&h=300&fit=crop&crop=center',
        'pork': 'https://images.unsplash.com/photo-1602470520998-f4a52199a3d6?w=400&h=300&fit=crop&crop=center',
        
        // Vegetables
        'tomato': 'https://images.unsplash.com/photo-1546470427-e5ac89cd0b9b?w=400&h=300&fit=crop&crop=center',
        'tomatoes': 'https://images.unsplash.com/photo-1546470427-e5ac89cd0b9b?w=400&h=300&fit=crop&crop=center',
        'spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400&h=300&fit=crop&crop=center',
        'kale': 'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=400&h=300&fit=crop&crop=center',
        'lettuce': 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400&h=300&fit=crop&crop=center',
        'arugula': 'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=400&h=300&fit=crop&crop=center',
        'broccoli': 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=400&h=300&fit=crop&crop=center',
        'cauliflower': 'https://images.unsplash.com/photo-1568584711271-946d4d46b7d8?w=400&h=300&fit=crop&crop=center',
        'carrot': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400&h=300&fit=crop&crop=center',
        'carrots': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400&h=300&fit=crop&crop=center',
        'potato': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&h=300&fit=crop&crop=center',
        'potatoes': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&h=300&fit=crop&crop=center',
        'sweet potato': 'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=400&h=300&fit=crop&crop=center',
        'onion': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&h=300&fit=crop&crop=center',
        'onions': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&h=300&fit=crop&crop=center',
        'avocado': 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400&h=300&fit=crop&crop=center',
        'avocados': 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400&h=300&fit=crop&crop=center',
        'mushroom': 'https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9?w=400&h=300&fit=crop&crop=center',
        'mushrooms': 'https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9?w=400&h=300&fit=crop&crop=center',
        'pepper': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400&h=300&fit=crop&crop=center',
        'peppers': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400&h=300&fit=crop&crop=center',
        'bell pepper': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400&h=300&fit=crop&crop=center',
        'bell peppers': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400&h=300&fit=crop&crop=center',
        
        // Herbs
        'basil': 'https://images.unsplash.com/photo-1618375569909-3c8616cf7733?w=400&h=300&fit=crop&crop=center',
        'parsley': 'https://images.unsplash.com/photo-1616040808050-6d0f2e6c8b8e?w=400&h=300&fit=crop&crop=center',
        'cilantro': 'https://images.unsplash.com/photo-1616040808050-6d0f2e6c8b8e?w=400&h=300&fit=crop&crop=center',
        'mint': 'https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=400&h=300&fit=crop&crop=center',
        
        // Mixed/Salad Greens
        'greens': 'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=400&h=300&fit=crop&crop=center',
        'mixed greens': 'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=400&h=300&fit=crop&crop=center',
        'salad greens': 'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=400&h=300&fit=crop&crop=center',
        
        // Fruits
        'apple': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=300&fit=crop&crop=center',
        'apples': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=300&fit=crop&crop=center',
        'banana': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400&h=300&fit=crop&crop=center',
        'bananas': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400&h=300&fit=crop&crop=center',
        'orange': 'https://images.unsplash.com/photo-1547514701-42782101795e?w=400&h=300&fit=crop&crop=center',
        'oranges': 'https://images.unsplash.com/photo-1547514701-42782101795e?w=400&h=300&fit=crop&crop=center',
        'strawberry': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400&h=300&fit=crop&crop=center',
        'strawberries': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400&h=300&fit=crop&crop=center',
        'blueberry': 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=400&h=300&fit=crop&crop=center',
        'blueberries': 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=400&h=300&fit=crop&crop=center',
        'grape': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=400&h=300&fit=crop&crop=center',
        'grapes': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=400&h=300&fit=crop&crop=center',
        'lemon': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop&crop=center',
        'lemons': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop&crop=center',
        
        // Grains & Bread
        'bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=300&fit=crop&crop=center',
        'sourdough': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=300&fit=crop&crop=center',
        'baguette': 'https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=400&h=300&fit=crop&crop=center',
        'rice': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=300&fit=crop&crop=center',
        
        // Dairy
        'cheese': 'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400&h=300&fit=crop&crop=center',
        'milk': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=300&fit=crop&crop=center',
        'eggs': 'https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?w=400&h=300&fit=crop&crop=center',
        
        // Beverages
        'coffee': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&h=300&fit=crop&crop=center',
        'tea': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=400&h=300&fit=crop&crop=center',
        'beer': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400&h=300&fit=crop&crop=center',
        'water': 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&h=300&fit=crop&crop=center'
      };
      
      // Use CORS-friendly image sources with improved search terms
      const searchTerms = mainFood.replace(/\s+/g, '+');
      const imageSources = [
        // Direct Unsplash images (CORS-friendly) - no fallback to strawberries
        foodImageMap[mainFood],
        // Unsplash search API with better search terms
        `https://images.unsplash.com/photo-1546470427-e5ac89cd0b9b?w=400&h=300&fit=crop&crop=center&q=${searchTerms}`,
        // Picsum with seed for consistency (CORS-friendly)
        `https://picsum.photos/seed/${searchTerms}/400/300`,
        // Lorem Flickr with multiple search terms (CORS-friendly)
        `https://loremflickr.com/400/300/${searchTerms},food,fresh`,
        // Final fallback - a simple colored placeholder with the food name
        `data:image/svg+xml;base64,${btoa(`
          <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#10B981"/>
            <text x="200" y="150" font-family="Arial, sans-serif" font-size="20" fill="white" text-anchor="middle" dominant-baseline="middle">
              ${mainFood.charAt(0).toUpperCase() + mainFood.slice(1)}
            </text>
          </svg>
        `)}`
      ].filter(Boolean); // Remove any undefined entries
      
      // Try each image source with timeout
      const tryImageSource = (index = 0) => {
        if (index >= imageSources.length) {
          console.log(`All image sources failed for ${productName}`);
          setLoadingImages(prev => ({ ...prev, [productId]: false }));
          return;
        }
        
        const imageUrl = imageSources[index];
        console.log(`Trying image source ${index + 1}: ${imageUrl.substring(0, 100)}...`);
        
        const img = new Image();
        
        // Set timeout for image loading
        const timeout = setTimeout(() => {
          console.log(`Timeout for image source ${index + 1}`);
          tryImageSource(index + 1);
        }, 3000);
        
        img.onload = () => {
          clearTimeout(timeout);
          console.log(`Successfully loaded image for ${productName}`);
          setAiImages(prev => ({ ...prev, [productId]: imageUrl }));
          setLoadingImages(prev => ({ ...prev, [productId]: false }));
        };
        
        img.onerror = () => {
          clearTimeout(timeout);
          console.log(`Failed to load image source ${index + 1} for ${productName}`);
          tryImageSource(index + 1);
        };
        
        img.src = imageUrl;
      };
      
      tryImageSource();
      
    } catch (error) {
      console.error('Error generating AI image:', error);
      setLoadingImages(prev => ({ ...prev, [productId]: false }));
    }
  };

  // Generate AI images for products when they load
  useEffect(() => {
    if (products.length > 0) {
      products.forEach(product => {
        // Only generate AI image if no product image exists
        if (!product.image_urls || product.image_urls.length === 0) {
          generateAIImage(product.name, product.id);
        }
      });
    }
  }, [products]);

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <StarSolidIcon key={`star-${i}`} className="h-4 w-4 text-yellow-400" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={`star-${i}`} className="relative">
            <StarIcon className="h-4 w-4 text-gray-300" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <StarSolidIcon className="h-4 w-4 text-yellow-400" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <StarIcon key={`star-${i}`} className="h-4 w-4 text-gray-300" />
        );
      }
    }
    return stars;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading storefront...</p>
        </div>
      </div>
    );
  }

  if (!storefront) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <BuildingStorefrontIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Storefront Not Found</h2>
          <p className="text-gray-600">The requested vendor storefront could not be found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            {/* Back to Marketplace Button */}
            <div className="flex items-center space-x-6">
              <Link
                href="/dashboard"
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded-lg px-2 py-1"
              >
                <ArrowLeftIcon className="h-5 w-5" />
                <span className="font-medium">Back to Marketplace</span>
              </Link>
            </div>

            {/* Vendor Info */}
            <div className="flex items-center space-x-6">
              {/* Logo */}
              <div className="flex-shrink-0">
                {storefront.logo_url ? (
                  <img
                    src={storefront.logo_url}
                    alt={`${storefront.business_name} logo`}
                    className="h-16 w-16 rounded-xl object-cover"
                    onError={(e) => {
                      // Hide the broken image and show fallback
                      e.target.style.display = 'none';
                      e.target.nextElementSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div
                  className="h-16 w-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center"
                  style={{ display: storefront.logo_url ? 'none' : 'flex' }}
                >
                  <span className="text-2xl font-bold text-white">
                    {storefront.business_name?.charAt(0) || 'V'}
                  </span>
                </div>
              </div>
              
              {/* Business Details */}
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  {storefront.business_name || `Vendor ${vendorId}'s Store`}
                </h1>
                {storefront.tagline && (
                  <p className="text-lg text-gray-600 mt-1">{storefront.tagline}</p>
                )}
                
                {/* Rating */}
                {storefront.average_rating && (
                  <div className="flex items-center mt-2 space-x-2">
                    <div className="flex items-center">
                      {renderStars(storefront.average_rating)}
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {storefront.average_rating.toFixed(1)}
                    </span>
                    {storefront.review_count && (
                      <span className="text-sm text-gray-600">
                        ({storefront.review_count} reviews)
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
            
            {/* Cart */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsCartModalOpen(true)}
                className="flex items-center space-x-2 bg-blue-50 hover:bg-blue-100 px-4 py-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
              >
                <div className="relative">
                  <ShoppingCartIcon className="h-5 w-5 text-blue-600" />
                  {getCartItemCount() > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                      {getCartItemCount()}
                    </span>
                  )}
                </div>
                <span className="font-medium text-blue-900">
                  Cart ({getCartItemCount()})
                </span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Welcome Message & Info */}
      {(storefront.welcome_message || storefront.business_hours || storefront.location) && (
        <section className="bg-blue-50 border-b border-blue-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {storefront.welcome_message && (
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">Welcome</h2>
                  <p className="text-gray-700 leading-relaxed">{storefront.welcome_message}</p>
                </div>
              )}
              
              <div className="space-y-3">
                {storefront.business_hours && (
                  <div className="flex items-center text-gray-700">
                    <ClockIcon className="h-5 w-5 mr-3 text-gray-400" />
                    <span>{storefront.business_hours}</span>
                  </div>
                )}
                
                {storefront.location && (
                  <div className="flex items-center text-gray-700">
                    <MapPinIcon className="h-5 w-5 mr-3 text-gray-400" />
                    <span>{storefront.location}</span>
                  </div>
                )}
                
                {storefront.contact_phone && (
                  <div className="flex items-center text-gray-700">
                    <PhoneIcon className="h-5 w-5 mr-3 text-gray-400" />
                    <span>{storefront.contact_phone}</span>
                  </div>
                )}
                
                {storefront.contact_email && (
                  <div className="flex items-center text-gray-700">
                    <EnvelopeIcon className="h-5 w-5 mr-3 text-gray-400" />
                    <span>{storefront.contact_email}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
      )}
      
      {/* Products Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Our Products</h2>
          <p className="text-gray-600">
            {products.length} {products.length === 1 ? 'product' : 'products'} available
          </p>
        </div>
        
        {products.length === 0 ? (
          <div className="text-center py-16">
            <BuildingStorefrontIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Products Available</h3>
            <p className="text-gray-600">This vendor hasn't added any products yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map(product => (
              <div key={product.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200 hover:-translate-y-1 flex flex-col h-full">
                {/* Product Image */}
                <div className="aspect-w-1 aspect-h-1 bg-gray-200 relative overflow-hidden">
                  {/* Show original product image if available and not errored */}
                  {product.image_urls && product.image_urls.length > 0 && !imageErrors[product.id] ? (
                    <img
                      src={product.image_urls[0]}
                      alt={product.name}
                      className="w-full h-48 object-cover"
                      onError={() => handleImageError(product.id)}
                    />
                  ) : aiImages[product.id] ? (
                    /* Show AI-generated image if available */
                    <div className="relative">
                      <img
                        src={aiImages[product.id]}
                        alt={`AI generated image for ${product.name}`}
                        className="w-full h-48 object-cover"
                        onError={() => {
                          setAiImages(prev => {
                            const newState = { ...prev };
                            delete newState[product.id];
                            return newState;
                          });
                        }}
                      />
                      {/* AI Badge */}
                      <div className="absolute top-2 right-2 bg-blue-600 text-white text-xs px-2 py-1 rounded-full flex items-center space-x-1">
                        <PhotoIcon className="h-3 w-3" />
                        <span>AI</span>
                      </div>
                    </div>
                  ) : loadingImages[product.id] ? (
                    /* Show loading state while generating AI image */
                    <div className="w-full h-48 bg-gradient-to-br from-blue-50 to-blue-100 flex flex-col items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
                      <p className="text-xs text-blue-600 font-medium">Generating image...</p>
                    </div>
                  ) : (
                    /* Fallback placeholder */
                    <div className="w-full h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                      <BuildingStorefrontIcon className="h-12 w-12 text-gray-400" />
                    </div>
                  )}
                </div>
                
                {/* Product Info */}
                <div className="p-6 flex flex-col flex-grow">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                    {product.name}
                  </h3>
                  
                  <div className="flex-grow mb-4">
                    {product.description ? (
                      <p className="text-sm text-gray-600 line-clamp-3">
                        {product.description}
                      </p>
                    ) : (
                      <div className="h-12"></div>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between mt-auto">
                    <span className="text-xl font-bold text-gray-900">
                      {formatCurrency(product.price)}
                    </span>
                    
                    <button
                      onClick={() => addToCart(product)}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 flex items-center space-x-2"
                    >
                      <ShoppingCartIcon className="h-4 w-4" />
                      <span>Add to Cart</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Cart Modal */}
      <CartModal
        isOpen={isCartModalOpen}
        onClose={() => setIsCartModalOpen(false)}
      />
    </div>
  );
}