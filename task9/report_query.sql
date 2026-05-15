-- Analytical Report on Seller Efficiency (Last 30 Days)
-- Metrics: Seller Info, Total Orders, Revenue, Avg Rating, Commission, Return Rate

WITH SellerStats AS (
    -- 1. Aggregate Order and Revenue Data
    SELECT 
        s.id AS seller_id,
        s.name AS seller_name,
        COUNT(DISTINCT o.id) AS total_completed_orders,
        SUM(oi.quantity * oi.price_at_purchase) AS total_revenue,
        SUM(oi.quantity * oi.price_at_purchase * 0.12) AS total_commission, -- Assuming 12% default commission
        COUNT(DISTINCT CASE WHEN o.status = 'returned' THEN o.id END) * 100.0 / COUNT(DISTINCT o.id) AS return_percentage
    FROM 
        sellers s
    JOIN 
        products p ON s.id = p.seller_id
    JOIN 
        order_items oi ON p.id = oi.product_id
    JOIN 
        orders o ON oi.order_id = o.id
    WHERE 
        o.order_date >= CURRENT_DATE - INTERVAL '30 days'
        AND o.status != 'cancelled'
    GROUP BY 
        s.id, s.name
    HAVING 
        COUNT(DISTINCT o.id) > 10
),
SellerRatings AS (
    -- 2. Aggregate Ratings from Reviews
    SELECT 
        p.seller_id,
        ROUND(AVG(r.rating), 2) AS avg_rating
    FROM 
        reviews r
    JOIN 
        products p ON r.product_id = p.id
    GROUP BY 
        p.seller_id
)
SELECT 
    ss.seller_id,
    ss.seller_name,
    ss.total_completed_orders,
    ROUND(ss.total_revenue, 2) AS total_revenue,
    COALESCE(sr.avg_rating, 0) AS average_rating,
    ROUND(ss.total_commission, 2) AS platform_commission,
    ROUND(ss.return_percentage, 2) AS return_rate_percent
FROM 
    SellerStats ss
LEFT JOIN 
    SellerRatings sr ON ss.seller_id = sr.seller_id
ORDER BY 
    ss.total_commission DESC
LIMIT 20;
