package shoppingapplicationbackend.order.service.services;

import lombok.RequiredArgsConstructor;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import shoppingapplicationbackend.order.service.clients.InventoryClient;
import shoppingapplicationbackend.order.service.dao.Order;
import shoppingapplicationbackend.order.service.models.OrderEvent;
import shoppingapplicationbackend.order.service.repositories.OrderRepository;
import shoppingapplicationbackend.order.service.resources.OrderResource;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final InventoryClient inventoryClient;
    private final KafkaTemplate kafkaTemplate;

    @Transactional(rollbackFor = Throwable.class)
    public Order placeOrder(OrderResource orderResource) {
        Order order = orderResource.getModel();
        boolean productInStock = inventoryClient.isInStock(order.getSkuCode(), order.getQuantity());

        if (!productInStock) {
            throw new RuntimeException(
                    String.format("Product with SKU Code %s is out of stock.", order.getSkuCode())
            );
        }

        order.setOrderNumber(UUID.randomUUID().toString());
        order = orderRepository.save(order);

        OrderEvent orderEvent = new OrderEvent(order.getOrderNumber());
        kafkaTemplate.send("order-topic", orderEvent);

        return order;
    }
}
