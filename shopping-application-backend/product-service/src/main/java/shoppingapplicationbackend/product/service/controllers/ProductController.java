package shoppingapplicationbackend.product.service.controllers;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import shoppingapplicationbackend.product.service.dao.Product;
import shoppingapplicationbackend.product.service.resources.ProductResource;
import shoppingapplicationbackend.product.service.services.ProductService;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/products")
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

    @GetMapping
    @ResponseStatus(HttpStatus.OK)
    public List<ProductResource> getProducts() {
        List<Product> products = productService.getProducts();
        return products.stream()
                .map(ProductResource::new)
                .collect(Collectors.toList());
    }
}
