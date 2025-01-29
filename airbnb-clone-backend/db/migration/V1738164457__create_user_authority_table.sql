CREATE TABLE user_authority (
    user_id INTEGER NOT NULL REFERENCES users(id),
    authority VARCHAR(50) NOT NULL,

    PRIMARY KEY (user_id, authority)
)