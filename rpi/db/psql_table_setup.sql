CREATE TABLE activities 
(
	id				SERIAL PRIMARY KEY, 
	activity_type	text, 
	body			text, 
	target_name		text, 
	target_url		text, 
	created_at		timestamp
);

CREATE TABLE nodes
(
	id				SERIAL PRIMARY KEY, 
	identifier		text,
	name            text,
	created_at		timestamp
);

CREATE TABLE configurations
(
	id				SERIAL PRIMARY KEY,
	node_id			integer REFERENCES nodes (id),
	sensor_id		integer REFERENCES sensors (id),
	formula			text,
	created_at		timestamp
);

CREATE TYPE sensor_type AS ENUM ('default', 'counter', 'temp', 'hum');
CREATE TABLE sensors
(
	id				SERIAL PRIMARY KEY,
	type			sensor_type, 
	name            text,
	created_at		timestamp,
	updated_at		timestamp
);

CREATE TABLE measurements
(
	id				SERIAL PRIMARY KEY, 
	sensor_id		integer REFERENCES sensors (id),
	value			real, 
	created_at		timestamp
);
