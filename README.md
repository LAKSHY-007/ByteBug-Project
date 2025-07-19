# 🗳️ SecureVote (Decentralized Voting System)


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)  
[![Solidity](https://img.shields.io/badge/Solidity-^0.8.0-blue)](https://soliditylang.org/)  
[![Build Status](https://img.shields.io/github/actions/workflow/status/yourusername/decentralized-voting/ci.yml)](https://github.com/yourusername/decentralized-voting/actions)

> A secure, transparent, and tamper-proof blockchain-based electronic voting system.

---

## 👨‍💻 Team Members

This project is a collaborative effort developed by:

- **Lakshya Pendharkar**
- **Pragati Bhadoria**
- **Pradeep Singh Gurjar**
- **Khushi Pal**
- **Yash Dubey**
- 
and was presented in a hackathon held in Delhi and were the finalists.
---

## 🧠 Project Overview

The **Decentralized Voting System** ensures integrity, anonymity, and accessibility for elections through a fully digital and transparent process. Leveraging **blockchain technology**, **biometric authentication**, and **QR-based receipts**, the system guarantees that:

- Each vote is securely verified.
- No individual can vote twice.
- All data is encrypted and hashed.
- Voting records are immutable and audit-friendly.

---

## 🔄 Workflow Overview

The process is divided into three main modules:

### 🖥️ 1. Dashboard
- 🔄 Language Switching Button  
- 📊 Display number of votes cast so far  
- 🔘 "Continue to Vote" button initiates the voting process  

### 🔐 2. Verification
- 🆔 User enters **Voter ID**  
- 📂 System checks **eligibility** against the database  
- ❌ If **Not Eligible**, voting access is denied  
- ✅ If **Eligible**, proceed to **Face Recognition and Fingerprint** biometric validation  

### 🗳️ 3. Voting
- 🧾 Display **voter’s name and location**  
- 🏛️ Display **party names** with a vote button for each candidate  
- 🧠 Store voter and voting data (hashed for anonymity)  
- 🎁 Generate **Reward Receipt** (with QR Code & Voter Info)  
- 💾 Receipt available for download  
- 🙏 Display **Thank You** message and redirect to dashboard  

### System Flow
<img width="845" height="570" alt="image" src="https://github.com/user-attachments/assets/4ab44609-5c22-4fd2-9f2d-c21f93f64738" />

  


---

## 💡 Key Features

- 🔒 **Biometric & ID Verification**
- 🔐 **Blockchain-based Data Integrity**
- 🔏 **Tamper-proof and Immutable Ledger**
- 🧾 **QR Code Receipts**
- 🌐 **Language Switching for Accessibility**
- 👁️‍🗨️ **Real-time Voting Stats**
- 📦 **Downloadable Proof of Vote**

---

## ⚙️ Tech Stack

### Blockchain & Backend
- **Solidity** – Smart Contracts  
- **Hardhat** – Local Ethereum development  
- **IPFS** – Decentralized file storage  
- **Node.js** – Backend scripting  

### Frontend
- **Streamlit** 
- **Tailwind CSS** – Styling framework  
- **Ethers.js** – Blockchain integration  

### Optional Enhancements
- **Zero-Knowledge Proofs** for voter privacy  
- **Facial Recognition Libraries** for biometric validation  

---

## 🚀 Getting Started

### Prerequisites

- Streamlit
- yarn or npm
- MetaMask (or compatible Ethereum wallet)
- Hardhat for local testing

### Installation

```bash
git clone https://github.com/yourusername/decentralized-voting.git
cd decentralized-voting
yarn install
```

## ScreenShots


<img width="1920" height="1080" alt="Screenshot 2025-07-19 161039" src="https://github.com/user-attachments/assets/a4fe3a83-55b2-46ec-a2ec-c13430011d00" />
<img width="1920" height="1080" alt="Screenshot 2025-07-19 161159" src="https://github.com/user-attachments/assets/975e0d71-6675-4343-8c89-e40d45ff89d9" />
<img width="1920" height="1080" alt="Screenshot 2025-07-19 161324" src="https://github.com/user-attachments/assets/f9dcf0b2-6425-4e20-a2ce-c3bb684aa5ea" />
<img width="1920" height="723" alt="ss2" src="https://github.com/user-attachments/assets/fa7f19e2-830a-4afa-8305-0506539da821" />
<img width="1920" height="856" alt="ss3" src="https://github.com/user-attachments/assets/ce37870b-57c7-4e87-b11b-f90ec84c6102" />
<img width="1523" height="904" alt="ss4" src="https://github.com/user-attachments/assets/5b7f75a3-5f34-421b-a84f-423a4e293e42" />
<img width="1920" height="504" alt="ss5" src="https://github.com/user-attachments/assets/471ba916-6c0e-4b62-8f46-d4df1ee9e1cb" />

##Voting Receipt##
<img width="1920" height="471" alt="image" src="https://github.com/user-attachments/assets/93e2c5b6-d805-4e26-b9c0-677f7f5cd0ef" />






## ⚠️ License and Usage Warning

This repository is public only for demonstration purposes.

- ❌ Forking not allowed
- ❌ Cloning not allowed
- ❌ Reuse not allowed

All rights reserved © 2025 by Khushi, Lakshya, Pradeep, Pragati, and Yash.





