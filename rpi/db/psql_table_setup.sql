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
	created_at		timestamp,
	updated_at		timestamp
);

CREATE TYPE sensor_type AS ENUM ('default', 'counter', 'temperature', 'humidity');
CREATE TABLE sensors
(
	id				SERIAL PRIMARY KEY,
	stype			sensor_type, 
	name            text,
	created_at		timestamp,
	updated_at		timestamp
);

CREATE TABLE configurations
(
	id				SERIAL PRIMARY KEY,
	name			text,
	node_id			integer REFERENCES nodes (id),
	sensor_id		integer REFERENCES sensors (id),
	formula			text,
	created_at		timestamp
);

CREATE TABLE measurements
(
	id				SERIAL PRIMARY KEY, 
	sensor_id		integer REFERENCES sensors (id),
	value			real, 
	created_at		timestamp
);
CREATE INDEX index_sensor_id_on_measurements ON measurements (sensor_id);
CREATE INDEX index_sensor_id_c_at_on_measurements ON measurements (sensor_id, created_at);

CREATE TABLE users
(
	id				SERIAL PRIMARY KEY,
	name			text,
	key				text,
	permissions		integer,
	created_at		timestamp
);

CREATE TYPE kpi_type AS ENUM ('minute', 'hour', 'day', 'month');
CREATE TABLE kpis
(
	id				SERIAL PRIMARY KEY,
	type			kpi_type,
	sensor_id		integer REFERENCES sensors (id),
	value			real,
	created_at		timestamp
);
CREATE INDEX index_sensor_id_on_kpis ON kpis (sensor_id);
