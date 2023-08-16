auction_table = """
    id int NOT NULL,
    auction_id INT NOT NULL,
    property_id VARCHAR(30),
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
    PRIMARY KEY (id),
    UNIQUE (auction_id),
    FOREIGN KEY (id) REFERENCES properties(id)
"""

property_table = """
    id int NOT NULL,
    street_address varchar(255),
    city VARCHAR(255),
    zip INT,
    folio VARCHAR(255),
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
"""