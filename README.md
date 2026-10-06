# Gmail Phishing & Threat Analyzer (Flutter Prototype)

An interactive, high-fidelity Flutter web/mobile prototype designed to simulate an advanced email security layer directly inside a modern Gmail-like interface. It helps users identify email spoofing, domain mismatches, malicious attachments, and calculate real-time visual safety scores.

---
---

## 📱 App Screenshots

### 1. Gmail-Style Inbox View
<p align="center">
  <img height="500" alt="Inbox View" src="https://github.com/user-attachments/assets/3574b4f0-99cf-4b4b-8c21-db6ebb172e49" />
</p>
> *Displays the primary inbox screen featuring unread message snippets, risk-colored avatar initials, timestamps, and the Gmail search header.*

---

### 2. Email Detail & Safety Card View
<p align="center">
  <img height="500" alt="Detail View" src="https://github.com/user-attachments/assets/cdbe6ec3-e072-4391-ba23-ad4cc7e73115" />
</p>

<p align="center">
  <img height="500" alt="Screenshot 2026-10-06 at 10 41 50 PM" src="https://github.com/user-attachments/assets/a4f8feda-04d3-4e6c-a1c1-4636363bf727" />
</p>
> *Same for yellow*
> *Shows the opened email view with the live safety score meter, sender verification mismatch warning, and threat analysis breakdown.*

---
## 🚀 Key Features

1. **Gmail-Style Authentic Interface**: 
   - Replicates core Gmail mobile aesthetics including search headers, primary tab views, profile avatar tags (`A`), unread message snippets, timestamps, and action bar controls.
   - Includes **10 diverse dummy emails** ranging from critical phishing threats (bank and government lookalikes) to safe verified correspondence.
2. **Real-Time Sender Verification & Spoofing Detection**:
   - Instantly compares the displayed sender name with actual server infrastructure headers to highlight domain mismatch attacks.
3. **Visual Safety Score & AI Threat Breakdown**:
   - Features a color-coded circular safety score meter (0-100 scale) categorized into Critical Risk, Suspicious, and Safe.
   - Dedicated threat analysis card explaining the reasoning behind each rating.
4. **Action Center Response Hub**:
   - Built-in interactive response controls inside the email view allowing users to **Block Sender**, **Report Cyber Fraud**, or **Mark as Safe**.

---

## 🛠️ Tech Stack
- **Framework**: Flutter (Dart)
- **Target Platform**: Flutter Web & Mobile Client Prototype
- **Design System**: Material Design 3 (Customized for client cloning)

---

## 💻 How to Run Locally

1. Ensure Flutter is installed on your machine (`flutter --version`).
2. Clone the repository and switch to the `aastha` branch:
   ```bash
   git clone [https://github.com/Tejas171099/Neurons-.git](https://github.com/Tejas171099/Neurons-.git)
   cd Neurons-
   git checkout aastha
3. Navigate to the project directory and run on Chrome:
   ```bash
   cd safety_card
   flutter run -d chrome

