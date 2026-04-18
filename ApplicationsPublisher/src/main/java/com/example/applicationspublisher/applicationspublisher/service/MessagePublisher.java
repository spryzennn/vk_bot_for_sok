package com.example.applicationspublisher.applicationspublisher.service;

import com.example.applicationspublisher.applicationspublisher.config.RabbitMQConfig;
import com.example.applicationspublisher.applicationspublisher.dto.ApplicationDto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

@Service
public class MessagePublisher {

    private static final Logger logger = LoggerFactory.getLogger(MessagePublisher.class);
    private final RabbitTemplate rabbitTemplate;

    public MessagePublisher(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void publishApplication(ApplicationDto application) {
        logger.info("Publishing application to queue: {}", application);
        rabbitTemplate.convertAndSend(RabbitMQConfig.QUEUE_NAME, application);
        logger.info("Application published successfully");
    }
}