![Architecture](architecture-diagram.png)
# 🚀 AWS VPC Architecture Lab

## 📌 Overview

This project demonstrates a secure AWS VPC setup with **public and private subnets**, using an **Internet Gateway (IGW)** and **NAT Gateway** for controlled internet access.

---

## 🧱 Architecture

* VPC: 10.0.0.0/16
* Public Subnet: 10.0.1.0/24
* Private Subnet: 10.0.2.0/24
* IGW + NAT Gateway
* Route Tables controlling traffic
* EC2 instances in both subnets

---

## 📊 Architecture Diagram

![Architecture](architecture-diagram.png)

---

## 🔄 Traffic Flow

* Public: Internet → IGW → EC2
* Private: EC2 → NAT → IGW → Internet

---

## 📸 Screenshots

### 🏗️ VPC

![VPC](screenshots/vpc-1.png)

---

### 🌐 Subnets

**Public Subnet**
![Public Subnet](screenshots/public-subnet.png)

**Private Subnet**
![Private Subnet](screenshots/private-subnet.png)

---

### 🚪 Internet Gateway

![IGW](screenshots/igw.png)

---

### 🔁 NAT Gateway

![NAT](screenshots/nat-gtw.png)

---

### 🧭 Route Tables

**Public Route Table**
![Public RT](screenshots/public-rt.png)

**Private Route Table**
![Private RT](screenshots/private-rt.png)

---

### 🖥️ EC2 Instances

**Public EC2**
![Public EC2](screenshots/public-ec2.png)

**Private EC2**
![Private EC2](screenshots/pvt-ec2.png)

---

## 🧠 Key Learnings

* Public vs Private subnet behavior
* IGW vs NAT Gateway usage
* Route table importance
* Secure AWS architecture basics

---

## 🧹 Cleanup

All resources deleted after testing to avoid cost.

---
