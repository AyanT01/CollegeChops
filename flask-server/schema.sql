DROP TABLE IF EXISTS recipes;

CREATE TABLE recipes (
	recipe_id INT PRIMARY KEY AUTOINCREMENT,
	title VARCHAR(100) NOT NULL,
	description TEXT,
	ingredients TEXT NOT NULL,
	instructions TEXT NOT NULL,
	prep_time INT,
	cook_time INT,
	total_time INT,
	difficulty ENUM('easy', 'medium', 'hard'),
	cost DECIMAL(10,2)
);
