package shoppingapplicationbackend.product.service.resources;

import shoppingapplicationbackend.product.service.dao.Product;

import java.math.BigDecimal;

public class ProductResource extends Resource<Product> {

    public ProductResource() {
        super(new Product());
    }

    public ProductResource(Product product) {
        super(product);
    }

    public String getId() {
        return getModel().getId();
    }

    public void setName(String name) {
        getModel().setName(name);
    }

    public String getName() {
        return getModel().getName();
    }

    public void setDescription(String description) {
        getModel().setDescription(description);
    }

    public String getDescription() {
        return getModel().getDescription();
    }

    public void setPrice(BigDecimal price) {
        getModel().setPrice(price);
    }

    public BigDecimal getPrice() {
        return getModel().getPrice();
    }

}
