-- MySQL Structure

-- Create `users` table
CREATE TABLE `users` (
    `userID` VARCHAR(256) PRIMARY KEY,
    `username` VARCHAR(80) NOT NULL UNIQUE,
    `password` VARCHAR(120) NOT NULL,
);

-- Add a test admin user with password admin
INSERT INTO `users` VALUES ("0","admin",MD5("admin"),"admin");