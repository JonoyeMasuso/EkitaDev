# EkitaDev
# 🤖 PEPS-Pay Agent: The Ethical Escrow System (Agent PEPS-Pay)

## 🌟 Overview

The **PEPS-Pay Agent** is an innovative, AI-driven solution designed to solve the "Last Mile Problem" in Real World Asset (RWA) payments on a blockchain layer, specifically using the **ARC (Algorand Request for Comments)** standard.

This system guarantees that funds held in an Escrow Smart Contract are only released after a **successful human verification** (the RWA Oracle) and ensures **payer protection** through built-in resilience and manual override features.

## 🎯 Core Problem Solved

Traditional decentralized payment escrows fail when they cannot reliably confirm that a real-world service (the RWA) was completed correctly (e.g., a delivery, a consultation, a quality check). The PEPS-Pay Agent bridges this gap by enforcing a mandatory human verification step.

## ✨ Key Features & Innovation

| Feature | Description | Ethical/Technical Value |
| :--- | :--- | :--- |
| **Human-in-the-Loop (HITL) Oracle** | The Agent pauses the transaction and waits for confirmation from a trusted **RWA Oracle (Operator)** via a dedicated UI switch. | **ETHICS:** Ensures the quality and correct completion of the RWA before payment is released. |
| **Resilient Retries Logic** | If the Agent fails to connect to the Oracle (simulating **NETWORK FAILURE**), it executes an exponential backoff retry logic (up to 3 attempts). | **RESILIENCE:** Prevents false failures and ensures the contract is not cancelled due to temporary network instability. |
| **The Ethical Panic Button** | Manual **"Cancel Contract & Refund"** functionality implemented in the UI. | **SECURITY:** Allows the Payer/Operator to override the process and **IMMEDIATELY CANCEL** the Escrow and initiate a **FULL REFUND** if human verification fails or fraud is suspected. |
| **Full-Stack Simulation** | The demo simulates the full cycle: UI Request (JS) → Agent Logic (Python) → Oracle Check (Toggle) → On-Chain Settlement (Logs). | **DEMONSTRATION:** Provides a clear visualization of the multi-layered system interaction. |

## 💻 Tech Stack

* **Agent Logic:** Python (`agent_logic.py`) – Handles the contract state, Oracle calls, and retry logic.
* **Smart Contract:** Simulated via Logs (Represents a stateful ARC Escrow contract with `releasePayment` and `cancelEscrow` functions).
* **Frontend UI:** HTML, CSS (`styles.css`), and JavaScript (`demo.js`) – Provides the user interface, the Oracle switch, and the **Cancellation Button**.

## 🚀 How to Run the Demo

1.  **Setup:** Ensure you have Python installed. The demo is run entirely via a local web server (or by opening `index.html` directly).
2.  **Start Contract:** Fill in the input fields (Amount, Supplier) and click **'INICIAR CONTRATO'**. The Agent will start the process.
3.  **Verification Check:** The Agent will pause and wait. You must interact with the **Section 2 (RWA Oracle Simulator)**.
    * **Success Path:** Toggle the switch to **VERIFICADO** (Verified). The Agent proceeds to Settlement.
    * **Failure/Cancel Path:** Click the **'❌ CANCELAR CONTRATO y Reembolsar'** button to manually override the Agent and trigger the immediate refund logic.
    * **Resilience Path:** Click **'🚨 Simular FALLA DE RED'** before verification. The Agent will enter the retry loop.

---
