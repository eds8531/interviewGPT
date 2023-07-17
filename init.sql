
CREATE TABLE jobs (
    id                  SERIAL PRIMARY KEY,
    title               VARCHAR,
    requirements        VARCHAR,
    company             VARCHAR

);

-- Insert initial rows into the "jobs" table
INSERT INTO jobs (title, requirements, company)
VALUES
    ('Developer', 'flask,git,html,css', 'yahoo'),
    ('Project Manager', 'jira,quality assurance,conflict/resolution', 'google'),
    ('DevOps Engineer', 'kubernetes,docker,ansible', 'facebook');

CREATE TABLE interviews (
    id                  SERIAL PRIMARY KEY,
    job_id              INTEGER REFERENCES jobs(id),
    base_prompt         VARCHAR,
    messages            VARCHAR,
    completed           BOOLEAN,
    prompt_tokens       INTEGER,
    completion_tokens   INTEGER
);
