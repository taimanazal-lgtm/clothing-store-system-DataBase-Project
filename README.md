🛍️ Meraki Closet — Online Clothing Store Database System
A full-stack web-based database management system for a Palestinian online clothing store. Built as part of the Database Systems (COMP333) course at Birzeit University.

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
EntityPrimary KeyDescriptionCustomercustomer_IDName, email, phone, addressOrderorder_IDDate, payment status, shipping statusOrder_Product(order_ID, product_ID)Junction table — quantity per product per orderProductproduct_IDTitle, price, sizes, colors, available quantityCategorycategory_IDProduct classificationSuppliersupplier_IDName, phone, addressBranchbranch_IDBranch name, cityBranch_Product(branch_ID, product_ID)Entry date, quantity in branchEmployeeemployee_IDName, position, salary, working hours, branchDeliverydelivery_IDShipping date, status, responsible employee
Key Relationships
RelationshipTypeNotesCustomer → Order1:NA customer can place multiple ordersOrder ↔ ProductM:N via Order_ProductStores quantity per product per orderSupplier → Product1:NEach supplier provides multiple productsProduct → CategoryN:1Each product belongs to one categoryBranch → Employee1:NEach branch can have multiple employeesBranch ↔ ProductM:N via Branch_ProductTracks stock per branchEmployee → Delivery1:NEach employee can handle multiple deliveriesDelivery → Order1:NEach delivery can cover multiple orders

🛠️ Tech Stack
LayerTechnologyDatabaseMySQLBackendPython (Flask)FrontendHTML, CSSToolsMySQL Workbench, Visual Studio Code, Lucidchart (ERD)

🚀 Getting Started
Prerequisites

Python 3.x
MySQL Server
pip



👥 Team
NameStudent
Taima Nazza  l1220701
Besan Maaly  1222776

Instructor: Dr. Ihab Alshaar
Course: Database Systems — COMP333, Section 7
University: Birzeit University

📄 License
This project was developed for academic purposes at Birzeit University.
