CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


DROP TYPE IF EXISTS YOUR_TYPE;
CREATE TYPE hazard_type AS ENUM ('Water', 'Ice', 'Potholes', 'Bad Road Conditions', 'Tight Turn', 'Debris', 'Other');

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
        id UUID default uuid_generate_v4() PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        firstname VARCHAR(100) NOT NULL,
        lastname VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS report CASCADE;
CREATE TABLE report (
        id UUID default uuid_generate_v4(),
        user_id UUID,
        risk_level integer,
        frequency integer NOT NULL,
        type hazard_type,
        description TEXT,
        title TEXT,
        latitude Decimal(8,6) NOT NULL,
        longitude Decimal(9,6) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES users(id),
        timestamp timestamp default current_timestamp
);

DROP TABLE IF EXISTS analysis CASCADE;
CREATE TABLE analysis (
        id UUID default uuid_generate_v4(),
        user_id UUID,
        analysis TEXT,
        public boolean,
        timestamp timestamp default current_timestamp,
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Indexes for query optimization on searches.
DROP INDEX IF EXISTS report_latitude;
CREATE INDEX report_latitude ON report (latitude);
DROP INDEX IF EXISTS report_longitude;
CREATE INDEX report_longitude ON report (longitude);
DROP INDEX IF EXISTS users_name;
CREATE INDEX users_name
ON users (id);

