CREATE TYPE hazard_type AS ENUM ('Water', 'Ice', 'Potholes', 'Bad Road Conditions', 'Tight Turn', 'Debris', 'Other');

DROP TABLE IF EXISTS hazard;

CREATE TABLE hazard (
        ID UUID DEFAULT uuid_generate_v4(),
        username VARCHAR,
        firstname VARCHAR(100) NOT NULL,
        lastname VARCHAR(100) NOT NULL,
        PRIMARY KEY (ID, username)
);

CREATE TABLE hazard_area (
        ID UUID DEFAULT uuid_generate_v4(),
        hazard_id UUID NOT NULL,
        PRIMARY KEY (ID),
        FOREIGN KEY (hazard_id) REFERENCES hazard(id)
);