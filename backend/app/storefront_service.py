from typing import List, Optional
from .storefront_models import (
    VendorStorefront, StorefrontUpdate,
    ProductCategory, ProductCategoryCreate, ProductCategoryUpdate,
    VendorProduct, VendorProductCreate, VendorProductUpdate,
    ShoppingCart, ShoppingCartItem,
    CustomerWishlist, WishlistCreate
)
from .inventory_models import InventoryItem, InventorySKU

class StorefrontService:
    @staticmethod
    async def get_storefront_by_vendor_id(vendor_id: str) -> Optional[VendorStorefront]:
        # First, find the vendor by their document ID to get their user_id
        from .user_models import User  # Local import to avoid circular dependency
        vendor = await User.get(vendor_id)
        if not vendor:
            return None

        storefront = await VendorStorefront.find_one(VendorStorefront.vendor_id == vendor.user_id)
        if not storefront:
            # If no storefront exists, create a default one for the vendor
            storefront = VendorStorefront(vendor_id=vendor.user_id)
            await storefront.insert()
        return storefront

    @staticmethod
    async def update_storefront(vendor_id: str, storefront_update: StorefrontUpdate) -> Optional[VendorStorefront]:
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if storefront:
            update_data = storefront_update.dict(exclude_unset=True)
            await storefront.update({"$set": update_data})
            return await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        return None

    @staticmethod
    async def create_product_category(vendor_id: str, category_create: ProductCategoryCreate) -> ProductCategory:
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if not storefront:
            return None
        category = ProductCategory(vendor_id=storefront.vendor_id, **category_create.dict())
        await category.insert()
        return category

    @staticmethod
    async def get_product_categories_by_vendor(vendor_id: str) -> List[ProductCategory]:
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if not storefront:
            return []
        return await ProductCategory.find(ProductCategory.vendor_id == storefront.vendor_id).to_list()

    @staticmethod
    @staticmethod
    async def create_vendor_product(vendor_id: str, product_create: VendorProductCreate) -> VendorProduct:
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if not storefront:
            return None
        product = VendorProduct(vendor_id=storefront.vendor_id, **product_create.dict())
        await product.insert()
        return product

    @staticmethod
    async def get_vendor_products(vendor_id: str) -> List[dict]:
        """Get vendor's actual inventory items for storefront display"""
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if not storefront:
            return []
        # Get all active inventory items for this vendor
        inventory_items = await InventoryItem.find(
            InventoryItem.vendor_id == storefront.vendor_id,
            InventoryItem.is_active == True
        ).to_list()
        
        products = []
        for item in inventory_items:
            # Get SKUs for this item
            skus = await InventorySKU.find(
                InventorySKU.item_id == item.item_id,
                InventorySKU.is_active == True
            ).to_list()
            
            # If no SKUs, create a basic product from the item
            if not skus:
                product = {
                    "id": item.item_id,
                    "name": item.name,
                    "description": item.description,
                    "price": item.base_price,
                    "unit_of_measure": item.unit_of_measure,
                    "brand": item.brand,
                    "image_urls": item.image_urls,
                    "is_featured": item.is_featured,
                    "minimum_order_quantity": item.minimum_order_quantity,
                    "maximum_order_quantity": item.maximum_order_quantity,
                    "current_stock": item.current_stock if item.track_inventory else None,
                    "in_stock": not item.track_inventory or (item.current_stock and item.current_stock > 0),
                    "sku": None,
                    "variant_name": None
                }
                products.append(product)
            else:
                # Create a product for each SKU
                for sku in skus:
                    product = {
                        "id": f"{item.item_id}-{sku.sku_id}",
                        "item_id": item.item_id,
                        "sku_id": sku.sku_id,
                        "name": f"{item.name}" + (f" - {sku.variant_name}" if sku.variant_name else ""),
                        "description": item.description,
                        "price": sku.price,
                        "unit_of_measure": item.unit_of_measure,
                        "brand": item.brand,
                        "image_urls": item.image_urls,
                        "is_featured": item.is_featured,
                        "minimum_order_quantity": item.minimum_order_quantity,
                        "maximum_order_quantity": item.maximum_order_quantity,
                        "current_stock": sku.available_stock,
                        "in_stock": sku.available_stock > 0,
                        "sku": sku.sku_code,
                        "variant_name": sku.variant_name,
                        "attributes": sku.attributes
                    }
                    products.append(product)
        
        return products

    @staticmethod
    async def get_cart(restaurant_id: int, vendor_id: str) -> Optional[ShoppingCart]:
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if not storefront:
            return None
        return await ShoppingCart.find_one(
            ShoppingCart.restaurant_id == restaurant_id,
            ShoppingCart.vendor_id == storefront.vendor_id
        )

    @staticmethod
    async def update_cart(restaurant_id: int, vendor_id: str, items: List[ShoppingCartItem]) -> ShoppingCart:
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if not storefront:
            return None
        cart = await ShoppingCart.find_one(
            ShoppingCart.restaurant_id == restaurant_id,
            ShoppingCart.vendor_id == storefront.vendor_id
        )
        if not cart:
            cart = ShoppingCart(restaurant_id=restaurant_id, vendor_id=storefront.vendor_id)
        
        cart.items = items
        await cart.save()
        return cart

    @staticmethod
    async def add_to_wishlist(restaurant_id: int, vendor_id: str, product_id: int) -> CustomerWishlist:
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if not storefront:
            return None
        wishlist_item = CustomerWishlist(
            restaurant_id=restaurant_id,
            vendor_id=storefront.vendor_id,
            product_id=product_id
        )
        await wishlist_item.insert()
        return wishlist_item

    @staticmethod
    async def get_wishlist(restaurant_id: int, vendor_id: str) -> List[CustomerWishlist]:
        storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
        if not storefront:
            return []
        return await CustomerWishlist.find(
            CustomerWishlist.restaurant_id == restaurant_id,
            CustomerWishlist.vendor_id == storefront.vendor_id
        ).to_list()