package shoppingapplicationbackend.order.service.resources;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.io.Serializable;

@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class Resource<T> implements Serializable {
    @Getter(onMethod = @__(@JsonIgnore))
    @Setter(value = AccessLevel.PUBLIC)
    private T model;

    public Resource(T model) {
        this.model = model;
    }
}
