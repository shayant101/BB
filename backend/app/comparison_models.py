from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SortBy(str, Enum):
    PRICE_LOW_TO_HIGH = "price_low_to_high"
    PRICE_HIGH_TO_LOW = "price_high_to_low"
    RATING = "rating"
    DELIVERY_TIME = "delivery_time"
    AVAILABILITY = "availability"

class ProductQuery(BaseModel):
    name: str = Field(..., description="Product name to search for")
    category: Optional[str] = Field(None, description="Product category filter")
    brand: Optional[str] = Field(None, description="Brand filter")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Product specifications")

class RequestFilters(BaseModel):
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    min_price: Optional[float] = Field(None, description="Minimum price filter")
    vendors: Optional[List[str]] = Field(None, description="List of vendor IDs to include")
    delivery_radius: Optional[float] = Field(None, description="Maximum delivery radius in miles")
    min_rating: Optional[float] = Field(None, description="Minimum vendor rating")
    sort_by: Optional[SortBy] = Field(SortBy.PRICE_LOW_TO_HIGH, description="Sort criteria")

class ComparisonRequest(BaseModel):
    products: List[ProductQuery] = Field(..., description="List of products to compare")
    restaurant_location: Optional[Dict[str, float]] = Field(None, description="Restaurant coordinates (lat, lng)")
    filters: Optional[RequestFilters] = Field(None, description="Comparison filters")
    include_recommendations: Optional[bool] = Field(True, description="Include smart recommendations")

class Availability(BaseModel):
    in_stock: bool = Field(..., description="Whether product is in stock")
    quantity_available: Optional[int] = Field(None, description="Available quantity")
    estimated_restock: Optional[datetime] = Field(None, description="Estimated restock date")
    lead_time_days: Optional[int] = Field(None, description="Lead time in days")

class PricingDetails(BaseModel):
    unit_price: float = Field(..., description="Price per unit")
    bulk_pricing: Optional[List[Dict[str, Any]]] = Field(None, description="Bulk pricing tiers")
    discounts: Optional[List[Dict[str, Any]]] = Field(None, description="Available discounts")
    total_cost: float = Field(..., description="Total cost including fees")
    delivery_fee: Optional[float] = Field(None, description="Delivery fee")
    tax_rate: Optional[float] = Field(None, description="Tax rate")

class VendorResult(BaseModel):
    vendor_id: str = Field(..., description="Vendor identifier")
    vendor_name: str = Field(..., description="Vendor business name")
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    brand: Optional[str] = Field(None, description="Product brand")
    category: str = Field(..., description="Product category")
    pricing: PricingDetails = Field(..., description="Pricing information")
    availability: Availability = Field(..., description="Availability information")
    vendor_rating: Optional[float] = Field(None, description="Vendor rating")
    delivery_time: Optional[str] = Field(None, description="Estimated delivery time")
    minimum_order: Optional[float] = Field(None, description="Minimum order amount")
    certifications: Optional[List[str]] = Field(None, description="Product certifications")

class ProductComparisonResult(BaseModel):
    query: ProductQuery = Field(..., description="Original product query")
    vendors: List[VendorResult] = Field(..., description="Vendor results for this product")
    best_price_vendor: Optional[str] = Field(None, description="Vendor ID with best price")
    average_price: Optional[float] = Field(None, description="Average price across vendors")
    price_range: Optional[Dict[str, float]] = Field(None, description="Min and max prices")

class PerformanceMetrics(BaseModel):
    search_time_ms: int = Field(..., description="Search execution time in milliseconds")
    vendors_searched: int = Field(..., description="Number of vendors searched")
    products_found: int = Field(..., description="Total products found")
    cache_hit_rate: Optional[float] = Field(None, description="Cache hit rate percentage")

class SmartSuggestion(BaseModel):
    type: str = Field(..., description="Suggestion type (alternative, bundle, etc.)")
    title: str = Field(..., description="Suggestion title")
    description: str = Field(..., description="Suggestion description")
    potential_savings: Optional[float] = Field(None, description="Potential cost savings")
    confidence_score: Optional[float] = Field(None, description="AI confidence score")

class Recommendation(BaseModel):
    vendor_id: str = Field(..., description="Recommended vendor ID")
    reason: str = Field(..., description="Recommendation reason")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    potential_savings: Optional[float] = Field(None, description="Potential savings amount")

class ComparisonSummary(BaseModel):
    total_products_compared: int = Field(..., description="Total products in comparison")
    total_vendors: int = Field(..., description="Total unique vendors")
    average_savings_potential: Optional[float] = Field(None, description="Average potential savings")
    best_overall_vendor: Optional[str] = Field(None, description="Best overall vendor recommendation")

class ComparisonResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(..., description="Response timestamp")
    results: List[ProductComparisonResult] = Field(..., description="Comparison results per product")
    performance_metrics: PerformanceMetrics = Field(..., description="Performance metrics")
    recommendations: List[Recommendation] = Field(..., description="AI-powered recommendations")
    summary: ComparisonSummary = Field(..., description="Comparison summary")
    smart_suggestions: Optional[List[SmartSuggestion]] = Field(None, description="Smart suggestions")