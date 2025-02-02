package shoppingapplicationbackend.product.service.services;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import shoppingapplicationbackend.product.service.dao.Product;
import shoppingapplicationbackend.product.service.repositories.ProductRepository;
import shoppingapplicationbackend.product.service.resources.ProductResource;

@Service
@RequiredArgsConstructor
@Slf4j
public class ProductService {

    private final ProductRepository productRepository;

    @Transactional(rollbackFor = Throwable.class)
    public Product createProduct(ProductResource productResource) {
        Product product = productResource.getModel();
        return productRepository.save(product);
    }
}
