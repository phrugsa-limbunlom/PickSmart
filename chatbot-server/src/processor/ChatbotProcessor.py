from typing import Any, Dict
import logging
import uuid
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ChatbotProcessor:
    """
    Processes chatbot messages by sending them to Kafka and retrieving responses.

    Attributes:
        service: The service used for answer generation.
        producer: The Kafka producer instance.
        consumer: The Kafka consumer instance.
        kafka_servers: The Kafka server address.
        input_topic: The name of the input topic.
        output_topic: The name of the output topic.
    """
    def __init__(
        self,
        service: Any,
        producer: Any,
        consumer: Any,
        server: str,
        input_topic: str,
        output_topic: str
    ) -> None:
        """
        Initializes the ChatbotProcessor with the required components.

        Args:
            service: A service implementing the answer generation logic.
            producer: The Kafka producer instance.
            consumer: The Kafka consumer instance.
            server: The address of the Kafka server.
            input_topic: The name of the Kafka topic to produce to.
            output_topic: The name of the Kafka topic to produce the response to.
        """
        self.service = service
        self.producer = producer
        self.consumer = consumer
        self.kafka_servers = server
        self.input_topic = input_topic
        self.output_topic = output_topic

    async def process_messages(self, message: str) -> Dict[str, Any]:
        """
        Sends the incoming message to Kafka, processes it, and retrieves the response.

        Args:
            message: The text to be processed by the chatbot.

        Returns:
            A dictionary containing the chatbot's response and a unique identifier.
        """
        consumer = self.consumer
        producer = self.producer

        logger.info(f"Producer: {producer}, Consumer: {consumer}")

        uid = str(uuid.uuid4())
        logger.info(f"Generated UID for message: {uid}")

        # produce the input message to Kafka
        await producer.send_and_wait(self.input_topic, {
            'uid': uid,
            'message': message,
            'timestamp': str(datetime.now())
        })

        # process the message using Agent
        answer = self.service.generate_answer_with_agent(query=message)

        # produce the generated answer to the output topic
        await producer.send_and_wait(self.output_topic, {
            'uid': uid,
            'response': answer,
            'timestamp': str(datetime.now())
        })

        # consume the response from the output topic
        msg = await consumer.getone()

        if msg.value['uid'] != uid:
            logger.error(f"UID mismatch: expected {uid}, got {msg.value['uid']}")
            raise ValueError("UID mismatch in Kafka message")

        return {"value": msg.value['response'],
                "uid": msg.value['uid']}
