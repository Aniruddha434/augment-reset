# Augment Code Extension Reset Tool

A Python script to completely reset and clean all Augment Code extension data from VS Code, allowing you to start fresh with a new account.

## 🚀 Features

- **Complete Extension Removal** - Removes all Augment-related extensions
- **Settings Cleanup** - Cleans configuration files and user settings
- **Cache & Storage Reset** - Clears all cached data and workspace storage
- **Registry Cleaning** - Cleans Windows registry entries (Windows only)
- **Cross-Platform Support** - Works on Windows, macOS, and Linux

## 📋 Requirements

- Python 3.6+
- Administrator/Root privileges
- VS Code installed

## 🚀 Usage

### Windows (Run as Administrator)
```cmd
python reset_augment.py
```

### macOS/Linux
```bash
sudo python3 reset_augment.py
```

**Steps:**
1. Close VS Code
2. Run the script with admin privileges
3. Type `YES` when prompted
4. Wait for completion
5. Restart computer (recommended)

## 📁 What Gets Removed

- ✅ Augment Code extensions
- ✅ VS Code settings (Augment-related)
- ✅ Cache files and logs
- ✅ Workspace storage
- ✅ Temporary files
- ✅ Registry entries (Windows)

## 🔄 After Reset

1. Restart your computer
2. Open VS Code
3. Install Augment Code extension fresh
4. Create new account

## ⚠️ Important Notes

- **Backup Important Data** - This permanently removes data
- **Administrator Rights Required** - Needed for complete cleanup
- **VS Code Will Be Closed** - Save your work first

## 🐛 Troubleshooting

- Ensure Python is installed: `python --version`
- Run with administrator privileges
- Manually close VS Code if needed

## 🏆 Credits

**Created by: Aniruddha ...!**

## 📝 License

MIT License - Use at your own risk. Always backup important data before running cleanup scripts.
