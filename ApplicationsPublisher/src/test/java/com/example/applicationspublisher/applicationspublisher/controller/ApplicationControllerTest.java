package com.example.applicationspublisher.applicationspublisher.controller;

import com.example.applicationspublisher.applicationspublisher.dto.ApplicationDto;
import com.example.applicationspublisher.applicationspublisher.service.MessagePublisher;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class ApplicationControllerTest {

    @Mock
    private MessagePublisher messagePublisher;

    @InjectMocks
    private ApplicationController controller;

    @Test
    void submitApplication_validRequest_returnsOk() {
        ApplicationDto application = new ApplicationDto();
        application.setFullName("Иван Иванов");
        application.setPhone("+79991234567");
        application.setOption("Тестовая заявка");

        ResponseEntity<String> response = controller.submitApplication(application);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals("Application submitted successfully", response.getBody());
        verify(messagePublisher, times(1)).publishApplication(application);
    }

    @Test
    void submitApplication_whenFullNameIsNull_returnsBadRequest() {
        ApplicationDto application = new ApplicationDto();
        application.setPhone("+79991234567");
        application.setOption("Тестовая заявка");

        ResponseEntity<String> response = controller.submitApplication(application);

        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals("fullName is required", response.getBody());
        verify(messagePublisher, never()).publishApplication(any());
    }

    @Test
    void submitApplication_whenPhoneIsNull_returnsBadRequest() {
        ApplicationDto application = new ApplicationDto();
        application.setFullName("Иван Иванов");
        application.setOption("Тестовая заявка");

        ResponseEntity<String> response = controller.submitApplication(application);

        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals("phone is required", response.getBody());
        verify(messagePublisher, never()).publishApplication(any());
    }

    @Test
    void submitApplication_whenOptionIsNull_returnsBadRequest() {
        ApplicationDto application = new ApplicationDto();
        application.setFullName("Иван Иванов");
        application.setPhone("+79991234567");

        ResponseEntity<String> response = controller.submitApplication(application);

        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals("option is required", response.getBody());
        verify(messagePublisher, never()).publishApplication(any());
    }

    @Test
    void submitApplication_whenOptionExceedsMaxLength_returnsBadRequest() {
        ApplicationDto application = new ApplicationDto();
        application.setFullName("Иван Иванов");
        application.setPhone("+79991234567");
        application.setOption("a".repeat(51));

        ResponseEntity<String> response = controller.submitApplication(application);

        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals("option must be max 50 characters", response.getBody());
        verify(messagePublisher, never()).publishApplication(any());
    }

    @Test
    void submitApplication_whenOptionIsMaxLength_returnsOk() {
        ApplicationDto application = new ApplicationDto();
        application.setFullName("Иван Иванов");
        application.setPhone("+79991234567");
        application.setOption("a".repeat(50));

        ResponseEntity<String> response = controller.submitApplication(application);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        verify(messagePublisher, times(1)).publishApplication(application);
    }
}
