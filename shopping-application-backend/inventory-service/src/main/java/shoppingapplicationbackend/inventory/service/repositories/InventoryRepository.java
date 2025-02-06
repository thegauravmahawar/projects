package shoppingapplicationbackend.inventory.service.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import shoppingapplicationbackend.inventory.service.dao.Inventory;

@Repository
public interface InventoryRepository extends JpaRepository<Inventory, Long> {

    boolean existsBySkuCodeAndQuantityIsGreaterThan(String skuCode, int quantity);
}
