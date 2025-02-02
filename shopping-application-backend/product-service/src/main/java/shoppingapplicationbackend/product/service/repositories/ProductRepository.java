package shoppingapplicationbackend.product.service.repositories;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import shoppingapplicationbackend.product.service.dao.Product;

@Repository
public interface ProductRepository extends MongoRepository<Product, String> {
}
