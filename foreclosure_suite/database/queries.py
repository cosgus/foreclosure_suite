
create_auction_table = """
CREATE TABLE auctions(
    id PRIMARY KEY NOT NULL,
    auction_id INT NOTNULL,
    date DATE,
    time TIME,
    status VARCHAR(255),
    sold_to VARCHAR(255),
    auction_sale_amount DECIMAL(15,2),
    final_judgement DECIMAL(15,2),
    plaintiff_max_bid DECIMAL(15,2),
    defendant JSON,
    plaintiff JSON,
    association BOOL,
    case_number VARCHAR(255),
    docket_count INT,
    auction_count_on_day INT,
    place_in_line INT,
    UNIQUE(auction_id),
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);"""


create_property_table = """
CREATE TABLE properties (
    id int NOT NULL,
    street_address varchar(255),
    city VARCHAR(255),
    zip INT,
    assessed_value DECIMAL(15,2),
    bedroom_count INT,
    bathroom_count INT,
    half_bathroom_count INT,
    building_actual_area INT,
    building_heated_area INT,
    floor_count INT,
    lot_size INT,
    zone_description VARCHAR(255),
    PRIMARY KEY (id)
);
"""

test = """CREATE TABLE Persons (
    ID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255),
    Age int,
    PRIMARY KEY (ID)
); """