package com.example.applicationspublisher.applicationspublisher.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        OpenAPI openAPI = new OpenAPI()
                .info(new Info()
                        .title("Applications Publisher API")
                        .version("1.0.0")
                        .description("API для приёма заявок и отправки в RabbitMQ")
                        .contact(new Contact()
                                .name("Support")));

        openAPI.addServersItem(new Server()
                .url("https://quattuordevs.ru")
                .description("Production server (HTTPS)"));

        return openAPI;
    }
}