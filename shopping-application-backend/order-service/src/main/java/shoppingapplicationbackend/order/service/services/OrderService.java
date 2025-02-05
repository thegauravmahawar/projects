package shoppingapplicationbackend.order.service.services;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import shoppingapplicationbackend.order.service.dao.Order;
import shoppingapplicationbackend.order.service.repositories.OrderRepository;
import shoppingapplicationbackend.order.service.resources.OrderResource;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;

    @Transactional(rollbackFor = Throwable.class)
    public Order placeOrder(OrderResource orderResource) {
        Order order = orderResource.getModel();
        order.setOrderNumber(UUID.randomUUID().toString());
        return orderRepository.save(order);
    }
}
