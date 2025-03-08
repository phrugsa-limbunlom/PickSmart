import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Dict

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service.ChatbotService import ChatbotService
from data.ChatMessage import ChatMessage
from processor.ChatbotProcessor import ChatbotProcessor

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = ['kafka:9092']
CHAT_TOPIC = 'chatbot_messages'
RESPONSE_TOPIC = 'chatbot_responses'


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    An asynchronous context manager that initializes and cleans up the
    Kafka producer, Kafka consumer, and ChatbotService for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded to allow the application to run within this context.

    Raises:
        Exception: Propagates any exceptions occurred during initialization or cleanup.
    """

    producer: AIOKafkaProducer | None = None
    consumer: AIOKafkaConsumer | None = None

    try:
        logger.info("Initializing Chatbot Service...")
        service = ChatbotService()
        service.initialize_service()

        logger.info("Initializing Kafka producer and consumer...")

        # Initialize producer
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await producer.start()

        # Initialize consumer
        consumer = AIOKafkaConsumer(
            RESPONSE_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id='chatbot_response_group',
            auto_offset_reset='latest',  # Changed from 'earliest' to 'latest'
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        await consumer.start()

        # Store in app state
        app.state.producer = producer
        app.state.consumer = consumer
        app.state.service = service

        logger.info("Kafka producer and consumer initialized successfully.")

        yield  # App runs here

    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise
    finally:
        logger.info("Closing Kafka producer and consumer...")
        # Proper async cleanup with checks
        if producer:
            try:
                await producer.stop()
            except Exception as e:
                logger.error(f"Error stopping producer: {e}")

        if consumer:
            try:
                await consumer.unsubscribe()
                await consumer.stop()
            except Exception as e:
                logger.error(f"Error stopping consumer: {e}")

        logger.info("Kafka producer and consumer closed.")


app = FastAPI(lifespan=lifespan)

# enable cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow only frontend
    allow_credentials=True,
    allow_methods=["POST"],  # Define methods
    allow_headers=["*"],
)


@app.post("/api/chat")
async def process_chat_message(chat_message: ChatMessage, request: Request) -> Dict[str, Any]:
    """
    Endpoint to process incoming chat messages. Sends the message to a Kafka topic,
    awaits the response, and returns the chatbot's answer.

    Args:
        chat_message (ChatMessage): The chat message sent by the client.
        request (Request): The HTTP request object containing app state
                           (producer, consumer, service).

    Returns:
        Dict[str, Any]: A dictionary containing the chatbot's response.

    Raises:
        HTTPException: If the Kafka producer or consumer is not initialized,
                       or if there's an error during message processing.
    """
    logger.info(f"Message: {chat_message.message}")

    producer: AIOKafkaProducer = request.app.state.producer
    consumer: AIOKafkaConsumer = request.app.state.consumer
    service: ChatbotService = request.app.state.service

    if not producer or not consumer:
        raise HTTPException(status_code=500, detail="Kafka producer or consumer is not initialized.")

    processor = ChatbotProcessor(service=service,
                                 producer=producer,
                                 consumer=consumer,
                                 server=KAFKA_BOOTSTRAP_SERVERS,
                                 input_topic=CHAT_TOPIC,
                                 output_topic=RESPONSE_TOPIC)

    try:
        logger.info("Waiting for Kafka response...")
        response = await processor.process_messages(chat_message.message)
        logger.info(f"Kafka response received: {response}")
        return response
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))