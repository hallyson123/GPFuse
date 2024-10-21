CREATE TABLE host (
  id INT PRIMARY KEY,
  host_id STR,
  OPTIONAL host_name STR
);

CREATE TABLE review (
  id INT PRIMARY KEY,
  date STR
);

CREATE TABLE listing (
  id INT PRIMARY KEY,
  minimum_nights INT,
  OPTIONAL neighbourhood_group STR,
  availability_365 INT,
  availability_365 INT,
  room_type STR,
  number_of_reviews_ltm INT,
  id STR,
  number_of_reviews INT,
  OPTIONAL price INT,
  OPTIONAL last_review STR,
  OPTIONAL reviews_per_month FLOAT,
  name STR,
  longitude FLOAT,
  latitude FLOAT,
  calculated_host_listings_count INT,
  neighbourhood STR,
  OPTIONAL license STR
);

CREATE TABLE neighbourhood (
  id INT PRIMARY KEY,
  OPTIONAL neighbourhood_group STR,
  neighbourhood STR
);

ALTER TABLE host ADD FOREIGN KEY (listingtype_id) REFERENCES listingtype(id);
ALTER TABLE review ADD FOREIGN KEY (listingtype_id) REFERENCES listingtype(id);
ALTER TABLE listing ADD FOREIGN KEY (neighbourhoodtype_id) REFERENCES neighbourhoodtype(id);
