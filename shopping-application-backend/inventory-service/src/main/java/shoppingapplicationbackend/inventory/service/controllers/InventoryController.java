package shoppingapplicationbackend.inventory.service.controllers;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import shoppingapplicationbackend.inventory.service.services.InventoryService;

@RestController
@RequestMapping("/api/inventory")
public class InventoryController {

    private final InventoryService inventoryService;

    public InventoryController(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    @GetMapping
    @ResponseStatus(HttpStatus.OK)
    public boolean isInStock(@RequestParam String skuCode) {
        return inventoryService.isInStock(skuCode);
    }
}
