from dataclasses import dataclass

@dataclass
class MySQL:
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
        FOREIGN KEY (id) REFERENCES property(id)
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

@dataclass
class Postgres:
    auction_table = """
        id SERIAL PRIMARY KEY,
        aid INT NOT NULL UNIQUE,
        case_type VARCHAR(255),
        certificate_number VARCHAR(255),
        date DATE,
        time TIME,
        status VARCHAR(255),
        opening_bid DECIMAL(15,2),
        sale_amount DECIMAL(15,2),
        final_judgment_amount DECIMAL(15,2),
        plaintiff_max_bid DECIMAL(15,2),
        auction_count_on_day INT,
        place_in_line INT,
        property_id INTEGER REFERENCES property(id),
        case_id INTEGER REFERENCES court_case(id)
    """

    court_case ="""
        id SERIAL,
        case_number VARCHAR(255),
        docket_count INT,
        PRIMARY KEY (id)
    """

    party = """
        id SERIAL PRIMARY KEY,
        party_name VARCHAR(255),
        side VARCHAR(255)
    """

    court_case_party = """
        party_id INT REFERENCES party(id),
        case_id INT REFERENCES court_case(id),
        CONSTRAINT court_case_party_pkey PRIMARY KEY (party_id, case_id)
    """

    auction_party = """
        party_id INT REFERENCES party(id),
        auction_id INT REFERENCES auction(id),
        CONSTRAINT auction_party_pkey PRIMARY KEY (party_id, auction_id)
    """

    property_table = """
        id SERIAL PRIMARY KEY,
        BathroomCount INT,
        BedroomCount INT,
        BuildingActualArea INT,
        BuildingBaseArea INT,
        BuildingEffectiveArea INT,
        BuildingGrossArea INT,
        BuildingHeatedArea INT,
        DORCode VARCHAR(255),
        DORDescription VARCHAR(255),
        DORDescriptionCurrent VARCHAR(255),
        EncodedFolioAndTaxYear VARCHAR(255),
        FloorCount INT,
        FolioNumber VARCHAR(255) UNIQUE,
        HalfBathroomCount INT,
        HxBaseYear INT,
        LotSize INT,
        Message VARCHAR(255),
        Municipality VARCHAR(255),
        Neighborhood VARCHAR(255),
        NeighborhoodDescription VARCHAR(255),
        ParentFolio VARCHAR(255),
        PercentHomesteadCapped VARCHAR(255),
        PlatBook VARCHAR(255),
        PlatPage VARCHAR(255),
        PrimaryZone VARCHAR(255),
        PrimaryZoneDescription VARCHAR(255),
        ShowCurrentValuesFlag VARCHAR(255),
        Status VARCHAR(255),
        Subdivision VARCHAR(255),
        SubdivisionDescription VARCHAR(255),
        UnitCount INT,
        YearAnnexed INT,
        YearBuilt VARCHAR(255)
    """

    no_folio = """
        id SERIAL,
        auction_id INT UNIQUE
    """

    multiple_parcel = """
        id SERIAL,
        auction_id INT UNIQUE
    """
