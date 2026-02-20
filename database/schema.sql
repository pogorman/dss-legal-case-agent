-- =============================================================
-- DSS Legal Case Agent — Database Schema
-- Database: dss-demo (Azure SQL)
-- =============================================================

-- Cases table: core case records
CREATE TABLE cases (
    case_id         VARCHAR(20) PRIMARY KEY,
    case_title      VARCHAR(200) NOT NULL,
    case_type       VARCHAR(100) NOT NULL,
    circuit         VARCHAR(50)  NOT NULL,
    county          VARCHAR(50)  NOT NULL,
    filed_date      DATE         NOT NULL,
    status          VARCHAR(50)  NOT NULL,
    plaintiff       VARCHAR(100) NOT NULL,
    summary         VARCHAR(2000),
    created_at      DATETIME2 DEFAULT GETDATE()
);

-- People table: parties, workers, and witnesses associated with cases
CREATE TABLE people (
    person_id       INT IDENTITY(1,1) PRIMARY KEY,
    case_id         VARCHAR(20) NOT NULL REFERENCES cases(case_id),
    full_name       VARCHAR(100) NOT NULL,
    role            VARCHAR(100) NOT NULL,
    relationship    VARCHAR(200),
    dob             DATE,
    notes           VARCHAR(500)
);

-- Timeline events: chronological record of case events
CREATE TABLE timeline_events (
    event_id        INT IDENTITY(1,1) PRIMARY KEY,
    case_id         VARCHAR(20) NOT NULL REFERENCES cases(case_id),
    event_date      DATE        NOT NULL,
    event_time      VARCHAR(20),
    event_type      VARCHAR(100) NOT NULL,
    description     VARCHAR(2000) NOT NULL,
    source_document VARCHAR(200),
    parties_involved VARCHAR(500)
);

-- Statements: recorded statements by case participants
CREATE TABLE statements (
    statement_id    INT IDENTITY(1,1) PRIMARY KEY,
    case_id         VARCHAR(20) NOT NULL REFERENCES cases(case_id),
    person_id       INT NOT NULL REFERENCES people(person_id),
    statement_date  DATE,
    made_to         VARCHAR(100) NOT NULL,
    statement_text  VARCHAR(2000) NOT NULL,
    source_document VARCHAR(200),
    page_reference  VARCHAR(50)
);

-- Discrepancies: conflicting accounts between parties
CREATE TABLE discrepancies (
    discrepancy_id      INT IDENTITY(1,1) PRIMARY KEY,
    case_id             VARCHAR(20) NOT NULL REFERENCES cases(case_id),
    topic               VARCHAR(200) NOT NULL,
    person_a_id         INT REFERENCES people(person_id),
    person_a_account    VARCHAR(1000),
    person_b_id         INT REFERENCES people(person_id),
    person_b_account    VARCHAR(1000),
    contradicted_by     VARCHAR(500),
    source_document     VARCHAR(200)
);

-- Indexes for common query patterns
CREATE INDEX IX_people_case_id ON people(case_id);
CREATE INDEX IX_timeline_events_case_id ON timeline_events(case_id);
CREATE INDEX IX_timeline_events_type ON timeline_events(case_id, event_type);
CREATE INDEX IX_statements_case_id ON statements(case_id);
CREATE INDEX IX_statements_person_id ON statements(person_id);
CREATE INDEX IX_discrepancies_case_id ON discrepancies(case_id);
