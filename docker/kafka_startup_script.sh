# Start ZooKeeper
setsid zookeeper-server-start.sh config/zookeeper.properties >/dev/null 2>&1 || echo "Zookeeper failed to start"

# Start Kafka
setsid kafka-server-start.sh config/server.properties >/dev/null 2>&1 || echo "Kafka failed to start"
if [ $? -eq 0 ]; then
	# Create the topic "ids"
	sleep 5
	kafka-topics.sh --create --topic ids --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
fi

# Start the subscriber
python3 subscriber.py
