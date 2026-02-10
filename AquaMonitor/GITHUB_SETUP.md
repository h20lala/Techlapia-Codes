# GitHub Setup & Raspberry Pi Sync Guide

This guide explains how to upload your `AquaMonitor` code to GitHub and sync it to your Raspberry Pi 5.

## Prerequisites
1.  **Git installed on Windows**: [Download Git for Windows](https://git-scm.com/download/win).
2.  **GitHub Account**: [Sign up here](https://github.com/).
3.  **SSH Access to Pi**: You should be able to `ssh pi@<ip-address>` from your computer.

---

## Part 1: Prepare Your Local Project (Windows)

1.  **Open Terminal** (Command Prompt or PowerShell) inside your project folder:
    `c:\Users\Louis Angelo Granada\Documents\School\tilapips researchh\Techlapia Codes\AquaMonitor`

2.  **Initialize Git**:
    ```powershell
    git init
    # I already created the .gitignore file for you, so it won't upload junk files.
    git add .
    git commit -m "Initial commit - AquaMonitor System"
    ```

3.  **Create Repository on GitHub**:
    *   Go to [GitHub.com/new](https://github.com/new).
    *   Repository Name: **AquaMonitor**
    *   Description: "Raspberry Pi 5 Aquaculture Monitoring System"
    *   **Do NOT** check "Add a README", ".gitignore", or "license" (you already have them).
    *   Click **Create repository**.

4.  **Upload Code**:
    *   Since you are on Windows, we will use the **HTTPS** link (easier to login).
    *   Run these exact commands in your terminal:
    ```powershell
    git remote add origin https://github.com/h20lala/Techlapia-Codes.git
    git branch -M main
    git push -u origin main
    ```
    *   *Note: If it asks for a username/password, a browser window should pop up to let you sign in.*

---

## Part 2: Setup on Raspberry Pi 5

1.  **SSH into your Pi**:
    ```powershell
    ssh pi@<your-pi-ip-address>
    ```

2.  **Clone the Repository** (First time only):
    ```bash
    cd ~
    # We use HTTPS here too for simplicity, or SSH if you set up keys
    git clone https://github.com/h20lala/Techlapia-Codes.git
    
    cd Techlapia-Codes
    ```

3.  **Setup Virtual Environment** (Required on Pi 5):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

---

## Part 3: Syncing Changes (Workflow)

Whenever you make changes on your Windows computer:

1.  **On Windows**: Save and Push
    ```powershell
    git add .
    git commit -m "Fixed load cell driver"
    git push
    ```

2.  **On Raspberry Pi**: Pull Updates
    ```bash
    # ( SSH into Pi first )
    cd ~/AquaMonitor
    git pull
    
    # If requirements changed:
    # pip install -r requirements.txt
    
    # Restart your program
    python main.py
    ```

---

## Part 4: SSH Authentication (Optional but Recommended)

To communicate with GitHub without typing passwords constantly, set up an **SSH Key on the Pi**.

1.  **Generate Key on Pi**:
    ```bash
    ssh-keygen -t ed25519 -C "pi@aquamonitor"
    # Press Enter for all prompts
    ```

2.  **View Public Key**:
    ```bash
    cat ~/.ssh/id_ed25519.pub
    ```
    *Copy the output (starts with `ssh-ed25519...`).*

3.  **Add to GitHub**:
    *   Go to [GitHub Settings > SSH Keys](https://github.com/settings/ssh/new).
    *   Title: "Raspberry Pi 5"
    *   Key: Paste the copied text.
    *   Click **Add SSH key**.

4.  **Switch Remote URL** (On Pi):
    ```bash
    git remote set-url origin git@github.com:YOUR_USERNAME/AquaMonitor.git
    ```
    Now `git pull` won't ask for a password!
