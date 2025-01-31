package airbnbclonebackend.dao;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "listing")
public class Listing extends BaseModel {
}
