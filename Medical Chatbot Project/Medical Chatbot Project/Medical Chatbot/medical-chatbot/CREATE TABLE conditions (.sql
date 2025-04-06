    CREATE TABLE conditions (
    id SERIAL PRIMARY KEY,             -- Unique identifier for each condition
    name VARCHAR(255) NOT NULL,        -- Name of the condition (e.g., fever)
    precautions TEXT,                  -- Precautions for the condition  
    diet TEXT,                         -- Recommended diet
    if_not_working TEXT,               -- Instructions if condition worsens
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- Timestamp for last update
);

CREATE TABLE medications (
    id SERIAL PRIMARY KEY,              -- Unique identifier for each medication
    condition_id INT NOT NULL,          -- Foreign key to conditions table
    name VARCHAR(255) NOT NULL,         -- Medication name (e.g., paracetamol)
    dosage VARCHAR(255),                -- Dosage for the medication
    link TEXT,                          -- URL link for purchasing medication
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Timestamp for last update
    FOREIGN KEY (condition_id) REFERENCES conditions(id) -- Foreign key constraint
);
