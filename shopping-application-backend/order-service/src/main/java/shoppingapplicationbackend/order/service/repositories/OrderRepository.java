package shoppingapplicationbackend.order.service.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import shoppingapplicationbackend.order.service.dao.Order;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
}
