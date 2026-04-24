🛍️ Meraki Closet — Online Clothing Store Database System
A full-stack web-based database management system for a Palestinian online clothing store. Built as part of the Database Systems (COMP333) course at Birzeit University.

📌 Project Overview
Meraki Closet is designed to manage the day-to-day operations of an online women's clothing store. The system handles products, inventory, orders, customers, suppliers, employees, and delivery — all through a centralized, normalized relational database.

The goal is to replace manual data management with an organized, efficient system that reduces human error and improves decision-making.


✨ Features

🗂️ Product Management — Store clothing info (sizes, colors, prices, categories, quantities)
🛒 Order Management — Track customer orders and payment status
🚚 Delivery Tracking — Monitor shipments from warehouse to customer
👥 Customer & Supplier Management — Centralized contact and transaction records
🏪 Branch & Inventory Management — Multi-branch stock tracking with auto-updates
👔 Employee Management — Staff records, positions, salaries, and working hours
📊 Sales Reporting — Query-based reports for inventory, sales, and performance insights


🗄️ Database Design
The system uses a normalized relational schema (MySQL) with the following core entities:
Entity               Description
Customer             Name, email, phone, address
OrderOrder           ID, date, payment & shipping status
Order_Product        Junction table for Order ↔ Product (M:N)
Product              Title, category, price, sizes, colors, quantity            Category             Product classification (dresses, blouses, skirts…)                Branch               Store branch info for inventory and shipping               Supplier             Supplier contact and product supply data                  Employee             Staff name, position, salary, working hours                       Delivery             Shipping date, delivery status, responsible employee


Key Relationships

Customer places many Orders (1:N)
Order contains many Products via Order_Product (M:N)
Supplier provides many Products (1:N)
Product belongs to one Category (N:1)
Branch has many Employees (1:N)
Branch stores many Products (M:N)
Employee handles many deliveries (1:N)


🛠️ Tech Stack
Layer      Technology  
Database   MySQL 
Backend    Python (Flask)
Frontend   HTML, CSS
Tools      MySQL Workbench, Visual Studio Code, Draw.io (ERD)


🚀 Getting Started

   Prerequisites
   
    Python 3.x
    MySQL Server
    pip

👥 Team
Name    Student ID
Taima Nazzal  #1220701
Besan Maaly   #1222776

📄 License
This project was developed for academic purposes at Birzeit University.
