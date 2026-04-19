package com.example.applicationspublisher.applicationspublisher.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class OpenApiConfigTest {

    private final OpenApiConfig config = new OpenApiConfig();

    @Test
    void openAPI_shouldReturnOpenAPIObjectWithCorrectInfo() {
        // Act
        OpenAPI api = config.openAPI();

        // Assert
        assertNotNull(api);
        assertNotNull(api.getInfo());
        assertEquals("Applications Publisher API", api.getInfo().getTitle());
        assertEquals("API для приёма заявок и отправки в RabbitMQ", api.getInfo().getDescription());
        assertEquals("1.0.0", api.getInfo().getVersion());
        assertNotNull(api.getInfo().getContact());
        assertEquals("Support", api.getInfo().getContact().getName());
        assertEquals("lapinka.maksimka@gmail.com", api.getInfo().getContact().getEmail());
    }
}
