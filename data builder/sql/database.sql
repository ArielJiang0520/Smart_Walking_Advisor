USE `cs125`;

Create TABLE IF NOT EXISTS `User`(
	`uid` VARCHAR(2),
	PRIMARY KEY (`uid`)
);

Create TABLE IF NOT exists `Location History`(
	`uid` VARCHAR(2),
    `start_time` DATETIME,
    `end_time` DATETIME NOT NULL,
    `location` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`uid`,`start_time`),
    FOREIGN KEY(`uid`) REFERENCES User(`uid`) ON DELETE CASCADE
);

Create TABLE IF NOT exists `Calendar`(
	`uid` VARCHAR(2),
    `start_time` DATETIME,
    `end_time` DATETIME NOT NULL,
    `location` VARCHAR(100),
    PRIMARY KEY (`uid`,`start_time`),
    FOREIGN KEY(`uid`) REFERENCES User(`uid`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `Location Index`(
	`location_name` VARCHAR(100),
    `lat` INT NOT NULL,
    `long` INT NOT NULL,
    PRIMARY KEY (`location_name`)
);
