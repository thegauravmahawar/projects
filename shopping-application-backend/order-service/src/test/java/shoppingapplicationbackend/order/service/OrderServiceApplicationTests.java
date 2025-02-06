package shoppingapplicationbackend.order.service;

import io.restassured.RestAssured;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.cloud.contract.wiremock.AutoConfigureWireMock;
import org.springframework.context.annotation.Import;
import org.testcontainers.containers.PostgreSQLContainer;
import org.hamcrest.Matchers;
import shoppingapplicationbackend.order.service.stubs.InventoryClientStub;

@Import(TestcontainersConfiguration.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureWireMock(port = 0)
class OrderServiceApplicationTests {

    @ServiceConnection
    static PostgreSQLContainer postgreSQLContainer = new PostgreSQLContainer("postgres:17-alpine");
    @LocalServerPort
    private Integer port;

    @BeforeEach
    void setup() {
        RestAssured.baseURI = "http://localhost";
        RestAssured.port = port;
    }

    static {
        postgreSQLContainer.start();
    }

    @Test
    void shouldPlaceOrder() {
        String request = """
                {
                    "skuCode": "iphone_15",
                    "price": 100,
                    "quantity": 1
                 }
                """;
        InventoryClientStub.stubInventoryCall("iphone_15", 1);
        RestAssured.given()
                .contentType("application/json")
                .body(request)
                .when()
                .post("/api/orders")
                .then()
                .statusCode(201)
                .body("id", Matchers.notNullValue())
                .body("orderNumber", Matchers.notNullValue())
                .body("skuCode", Matchers.equalTo("iphone_15"))
                .body("price", Matchers.equalTo(100))
                .body("quantity", Matchers.equalTo(1));
    }
}
