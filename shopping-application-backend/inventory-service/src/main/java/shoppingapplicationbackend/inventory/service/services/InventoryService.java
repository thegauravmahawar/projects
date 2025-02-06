package shoppingapplicationbackend.inventory.service.services;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import shoppingapplicationbackend.inventory.service.repositories.InventoryRepository;

@Service
@RequiredArgsConstructor
public class InventoryService {

    private final InventoryRepository inventoryRepository;

    @Transactional(readOnly = true)
    public boolean isInStock(String skuCode) {
        return inventoryRepository.existsBySkuCodeAndQuantityIsGreaterThan(skuCode, 0);
    }
}
