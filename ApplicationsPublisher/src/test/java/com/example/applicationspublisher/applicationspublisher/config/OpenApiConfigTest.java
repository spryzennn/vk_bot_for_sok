package com.example.applicationspublisher.applicationspublisher.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class OpenApiConfigTest {

    @Test
    void openAPI_shouldReturnOpenAPIObjectWithCorrectInfo() {
        OpenApiConfig config = new OpenApiConfig();
        // Устанавливаем sslEnabled=false для теста (значение по умолчанию)
        ReflectionTestUtils.setField(config, "sslEnabled", false);

        OpenAPI api = config.customOpenAPI();

        assertNotNull(api);
        assertNotNull(api.getInfo());
        assertEquals("Applications Publisher API", api.getInfo().getTitle());
        assertEquals("API для приёма заявок и отправки в RabbitMQ", api.getInfo().getDescription());
        assertEquals("1.0.0", api.getInfo().getVersion());
        assertNotNull(api.getInfo().getContact());
        assertEquals("Support", api.getInfo().getContact().getName());
        assertEquals("lapinka.maksimka@gmail.com", api.getInfo().getContact().getEmail());

        // Проверяем серверы
        assertFalse(api.getServers().isEmpty());
        assertEquals("http://quattuordevs.ru/api", api.getServers().get(0).getUrl());
        assertEquals("Development server (HTTP)", api.getServers().get(0).getDescription());
    }

    @Test
    void openAPI_shouldUseHttpsWhenSslEnabled() {
        OpenApiConfig config = new OpenApiConfig();
        ReflectionTestUtils.setField(config, "sslEnabled", true);

        OpenAPI api = config.customOpenAPI();

        assertFalse(api.getServers().isEmpty());
        assertEquals("https://quattuordevs.ru/api", api.getServers().get(0).getUrl());
        assertEquals("Production server (HTTPS)", api.getServers().get(0).getDescription());
    }
}
