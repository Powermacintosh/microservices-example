# Руководство по настройке Apache Kafka (bitnami/kafka)

Этот документ содержит полное руководство по настройке Apache Kafka с акцентом на режиме KRaft, используемом в данном проекте.

## Содержание

1. [Обзор режима KRaft](#обзор-режима-kraft)
2. [Основные настройки](#основные-настройки)
3. [Настройки хранения сообщений](#настройки-хранения-сообщений)
4. [Оптимизация производительности](#оптимизация-производительности)
5. [Мониторинг и обслуживание](#мониторинг-и-обслуживание)

## Сравнение пакетов контейнеров (bitnami/kafka и apache/kafka)

Основные отличия между `bitnami/kafka` и `apache/kafka`:

1. **Базовый образ**:

   - `bitnami/kafka` использует минимальный образ на основе Debian
   - `apache/kafka` использует образ на основе Ubuntu

2. **Управление процессом**:

   - Bitnami использует `tini` для корректной обработки сигналов
   - Apache Kafka использует скрипты обертки

3. **Безопасность**:

   - Bitnami запускает Kafka от непривилегированного пользователя `1001` по умолчанию
   - Apache Kafka может требовать настройки прав вручную

4. **Переменные окружения**:

   - Bitnami использует префикс `KAFKA_` для всех настроек
   - Apache Kafka может требовать ручного конфигурирования файлов

5. **Версионирование**:

   - Bitnami выпускает обновления быстрее
   - Apache Kafka обновляется реже, но официально

6. **Дополнительные утилиты**:

   - Bitnami включает дополнительные скрипты для управления
   - Apache Kafka предоставляет только базовый функционал

7. **Размер образа**:
   - `bitnami/kafka` обычно легче
   - `apache/kafka` может быть больше из-за включенных зависимостей

Для продакшена Bitnami часто предпочтительнее из-за лучшей безопасности и удобства настройки.

## Обзор режима KRaft

### Что такое KRaft?

KRaft (Kafka Raft Metadata Mode) — это новый протокол консенсуса, который устраняет необходимость в ZooKeeper для Apache Kafka. Он был представлен для упрощения архитектуры Kafka и улучшения её масштабируемости.

### Ключевые отличия от Kafka с ZooKeeper

| Характеристика         | Режим KRaft                                                   | Режим с ZooKeeper                                                |
| ---------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------- |
| **Архитектура**        | Один тип процесса (брокер + контроллер)                       | Требуется отдельный ансамбль ZooKeeper                           |
| **Масштабируемость**   | Лучшая обработка метаданных для больших кластеров             | Может стать узким местом при большом количестве топиков/партиций |
| **Развертывание**      | Более простое развертывание с меньшим количеством компонентов | Требует отдельного управления ZooKeeper                          |
| **Производительность** | Меньшая задержка операций с метаданными                       | Большая задержка из-за координации через ZooKeeper               |
| **Зрелость**           | Готово к продакшену начиная с Kafka 3.3                       | Проверено временем, но сложнее в настройке                       |

## Основные настройки

### Идентификация брокера

```yaml
KAFKA_BROKER_ID: 1 # Уникальный идентификатор брокера в кластере
KAFKA_CFG_NODE_ID: 1 # Идентификатор ноды в режиме KRaft
```

### Сеть и безопасность

```yaml
KAFKA_CFG_LISTENERS: "CONTROLLER://:9093,PLAINTEXT://:9092"
KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT"
KAFKA_CFG_ADVERTISED_LISTENERS: "PLAINTEXT://kafka:9092"
KAFKA_CFG_CONTROLLER_LISTENER_NAMES: "CONTROLLER"
KAFKA_CFG_INTER_BROKER_LISTENER_NAME: "PLAINTEXT"
```

### Настройки KRaft

```yaml
KAFKA_CFG_PROCESS_ROLES: "controller,broker" # Роли ноды в режиме KRaft
KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093" # Формат: {id}@{хост}:{порт}
```

## Настройки хранения сообщений

### Временное хранение

```yaml
# Хранить сообщения 7 дней (по умолчанию)
KAFKA_CFG_LOG_RETENTION_HOURS: "168"
# Альтернатива в миллисекундах
# KAFKA_CFG_LOG_RETENTION_MS: "604800000"
```

### Ограничение по размеру

```yaml
# Без ограничения по размеру
KAFKA_CFG_LOG_RETENTION_BYTES: "-1"
# Или установите лимит (например, 10 ГБ)
# KAFKA_CFG_LOG_RETENTION_BYTES: "10737418240"
```

### Управление сегментами логов

```yaml
# Максимальный размер одного файла сегмента (1 ГБ)
KAFKA_CFG_LOG_SEGMENT_BYTES: "1073741824"

# Максимальное время до создания нового сегмента (7 дней)
KAFKA_CFG_LOG_SEGMENT_MS: "604800000"

# Как часто проверять сегменты для удаления (5 минут)
KAFKA_CFG_LOG_RETENTION_CHECK_INTERVAL_MS: "300000"
```

## Оптимизация производительности

### Настройки памяти

```yaml
# Размер кучи (настройте в зависимости от доступной памяти)
KAFKA_HEAP_OPTS: "-Xmx4G -Xms4G"

# Прямая память для сетевых буферов
KAFKA_OPTS: "-XX:MaxDirectMemorySize=1G"
```

### Ввод-вывод и пропускная способность

```yaml
# Количество потоков для обработки сетевых запросов
# Рекомендуемое значение: (количество ядер CPU * 2) + 1
KAFKA_CFG_NUM_NETWORK_THREADS: "3"

# Количество потоков для операций ввода-вывода
# Рекомендуемое значение: количество ядер * 2
KAFKA_CFG_NUM_IO_THREADS: "8"

# Количество потоков для репликации данных между брокерами
# Рекомендуемое значение: количество ядер / 2
KAFKA_CFG_NUM_REPLICA_FETCHERS: "1"

# Размер буфера сокета (в байтах)
KAFKA_CFG_SOCKET_RECEIVE_BUFFER_BYTES: "102400"

# Максимальный размер запроса (в байтах)
KAFKA_CFG_MESSAGE_MAX_BYTES: "1048588" # 1 МБ

# Максимальный размер пакета (в байтах)
KAFKA_CFG_SOCKET_REQUEST_MAX_BYTES: "104857600" # 100 МБ
```

### Оптимизация для высоконагруженных систем

```yml
# Увеличиваем буферы для высоконагруженных систем
KAFKA_CFG_SOCKET_RECEIVE_BUFFER_BYTES: "1048576" # 1 МБ
KAFKA_CFG_SOCKET_SEND_BUFFER_BYTES: "1048576" # 1 МБ

# Настройки для большого количества подключений
KAFKA_CFG_MAX_CONNECTIONS_PER_IP: "2147483647"
KAFKA_CFG_MAX_CONNECTIONS_PER_IP_OVERRIDES: "127.0.0.1:PLAINTEXT:100"
```

## Топик

```yml
# Автоматическое создание топиков
KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
```

### Что делает:

- Если true (по умолчанию): Kafka автоматически создает топик при первой публикации сообщения в несуществующий топик.
- Если false: Kafka вернет ошибку при попытке отправить сообщение в несуществующий топик.

### Плюсы включения (true):

- Удобство разработки - не нужно создавать топики вручную
- Гибкость - приложения могут создавать топики "на лету"

### Минусы включения:

- Безопасность - любое приложение может создать топик
- Опечатки - можно случайно создать дубликат топика из-за опечатки в названии
- Неконтролируемый рост - может привести к созданию множества ненужных топиков

### Рекомендации:

- Для разработки: можно оставить true для удобства
- Для продакшена: лучше установить false и создавать топики вручную через:

```bash
docker exec -it kafka kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic <ваш_топик>
```

## Мониторинг и обслуживание

### Проверка работоспособности

```yml
healthcheck:
  test:
    [
      "CMD",
      "bash",
      "-c",
      "kafka-topics.sh --list --bootstrap-server localhost:9092",
    ]
  interval: 10s
  timeout: 5s
  retries: 6
  start_period: 20s
```

### Полезные команды

#### Проверка настроек брокеров

```bash
docker exec -it kafka bash -c "kafka-configs.sh --describe --all --bootstrap-server localhost:9092 --entity-type brokers"
```

#### Проверка конфигурации топика

```bash
docker exec -it kafka kafka-configs.sh --describe --all --bootstrap-server localhost:9092
```

#### Мониторинг групп потребителей

```bash
docker exec -it kafka kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```

#### Проверка хранения сообщений

```bash
docker exec -it kafka kafka-log-dirs.sh --bootstrap-server localhost:9092 --describe --topic-list ваш-топик
```

#### Проверка загрузки потоков

```bash
docker exec -it kafka kafka-run-class.sh kafka.tools.JmxTool --object-name kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent --jmx-url service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi
```

### Проверка очереди запросов

```bash
docker exec -it kafka kafka-run-class.sh kafka.tools.JmxTool --object-name kafka.network:type=RequestChannel,name=RequestQueueSize --jmx-url service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi
```

### Текущие настройки ретеншена

```bash
docker exec -it kafka kafka-configs.sh --describe --bootstrap-server localhost:9092 --entity-type brokers --entity-default
```

## Скрипты

### Удаление записей

#### Инструмент для принудительного удаления записей из топиков Kafka

```bash
# Создаем JSON-файл с указанием топика и оффсета, до которого нужно удалить записи
cat > delete-records.json << 'EOF'
{
  "partitions": [
    {
      "topic": "your_topic_name",
      "partition": 0,
      "offset": 100  # Удалить все сообщения до этого оффсета (не включительно)
    }
  ],
  "version": 1
}
EOF
```

#### Запускаем удаление записей

```bash
docker exec -it kafka kafka-delete-records.sh \
  --bootstrap-server localhost:9092 \
  --offset-json-file delete-records.json
```

## Рекомендации

1. **Для продакшена**:

   - Используйте минимум 3 ноды для отказоустойчивости
   - Установите подходящую политику хранения в зависимости от доступного места
   - Мониторьте использование диска и отставание потребителей

2. **Для разработки**:

   - Установите меньшее время хранения для экономии места
   - Включите автоматическое создание топиков для удобства
   - Используйте незащищенный протокол (PLAINTEXT) только в разработке

3. **Для KRaft**:
   - Убедитесь в правильности настройки `node.id` и `process.roles`
   - Следите за состоянием контроллера в режиме KRaft
   - Контролируйте рост лога метаданных

## Ссылки

- [Документация Apache Kafka](https://kafka.apache.org/documentation/)
- [Документация по KRaft](https://cwiki.apache.org/confluence/display/KAFKA/KIP-500%3A+Replace+ZooKeeper+with+a+Self-Managed+Metadata+Quorum)
- [Настройка Kafka](https://kafka.apache.org/documentation/#configuration)
