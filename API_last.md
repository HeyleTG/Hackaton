# API Documentation

## Оглавление

- [Общая информация](#общая-информация)
- [Аутентификация](#аутентификация)
- [Каналы](#каналы)
- [Рассылки](#рассылки)
- [Чаты](#чаты)
- [Статистика](#статистика)
- [Тарифы](#тарифы)

## Общая информация

Базовый URL: `http://localhost:5000`

### Формат ответа

Все ответы API имеют следующую структуру:

```json
{
    "status": "success/error",
    "data": {},  // или null
    "message": "Описание результата" // опционально
}
```

### Аутентификация

Для большинства эндпоинтов требуется JWT токен, который необходимо передавать в заголовке:

```
Authorization: Bearer <token>
```

## Эндпоинты

### Аутентификация

#### POST /api/auth/login

Авторизация через логин/пароль.

**Тело запроса:**

```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Ответ:**

```json
{
    "message": "Авторизация успешна",
    "status": "success",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "email": "user@example.com",
        "id": 1,
        "username": "user"
    }
}
```

#### POST /api/auth/register

Регистрация нового пользователя.

**Тело запроса:**

```json
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
}
```

**Ответ:**

```json
{
    "message": "Регистрация успешна",
    "status": "success",
    "token": "eyJhbGciOiJIUzI1NiIsI...",
    "user": {
        "email": "newuser@example.com",
        "id": 17,
        "username": "newuser"
    }
}
```

#### POST /api/auth/external

Внешняя авторизация (Google, Facebook и т.д.). Позволяет как авторизоваться существующему пользователю, так и автоматически зарегистрировать нового.

**Тело запроса:**

```json
{
    "email": "user@example.com",
    "username": "user123",
    "token": "external_auth_token",
    "auth_source": "Google"
}
```

**Ответ (для существующего пользователя):**

```json
{
    "status": "success",
    "message": "Авторизация успешна",
    "is_new_user": false,
    "username_updated": false,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "username": "user123",
        "email": "user@example.com"
    },
    "auth_source": "Google",
    "redirect_url": "/"
}
```

**Ответ (для существующего пользователя с обновлением имени):**

```json
{
    "status": "success",
    "message": "Имя пользователя обновлено",
    "is_new_user": false,
    "username_updated": true,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "username": "user1234",
        "email": "user@example.com"
    },
    "auth_source": "Google",
    "redirect_url": "/"
}
```

**Ответ (для нового пользователя - автоматическая регистрация):**

```json
{
    "status": "success",
    "message": "Регистрация успешна",
    "is_new_user": true,
    "username_updated": false,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 19,
        "username": "user12341",
        "email": "user1@example.com"
    },
    "auth_source": "Google",
    "redirect_url": "/"
}
```

#### GET /api/auth/me

Получение информации о текущем пользователе.

**Postman пример:**

```
GET http://localhost:5000/api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "status": "success",
    "user": {
        "account_created_at": "2025-03-28 20:33",
        "email": "user133@test.com",
        "id": 16,
        "stats": {
            "channels_count": 3,
            "chats_count": 0,
            "mailings_count": 3
        },
        "tariff": {
            "created_at": "2025-03-22 02:19",
            "description": "Базовый тариф для небольших рассылок",
            "max_recipients": 1000,
            "name": "Лайт",
            "remaining_recipients": 970,
            "used_recipients": 30
        },
        "username": "Tester_user"
    }
}
```

### Каналы

#### GET /api/channels

Получение списка каналов пользователя.

**Postman пример:**

```
GET http://localhost:5000/api/channels
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "status": "success",
    "channels": [
        {
            "apiHash": "********",
            "apiId": "********",
            "createdAt": "2024-03-28 20:35",
            "hasSession": true,
            "id": 1,
            "phoneNumber": "+7**********",
            "status": "active",
            "username": "channel1"
        }
    ]
}
```

#### POST /api/channels

Создание нового канала.

**Postman пример:**

```
POST http://localhost:5000/api/channels
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
    "username": "mychannel",
    "apiHash": "hash123",
    "apiId": "12345",
    "phoneNumber": "+79001234567"
}
```

**Ответ:**

```json
{
    "status": "success",
    "channel": {
        "apiHash": "hash123",
        "apiId": "12345",
        "createdAt": "2024-03-29 21:47",
        "id": 2,
        "phoneNumber": "+79001234567",
        "status": "inactive",
        "userId": 1,
        "username": "mychannel"
    }
}
```

#### DELETE /api/channels/

Удаление канала.

**Postman пример:**

```
DELETE http://localhost:5000/api/channels/2
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "status": "success",
}
```

#### PUT /api/channels/

Обновление информации о канале.

**Postman пример:**

```
PUT http://localhost:5000/api/channels/2
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
    "username": "newchannel",
    "apiHash": "hash123456",
    "apiId": "12345678",
    "phoneNumber": "+79001234567"
}
```

**Ответ:**

```json
{
    "status": "success",
    "message": "Канал успешно обновлен",
    "data": {
        "apiHash": "hash123456",
        "apiId": "12345678",
        "hasSession": false,
        "id": 2,
        "phoneNumber": "+79001234567",
        "status": "inactive",
        "user_id": 1,
        "username": "newchannel"
    }
}
```

#### POST /api/channels//revoke

Отзыв сессии канала.

**Postman пример:**

```
POST http://localhost:5000/api/channels/2/revoke
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "message": "Сессия успешно отозвана",
    "success": true
}
```

#### POST /api/channels//auth

Авторизация канала. Процесс авторизации происходит в два этапа:

1. При первом запросе будет отправлен код подтверждения в Telegram
2. При втором запросе необходимо отправить полученный код для завершения авторизации

**Postman пример:**

```
POST http://localhost:5000/api/channels/2/auth
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
    "code": "12345"  // Отправляется только на втором этапе
}
```

**Ответ при успешной авторизации:**

```json
{
    "status": "success",
    "message": "Канал успешно авторизован",
    "channel": {
        "apiHash": "********",
        "apiId": "12345678",
        "hasSession": true,
        "id": 14,
        "phoneNumber": "+7**********",
        "status": "active",
        "user_id": 15,
        "username": "test_channel"
    }
}
```

**Ответ при необходимости 2FA:**

```json
{
    "message": "Требуется пароль двухфакторной аутентификации",
    "status": "2fa_required"
}
```

В случае получения статуса `2fa_required`, необходимо отправить запрос на эндпоинт `/api/channels/{channel_id}/submit_2fa` с паролем 2FA:

```
POST http://localhost:5000/api/channels/2/submit_2fa
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
    "password": "1234"
}
```

#### POST /api/channels//submit_2fa

Отправка 2FA пароля для авторизации канала.

**Postman пример:**

```
POST http://localhost:5000/api/channels/2/submit_2fa
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
    "password": "1234"
}
```

**Ответ:**

```json
{
    "channel": {
        "apiHash": "********",
        "apiId": "12345678",
        "hasSession": true,
        "id": 14,
        "phoneNumber": "+7**********",
        "status": "active",
        "user_id": 15,
        "username": "test_channel"
    },
    "message": "Канал успешно авторизован с помощью 2FA",
    "status": "success"
}
```

#### POST /api/channels//verify

Проверка сессии канала.

**Postman пример:**

```
POST http://localhost:5000/api/channels/2/verify
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "channel": {
        "apiHash": "********",
        "apiId": "12345678",
        "hasSession": true,
        "id": 14,
        "phoneNumber": "+7**********",
        "status": "active",
        "user_id": 15,
        "username": "test_channel"
    },
    "message": "Сессия проверена и обновлена",
    "status": "success"
}
```

#### GET /api/user/sessions

Получение списка активных сессий пользователя. Запрос возвращает только активные каналы.

**Postman пример:**

```
GET http://localhost:5000/api/user/sessions
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "active": 1,
    "sessions": [
        {
            "apiHash": "hash123456",
            "apiId": "12345678",
            "createdAt": "2024-03-28 20:40",
            "hasSession": true,
            "id": 2,
            "phoneNumber": "+79001234567",
            "status": "active",
            "username": "mychannel"
        }
    ],
    "total": 3
}
```

### Рассылки

#### GET /api/mailings

Получение списка рассылок.

**Postman пример:**

```
GET http://localhost:5000/api/mailings
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "status": "success",
    "mailings": [
        {
            "aiPrompt": "Сгенерируй дружелюбное сообщение для клиента",
            "channelId": null,
            "channelsIds": [
                1,
                2
            ],
            "createdAt": "2024-03-29 00:08",
            "dailyNewLimit": 5,
            "delayedRecipients": [],
            "delayedRecipientsCount": 0,
            "dialogAiPrompt": "Ты дружелюбный менеджер, который помогает клиентам",
            "dialogMessagesLimit": 500,
            "endTime": null,
            "estimatedDays": 0,
            "id": 1,
            "name": "Тестовая рассылка",
            "nextSendTime": null,
            "recipients": [],
            "recipientsCount": 5,
            "schedule": null,
            "sentCount": 5,
            "startTime": null,
            "status": "in_progress",
            "template": "Здравствуйте, {{имя}}! Это тестовое сообщение для вас.",
            "updatedAt": "2024-03-29 00:44",
            "useAi": true,
            "useDialogAi": true,
            "useTimeWindow": false,
            "userId": 1
        }
    ]
}
```

#### POST /api/mailings

Создание новой рассылки.

**Postman пример:**

```
POST http://localhost:5000/api/mailings
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
    "name": "Рассылка с двумя типами ИИ",
    "channelIds": [16, 18],
    "dailyNewLimit": 5,
    "useTimeWindow": false,
    "useAi": true,
    "aiPrompt": "Ты фитнес консультант",
    "useDialogAi": true,
    "dialogAiPrompt": "Ты фитнес консультант",
    "dialogMessagesLimit": 100
}
```

**Ответ:**

```json
{
    "aiPrompt": "Ты фитнес консультант",
    "channelId": null,
    "channelsIds": [
        16,
        18
    ],
    "createdAt": "2024-03-30 00:12",
    "dailyNewLimit": 5,
    "dialogAiPrompt": "Ты фитнес консультант",
    "dialogMessagesLimit": 100,
    "id": 18,
    "name": "Рассылка с двумя типами ИИ",
    "recipients": [],
    "schedule": null,
    "sentCount": 0,
    "status": "pending",
    "template": "Привет, {{username}}! Этот текст будет использован как основа для приветственного сообщения.",
    "updatedAt": "2024-03-30 00:12",
    "useAi": true,
    "useDialogAi": true,
    "userId": 16
}
```

#### GET /api/mailings/

Получение информации о рассылке.

**Postman пример:**

```
GET http://localhost:5000/api/mailings/17
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "status": "success",
    "mailing": {
        "aiPrompt": "Сгенерируй дружелюбное приветствие для клиента",
        "channelId": null,
        "channelsIds": [
            14,
            16
        ],
        "createdAt": "2024-03-29 00:08",
        "dailyNewLimit": 7,
        "delayedRecipients": [],
        "delayedRecipientsCount": 0,
        "dialogAiPrompt": "Ты дружелюбный ассистент, который помогает клиентам с вопросами",
        "dialogMessagesLimit": 500,
        "endTime": null,
        "estimatedDays": 0,
        "id": 17,
        "name": "Новая рассылка",
        "nextSendTime": null,
        "recipients": [],
        "recipientsCount": 10,
        "schedule": null,
        "sentCount": 10,
        "startTime": null,
        "status": "in_progress",
        "template": "Привет, {{имя}}! Это персонализированное сообщение для вас.",
        "updatedAt": "2024-03-29 00:44",
        "useAi": true,
        "useDialogAi": true,
        "useTimeWindow": false,
        "userId": 16
    }
}
```

#### DELETE /api/mailings/

Удаление рассылки.

**Postman пример:**

```
DELETE http://localhost:5000/api/mailings/2
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "status": "success",
    "message": "Рассылка успешно удалена"
}
```

#### POST /api/mailings//recipients

Загрузка получателей для рассылки.

**Метод:** POST (DELETE - для удаления)
**URL:** `/api/mailings/{mailing_id}/recipients`
**Заголовки:** `Authorization: Bearer {{authToken}}`

**Тип запроса:** `form-data`
**Параметры:**

- `file`: Excel-файл (.xlsx или .xls)
  - Тип параметра должен быть установлен как `File`
  - В Postman: нажмите на кнопку "Select Files" для выбора файла
- `usernameColumn`: название столбца с юзернеймами (по умолчанию "username")
  - Тип параметра должен быть установлен как `Text`
  - Укажите точное название столбца из вашего Excel файла

**Важные замечания:**

1. В Postman убедитесь, что выбран тип Body -> form-data
2. Для параметра `file` обязательно выберите тип File в выпадающем меню справа от ключа
3. Excel файл должен содержать столбец с юзернеймами пользователей
4. Система автоматически добавит символ "@" к юзернеймам, если он отсутствует
5. Пустые строки в файле будут пропущены

**Пример настройки в Postman:**

```
KEY             TYPE    VALUE
file            File    [ваш_файл.xlsx]
usernameColumn  Text    username
```

**Возможные ошибки:**

- `Файл не найден` - параметр `file` отсутствует в запросе
- `Выберите файл` - файл не был выбран
- `Поддерживаются только файлы Excel (.xlsx, .xls)` - неверный формат файла
- `Столбец "username" не найден в файле` - указанное название столбца отсутствует в файле
- `Недостаточно оставшихся получателей по вашему тарифу` - превышен лимит получателей

**Ответ:**

```json
{
    "count": 10,
    "mailing": {
        "aiPrompt": "Ты дружелюбный консультант",
        "channelId": null,
        "channelsIds": [
            14,
            15
        ],
        "createdAt": "2024-03-30 00:12",
        "dailyNewLimit": 5,
        "delayedRecipients": [],
        "delayedRecipientsCount": 0,
        "dialogAiPrompt": "Ты дружелюбный консультант",
        "dialogMessagesLimit": 100,
        "endTime": null,
        "estimatedDays": 0,
        "id": 17,
        "name": "Тестовая рассылка с ИИ",
        "nextSendTime": null,
        "recipients": [
            "@user123",
            "@client456",
            "@customer789",
            "@testuser1",
            "@testuser2",
            "@client111",
            "@user222",
            "@customer333",
            "@test444",
            "@client555"
        ],
        "recipientsCount": 10,
        "schedule": null,
        "sentCount": 0,
        "startTime": null,
        "status": "pending",
        "template": "Привет, {{username}}! Это тестовое сообщение для демонстрации рассылки.",
        "updatedAt": "2024-03-29 21:19",
        "useAi": true,
        "useDialogAi": true,
        "useTimeWindow": false,
        "userId": 15
    },
    "success": true
}
```

#### POST /api/mailings//send

Запуск рассылки.

**Postman пример:**

```
POST http://localhost:5000/api/mailings/2/send
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "message": "Рассылка запущена и будет выполнена в фоновом режиме",
    "recipients_remaining": 980,
    "recipients_used": 10,
    "success": true
}
```

### Чаты

#### GET /api/chats

Получение списка чатов.

**Postman пример:**

```
GET http://localhost:5000/api/chats
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "status": "success",
    "chats": [
        {
            "channelId": 14,
            "createdAt": "2024-03-29 21:45",
            "id": "user123_17",
            "isTyping": false,
            "lastMessage": "Здравствуйте! У меня есть вопрос.",
            "mailingId": 17,
            "mailingName": "Тестовая рассылка с ИИ",
            "userId": 15,
            "username": "user123"
        },
        {
            "channelId": 14,
            "createdAt": "2024-03-29 21:40",
            "id": "client456_17",
            "isTyping": false,
            "lastMessage": "Добрый день! Можете помочь?",
            "mailingId": 17,
            "mailingName": "Тестовая рассылка с ИИ",
            "userId": 15,
            "username": "client456"
        }
    ]
}
```

#### GET /api/chats//messages

Получение сообщений чата.

**Postman пример:**

```
GET http://localhost:5000/api/chats/user123_17/messages
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "messages": [
        {
            "sender": "user",
            "text": "Здравствуйте! Можно задать вопрос?",
            "timestamp": "2024-03-29 21:45"
        },
        {
            "isAi": true,
            "sender": "ai",
            "text": "Конечно! Как я могу помочь вам сегодня?",
            "timestamp": "2024-03-29 21:45"
        }
    ]
}
```

#### DELETE /api/chats/

Удаление чата.

**Postman пример:**

```
DELETE http://localhost:5000/api/chats/user123_17
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "message": "Чат успешно удален",
    "success": true
}
```

### Статистика

#### GET /api/dashboard

Получение данных для дашборда.

**Postman пример:**

```
GET http://localhost:5000/api/dashboard
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Ответ:**

