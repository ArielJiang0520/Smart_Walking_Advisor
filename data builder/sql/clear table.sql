USE `cs125`;

SET SQL_SAFE_UPDATES = 0;

DELETE FROM `location history`;
DELETE FROM `location frequency`;
DELETE FROM `user`;

INSERT INTO `user`(uid)
VALUES("1");

DELETE FROM `location index`;