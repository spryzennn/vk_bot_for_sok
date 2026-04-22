package com.example.applicationspublisher.applicationspublisher.controller;

import com.example.applicationspublisher.applicationspublisher.dto.ApplicationDto;
import com.example.applicationspublisher.applicationspublisher.service.MessagePublisher;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class TildaEndpointTest {

    @Mock
    private MessagePublisher messagePublisher;

    @Test
    void testReceiveFromTilda_Success() {
        ApplicationController controller = new ApplicationController(messagePublisher);
        var response = controller.receiveFromTilda("Арсений", "+79991234567", "test");

        assertEquals("Application submitted from Tilda", response.getBody());
        verify(messagePublisher).publishApplication(argThat(arg ->
            "Арсений".equals(arg.getFullName()) &&
            "+79991234567".equals(arg.getPhone()) &&
            "test".equals(arg.getOption())
        ));
    }

    @Test
    void testReceiveFromTilda_EmptyFullName() {
        ApplicationController controller = new ApplicationController(messagePublisher);
        var response = controller.receiveFromTilda("", "+79991234567", "test");

        assertEquals("fullName is required", response.getBody());
        verify(messagePublisher, never()).publishApplication(any());
    }

    @Test
    void testReceiveFromTilda_EmptyPhone() {
        ApplicationController controller = new ApplicationController(messagePublisher);
        var response = controller.receiveFromTilda("Арсений", "", "test");

        assertEquals("phone is required", response.getBody());
        verify(messagePublisher, never()).publishApplication(any());
    }

    @Test
    void testReceiveFromTilda_EmptyOption() {
        ApplicationController controller = new ApplicationController(messagePublisher);
        var response = controller.receiveFromTilda("Арсений", "+79991234567", "");

        assertEquals("option is required", response.getBody());
        verify(messagePublisher, never()).publishApplication(any());
    }

    @Test
    void testReceiveFromTilda_OptionTooLong() {
        ApplicationController controller = new ApplicationController(messagePublisher);
        String longOption = "a".repeat(51);
        var response = controller.receiveFromTilda("Арсений", "+79991234567", longOption);

        assertEquals("option must be max 50 characters", response.getBody());
        verify(messagePublisher, never()).publishApplication(any());
    }
}
