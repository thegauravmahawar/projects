package airbnbclonebackend.dao;

import jakarta.persistence.*;

@Entity
@Table(name = "users")
public class User extends AbstractAuditingEntity<Integer> {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Override
    public Integer getId() {
        return id;
    }
}
