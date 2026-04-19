package com.example.applicationspublisher.applicationspublisher.config;

import org.junit.jupiter.api.Test;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;

import static org.junit.jupiter.api.Assertions.*;

class RabbitMQConfigTest {

    private final RabbitMQConfig config = new RabbitMQConfig();

    @Test
    void applicationsQueue_shouldReturnQueueWithCorrectNameAndDurable() {
        Queue queue = config.applicationsQueue();

        assertNotNull(queue);
        assertEquals("applicationsQueue", queue.getName());
        assertTrue(queue.isDurable());
    }

    @Test
    void jsonMessageConverter_shouldReturnJacksonConverter() {
        MessageConverter converter = config.jsonMessageConverter();

        assertNotNull(converter);
        assertTrue(converter instanceof Jackson2JsonMessageConverter);
    }
}
