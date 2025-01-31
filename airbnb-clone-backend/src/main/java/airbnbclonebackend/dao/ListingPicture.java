package airbnbclonebackend.dao;

import jakarta.persistence.*;

@Entity
@Table(name = "listing_picture")
public class ListingPicture {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;
}
