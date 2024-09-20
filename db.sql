-- MySQL Structure

-- Create `users` table
CREATE TABLE `users` (
    `userID` VARCHAR(256) PRIMARY KEY,
    `username` VARCHAR(80) NOT NULL,
    `password` VARCHAR(120) NOT NULL
);

-- Add a test admin user with password admin
INSERT INTO `users` VALUES ("0", "admin", MD5("admin"));

-- Create `pets` table
CREATE TABLE `pets` (
    `petID` VARCHAR(256) PRIMARY KEY,
    `petName` VARCHAR(80) NOT NULL,
    `weight` FLOAT NOT NULL DEFAULT 0.00,
    `normalDrinkValue` FLOAT NOT NULL DEFAULT 0.00,
    `lastTagDate` VARCHAR(100) NOT NULL
);

-- Create the `turbidity` table
CREATE TABLE `turbidity` (
    `eventID` VARCHAR(256) PRIMARY KEY,
    `create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `turbidityValue` FLOAT NOT NULL DEFAULT 0.00
);

-- Create the `valve` table
CREATE TABLE `valve` (
    `eventID` VARCHAR(256) PRIMARY KEY,
    `create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `valve_status` INT NOT NULL DEFAULT 0
);

-- Create the `wasteTank` table
CREATE TABLE `wasteTank` (
    `eventID` VARCHAR(256) PRIMARY KEY,
    `create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `is_full` INT NOT NULL DEFAULT 0
);

-- Create the `petdrink` table
CREATE TABLE `petdrink` (
    `eventID` VARCHAR(256) PRIMARY KEY,
    `petID` VARCHAR(256) NOT NULL,
    `create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `drinkAmount` FLOAT NOT NULL DEFAULT 0.00,
    CONSTRAINT petdrinkFK1 FOREIGN KEY (`petID`) REFERENCES `pets`(`petID`)
);

CREATE TABLE noticeEvent (
    eventID VARCHAR(256) PRIMARY KEY,
    petID VARCHAR(256) NOT NULL,
    eventType VARCHAR(20) NOT NULL DEFAULT 'None',
    create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    eventCritical VARCHAR(80) NOT NULL DEFAULT 'Notice',
    eventDetail VARCHAR(120) NOT NULL DEFAULT 'None',
    CONSTRAINT neFK1 FOREIGN KEY (petID) REFERENCES pets(petID)
);
