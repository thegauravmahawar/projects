package shoppingapplicationbackend.notification.service.services;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import shoppingapplicationbackend.notification.service.models.OrderEvent;

@Service
@RequiredArgsConstructor
@Slf4j
public class NotificationService {

    @KafkaListener(topics = "order-topic")
    public void orderListener(OrderEvent event) {
        log.info("Received new order");
        System.out.println(event.getOrderNumber());
    }
}
