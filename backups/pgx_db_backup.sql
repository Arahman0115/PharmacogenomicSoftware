-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: pgx_db
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ActivatedPrescriptions`
--

DROP TABLE IF EXISTS `ActivatedPrescriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ActivatedPrescriptions` (
  `prescription_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `medication_id` int DEFAULT NULL,
  `prescriber_id` int DEFAULT NULL,
  `quantity_dispensed` int DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `rx_store_num` varchar(50) DEFAULT NULL,
  `store_number` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'active',
  `fill_date` date DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`prescription_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `ActivatedPrescriptions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patientsinfo` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ActivatedPrescriptions`
--

LOCK TABLES `ActivatedPrescriptions` WRITE;
/*!40000 ALTER TABLE `ActivatedPrescriptions` DISABLE KEYS */;
INSERT INTO `ActivatedPrescriptions` VALUES (1,4,4,1,30,'Jennifer','Davis','03102-004','1618','active','2024-03-01','2026-02-01 04:24:36'),(2,5,5,4,30,'Michael','Wilson','03102-005','1618','active','2024-01-25','2026-02-01 04:24:36'),(3,6,6,2,30,'Lisa','Anderson','03102-006','1618','bottle_selected','2024-02-10','2026-02-01 04:24:36'),(4,1,1,NULL,30,NULL,NULL,'03102-001','1618','rejected','2026-02-01','2026-02-06 05:58:13'),(5,1,8,NULL,20,NULL,NULL,'03102-007','1618','product_dispensing_pending','2026-02-06','2026-02-06 06:10:16');
/*!40000 ALTER TABLE `ActivatedPrescriptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FinishedTransactions`
--

DROP TABLE IF EXISTS `FinishedTransactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FinishedTransactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `rx_store_num` varchar(50) DEFAULT NULL,
  `medication_id` int DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `release_time` datetime DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FinishedTransactions`
--

LOCK TABLES `FinishedTransactions` WRITE;
/*!40000 ALTER TABLE `FinishedTransactions` DISABLE KEYS */;
INSERT INTO `FinishedTransactions` VALUES (1,1,'03102-001',1,30,'2024-11-15 10:30:00','Insurance',5.50,'completed','2026-02-01 04:24:37'),(2,2,'03102-002',2,90,'2024-11-01 14:15:00','Cash',15.00,'completed','2026-02-01 04:24:37'),(3,3,'03102-003',3,30,'2024-12-20 09:45:00','Card',8.75,'completed','2026-02-01 04:24:37'),(4,4,'03102-004',4,30,'2024-10-01 11:20:00','Insurance',6.25,'completed','2026-02-01 04:24:37'),(5,5,'03102-005',5,30,'2024-12-25 16:00:00','Card',12.00,'completed','2026-02-01 04:24:37'),(6,6,'03102-006',6,30,'2024-11-10 13:45:00','Insurance',7.50,'completed','2026-02-01 04:24:37'),(7,7,'03102-008',1,30,'2026-02-01 00:27:23',NULL,NULL,'released','2026-02-01 05:27:23'),(8,8,'03102-009',2,90,'2026-02-01 00:27:26',NULL,NULL,'released','2026-02-01 05:27:26');
/*!40000 ALTER TABLE `FinishedTransactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Prescribers`
--

DROP TABLE IF EXISTS `Prescribers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Prescribers` (
  `prescriber_id` int NOT NULL AUTO_INCREMENT,
  `prescriber_name` varchar(255) NOT NULL,
  `npi` varchar(20) DEFAULT NULL,
  `license_number` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`prescriber_id`),
  KEY `idx_name` (`prescriber_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Prescribers`
--

LOCK TABLES `Prescribers` WRITE;
/*!40000 ALTER TABLE `Prescribers` DISABLE KEYS */;
INSERT INTO `Prescribers` VALUES (1,'Dr. James Wilson','1234567890','MD12345','555-0101','james.wilson@clinic.com','123 Medical Dr','Springfield','IL','62701','2026-02-01 04:24:36'),(2,'Dr. Sarah Mitchell','0987654321','MD67890','555-0102','sarah.mitchell@clinic.com','456 Health Ave','Springfield','IL','62701','2026-02-01 04:24:36'),(3,'Dr. Robert Chen','1122334455','MD11111','555-0103','robert.chen@clinic.com','789 Wellness Blvd','Springfield','IL','62701','2026-02-01 04:24:36'),(4,'Dr. Patricia Johnson','5544332211','MD22222','555-0104','patricia.johnson@clinic.com','321 Cure Lane','Springfield','IL','62701','2026-02-01 04:24:36');
/*!40000 ALTER TABLE `Prescribers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Prescriptions`
--

DROP TABLE IF EXISTS `Prescriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Prescriptions` (
  `prescription_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `medication_id` int DEFAULT NULL,
  `prescriber_id` int DEFAULT NULL,
  `quantity_dispensed` int DEFAULT NULL,
  `refills_remaining` int DEFAULT '0',
  `instructions` text,
  `fill_date` date DEFAULT NULL,
  `last_fill_date` date DEFAULT NULL,
  `expiration_date` date DEFAULT NULL,
  `bottle_id` int DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `store_number` varchar(50) DEFAULT NULL,
  `rx_store_num` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`prescription_id`),
  KEY `medication_id` (`medication_id`),
  KEY `prescriber_id` (`prescriber_id`),
  KEY `bottle_id` (`bottle_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_prescriptions_user_id` (`user_id`),
  KEY `idx_prescriptions_status` (`status`),
  CONSTRAINT `Prescriptions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patientsinfo` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `Prescriptions_ibfk_2` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`medication_id`),
  CONSTRAINT `Prescriptions_ibfk_3` FOREIGN KEY (`prescriber_id`) REFERENCES `Prescribers` (`prescriber_id`),
  CONSTRAINT `Prescriptions_ibfk_4` FOREIGN KEY (`bottle_id`) REFERENCES `bottles` (`bottle_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Prescriptions`
--

LOCK TABLES `Prescriptions` WRITE;
/*!40000 ALTER TABLE `Prescriptions` DISABLE KEYS */;
INSERT INTO `Prescriptions` VALUES (1,1,1,1,30,7,'Take one tablet daily with food','2024-01-15','2024-12-15',NULL,NULL,'active','1618','03102-001','2026-02-01 04:24:36','2026-02-06 05:57:40'),(2,2,2,2,90,5,'Take twice daily with meals','2024-02-01','2024-11-01',NULL,NULL,'active','1618','03102-002','2026-02-01 04:24:36','2026-02-01 04:24:36'),(3,3,3,3,30,11,'Take one tablet daily','2024-01-20','2024-12-20',NULL,NULL,'active','1618','03102-003','2026-02-01 04:24:36','2026-02-01 04:24:36'),(4,4,4,1,30,5,'Take one capsule daily before breakfast','2024-03-01','2024-10-01',NULL,NULL,'active','1618','03102-004','2026-02-01 04:24:36','2026-02-01 04:24:36'),(5,5,5,4,30,9,'Take one tablet daily, may cause dizziness','2024-01-25','2024-12-25',NULL,NULL,'active','1618','03102-005','2026-02-01 04:24:36','2026-02-01 04:24:36'),(6,6,6,2,30,11,'Take one tablet daily to prevent blood clots','2024-02-10','2024-11-10',NULL,NULL,'active','1618','03102-006','2026-02-01 04:24:36','2026-02-01 04:24:36'),(7,1,8,3,20,1,'Take as needed for pain, max 3 times daily','2024-03-15','2024-10-15',NULL,NULL,'active','1618','03102-007','2026-02-01 04:24:36','2026-02-06 06:09:47'),(8,7,1,1,30,11,'Take one tablet daily with food','2024-02-20','2024-11-20',NULL,NULL,'active','1618','03102-008','2026-02-01 04:24:36','2026-02-01 04:24:36');
/*!40000 ALTER TABLE `Prescriptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ProductSelectionQueue`
--

DROP TABLE IF EXISTS `ProductSelectionQueue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ProductSelectionQueue` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `product` varchar(255) DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `instructions` text,
  `delivery` varchar(50) DEFAULT NULL,
  `promise_time` datetime DEFAULT NULL,
  `rx_store_num` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `refills` int DEFAULT '0',
  `created_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_created` (`created_date`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ProductSelectionQueue`
--

LOCK TABLES `ProductSelectionQueue` WRITE;
/*!40000 ALTER TABLE `ProductSelectionQueue` DISABLE KEYS */;
INSERT INTO `ProductSelectionQueue` VALUES (1,1,'John','Smith','Lisinopril 10mg',30,'Take one daily','Pick Up','2026-02-02 14:00:00','03102-001','data_entry_complete',0,'2026-02-01 04:24:36','2026-02-01 05:04:05'),(2,2,'Maria','Garcia','Metformin 500mg',90,'Take twice daily','Delivery','2026-02-03 14:00:00','03102-002','data_entry_complete',0,'2026-02-01 04:24:36','2026-02-01 05:10:35'),(3,3,'James','Brown','Atorvastatin 20mg',30,'Take daily','Pick Up','2026-02-02 14:00:00','03102-003','data_entry_complete',0,'2026-02-01 04:24:36','2026-02-01 05:25:55'),(4,1,'John','Smith','Lisinopril',30,'Take one tablet daily with food','Pick Up','2026-02-01 14:00:00','03102-001','data_entry_complete',1,'2026-02-01 04:48:10','2026-02-06 05:28:24'),(5,1,'John','Smith','Lisinopril',30,'Take one tablet daily with food','Pick Up','2026-02-02 14:00:00','03102-001','data_entry_complete',1,'2026-02-01 05:21:58','2026-02-01 05:22:28'),(6,1,'John','Smith','Lisinopril',30,'Take one tablet daily with food','Pick Up','2026-02-07 14:00:00','03102-001','data_entry_complete',1,'2026-02-06 05:28:17','2026-02-06 06:34:04'),(7,1,'John','Smith','Lisinopril',30,'Take one tablet daily with food','Pick Up','2026-02-07 14:00:00','03102-001','data_entry_complete',1,'2026-02-06 05:57:40','2026-02-06 05:58:03'),(8,1,'John','Smith','Ibuprofen',20,'Take as needed for pain, max 3 times daily','Pick Up','2026-02-07 14:00:00','03102-007','data_entry_complete',1,'2026-02-06 05:58:40','2026-02-06 06:10:16'),(9,1,'John','Smith','Ibuprofen',20,'Take as needed for pain, max 3 times daily','Pick Up','2026-02-07 14:00:00','03102-007','in_progress',1,'2026-02-06 06:09:47','2026-02-06 06:12:34');
/*!40000 ALTER TABLE `ProductSelectionQueue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ReadyForPickUp`
--

DROP TABLE IF EXISTS `ReadyForPickUp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ReadyForPickUp` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `medication_id` int DEFAULT NULL,
  `rx_store_num` varchar(50) DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `ready_date` date DEFAULT NULL,
  `payment_status` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `ReadyForPickUp_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patientsinfo` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ReadyForPickUp`
--

LOCK TABLES `ReadyForPickUp` WRITE;
/*!40000 ALTER TABLE `ReadyForPickUp` DISABLE KEYS */;
/*!40000 ALTER TABLE `ReadyForPickUp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UserEntry`
--

DROP TABLE IF EXISTS `UserEntry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserEntry` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UserEntry`
--

LOCK TABLES `UserEntry` WRITE;
/*!40000 ALTER TABLE `UserEntry` DISABLE KEYS */;
INSERT INTO `UserEntry` VALUES (1,'admin','admin123','2026-02-01 04:24:36'),(2,'pharmacist','pharm123','2026-02-01 04:24:36');
/*!40000 ALTER TABLE `UserEntry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bottles`
--

DROP TABLE IF EXISTS `bottles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bottles` (
  `bottle_id` int NOT NULL AUTO_INCREMENT,
  `medication_id` int NOT NULL,
  `ndc` varchar(20) DEFAULT NULL,
  `lot_number` varchar(100) DEFAULT NULL,
  `expiration_date` date NOT NULL,
  `quantity` int NOT NULL,
  `unit_of_measure` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'in_stock',
  `location` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`bottle_id`),
  KEY `medication_id` (`medication_id`),
  KEY `idx_expiration` (`expiration_date`),
  KEY `idx_status` (`status`),
  CONSTRAINT `bottles_ibfk_1` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`medication_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bottles`
--

LOCK TABLES `bottles` WRITE;
/*!40000 ALTER TABLE `bottles` DISABLE KEYS */;
INSERT INTO `bottles` VALUES (1,1,'0069-4020-93','LOT001','2026-12-31',150,'tablets','in_stock','Shelf A-1','2026-02-01 04:24:36','2026-02-01 04:24:36'),(2,1,'0069-4020-93','LOT002','2025-06-30',75,'tablets','in_stock','Shelf A-1','2026-02-01 04:24:36','2026-02-01 04:24:36'),(3,2,'0093-1000-01','LOT003','2027-03-15',200,'tablets','in_stock','Shelf B-1','2026-02-01 04:24:36','2026-02-01 04:24:36'),(4,3,'0071-0156-23','LOT004','2026-09-20',120,'tablets','in_stock','Shelf C-1','2026-02-01 04:24:36','2026-02-01 04:24:36'),(5,4,'0178-0711-13','LOT005','2025-12-10',90,'capsules','in_stock','Shelf D-1','2026-02-01 04:24:36','2026-02-01 04:24:36'),(6,5,'0004-0277-01','LOT006','2026-08-15',100,'tablets','in_stock','Shelf E-1','2026-02-01 04:24:36','2026-02-01 04:24:36'),(7,6,'0087-2159-93','LOT007','2026-11-25',60,'tablets','in_stock','Shelf F-1','2026-02-01 04:24:36','2026-02-01 04:24:36'),(8,7,'0029-6014-18','LOT008','2025-10-05',80,'capsules','in_stock','Shelf G-1','2026-02-01 04:24:36','2026-02-01 04:24:36'),(9,8,'0067-0219-20','LOT009','2027-01-30',300,'tablets','in_stock','Shelf H-1','2026-02-01 04:24:36','2026-02-01 04:24:36');
/*!40000 ALTER TABLE `bottles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drug_drug_interactions`
--

DROP TABLE IF EXISTS `drug_drug_interactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drug_drug_interactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `medication_id_1` int NOT NULL,
  `medication_id_2` int NOT NULL,
  `severity` varchar(50) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  KEY `idx_med1` (`medication_id_1`),
  KEY `idx_med2` (`medication_id_2`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drug_drug_interactions`
--

LOCK TABLES `drug_drug_interactions` WRITE;
/*!40000 ALTER TABLE `drug_drug_interactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `drug_drug_interactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drug_review`
--

DROP TABLE IF EXISTS `drug_review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drug_review` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `medication_id` int DEFAULT NULL,
  `gene` varchar(100) DEFAULT NULL,
  `variant` varchar(255) DEFAULT NULL,
  `risk_level` varchar(50) DEFAULT NULL,
  `notes` text,
  `status` varchar(50) DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `medication_id` (`medication_id`),
  KEY `idx_user` (`user_id`),
  CONSTRAINT `drug_review_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patientsinfo` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `drug_review_ibfk_2` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`medication_id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drug_review`
--

LOCK TABLES `drug_review` WRITE;
/*!40000 ALTER TABLE `drug_review` DISABLE KEYS */;
INSERT INTO `drug_review` VALUES (1,1,1,'CYP2C9','rs1799853','Low','Normal metabolism expected','active','2026-02-01 04:24:36'),(2,2,2,'CYP2D6','rs16947','Moderate','Intermediate metabolizer - monitor','active','2026-02-01 04:24:36'),(3,4,6,'CYP2C19','rs4244285','High','Reduced function - may reduce efficacy','active','2026-02-01 04:24:36'),(4,1,3,'SLCO1B1','rs4149056','Moderate','Score: 3.25 - Genotypes CC + CT is associated with increased likelihood of statin-related myopathy when treated with atorvastatin in people with Cardiovascular Disease, Diabetes Mellitus, Acute coronary syndrome or Dyslipidaemia as compared to genotype TT.','active','2026-02-01 04:47:40'),(5,1,3,'SLCO1B1','rs4149056','Low','Score: 0.0 - Genotype CT is associated with increased severity of statin-related myopathy when treated with atorvastatin, carvedilol, diltiazem, dulaglutide, ezetimibe, fluoxetine, furosemide, lansoprazole, levothyroxine, lorazepam and warfarin.','active','2026-02-01 04:47:40'),(6,1,3,'SLCO1B1','rs4149056','Low','Score: -0.0 - Genotype CC is not associated with the short-term effects of statins on cholesterol homeostasis when exposed to atorvastatin, fluvastatin, pravastatin, rosuvastatin and simvastatin.','active','2026-02-01 04:47:40'),(7,1,3,'SLCO1B1','rs4149056','Low','Score: 0.125 - Genotypes CC + CT are associated with decreased oral clearance of atorvastatin when exposed to atorvastatin in people with Obesity as compared to genotype TT.','active','2026-02-01 04:47:40'),(8,1,3,'SLCO1B1','rs4149056','Moderate','Score: 3.25 - Allele C is associated with all statin-induced myopathy and severe myopathy when treated with atorvastatin, fluvastatin, hmg coa reductase inhibitors, pravastatin, rosuvastatin or simvastatin as compared to allele T.','active','2026-02-01 04:47:40'),(9,1,3,'SLCO1B1','rs4149056','Moderate','Score: 2.0 - Genotypes CC + CT are associated with increased concentrations of atorvastatin in healthy individuals as compared to genotype TT.','active','2026-02-01 04:47:40'),(10,1,3,'SLCO1B1','rs4149056','Low','Score: 1.5 - Genotypes CC + CT are associated with increased concentrations of atorvastatin in people with Hypercholesterolemia as compared to genotype TT.','active','2026-02-01 04:47:40'),(11,1,3,'SLCO1B1','rs4149056','Low','Score: 0.0 - Allele C is associated with increased exposure to atorvastatin as compared to allele T.','active','2026-02-01 04:47:40'),(12,1,3,'SLCO1B1','rs4149056','Moderate','Score: 2.5 - Genotypes CC + CT are associated with increased likelihood of statin-related myopathy when treated with atorvastatin or simvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(13,1,3,'SLCO1B1','rs4149056','Low','Score: 0.125 - Genotype CT is associated with increased exposure to atorvastatin in healthy individuals as compared to genotype TT.','active','2026-02-01 04:47:40'),(14,1,3,'SLCO1B1','rs4149056','Low','Score: 1.0 - Genotype CT is associated with increased exposure to atorvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(15,1,3,'SLCO1B1','rs4149056','Low','Score: 1.75 - Genotypes CC + CT are associated with decreased response to atorvastatin, hmg coa reductase inhibitors, pravastatin or simvastatin in people with Hyperlipidemias as compared to genotype TT.','active','2026-02-01 04:47:40'),(16,1,3,'SLCO1B1','rs4149056','Low','Score: 1.75 - Genotypes CC + CT are associated with increased concentrations of atorvastatin in healthy individuals as compared to genotype TT.','active','2026-02-01 04:47:40'),(17,1,3,'SLCO1B1','rs4149056','Low','Score: 1.25 - Genotypes CC + CT are associated with increased concentrations of atorvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(18,1,3,'SLCO1B1','rs4149056','Moderate','Score: 3.25 - Genotypes CC + CT are associated with increased risk of dose decrease or switch to another cholesterol-lowering drug in users with a starting dose of more than 20 mg when treated with atorvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(19,1,3,'SLCO1B1','rs4149056','Low','Score: 0.125 - Genotypes CC + CT are associated with increased concentrations of atorvastatin in healthy individuals as compared to genotype TT.','active','2026-02-01 04:47:40'),(20,1,3,'SLCO1B1','rs4149056','Low','Score: 1.25 - Genotype TT is associated with decreased response to atorvastatin as compared to genotypes CC + CT.','active','2026-02-01 04:47:40'),(21,1,3,'SLCO1B1','rs4149056','Low','Score: 0.0 - Genotype TT is associated with increased likelihood of discontinuation when treated with atorvastatin or simvastatin as compared to genotypes CC + CT.','active','2026-02-01 04:47:40'),(22,1,3,'SLCO1B1','rs4149056','Low','Score: 1.375 - Genotypes CC + CT is associated with decreased response to atorvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(23,1,3,'SLCO1B1','rs4149056','Low','Score: 1.375 - Genotypes CC + CT are associated with increased risk of statin-related myopathy when treated with atorvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(24,1,3,'SLCO1B1','rs4149056','Moderate','Score: 3.0 - Allele C is associated with increased risk of Muscular Diseases when treated with atorvastatin.','active','2026-02-01 04:47:40'),(25,1,3,'SLCO1B1','rs4149056','Moderate','Score: 2.5 - Genotypes CC + CT is associated with increased likelihood of Drug Toxicity, Muscular Diseases, Rhabdomyolysis and Toxic liver disease when treated with atorvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(26,1,3,'SLCO1B1','rs4149056','Moderate','Score: 2.5 - Allele C is associated with increased exposure to 2-hydroxyatorvastatin, 2-hydroxyatorvastatin lactone, 4-hydroxyatorvastatin, 4-hydroxyatorvastatin lactone, atorvastatin and atorvastatin lactone in healthy individuals as compared to allele T.','active','2026-02-01 04:47:40'),(27,1,3,'SLCO1B1','rs4149056','Low','Score: 1.5 - Allele C is associated with increased plasma concentrations of atorvastatin as compared to allele T.','active','2026-02-01 04:47:40'),(28,1,3,'SLCO1B1','rs4149056','Low','Score: 1.0 - Genotype CC is associated with increased AUC when exposed to atorvastatin in healthy individuals as compared to genotype TT.','active','2026-02-01 04:47:40'),(29,1,3,'SLCO1B1','rs4149056','Low','Score: 1.25 - Genotypes CC + CT are associated with increased risk of statin-related myopathy when treated with atorvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(30,1,3,'SLCO1B1','rs4149056','Low','Score: 1.5 - Genotype TT is associated with a nearly tripled increased percentage of atorvastatin AUC(0 - 48) values after a single oral dose of rifampicin when exposed to atorvastatin and rifampin as compared to genotype CC.','active','2026-02-01 04:47:40'),(31,1,3,'SLCO1B1','rs4149056','Low','Score: 0.5 - Genotype CC is associated with increased cholesterol synthesis rate when exposed to atorvastatin, fluvastatin, pravastatin, rosuvastatin and simvastatin as compared to genotype TT.','active','2026-02-01 04:47:40'),(32,1,3,'SLCO1B1','rs4149056','Low','Score: 1.5 - Allele C is associated with increased dose-adjusted trough concentrations of atorvastatin in children with Hypercholesterolemia as compared to allele T.','active','2026-02-01 04:47:40'),(33,1,3,'SLCO1B1','rs4149056','Moderate','Score: 2.25 - Genotype CC is associated with increased likelihood of Treatment modification or Discontinuation when treated with atorvastatin or simvastatin in people with Hypercholesterolemia.','active','2026-02-01 04:47:40');
/*!40000 ALTER TABLE `drug_review` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drugreviewqueue`
--

DROP TABLE IF EXISTS `drugreviewqueue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drugreviewqueue` (
  `id` int NOT NULL AUTO_INCREMENT,
  `prescription_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  `medication_id` int DEFAULT NULL,
  `risk_level` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `reviewed_by` varchar(100) DEFAULT NULL,
  `reviewed_date` datetime DEFAULT NULL,
  `notes` text,
  `created_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `drugreviewqueue_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patientsinfo` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drugreviewqueue`
--

LOCK TABLES `drugreviewqueue` WRITE;
/*!40000 ALTER TABLE `drugreviewqueue` DISABLE KEYS */;
INSERT INTO `drugreviewqueue` VALUES (3,4,1,1,'Low','approved','pharmacist','2026-02-01 05:23:42',NULL,'2026-02-01 05:22:28'),(4,4,1,1,'Low','approved','pharmacist','2026-02-06 05:33:02','','2026-02-06 05:28:24'),(5,4,1,1,'Low','approved','pharmacist','2026-02-06 05:33:28','','2026-02-06 05:28:41'),(6,4,1,1,'Low','rejected','pharmacist','2026-02-06 05:58:13','Prescription rejected - requires prescriber contact','2026-02-06 05:58:03'),(7,4,1,1,'Low','pending',NULL,NULL,NULL,'2026-02-06 06:34:04');
/*!40000 ALTER TABLE `drugreviewqueue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `final_genetic_info`
--

DROP TABLE IF EXISTS `final_genetic_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `final_genetic_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `gene` varchar(100) DEFAULT NULL,
  `variant` varchar(255) DEFAULT NULL,
  `genotype` varchar(255) DEFAULT NULL,
  `date_tested` date DEFAULT NULL,
  `test_result` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  CONSTRAINT `final_genetic_info_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patientsinfo` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `final_genetic_info`
--

LOCK TABLES `final_genetic_info` WRITE;
/*!40000 ALTER TABLE `final_genetic_info` DISABLE KEYS */;
INSERT INTO `final_genetic_info` VALUES (1,1,'CYP2C9','rs1799853','A/A','2024-06-15','Normal metabolizer','2026-02-01 04:24:36'),(2,2,'CYP2D6','rs16947','G/A','2024-07-20','Intermediate metabolizer','2026-02-01 04:24:36'),(3,3,'CYP3A4','rs2740574','A/A','2024-05-10','Normal metabolizer','2026-02-01 04:24:36'),(4,4,'VKORC1','rs9923231','G/A','2024-08-01','Sensitive to warfarin','2026-02-01 04:24:36'),(5,5,'TPMT','rs1142345','G/G','2024-06-30','Normal metabolizer','2026-02-01 04:24:36'),(6,6,'HLA-B','*5701','Positive','2024-07-15','Risk for abacavir hypersensitivity','2026-02-01 04:24:36'),(7,1,'SLCO1B1','rs4149056','A/A','2026-01-31','Variant rs4149056 tested via PharmGKB','2026-02-01 04:47:40');
/*!40000 ALTER TABLE `final_genetic_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inusebottles`
--

DROP TABLE IF EXISTS `inusebottles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inusebottles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bottle_id` int NOT NULL,
  `prescription_id` int DEFAULT NULL,
  `quantity_used` int DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bottle_id` (`bottle_id`),
  CONSTRAINT `inusebottles_ibfk_1` FOREIGN KEY (`bottle_id`) REFERENCES `bottles` (`bottle_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inusebottles`
--

LOCK TABLES `inusebottles` WRITE;
/*!40000 ALTER TABLE `inusebottles` DISABLE KEYS */;
/*!40000 ALTER TABLE `inusebottles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medications`
--

DROP TABLE IF EXISTS `medications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medications` (
  `medication_id` int NOT NULL AUTO_INCREMENT,
  `medication_name` varchar(255) NOT NULL,
  `generic_name` varchar(255) DEFAULT NULL,
  `ndc` varchar(20) DEFAULT NULL,
  `strength` varchar(100) DEFAULT NULL,
  `form` varchar(50) DEFAULT NULL,
  `description` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`medication_id`),
  UNIQUE KEY `medication_name` (`medication_name`),
  KEY `idx_name` (`medication_name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medications`
--

LOCK TABLES `medications` WRITE;
/*!40000 ALTER TABLE `medications` DISABLE KEYS */;
INSERT INTO `medications` VALUES (1,'Lisinopril','Lisinopril','0069-4020-93','10 mg','Tablet','ACE inhibitor for hypertension','2026-02-01 04:24:36'),(2,'Metformin','Metformin HCl','0093-1000-01','500 mg','Tablet','Oral diabetes medication','2026-02-01 04:24:36'),(3,'Atorvastatin','Atorvastatin Calcium','0071-0156-23','20 mg','Tablet','Statin for cholesterol','2026-02-01 04:24:36'),(4,'Omeprazole','Omeprazole','0178-0711-13','20 mg','Capsule','Proton pump inhibitor','2026-02-01 04:24:36'),(5,'Sertraline','Sertraline HCl','0004-0277-01','50 mg','Tablet','SSRI antidepressant','2026-02-01 04:24:36'),(6,'Clopidogrel','Clopidogrel Bisulfate','0087-2159-93','75 mg','Tablet','Antiplatelet agent','2026-02-01 04:24:36'),(7,'Amoxicillin','Amoxicillin','0029-6014-18','500 mg','Capsule','Beta-lactam antibiotic','2026-02-01 04:24:36'),(8,'Ibuprofen','Ibuprofen','0067-0219-20','200 mg','Tablet','NSAID pain reliever','2026-02-01 04:24:36');
/*!40000 ALTER TABLE `medications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient_allergies`
--

DROP TABLE IF EXISTS `patient_allergies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient_allergies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `allergen` varchar(255) NOT NULL,
  `reaction` varchar(255) DEFAULT NULL,
  `severity` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `patient_allergies_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patientsinfo` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_allergies`
--

LOCK TABLES `patient_allergies` WRITE;
/*!40000 ALTER TABLE `patient_allergies` DISABLE KEYS */;
INSERT INTO `patient_allergies` VALUES (1,1,'Penicillin','Rash','Moderate','2026-02-01 04:24:36'),(2,2,'Sulfa Drugs','Hives','Severe','2026-02-01 04:24:36'),(3,3,'Ibuprofen','Stomach upset','Mild','2026-02-01 04:24:36'),(4,4,'Aspirin','Anaphylaxis','Severe','2026-02-01 04:24:36'),(5,5,'Codeine','Itching','Mild','2026-02-01 04:24:36'),(6,6,'NSAIDs','Rash','Moderate','2026-02-01 04:24:36');
/*!40000 ALTER TABLE `patient_allergies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient_insurance`
--

DROP TABLE IF EXISTS `patient_insurance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient_insurance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `insurance_provider` varchar(255) DEFAULT NULL,
  `policy_number` varchar(100) DEFAULT NULL,
  `group_number` varchar(100) DEFAULT NULL,
  `member_id` varchar(100) DEFAULT NULL,
  `effective_date` date DEFAULT NULL,
  `termination_date` date DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `plan_name` varchar(100) DEFAULT NULL,
  `bin_number` varchar(6) DEFAULT NULL,
  `pcn` varchar(20) DEFAULT NULL,
  `cardholder_id` varchar(30) DEFAULT NULL,
  `person_code` varchar(5) DEFAULT NULL,
  `relationship_code` varchar(3) DEFAULT NULL,
  `plan_type` varchar(30) DEFAULT 'Commercial',
  `expiration_date` date DEFAULT NULL,
  `copay_generic` decimal(6,2) DEFAULT NULL,
  `copay_brand` decimal(6,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `patient_insurance_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `patientsinfo` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_insurance`
--

LOCK TABLES `patient_insurance` WRITE;
/*!40000 ALTER TABLE `patient_insurance` DISABLE KEYS */;
INSERT INTO `patient_insurance` VALUES (1,1,'Blue Cross Blue Shield','BC123456','GRP001','MEM001','2023-01-01',NULL,'2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,NULL,NULL,NULL,NULL,'Commercial',NULL,NULL,NULL),(2,2,'Aetna','AET789012','GRP002','MEM002','2023-06-15',NULL,'2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,NULL,NULL,NULL,NULL,'Commercial',NULL,NULL,NULL),(3,3,'United Healthcare','UHC345678','GRP003','MEM003','2023-03-01',NULL,'2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,NULL,NULL,NULL,NULL,'Commercial',NULL,NULL,NULL),(4,4,'Cigna','CIG901234','GRP004','MEM004','2023-02-01',NULL,'2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,NULL,NULL,NULL,NULL,'Commercial',NULL,NULL,NULL),(5,5,'Humana','HUM567890','GRP005','MEM005','2023-07-01',NULL,'2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,NULL,NULL,NULL,NULL,'Commercial',NULL,NULL,NULL),(6,6,'Kaiser Permanente','KAI123456','GRP006','MEM006','2023-04-01',NULL,'2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,NULL,NULL,NULL,NULL,'Commercial',NULL,NULL,NULL),(7,7,'Medicare','CMS789012','GRP007','MEM007','2023-01-01',NULL,'2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,NULL,NULL,NULL,NULL,'Commercial',NULL,NULL,NULL),(8,8,'Medicaid','MCD345678','GRP008','MEM008','2023-05-01',NULL,'2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,NULL,NULL,NULL,NULL,'Commercial',NULL,NULL,NULL);
/*!40000 ALTER TABLE `patient_insurance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patientsinfo`
--

DROP TABLE IF EXISTS `patientsinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patientsinfo` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `Dateofbirth` date DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address_1` varchar(255) DEFAULT NULL,
  `address_2` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `gender` varchar(20) DEFAULT NULL,
  `race_ethnicity` varchar(50) DEFAULT NULL,
  `language` varchar(30) DEFAULT 'English',
  `cell_phone` varchar(20) DEFAULT NULL,
  `work_phone` varchar(20) DEFAULT NULL,
  `emergency_contact_name` varchar(100) DEFAULT NULL,
  `emergency_contact_phone` varchar(20) DEFAULT NULL,
  `preferred_location` varchar(100) DEFAULT NULL,
  `child_resistant_caps` tinyint(1) DEFAULT '1',
  `generic_substitution` tinyint(1) DEFAULT '1',
  `large_print_labels` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`user_id`),
  KEY `idx_name` (`last_name`,`first_name`),
  KEY `idx_phone` (`phone`),
  KEY `idx_patientsinfo_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patientsinfo`
--

LOCK TABLES `patientsinfo` WRITE;
/*!40000 ALTER TABLE `patientsinfo` DISABLE KEYS */;
INSERT INTO `patientsinfo` VALUES (1,'John','Smith','1965-03-15','555-1001','john.smith@email.com','100 Oak Street',NULL,'Springfield','IL','62701','USA','2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,'English',NULL,NULL,NULL,NULL,NULL,1,1,0),(2,'Maria','Garcia','1978-07-22','555-1002','maria.garcia@email.com','200 Maple Avenue',NULL,'Springfield','IL','62701','USA','2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,'English',NULL,NULL,NULL,NULL,NULL,1,1,0),(3,'James','Brown','1952-11-08','555-1003','james.brown@email.com','300 Pine Road',NULL,'Springfield','IL','62701','USA','2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,'English',NULL,NULL,NULL,NULL,NULL,1,1,0),(4,'Jennifer','Davis','1985-05-30','555-1004','jennifer.davis@email.com','400 Elm Street',NULL,'Springfield','IL','62701','USA','2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,'English',NULL,NULL,NULL,NULL,NULL,1,1,0),(5,'Michael','Wilson','1960-12-25','555-1005','michael.wilson@email.com','500 Birch Lane',NULL,'Springfield','IL','62701','USA','2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,'English',NULL,NULL,NULL,NULL,NULL,1,1,0),(6,'Lisa','Anderson','1972-09-14','555-1006','lisa.anderson@email.com','600 Cedar Drive',NULL,'Springfield','IL','62701','USA','2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,'English',NULL,NULL,NULL,NULL,NULL,1,1,0),(7,'Robert','Taylor','1948-02-20','555-1007','robert.taylor@email.com','700 Spruce Way',NULL,'Springfield','IL','62701','USA','2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,'English',NULL,NULL,NULL,NULL,NULL,1,1,0),(8,'Patricia','Martinez','1980-06-10','555-1008','patricia.martinez@email.com','800 Walnut Court',NULL,'Springfield','IL','62701','USA','2026-02-01 04:24:36','2026-02-01 04:24:36',NULL,NULL,'English',NULL,NULL,NULL,NULL,NULL,1,1,0);
/*!40000 ALTER TABLE `patientsinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prescription_audit_log`
--

DROP TABLE IF EXISTS `prescription_audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prescription_audit_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `prescription_id` int NOT NULL,
  `from_status` varchar(100) DEFAULT NULL,
  `to_status` varchar(100) NOT NULL,
  `action` varchar(255) NOT NULL,
  `performed_by` varchar(100) DEFAULT 'pharmacist',
  `notes` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_prescription_id` (`prescription_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prescription_audit_log`
--

LOCK TABLES `prescription_audit_log` WRITE;
/*!40000 ALTER TABLE `prescription_audit_log` DISABLE KEYS */;
INSERT INTO `prescription_audit_log` VALUES (1,4,'data_entry_complete','drug_review_pending','Data entry complete - drug-gene conflict detected','pharmacist',NULL,'2026-02-06 05:58:03'),(2,4,'drug_review_pending','rejected','Drug review rejected - prescriber contact required','pharmacist','Prescription rejected - requires prescriber contact','2026-02-06 05:58:13'),(3,5,'data_entry_complete','product_dispensing_pending','Data entry complete - no conflicts, skipping drug review','pharmacist',NULL,'2026-02-06 06:10:16'),(4,4,'data_entry_complete','drug_review_pending','Data entry complete - drug-gene conflict detected','pharmacist',NULL,'2026-02-06 06:34:04');
/*!40000 ALTER TABLE `prescription_audit_log` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-06 19:22:21
