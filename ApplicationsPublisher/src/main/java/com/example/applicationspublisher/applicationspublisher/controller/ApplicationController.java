package com.example.applicationspublisher.applicationspublisher.controller;

import com.example.applicationspublisher.applicationspublisher.dto.ApplicationDto;
import com.example.applicationspublisher.applicationspublisher.service.MessagePublisher;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/applications")
@Tag(name = "Applications", description = "API для работы с заявками")
public class ApplicationController {

    private final MessagePublisher messagePublisher;

    public ApplicationController(MessagePublisher messagePublisher) {
        this.messagePublisher = messagePublisher;
    }

    @PostMapping
    @Operation(summary = "Создать заявку", description = "Принимает заявку и отправляет в очередь RabbitMQ")
    @ApiResponse(responseCode = "200", description = "Заявка успешно создана", content = @Content)
    @ApiResponse(responseCode = "400", description = "Ошибка валидации", content = @Content)
    public ResponseEntity<String> submitApplication(@RequestBody ApplicationDto application) {
        if (application.getFullName() == null || application.getFullName().isEmpty()) {
            return ResponseEntity.badRequest().body("fullName is required");
        }
        if (application.getPhone() == null || application.getPhone().isEmpty()) {
            return ResponseEntity.badRequest().body("phone is required");
        }
        if (application.getOption() == null || application.getOption().isEmpty()) {
            return ResponseEntity.badRequest().body("option is required");
        }
        if (application.getOption().length() > 50) {
            return ResponseEntity.badRequest().body("option must be max 50 characters");
        }

        messagePublisher.publishApplication(application);
        return ResponseEntity.ok("Application submitted successfully");
    }

    @PostMapping(value = "/tilda", consumes = MediaType.APPLICATION_FORM_URLENCODED_VALUE)
    public ResponseEntity<String> receiveFromTilda(
            @RequestParam("Name") String name,
            @RequestParam("Phone") String phone,
            @RequestParam("Option") String option) {

        ApplicationDto dto = new ApplicationDto();
        dto.setFullName(name);
        dto.setPhone(phone);
        dto.setOption(option);

        if (dto.getFullName() == null || dto.getFullName().isEmpty()) {
            return ResponseEntity.badRequest().body("fullName is required");
        }
        if (dto.getPhone() == null || dto.getPhone().isEmpty()) {
            return ResponseEntity.badRequest().body("phone is required");
        }
        if (dto.getOption() == null || dto.getOption().isEmpty()) {
            return ResponseEntity.badRequest().body("option is required");
        }
        if (dto.getOption().length() > 50) {
            return ResponseEntity.badRequest().body("option must be max 50 characters");
        }

        messagePublisher.publishApplication(dto);
        return ResponseEntity.ok("Application submitted from Tilda");
    }
}