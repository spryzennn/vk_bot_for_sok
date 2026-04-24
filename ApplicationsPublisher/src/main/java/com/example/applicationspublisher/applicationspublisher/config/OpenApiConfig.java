package com.example.applicationspublisher.applicationspublisher.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Value("${server.ssl.enabled:false}")
    private boolean sslEnabled;

    @Bean
    public OpenAPI customOpenAPI() {
        OpenAPI openAPI = new OpenAPI()
                .info(new Info()
                        .title("Applications Publisher API")
                        .version("1.0.0")
                        .description("API для приёма заявок и отправки в RabbitMQ")
                        .contact(new Contact()
                                .name("Support")
                                .email("lapinka.maksimka@gmail.com")));

        String protocol = sslEnabled ? "https" : "http";
        String host = "quattuordevs.ru";
        String url = protocol + "://" + host + "/api";

        openAPI.addServersItem(new Server()
                .url(url)
                .description(sslEnabled ? "Production server (HTTPS)" : "Development server (HTTP)"));

        return openAPI;
    }
}

