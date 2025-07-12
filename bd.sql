CREATE DATABASE  IF NOT EXISTS `tienda_zapatillas` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `tienda_zapatillas`;
-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: tienda_zapatillas
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `detalles_pedido`
--

DROP TABLE IF EXISTS `detalles_pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalles_pedido` (
  `id_detalle` int NOT NULL AUTO_INCREMENT,
  `id_pedido` int NOT NULL,
  `id_variante` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unidad` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_variante` (`id_variante`),
  CONSTRAINT `detalles_pedido_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`) ON DELETE CASCADE,
  CONSTRAINT `detalles_pedido_ibfk_2` FOREIGN KEY (`id_variante`) REFERENCES `variantes_zapatillas` (`id_variante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_pedido`
--

LOCK TABLES `detalles_pedido` WRITE;
/*!40000 ALTER TABLE `detalles_pedido` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalles_pedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_carrito`
--

DROP TABLE IF EXISTS `historial_carrito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_carrito` (
  `id_historial` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `carrito_data` json DEFAULT NULL,
  PRIMARY KEY (`id_historial`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `historial_carrito_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_carrito`
--

LOCK TABLES `historial_carrito` WRITE;
/*!40000 ALTER TABLE `historial_carrito` DISABLE KEYS */;
INSERT INTO `historial_carrito` VALUES (1,3,'2025-07-11 21:53:50','{\"1\": {\"nombre\": \"Air Max 90\", \"precio\": 120.0, \"cantidad\": 1}, \"2\": {\"nombre\": \"Ultraboost 22\", \"precio\": 150.0, \"cantidad\": 1}, \"4\": {\"nombre\": \"Classic Leather\", \"precio\": 80.0, \"cantidad\": 1}}');
/*!40000 ALTER TABLE `historial_carrito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marcas`
--

DROP TABLE IF EXISTS `marcas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `marcas` (
  `id_marca` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id_marca`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marcas`
--

LOCK TABLES `marcas` WRITE;
/*!40000 ALTER TABLE `marcas` DISABLE KEYS */;
INSERT INTO `marcas` VALUES (2,'Adidas'),(5,'New Balance'),(1,'Nike'),(3,'Puma'),(4,'Reebok');
/*!40000 ALTER TABLE `marcas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `fecha_pedido` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('pendiente','enviado','entregado','cancelado') NOT NULL DEFAULT 'pendiente',
  `total` decimal(10,2) NOT NULL,
  `direccion_envio` text,
  `telefono` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_pedido`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` VALUES (1,3,'2025-07-11 12:34:46','enviado',0.00,NULL,NULL),(2,1,'2025-07-11 12:34:46','pendiente',0.00,NULL,NULL),(3,2,'2025-07-11 12:34:46','entregado',0.00,NULL,NULL);
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `rol` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'lamin Yamal','lamin@gmail.com','$2b$12$h/BDtm3h/0WIXHVxKK0EYuI0DtqKiKqJOK6zni32qOmpAcf8axrxK','Los olivos Lima Peru Mundo','908273324',NULL),(2,'karina','kari@gmail.com','$2b$12$eIQDV8BybzMQUvAAQCFrqOl7xF7z9D5MDCRi3K/K3SwjdF4zRJMkq','dfsdf','234234234',NULL),(3,'Juan','ejemplo@gmail.com','$2b$12$2dSBZZjOKUultu7B1sQhquf.mmz8G1j8rxpKH/XR9Od4MbPXFUhXe','Av 13 de Mayo','984098374','USER'),(4,'Joel','Ana@gmail.com','$2b$12$pGccW7o6t8JRzO3QyBUQTumWY1lhM3MlYIDQ4QlG6btrIKEGXt4j.','Lima','917084917','USER'),(5,'nuevoItem','nuevo@gmail.com','$2b$12$suzAlD9miSDwb0VpN8dGmuN9Nz1QJStdwmUJQ/uSbqIFxkb2ibOEq','Av 13 de Mayo','909876557','USER');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `variantes_zapatillas`
--

DROP TABLE IF EXISTS `variantes_zapatillas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variantes_zapatillas` (
  `id_variante` int NOT NULL AUTO_INCREMENT,
  `id_zapatilla` int NOT NULL,
  `talla` decimal(4,2) NOT NULL,
  `color` varchar(50) NOT NULL,
  `stock` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_variante`),
  KEY `id_zapatilla` (`id_zapatilla`),
  CONSTRAINT `variantes_zapatillas_ibfk_1` FOREIGN KEY (`id_zapatilla`) REFERENCES `zapatillas` (`id_zapatilla`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `variantes_zapatillas`
--

LOCK TABLES `variantes_zapatillas` WRITE;
/*!40000 ALTER TABLE `variantes_zapatillas` DISABLE KEYS */;
INSERT INTO `variantes_zapatillas` VALUES (1,1,8.00,'Negro',50),(2,1,9.00,'Blanco',45),(3,1,8.50,'Rojo',30),(4,2,9.00,'Negro',60),(5,2,10.00,'Azul',55),(6,3,7.50,'Gris',40),(7,4,7.00,'Blanco',70),(8,5,9.50,'Verde',35);
/*!40000 ALTER TABLE `variantes_zapatillas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zapatillas`
--

DROP TABLE IF EXISTS `zapatillas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `zapatillas` (
  `id_zapatilla` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `id_marca` int DEFAULT NULL,
  PRIMARY KEY (`id_zapatilla`),
  KEY `id_marca` (`id_marca`),
  CONSTRAINT `zapatillas_ibfk_1` FOREIGN KEY (`id_marca`) REFERENCES `marcas` (`id_marca`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zapatillas`
--

LOCK TABLES `zapatillas` WRITE;
/*!40000 ALTER TABLE `zapatillas` DISABLE KEYS */;
INSERT INTO `zapatillas` VALUES (1,'Air Max 90','Clásico modelo de Nike con amortiguación Air.',120.00,1),(2,'Ultraboost 22','Zapatillas de running con amortiguación Boost.',150.00,2),(3,'RS-X Reinvention','Diseño retro running con tecnología de amortiguación.',100.00,3),(4,'Classic Leather','Un icono atemporal de Reebok.',80.00,4),(5,'574 Core','Estilo clásico y comodidad para el día a día.',90.00,5);
/*!40000 ALTER TABLE `zapatillas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'tienda_zapatillas'
--

--
-- Dumping routines for database 'tienda_zapatillas'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-11 16:55:40
