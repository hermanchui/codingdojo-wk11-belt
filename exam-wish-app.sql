-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema exam-wish-app
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `exam-wish-app` ;

-- -----------------------------------------------------
-- Schema exam-wish-app
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `exam-wish-app` DEFAULT CHARACTER SET utf8 ;
USE `exam-wish-app` ;

-- -----------------------------------------------------
-- Table `exam-wish-app`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `exam-wish-app`.`users` ;

CREATE TABLE IF NOT EXISTS `exam-wish-app`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `pwd_hash` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `exam-wish-app`.`wishes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `exam-wish-app`.`wishes` ;

CREATE TABLE IF NOT EXISTS `exam-wish-app`.`wishes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `item` VARCHAR(255) NULL,
  `description` TEXT NULL,
  `is_granted` TINYINT NULL,
  `granted_at` DATETIME NULL,
  `user_id` INT NOT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_wishes_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_wishes_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `exam-wish-app`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `exam-wish-app`.`likes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `exam-wish-app`.`likes` ;

CREATE TABLE IF NOT EXISTS `exam-wish-app`.`likes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `wish_id` INT NOT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_likes_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_likes_wishes1_idx` (`wish_id` ASC) VISIBLE,
  CONSTRAINT `fk_likes_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `exam-wish-app`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_likes_wishes1`
    FOREIGN KEY (`wish_id`)
    REFERENCES `exam-wish-app`.`wishes` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
