package com.example.applicationspublisher.applicationspublisher.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class OpenApiConfigTest {

    @Test
    void openAPI_shouldReturnOpenAPIObjectWithCorrectInfo() {
        OpenApiConfig config = new OpenApiConfig();

        OpenAPI api = config.customOpenAPI();

        assertNotNull(api);
        assertNotNull(api.getInfo());
        assertEquals("Applications Publisher API", api.getInfo().getTitle());
        assertEquals("API для приёма заявок и отправки в RabbitMQ", api.getInfo().getDescription());
        assertEquals("1.0.0", api.getInfo().getVersion());
        assertNotNull(api.getInfo().getContact());
        assertEquals("Support", api.getInfo().getContact().getName());

        // Проверяем серверы
        assertFalse(api.getServers().isEmpty());
        assertEquals("https://quattuordevs.ru", api.getServers().get(0).getUrl());
        assertEquals("Production server (HTTPS)", api.getServers().get(0).getDescription());
    }

    @Test
    void openAPI_shouldUseHttpsByDefault() {
        OpenApiConfig config = new OpenApiConfig();

        OpenAPI api = config.customOpenAPI();

        assertFalse(api.getServers().isEmpty());
        assertEquals("https://quattuordevs.ru", api.getServers().get(0).getUrl());
        assertEquals("Production server (HTTPS)", api.getServers().get(0).getDescription());
    }
}