```json
{
    "recent_activity": [
        {
            "action": "Запущена рассылка: Рассылка с двумя типами ИИ",
            "id": 247,
            "status": "Использовано 10 получателей. Осталось 970",
            "status_class": "warning",
            "timestamp": "2025-03-30 00:41",
            "user_id": 16
        },
        {
            "action": "Загружены получатели для рассылки: Рассылка с двумя типами ИИ",
            "id": 246,
            "status": "Добавлено 10 получателей",
            "status_class": "success",
            "timestamp": "2025-03-30 00:41",
            "user_id": 16
        }
    ],
    "stats": {
        "channels": 3,
        "chats": 0,
        "mailings": 3,
        "messages": 4
    },
    "status": "success"
}
```

### Тарифы

#### GET /api/users

Получение списка всех пользователей с информацией о тарифах. Требует ключ администратора.

**Заголовки запроса:**

```
X-Admin-Key: ваш_ключ_администратора
```

**Параметры запроса:**

- `sort`: поле для сортировки (username, email, tariff, used_recipients)
- `order`: направление сортировки (asc или desc)
- `search`: поиск по username или email
- `tariff`: фильтр по названию тарифа

**Ответ:**

```json
{
    "status": "success",
    "users": [
        {
            "id": 1,
            "username": "user123",
            "email": "user@example.com",
            "created_at": "2024-03-29 20:33",
            "tariff": {
                "name": "Лайт",
                "description": "Базовый тариф для небольших рассылок",
                "max_recipients": 1000,
                "used_recipients": 30,
                "remaining_recipients": 970
            },
            "stats": {
                "mailings_count": 3,
                "channels_count": 2,
                "chats_count": 0
            }
        }
    ],
    "stats": {
        "total_users": 10,
        "total_mailings": 25,
        "total_channels": 15,
        "total_chats": 50,
        "total_recipients_used": 5000
    },
    "filters": {
        "sort": "id",
        "order": "asc",
        "search": "",
        "tariff": ""
    }
}
```

