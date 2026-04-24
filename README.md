🛍️ Meraki Closet — Online Clothing Store Database System

A full-stack web-based database management system for a Palestinian online clothing store. Built as part of the **Database Systems (COMP333)** course at Birzeit University.



📌 Project Overview

Meraki Closet is designed to manage the day-to-day operations of an online women's clothing store. The system handles products, inventory, orders, customers, suppliers, employees, and delivery — all through a centralized, normalized relational database.

The goal is to replace manual data management with an organized, efficient system that reduces human error and improves decision-making.



✨ Features

 🗂️ Product Management — Store clothing info (sizes, colors, prices, categories, quantities)
 🛒 Order Management — Track customer orders and payment/shipping status
 🚚 Delivery Tracking — Monitor shipments handled by employees
 👥 Customer & Supplier Management — Centralized contact and transaction records
 🏪 Branch & Inventory Management — Multi-branch stock tracking with entry dates
 👔 Employee Management — Staff records, positions, salaries, and working hours



🗄️ Database Design

The system uses a normalized relational schema (MySQL) with the following core entities:

| Entity | Primary Key | Description |

| `Customer` | customer_ID | Name, email, phone, address |
| `Order` | order_ID | Date, payment status, shipping status |
| `Order_Product` | (order_ID, product_ID) | Junction table — quantity per product per order |
| `Product` | product_ID | Title, price, sizes, colors, available quantity |
| `Category` | category_ID | Product classification |
| `Supplier` | supplier_ID | Name, phone, address |
| `Branch` | branch_ID | Branch name, city |
| `Branch_Product` | (branch_ID, product_ID) | Entry date, quantity in branch |
| `Employee` | employee_ID | Name, position, salary, working hours, branch |
| `Delivery` | delivery_ID | Shipping date, status, responsible employee |

 Key Relationships

| Relationship | Type | Notes |

| Customer → Order | 1:N | A customer can place multiple orders |
| Order ↔ Product | M:N via `Order_Product` | Stores quantity per product per order |
| Supplier → Product | 1:N | Each supplier provides multiple products |
| Product → Category | N:1 | Each product belongs to one category |
| Branch → Employee | 1:N | Each branch can have multiple employees |
| Branch ↔ Product | M:N via `Branch_Product` | Tracks stock per branch |
| Employee → Delivery | 1:N | Each employee can handle multiple deliveries |
| Delivery → Order | 1:N | Each delivery can cover multiple orders |



🛠️ Tech Stack

| Layer | Technology |

| Database | MySQL |
| Backend | Python (Flask) |
| Frontend | HTML, CSS |
| Tools | MySQL Workbench, Visual Studio Code, Lucidchart (ERD) |



🚀 Getting Started

 Prerequisites
 Python 3.x
 MySQL Server
 pip

👥 Team

| Name | Student ID |
| Besan Maaly | 1222776 |
| Taima Nazzal | 1220701 |





📄 License

This project was developed for academic purposes at Birzeit University.
