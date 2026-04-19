package com.example.applicationspublisher.applicationspublisher.service;

import com.example.applicationspublisher.applicationspublisher.config.RabbitMQConfig;
import com.example.applicationspublisher.applicationspublisher.dto.ApplicationDto;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.amqp.rabbit.core.RabbitTemplate;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MessagePublisherTest {

    @Mock
    private RabbitTemplate rabbitTemplate;

    @InjectMocks
    private MessagePublisher messagePublisher;

    @Test
    void publishApplication_shouldSendMessageToQueue() {
        // Arrange
        ApplicationDto application = new ApplicationDto();
        application.setFullName("Test");
        application.setPhone("123");
        application.setOption("Option");

        // Act
        messagePublisher.publishApplication(application);

        // Assert
        verify(rabbitTemplate).convertAndSend(eq(RabbitMQConfig.QUEUE_NAME), eq(application));
    }

    @Test
    void publishApplication_whenRabbitTemplateThrowsException_shouldPropagate() {
        // Arrange
        ApplicationDto application = new ApplicationDto();
        application.setFullName("Test");
        application.setPhone("123");
        application.setOption("Option");

        // Simulate exception
        doThrow(new RuntimeException("RabbitMQ error")).when(rabbitTemplate).convertAndSend(anyString(), (Object) any());

        // Act & Assert
        RuntimeException thrown = assertThrows(RuntimeException.class, () -> messagePublisher.publishApplication(application));
        assertEquals("RabbitMQ error", thrown.getMessage());
    }
}
