CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


DROP TYPE IF EXISTS YOUR_TYPE;
CREATE TYPE hazard_type AS ENUM ('Water', 'Ice', 'Potholes', 'Bad Road Conditions', 'Tight Turn', 'Debris', 'Other');

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
        id UUID default uuid_generate_v4() PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        firstname VARCHAR(100) NOT NULL,
        lastname VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS hazard CASCADE;
CREATE TABLE hazard (
        id UUID default uuid_generate_v4(),
        user_id UUID,
        risk_level integer,
        frequency integer NOT NULL,
        type hazard_type,
        description TEXT,
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS hazard_area CASCADE;
CREATE TABLE hazard_area (
        id UUID,
        hazard_id UUID NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (hazard_id) REFERENCES hazard(id)
);