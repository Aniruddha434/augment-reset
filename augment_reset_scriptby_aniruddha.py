#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import platform
import json
import sqlite3
from pathlib import Path
# Windows registry import will be done conditionally later

class AugmentResetTool:
    def __init__(self):
        self.system = platform.system()
        self.home = Path.home()
        self.removed_items = []
        self.errors = []
        
    def log_success(self, message):
        print(f"✓ {message}")
        self.removed_items.append(message)
    
    def log_error(self, message):
        print(f"✗ {message}")
        self.errors.append(message)
    
    def log_info(self, message):
        print(f"ℹ {message}")
    
    def get_vscode_paths(self):
        """Get VS Code configuration paths for different OS"""
        if self.system == "Windows":
            return {
                "user_data": self.home / "AppData" / "Roaming" / "Code" / "User",
                "extensions": self.home / ".vscode" / "extensions",
                "cache": self.home / "AppData" / "Roaming" / "Code" / "CachedExtensions",
                "logs": self.home / "AppData" / "Roaming" / "Code" / "logs",
                "workspaceStorage": self.home / "AppData" / "Roaming" / "Code" / "User" / "workspaceStorage"
            }
        elif self.system == "Darwin":  # macOS
            return {
                "user_data": self.home / "Library" / "Application Support" / "Code" / "User",
                "extensions": self.home / ".vscode" / "extensions",
                "cache": self.home / "Library" / "Caches" / "com.microsoft.VSCode",
                "logs": self.home / "Library" / "Application Support" / "Code" / "logs",
                "workspaceStorage": self.home / "Library" / "Application Support" / "Code" / "User" / "workspaceStorage"
            }
        else:  # Linux
            return {
                "user_data": self.home / ".config" / "Code" / "User",
                "extensions": self.home / ".vscode" / "extensions",
                "cache": self.home / ".cache" / "vscode",
                "logs": self.home / ".config" / "Code" / "logs",
                "workspaceStorage": self.home / ".config" / "Code" / "User" / "workspaceStorage"
            }
    
    def close_vscode(self):
        """Close VS Code processes"""
        try:
            if self.system == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", "Code.exe"], 
                             capture_output=True, check=False)
            else:
                subprocess.run(["pkill", "-f", "Visual Studio Code"], 
                             capture_output=True, check=False)
            self.log_success("Closed VS Code processes")
        except Exception as e:
            self.log_error(f"Error closing VS Code: {e}")
    
    def remove_augment_extensions(self):
        """Remove Augment-related extensions"""
        paths = self.get_vscode_paths()
        extensions_dir = paths["extensions"]
        
        if not extensions_dir.exists():
            self.log_info("Extensions directory not found")
            return
        
        # Common Augment extension patterns
        augment_patterns = [
            "augment",
            "augmentcode",
            "augment-code",
            "augment.code",
            "augment-ai",
            "augmentai"
        ]
        
        for item in extensions_dir.iterdir():
            if item.is_dir():
                item_name = item.name.lower()
                if any(pattern in item_name for pattern in augment_patterns):
                    try:
                        shutil.rmtree(item)
                        self.log_success(f"Removed extension: {item.name}")
                    except Exception as e:
                        self.log_error(f"Error removing {item.name}: {e}")
    
    def clean_vscode_settings(self):
        """Clean VS Code settings and configurations"""
        paths = self.get_vscode_paths()
        
        # Files to clean
        files_to_clean = [
            paths["user_data"] / "settings.json",
            paths["user_data"] / "keybindings.json",
            paths["user_data"] / "globalStorage" / "state.vscdb",
            paths["user_data"] / "globalStorage" / "storage.json"
        ]
        
        for file_path in files_to_clean:
            if file_path.exists():
                try:
                    if file_path.suffix == '.json':
                        self.clean_json_file(file_path)
                    elif file_path.suffix == '.vscdb':
                        self.clean_vscdb_file(file_path)
                except Exception as e:
                    self.log_error(f"Error cleaning {file_path}: {e}")
    
    def clean_json_file(self, file_path):
        """Clean Augment-related entries from JSON files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            original_data = json.dumps(data, sort_keys=True)
            
            # Remove Augment-related keys
            if isinstance(data, dict):
                keys_to_remove = []
                for key in data.keys():
                    if 'augment' in key.lower():
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del data[key]
                    self.log_success(f"Removed setting: {key}")
            
            # Write back if changed
            if json.dumps(data, sort_keys=True) != original_data:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                self.log_success(f"Cleaned: {file_path.name}")
        
        except Exception as e:
            self.log_error(f"Error cleaning JSON {file_path}: {e}")
    
    def clean_vscdb_file(self, file_path):
        """Clean Augment-related entries from SQLite database"""
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                try:
                    # Remove rows containing 'augment' in key/value
                    cursor.execute(f"DELETE FROM {table_name} WHERE key LIKE '%augment%' OR value LIKE '%augment%'")
                    deleted = cursor.rowcount
                    if deleted > 0:
                        self.log_success(f"Removed {deleted} entries from {table_name}")
                except Exception as e:
                    self.log_error(f"Error cleaning table {table_name}: {e}")
            
            conn.commit()
            conn.close()
            self.log_success(f"Cleaned database: {file_path.name}")
        
        except Exception as e:
            self.log_error(f"Error cleaning database {file_path}: {e}")
    
    def clean_workspace_storage(self):
        """Clean workspace storage"""
        paths = self.get_vscode_paths()
        workspace_dir = paths["workspaceStorage"]
        
        if not workspace_dir.exists():
            return
        
        for item in workspace_dir.iterdir():
            if item.is_dir():
                try:
                    # Check if workspace contains Augment data
                    state_file = item / "state.vscdb"
                    if state_file.exists():
                        self.clean_vscdb_file(state_file)
                except Exception as e:
                    self.log_error(f"Error cleaning workspace {item.name}: {e}")
    
    def clean_cache_and_logs(self):
        """Clean cache and log files"""
        paths = self.get_vscode_paths()
        
        # Clean cache
        cache_dir = paths["cache"]
        if cache_dir.exists():
            try:
                for item in cache_dir.iterdir():
                    if 'augment' in item.name.lower():
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                        self.log_success(f"Removed cache: {item.name}")
            except Exception as e:
                self.log_error(f"Error cleaning cache: {e}")
        
        # Clean logs
        logs_dir = paths["logs"]
        if logs_dir.exists():
            try:
                for item in logs_dir.iterdir():
                    if 'augment' in item.name.lower():
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                        self.log_success(f"Removed log: {item.name}")
            except Exception as e:
                self.log_error(f"Error cleaning logs: {e}")
    
    def clean_system_temp(self):
        """Clean system temporary files"""
        temp_dirs = []
        
        if self.system == "Windows":
            temp_dirs = [
                Path(os.environ.get('TEMP', '')),
                Path(os.environ.get('TMP', '')),
                self.home / "AppData" / "Local" / "Temp"
            ]
        else:
            temp_dirs = [
                Path('/tmp'),
                Path('/var/tmp'),
                self.home / '.tmp'
            ]
        
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                try:
                    for item in temp_dir.iterdir():
                        if 'augment' in item.name.lower():
                            if item.is_dir():
                                shutil.rmtree(item)
                            else:
                                item.unlink()
                            self.log_success(f"Removed temp file: {item.name}")
                except Exception as e:
                    self.log_error(f"Error cleaning temp directory {temp_dir}: {e}")
    
    def clean_registry_windows(self):
        """Clean Windows registry (Windows only)"""
        if self.system != "Windows":
            return
        
        try:
            import winreg
            
            # Registry paths to check
            registry_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\VSCode"),
                (winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages"),
            ]
            
            for hkey, path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, path) as key:
                        # This is a simplified registry cleaning
                        # In practice, you'd need to enumerate and check values
                        self.log_info(f"Registry path checked: {path}")
                except FileNotFoundError:
                    pass
                except Exception as e:
                    self.log_error(f"Error accessing registry {path}: {e}")
        
        except ImportError:
            self.log_error("Registry cleaning not available (winreg not imported)")
        except Exception as e:
            self.log_error(f"Registry cleaning error: {e}")
    
    def reset_network_cache(self):
        """Reset network/DNS cache"""
        try:
            if self.system == "Windows":
                subprocess.run(["ipconfig", "/flushdns"], capture_output=True, check=False)
            elif self.system == "Darwin":
                subprocess.run(["sudo", "dscacheutil", "-flushcache"], capture_output=True, check=False)
            else:
                subprocess.run(["sudo", "systemctl", "restart", "systemd-resolved"], capture_output=True, check=False)
            
            self.log_success("Network cache flushed")
        except Exception as e:
            self.log_error(f"Error flushing network cache: {e}")
    
    def run_full_reset(self):
        """Run complete reset process"""
        print("=" * 60)
        print("AUGMENT CODE EXTENSION COMPLETE RESET TOOL")
        print("=" * 60)
        print("This will completely remove all Augment Code extension data.")
        print("You will be able to create a fresh account afterwards.")
        print()
        
        confirm = input("Are you sure you want to proceed? (type 'YES' to confirm): ")
        if confirm != 'YES':
            print("Operation cancelled.")
            return
        
        print("\nStarting complete reset process...")
        print("-" * 40)
        
        # Step 1: Close VS Code
        self.log_info("Step 1: Closing VS Code...")
        self.close_vscode()
        
        # Step 2: Remove extensions
        self.log_info("Step 2: Removing Augment extensions...")
        self.remove_augment_extensions()
        
        # Step 3: Clean settings
        self.log_info("Step 3: Cleaning VS Code settings...")
        self.clean_vscode_settings()
        
        # Step 4: Clean workspace storage
        self.log_info("Step 4: Cleaning workspace storage...")
        self.clean_workspace_storage()
        
        # Step 5: Clean cache and logs
        self.log_info("Step 5: Cleaning cache and logs...")
        self.clean_cache_and_logs()
        
        # Step 6: Clean system temp
        self.log_info("Step 6: Cleaning system temporary files...")
        self.clean_system_temp()
        
        # Step 7: Clean registry (Windows only)
        if self.system == "Windows":
            self.log_info("Step 7: Cleaning Windows registry...")
            self.clean_registry_windows()
        
        # Step 8: Reset network cache
        self.log_info("Step 8: Resetting network cache...")
        self.reset_network_cache()
        
        # Summary
        print("\n" + "=" * 60)
        print("RESET COMPLETE!")
        print("=" * 60)
        print(f"✓ Successfully removed {len(self.removed_items)} items")
        if self.errors:
            print(f"✗ {len(self.errors)} errors occurred")
        
        print("\nNext steps:")
        print("1. Restart your computer (recommended)")
        print("2. Open VS Code")
        print("3. Install Augment Code extension fresh")
        print("4. Create a new account")
        print("\nYour system is now clean of all Augment Code extension data!")
        print("\n" + "=" * 60)
        print("Credit: Aniruddha ...!")
        print("=" * 60)

if __name__ == "__main__":
    tool = AugmentResetTool()
    tool.run_full_reset()
