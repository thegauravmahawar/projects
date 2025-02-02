package shoppingapplicationbackend.product.service.controllers;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import shoppingapplicationbackend.product.service.dao.Product;
import shoppingapplicationbackend.product.service.resources.ProductResource;
import shoppingapplicationbackend.product.service.services.ProductService;

@RestController
@RequestMapping("/api/product")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProductResource createProduct(@RequestBody ProductResource productResource) {
        Product product = productService.createProduct(productResource);
        return new ProductResource(product);
    }
}
