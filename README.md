## Работа с проектом:
### 1. Создать в корневой папке .env файл и записать значения переменных: VK_TOKEN, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
### 2. Установить библиотеки командами:
<pre class="language-bash"><code>pip install secure-smtplib
</code></pre>
<pre class="language-bash"><code>pip install psycopg2
</code></pre>
### 3. Создать базу данных:
<pre class="sql"><code>CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    vk_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);</code></pre>
### 4. Перейти в папку src и Запустить проект:
<pre class="language-bash"><code>cd src</code></pre>
<pre class="language-bash"><code>pythhon main.py</code></pre>