#### POST /api/users//recipients

Управление тарифом и лимитами пользователя. Требует ключ администратора.

**Заголовки запроса:**

```
X-Admin-Key: ваш_ключ_администратора
Content-Type: application/json
```

**Тело запроса:**

1. Добавление получателей:

```json
{
    "action": "add",
    "recipients_count": 100,
    "description": "Добавление бонусных получателей"
}
```

2. Установка точного количества получателей:

```json
{
    "action": "set",
    "recipients_count": 500,
    "description": "Установка нового лимита"
}
```

3. Уменьшение количества получателей:

```json
{
    "action": "reduce",
    "recipients_count": 50,
    "description": "Уменьшение лимита"
}
```

4. Сброс счетчика использованных получателей:

```json
{
    "action": "reset",
    "description": "Сброс счетчика"
}
```

5. Назначение тарифа по имени:

```json
{
    "action": "assign_tariff",
    "tariff_name": "Бизнес",
    "description": "Повышение тарифа"
}
```

**Ответ:**

```json
{
    "status": "success",
    "message": "Добавлено 100 получателей (новый лимит: 1100)",
    "user": {
        "id": 1,
        "username": "user123",
        "email": "user@example.com",
        "tariff": {
            "name": "Лайт",
            "max_recipients": 1100,
            "used_recipients": 30,
            "remaining_recipients": 1070
        }
    }
}
```

