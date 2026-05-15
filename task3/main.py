from typing import Union

# Константы для настроек цен и комиссий
CUSTOMER_DISCOUNTS = {
    1: 0.15,
    2: 0.10,
    "default": 0.05
}

REGIONAL_TAXES = {
    1: 0.20,
    2: 0.18,
    3: 0.13,
    "default": 0.15
}

SELLER_COMMISSIONS = {
    (101, 102, 103, 104): 0.05,
    (201, 202, 203): 0.08,
    "default": 0.12
}

def calculate_final_price(
    price: float, 
    quantity: int, 
    seller_id: int, 
    customer_type: int, 
    region_id: int, 
    coupon_value: float
) -> Union[float, str]:
    """
    Вычисляет итоговую стоимость товара с учетом скидок, региональных налогов и комиссии продавца.
    """
    # 1. Расчет базовой стоимости
    total_price = price * quantity
    
    # 2. Применение скидки клиента
    discount_rate = CUSTOMER_DISCOUNTS.get(customer_type, CUSTOMER_DISCOUNTS["default"])
    total_price -= total_price * discount_rate
    
    # 3. Применение купона
    if coupon_value > 0:
        total_price -= coupon_value
    
    # 4. Добавление регионального налога
    tax_rate = REGIONAL_TAXES.get(region_id, REGIONAL_TAXES["default"])
    total_price += total_price * tax_rate
    
    # 5. Вычет комиссии продавца
    commission_rate = SELLER_COMMISSIONS["default"]
    for sellers, rate in SELLER_COMMISSIONS.items():
        if isinstance(sellers, tuple) and seller_id in sellers:
            commission_rate = rate
            break
            
    final_price = total_price * (1 - commission_rate)
    
    # Валидация итоговой суммы
    if final_price <= 0:
        return "Ошибка"
    
    return round(final_price, 2)

if __name__ == "__main__":
    # Тест
    print(calculate_final_price(100.0, 2, 101, 1, 1, 10.0))
