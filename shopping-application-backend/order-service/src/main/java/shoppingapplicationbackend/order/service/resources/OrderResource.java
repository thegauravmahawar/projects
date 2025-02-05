package shoppingapplicationbackend.order.service.resources;

import shoppingapplicationbackend.order.service.dao.Order;

public class OrderResource extends Resource<Order> {

    public OrderResource() {
        super(new Order());
    }

    public OrderResource(Order order) {
        super(order);
    }
}
