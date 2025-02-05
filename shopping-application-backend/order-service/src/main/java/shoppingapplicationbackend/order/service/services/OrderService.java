package shoppingapplicationbackend.order.service.services;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import shoppingapplicationbackend.order.service.repositories.OrderRepository;

@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
}
