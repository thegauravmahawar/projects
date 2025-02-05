package shoppingapplicationbackend.order.service.controllers;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import shoppingapplicationbackend.order.service.dao.Order;
import shoppingapplicationbackend.order.service.resources.OrderResource;
import shoppingapplicationbackend.order.service.services.OrderService;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResource placeOrder(@RequestBody OrderResource orderResource) {
        Order order = orderService.placeOrder(orderResource);
        return new OrderResource(order);
    }
}
