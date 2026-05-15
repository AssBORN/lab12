-- Migration 002: Optimization and Indexing
-- Adding indices for frequently queried fields to improve performance

-- Index for product search by name (using btree for exact matches/prefixes)
CREATE INDEX idx_products_name ON products(name);

-- Index for filtering products by seller (Crucial for "My Products" page)
CREATE INDEX idx_products_seller_id ON products(seller_id);

-- Index for retrieving reviews for a specific product
CREATE INDEX idx_reviews_product_id ON reviews(product_id);

-- Index for order date to optimize reporting and history queries
CREATE INDEX idx_orders_date ON orders(order_date);
