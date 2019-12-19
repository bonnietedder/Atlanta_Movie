SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

DROP SCHEMA IF EXISTS `Team8` ;

CREATE SCHEMA IF NOT EXISTS `Team8` ;
USE `Team8` ;

DROP TABLE IF EXISTS `Team8`.`user` ;

CREATE TABLE IF NOT EXISTS `Team8`.`user` (
  `username` VARCHAR(50) NOT NULL, 
  `status` ENUM("Pending", "Declined", "Approved") NOT NULL DEFAULT 'Pending',
  `password` VARCHAR(50) NOT NULL,
  `firstname` VARCHAR(50) NOT NULL,
  `lastname` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`username`))
ENGINE = InnoDB;


DROP TABLE IF EXISTS `Team8`.`customer` ;

CREATE TABLE IF NOT EXISTS `Team8`.`customer` (
  `username` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `fk1`
    FOREIGN KEY (`username`)
    REFERENCES `Team8`.`user` (`username`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


DROP TABLE IF EXISTS `Team8`.`employee` ;

CREATE TABLE IF NOT EXISTS `Team8`.`employee` (
  `username` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `fk2`
    FOREIGN KEY (`username`)
    REFERENCES `Team8`.`user` (`username`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


DROP TABLE IF EXISTS `Team8`.`admin` ;

CREATE TABLE IF NOT EXISTS `Team8`.`admin` (
  `username` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `fk5`
    FOREIGN KEY (`username`)
    REFERENCES `Team8`.`employee` (`username`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


DROP TABLE IF EXISTS `Team8`.`company` ;

CREATE TABLE IF NOT EXISTS `Team8`.`company` (
  `comName` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`comName`))
ENGINE = InnoDB;


DROP TABLE IF EXISTS `Team8`.`manager` ;

CREATE TABLE IF NOT EXISTS `Team8`.`manager` (
  `username` VARCHAR(50) NOT NULL,
  `comName` VARCHAR(50) NOT NULL,
  `manStreet` VARCHAR(50) NOT NULL,
  `manCity` VARCHAR(50) NOT NULL,
  `manState` CHAR(3) NOT NULL,
  `manZipcode` CHAR(5) NOT NULL,
PRIMARY KEY (`username`),
  CONSTRAINT `fk3`
    FOREIGN KEY (`username`)
    REFERENCES `Team8`.`employee` (`username`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk4`
    FOREIGN KEY (`comName`)
    REFERENCES `Team8`.`company` (`comName`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk4_idx` ON `Team8`.`manager` (`comName` ASC);

CREATE UNIQUE INDEX `address_UNIQUE` ON `Team8`.`manager` (`manStreet` ASC, `manCity` ASC, `manState` ASC, `manZipcode` ASC);


DROP TABLE IF EXISTS `Team8`.`theater` ;

CREATE TABLE IF NOT EXISTS `Team8`.`theater` (
  `thName` VARCHAR(50) NOT NULL,
  `comName` VARCHAR(50) NOT NULL,
  `capacity` INT NOT NULL,
  `thStreet` VARCHAR(50) NOT NULL,
  `thCity` VARCHAR(50) NOT NULL,
  `thState` CHAR(3) NOT NULL,
  `thZipcode` CHAR(5) NOT NULL,
  `manUsername` VARCHAR(50) NOT NULL,
PRIMARY KEY (`thName`, `comName`),
  CONSTRAINT `fk13`
    FOREIGN KEY (`manUsername`)
    REFERENCES `Team8`.`manager` (`username`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk9`
    FOREIGN KEY (`comName`)
    REFERENCES `Team8`.`company` (`comName`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk13_idx` ON `Team8`.`theater` (`manUsername` ASC);

CREATE INDEX `fk9_idx` ON `Team8`.`theater` (`comName` ASC);

CREATE UNIQUE INDEX `manUsername_UNIQUE` ON `Team8`.`theater` (`manUsername` ASC);


DROP TABLE IF EXISTS `Team8`.`customerCreditCard` ;

CREATE TABLE IF NOT EXISTS `Team8`.`customerCreditCard` (
  `creditCardNum` CHAR(16) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`creditCardNum`),
  CONSTRAINT `fk6`
    FOREIGN KEY (`username`)
    REFERENCES `Team8`.`customer` (`username`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk6_idx` ON `Team8`.`customerCreditCard` (`username` ASC);


DROP TABLE IF EXISTS `Team8`.`movie` ;

CREATE TABLE IF NOT EXISTS `Team8`.`movie` (
  `movName` VARCHAR(50) NOT NULL,
  `movReleaseDate` DATE NOT NULL,
  `duration` INT NOT NULL,
  PRIMARY KEY (`movName`, `movReleaseDate`))
ENGINE = InnoDB;


DROP TABLE IF EXISTS `Team8`.`moviePlay` ;

CREATE TABLE IF NOT EXISTS `Team8`.`moviePlay` (
  `thName` VARCHAR(50) NOT NULL,
  `comName` VARCHAR(50) NOT NULL,
  `movName` VARCHAR(50) NOT NULL,
  `movReleaseDate` DATE NOT NULL,
  `movPlayDate` DATE,
PRIMARY KEY (`thName`, `comName`, `movName`, `movReleaseDate`, `movPlayDate`),
  CONSTRAINT `fk7`
    FOREIGN KEY (`movName` , `movReleaseDate`)
    REFERENCES `Team8`.`movie` (`movName` , `movReleaseDate`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk8`
    FOREIGN KEY (`thName` , `comName`)
    REFERENCES `Team8`.`theater` (`thName` , `comName`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk7_idx` ON `Team8`.`moviePlay` (`movName` ASC, `movReleaseDate` ASC);

CREATE INDEX `fk8_idx` ON `Team8`.`moviePlay` (`thName` ASC, `comName` ASC);


DROP TABLE IF EXISTS `Team8`.`userVisitTheater` ;

CREATE TABLE IF NOT EXISTS `Team8`.`userVisitTheater` (
  `visitID` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `thName` VARCHAR(50) NOT NULL,
  `comName` VARCHAR(50) NOT NULL,
  `visitDate` DATE NOT NULL,
PRIMARY KEY (`visitID`),
  CONSTRAINT `fk11`
    FOREIGN KEY (`thName` , `comName`)
    REFERENCES `Team8`.`theater` (`thName` , `comName`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk12`
    FOREIGN KEY (`username`)
    REFERENCES `Team8`.`user` (`username`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk11_idx` ON `Team8`.`userVisitTheater` (`thName` ASC, `comName` ASC);

CREATE INDEX `fk12_idx` ON `Team8`.`userVisitTheater` (`username` ASC);


DROP TABLE IF EXISTS `Team8`.`customerViewMovie` ;

CREATE TABLE IF NOT EXISTS `Team8`.`customerViewMovie` (
  `creditCardNum` CHAR(16) NOT NULL,
  `thName` VARCHAR(50) NOT NULL,
  `comName` VARCHAR(50) NOT NULL,
  `movName` VARCHAR(50) NOT NULL,
  `movReleaseDate` DATE NOT NULL,
  `movPlayDate` DATE NOT NULL,
PRIMARY KEY (`creditCardNum`, `thName`, `comName`, `movName`, `movReleaseDate`, `movPlayDate`),
  CONSTRAINT `fk10`
    FOREIGN KEY (`thName` , `comName` , `movName` , `movReleaseDate` , `movPlayDate`)
    REFERENCES `Team8`.`moviePlay` (`thName` , `comName` , `movName` , `movReleaseDate` , `movPlayDate`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk14`
    FOREIGN KEY (`creditCardNum`)
    REFERENCES `Team8`.`customerCreditCard` (`creditCardNum`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `fk10_idx` ON `Team8`.`customerViewMovie` (`movReleaseDate` ASC, `movName` ASC, `movPlayDate` ASC, `thName` ASC, `comName` ASC);


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