### Доступные тарифы

1. **Лайт**

   - Базовый тариф для небольших рассылок
   - Лимит получателей: 1000
2. **Стандарт**

   - Тариф для средних рассылок
   - Лимит получателей: 5000
3. **Бизнес**

   - Тариф для крупных рассылок
   - Лимит получателей: 10000
4. **Про**

   - Профессиональный тариф
   - Лимит получателей: 50000
5. **Энтерпрайз**

   - Корпоративный тариф
   - Лимит получателей: 100000

**Примечания:**

- При назначении тарифа по имени поиск осуществляется без учета регистра
- Поддерживается частичное совпадение имени тарифа
- Кастомные тарифы исключаются из поиска по имени
- При превышении лимита получателей операция будет отклонена
- При смене тарифа на меньший лимит, счетчик использованных получателей корректируется автоматически

## Обработка ошибок

API использует следующие HTTP коды состояния:

- 200: Успешный запрос
- 201: Ресурс создан
- 400: Некорректный запрос
- 401: Не авторизован
- 403: Доступ запрещен
- 404: Ресурс не найден
- 500: Внутренняя ошибка сервера

Пример ответа с ошибкой:

```json
{
    "status": "error",
    "message": "Недостаточно прав для выполнения операции",
    "code": "FORBIDDEN"
}
```
