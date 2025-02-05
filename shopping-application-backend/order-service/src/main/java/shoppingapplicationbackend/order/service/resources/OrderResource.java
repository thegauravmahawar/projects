package shoppingapplicationbackend.order.service.resources;

import shoppingapplicationbackend.order.service.dao.Order;

import java.math.BigDecimal;

public class OrderResource extends Resource<Order> {

    public OrderResource() {
        super(new Order());
    }

    public OrderResource(Order order) {
        super(order);
    }

    public Long getId() {
        return getModel().getId();
    }

    public String getOrderNumber() {
        return getModel().getOrderNumber();
    }

    public void setSkuCode(String skuCode) {
        getModel().setSkuCode(skuCode);
    }

    public String getSkuCode() {
        return getModel().getSkuCode();
    }

    public void setPrice(BigDecimal price) {
        getModel().setPrice(price);
    }

    public BigDecimal getPrice() {
        return getModel().getPrice();
    }

    public void setQuantity(Integer quantity) {
        getModel().setQuantity(quantity);
    }

    public Integer getQuantity() {
        return getModel().getQuantity();
    }
}
