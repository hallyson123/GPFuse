CREATE DATABASE TesteRel; 
\c TesteRel

CREATE TYPE NEIGHBOURHOOD_NEIGHBOURHOOD_GROUP_ENUM AS ENUM("Staten Island", "Manhattan", "Queens", "Brooklyn", "Bronx")

CREATE TABLE host (
  host_id VARCHAR(100) UNIQUE NOT NULL,
  host_name VARCHAR(100) NOT NULL,
  CONSTRAINT pk_Host PRIMARY KEY (host_id) 
);

CREATE TABLE review (
  date VARCHAR(100) UNIQUE NOT NULL,
  CONSTRAINT pk_Review PRIMARY KEY (date) 
);

CREATE TABLE listing (
  minimum_nights INTEGER NOT NULL,
  neighbourhood_group VARCHAR(100),
  availability_365 INTEGER NOT NULL,
  room_type VARCHAR(100) NOT NULL,
  number_of_reviews_ltm INTEGER NOT NULL,
  id VARCHAR(100) UNIQUE NOT NULL,
  number_of_reviews INTEGER NOT NULL,
  price INTEGER,
  last_review VARCHAR(100),
  reviews_per_month REAL,
  name VARCHAR(100) NOT NULL,
  longitude REAL NOT NULL,
  latitude REAL NOT NULL,
  calculated_host_listings_count INTEGER NOT NULL,
  neighbourhood VARCHAR(100) NOT NULL,
  license VARCHAR(100),
  CONSTRAINT pk_Listing PRIMARY KEY (id) 
);

CREATE TABLE neighbourhood (
  neighbourhood_group NEIGHBOURHOOD_NEIGHBOURHOOD_GROUP_ENUM,
  neighbourhood VARCHAR(100) UNIQUE NOT NULL,
  CONSTRAINT pk_Neighbourhood PRIMARY KEY (neighbourhood) 
);

