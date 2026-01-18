# Setup & Installation Guide
## Smart Expense Manager Agent | Droidrun DevSprint 2026

---

## 📋 Prerequisites

### System Requirements
- **OS:** macOS, Linux, or Windows
- **Python:** 3.8 or higher
- **Android Studio:** 2023.1 or later
- **Emulator:** API level 28+ (Android 9.0)
- **RAM:** Minimum 8GB (16GB recommended)
- **Disk Space:** 10GB for Android setup

### Install Python 3.8+
```bash
# macOS (using Homebrew)
brew install python@3.8

# Ubuntu/Debian
sudo apt-get install python3.8 python3.8-dev

# Windows
# Download from https://www.python.org/downloads/
```

### Install Git
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt-get install git

# Windows
# Download from https://git-scm.com/
```

---

## 🚀 Step-by-Step Setup

### Step 1: Register & Join Hackathon

1. Go to https://unstop.com/ and search "Droidrun DevSprint"
2. Click **Register** for the hackathon
3. Join Discord server from Unstop page
4. Go to hackathon channel and introduce yourself

### Step 2: Setup Droidrun Environment

#### Option A: Using Droidrun SDK (Recommended)

1. **Download Droidrun SDK**
   ```bash
   # Create workspace directory
   mkdir -p ~/droidrun-workspace
   cd ~/droidrun-workspace
   
   # Clone Droidrun
   git clone https://github.com/droidrun/framework.git
   cd framework
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Register on Mobilerun Cloud**
   - Visit https://mobilerun.ai
   - Create account
   - Get API credentials (you'll need these for Round 2)

3. **Star Droidrun on GitHub** (Mandatory)
   - Go to https://github.com/droidrun/framework
   - Click ⭐ Star button

#### Option B: Quick Start (Testing Only)

```bash
# Just install Python dependencies
pip install requests pandas scikit-learn sqlite3
```

### Step 3: Clone Project Repository

```bash
# Navigate to workspace
cd ~/droidrun-workspace

# Clone this project
git clone https://github.com/yourusername/smart-expense-manager-agent.git
cd smart-expense-manager-agent

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Setup Android Development Environment

#### A. Install Android Studio

1. Download from https://developer.android.com/studio
2. Follow installation wizard
3. Open Android Studio

#### B. Install Android SDK

In Android Studio:
1. Go to **SDK Manager** (Tools → SDK Manager)
2. Install:
   - Android API 33+ (latest stable)
   - Android Build Tools 33.0.0+
   - Android SDK Platform Tools
   - Android Emulator
   - Intel HAXM (for x86 emulation)

#### C. Create Android Emulator

```bash
# List available system images
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --list

# Create emulator
$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd \
  -n "DroidrunEmulator" \
  -k "system-images;android;33;google_apis" \
  -d "pixel_3a"

# Start emulator
$ANDROID_HOME/emulator/emulator -avd DroidrunEmulator
```

### Step 5: Verify Installation

```bash
# Test Python setup
python --version
# Should output: Python 3.8+

# Test Droidrun
python -c "import droidrun; print('✅ Droidrun ready')" || echo "⚠️ Droidrun not installed"

# Test Android SDK
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --version

# Test emulator is running
adb devices
# Should list one emulator device
```

---

## 🏃 Running the Project

### Quick Start - Python Agent Demo

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run the agent demo
python droidrun_agent.py
```

**Expected Output:**
```
============================================================
🤖 SMART EXPENSE MANAGER AGENT - DEMO
============================================================
✅ Demo budgets created

[DEMO] Processing sample transactions...

--- Transaction 1 ---
[AGENT] Processing notification: {'text': '₹250 to Starbucks Coffee', 'app': 'Google Pay'}
✅ Transaction recorded:
   Amount: ₹250
   Merchant: Starbucks Coffee
   Category: Food & Dining (confidence: 100%)
   App: Google Pay

[... more transactions ...]

📊 DAILY EXPENSE SUMMARY - [Date]
============================================================
💰 Total Spent: ₹6200.00
📍 Transactions: 6

[... breakdown and analysis ...]
```

### Build Android App

```bash
# Navigate to android directory
cd android

# Build APK
./gradlew build

# Or use Android Studio
# 1. Open Android Studio
# 2. File → Open → Select 'android' folder
# 3. Click Build → Build APK
```

### Deploy to Emulator

```bash
# Build and install
./gradlew installDebug

# Or use Android Studio
# 1. Click Run (or Shift + F10)
# 2. Select emulator
# 3. App will install and launch
```

### Deploy to Physical Device

```bash
# Enable USB debugging on device
# Settings → Developer Options → USB Debugging (ON)

# Connect device via USB

# Verify device connected
adb devices

# Build and install
./gradlew installDebug

# Or in Android Studio: Run → Select physical device
```

---

## 📊 Project Structure

```
smart-expense-manager-agent/
├── README.md                          # Project overview
├── SETUP_GUIDE.md                     # This file
├── requirements.txt                   # Python dependencies
├── droidrun_agent.py                  # Main Python agent
├── expense_processor.py               # Transaction processing
├── ml_categorizer.py                  # ML categorization
├── database.py                        # Database operations
├── config.json                        # Configuration
│
├── android/                           # Android app
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/
│   │   │   │   └── com/example/expensemanager/
│   │   │   │       ├── MainActivity.kt
│   │   │   │       ├── ExpenseAgentEngine.kt
│   │   │   │       ├── ExpenseDatabase.kt
│   │   │   │       └── NotificationListener.kt
│   │   │   └── res/
│   │   │       └── layout/
│   │   │           └── activity_main.xml
│   │   ├── build.gradle
│   │   └── AndroidManifest.xml
│   ├── build.gradle
│   ├── settings.gradle
│   └── gradle/
│
├── tests/                             # Test files
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_categorizer.py
│   └── test_database.py
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── CONTRIBUTING.md
│   └── TROUBLESHOOTING.md
│
└── .github/
    ├── workflows/
    │   └── ci.yml                     # CI/CD workflow
    └── ISSUE_TEMPLATE.md
```

---

## ✅ Testing the Application

### Run Unit Tests

```bash
# Install testing dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=. tests/

# Run specific test
pytest tests/test_agent.py::TestAgentInit
```

### Manual Testing Checklist

- [ ] Python agent runs without errors
- [ ] Database creates correctly
- [ ] Sample transactions process successfully
- [ ] Categories are assigned correctly
- [ ] Budget alerts trigger properly
- [ ] Daily summary generates
- [ ] Android app compiles
- [ ] Android app installs on emulator
- [ ] Notification processing works
- [ ] UI updates correctly

---

## 🐛 Troubleshooting

### Python Issues

**Error: `ModuleNotFoundError: No module named 'sqlite3'`**
```bash
# Reinstall Python development headers
# macOS
brew reinstall python@3.8

# Ubuntu/Debian
sudo apt-get install python3.8-dev

# Reinstall virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Error: `Permission denied` on Linux/macOS**
```bash
# Make script executable
chmod +x droidrun_agent.py
```

### Android Issues

**Error: `sdkmanager: command not found`**
```bash
# Set ANDROID_HOME environment variable
# macOS/Linux - add to ~/.bashrc or ~/.zshrc
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin

# Then reload
source ~/.bashrc  # or ~/.zshrc
```

**Error: `Emulator not starting`**
```bash
# Check if HAXM is installed and enabled
# macOS: System Preferences → Security & Privacy → Allow Intel HAXM

# Or use ARM-based system image (slower but no HAXM needed)
sdkmanager "system-images;android;33;google_apis_playstore;arm64-v8a"
avdmanager create avd -n "ARMEmulator" -k "system-images;android;33;google_apis_playstore;arm64-v8a"
```

**Error: `Build failed: SDK not found`**
```bash
# Ensure Android SDK is set correctly in Android Studio
# File → Project Structure → SDK Location
# Set Android SDK location
```

### Droidrun Issues

**Error: `Droidrun framework not found`**
```bash
# Make sure you've cloned and installed Droidrun
cd ~/droidrun-workspace/framework
pip install -e .
```

---

## 📱 Running on Different Platforms

### Windows Users

1. **Install Visual C++ Build Tools**
   ```bash
   # Download from Microsoft website
   # Or use chocolatey
   choco install microsoft-visual-cpp-build-tools
   ```

2. **Set Environment Variables**
   - Right-click Computer → Properties → Advanced System Settings
   - Click "Environment Variables"
   - Add `ANDROID_HOME` = `C:\Users\YourUsername\AppData\Local\Android\Sdk`
   - Add `Path` entry for Android tools

3. **Use PowerShell or Git Bash** (not CMD)
   ```powershell
   # In PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

### macOS Users

1. **Update Xcode Command Line Tools**
   ```bash
   xcode-select --install
   ```

2. **Use Homebrew for easier installation**
   ```bash
   brew install python@3.8 android-platform-tools
   ```

### Linux Users

1. **Install development packages**
   ```bash
   sudo apt-get install build-essential python3-dev libssl-dev
   ```

2. **Use snap for Android Studio** (optional)
   ```bash
   sudo snap install android-studio --classic
   ```

---

## 🎯 Next Steps After Setup

1. **Understand the Code**
   - Read `README.md` for project overview
   - Review `droidrun_agent.py` - main agent logic
   - Check `docs/ARCHITECTURE.md` for system design

2. **Run the Demo**
   - Execute `python droidrun_agent.py`
   - Observe sample transaction processing
   - Check generated reports

3. **Customize for Your Use Case**
   - Modify categories in `ml_categorizer.py`
   - Adjust budgets in `config.json`
   - Add new automation workflows

4. **Develop the Android App**
   - Build APK with Android Studio
   - Test on emulator or device
   - Integrate with Droidrun framework

5. **Create Your Demo**
   - Record demo video (1-3 minutes)
   - Capture agent processing transactions
   - Show generated summaries and alerts

6. **Prepare for Submission**
   - Ensure GitHub repository is public
   - Create comprehensive README
   - Add demo video link to README
   - Test everything works from fresh clone

---

## 📚 Additional Resources

- **Droidrun Documentation:** https://docs.droidrun.ai
- **Android Documentation:** https://developer.android.com/docs
- **Python Packaging:** https://packaging.python.org/
- **SQLite Tutorial:** https://www.sqlitetutorial.net/
- **Git Guide:** https://git-scm.com/doc

---

## 🤝 Getting Help

- **Discord:** Join #hackathon-help channel
- **GitHub Issues:** Open issue in repository
- **Stack Overflow:** Tag with `droidrun`, `android`, `python`
- **Droidrun Support:** Visit https://github.com/droidrun/framework/discussions

---

## ✨ Tips for Success

1. ✅ **Test continuously** - Run demo frequently
2. ✅ **Keep code clean** - Use consistent style
3. ✅ **Document well** - Clear comments help judges
4. ✅ **Version control** - Commit often with meaningful messages
5. ✅ **Record early** - Don't wait until deadline for demo video
6. ✅ **Get feedback** - Share with team/friends for review
7. ✅ **Follow requirements** - Check all submission guidelines
8. ✅ **Have fun!** - This is meant to be enjoyable

---

**Good Luck! 🚀**

*Last Updated: January 2026*
