#!/usr/bin/env python3
"""
Setup Build Tools untuk Compilation Research
Automated installation PyInstaller, Nuitka, dan UPX
"""

import subprocess
import sys
import os
import platform
import requests
import zipfile
import tarfile
from pathlib import Path
import shutil
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SETUP - %(message)s')

class BuildToolsSetup:
    """
    Automated setup untuk build tools yang diperlukan
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()
        self.python_executable = sys.executable
        
        # Directories
        self.tools_dir = Path.cwd() / "build_tools"
        self.tools_dir.mkdir(exist_ok=True)
        
        logging.info(f"🔧 Build tools setup initialized")
        logging.info(f"💻 Platform: {platform.platform()}")
        logging.info(f"🐍 Python: {sys.version}")
    
    def check_current_installations(self):
        """Check current installations dari build tools"""
        logging.info("🔍 Checking current installations...")
        
        status = {
            'python': True,  # Already running Python
            'pip': False,
            'pyinstaller': False,
            'nuitka': False,
            'upx': False
        }
        
        # Check pip
        try:
            result = subprocess.run([self.python_executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                status['pip'] = True
                logging.info(f"✅ pip: {result.stdout.strip()}")
        except Exception:
            logging.warning("❌ pip not available")
        
        # Check PyInstaller
        try:
            result = subprocess.run([self.python_executable, '-m', 'PyInstaller', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                status['pyinstaller'] = True
                logging.info(f"✅ PyInstaller: {result.stdout.strip()}")
        except Exception:
            try:
                result = subprocess.run(['pyinstaller', '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    status['pyinstaller'] = True
                    logging.info(f"✅ PyInstaller: {result.stdout.strip()}")
            except Exception:
                logging.info("⚪ PyInstaller not installed")
        
        # Check Nuitka
        try:
            result = subprocess.run([self.python_executable, '-m', 'nuitka', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                status['nuitka'] = True
                logging.info(f"✅ Nuitka: {result.stdout.strip()}")
        except Exception:
            logging.info("⚪ Nuitka not installed")
        
        # Check UPX
        try:
            result = subprocess.run(['upx', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                status['upx'] = True
                version_line = result.stdout.split('\n')[0]
                logging.info(f"✅ UPX: {version_line}")
        except Exception:
            logging.info("⚪ UPX not installed")
        
        return status
    
    def install_python_packages(self):
        """Install PyInstaller dan Nuitka via pip"""
        logging.info("📦 Installing Python packages...")
        
        packages = [
            'pyinstaller>=5.0',
            'nuitka>=1.8',
            'setuptools',
            'wheel',
            'pynput',
            'psutil',
            'cryptography',
            'pillow',
            'requests',
            'dnspython'
        ]
        
        # Add Windows-specific packages
        if self.platform == 'windows':
            packages.extend(['wmi', 'pywin32'])
        
        success_count = 0
        
        for package in packages:
            try:
                logging.info(f"📦 Installing {package}...")
                result = subprocess.run([
                    self.python_executable, '-m', 'pip', 'install', 
                    '--upgrade', package
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logging.info(f"✅ Successfully installed {package}")
                    success_count += 1
                else:
                    logging.warning(f"⚠️ Failed to install {package}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logging.warning(f"⚠️ Timeout installing {package}")
            except Exception as e:
                logging.warning(f"⚠️ Error installing {package}: {e}")
        
        logging.info(f"📊 Installed {success_count}/{len(packages)} packages")
        return success_count == len(packages)
    
    def download_file(self, url, destination):
        """Download file dengan progress tracking"""
        try:
            logging.info(f"⬇️ Downloading {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Every MB
                                logging.info(f"📊 Progress: {progress:.1f}%")
            
            logging.info(f"✅ Downloaded: {destination}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Download failed: {e}")
            return False
    
    def install_upx(self):
        """Install UPX berdasarkan platform"""
        logging.info("📦 Installing UPX...")
        
        upx_dir = self.tools_dir / "upx"
        upx_dir.mkdir(exist_ok=True)
        
        if self.platform == 'windows':
            return self.install_upx_windows(upx_dir)
        elif self.platform == 'linux':
            return self.install_upx_linux(upx_dir)
        elif self.platform == 'darwin':  # macOS
            return self.install_upx_macos(upx_dir)
        else:
            logging.error(f"❌ Unsupported platform: {self.platform}")
            return False
    
    def install_upx_windows(self, upx_dir):
        """Install UPX untuk Windows"""
        try:
            # UPX download URL untuk Windows
            if '64' in self.arch or 'amd64' in self.arch:
                upx_url = "https://github.com/upx/upx/releases/download/v4.2.1/upx-4.2.1-win64.zip"
                upx_filename = "upx-4.2.1-win64.zip"
                upx_folder = "upx-4.2.1-win64"
            else:
                upx_url = "https://github.com/upx/upx/releases/download/v4.2.1/upx-4.2.1-win32.zip"
                upx_filename = "upx-4.2.1-win32.zip"
                upx_folder = "upx-4.2.1-win32"
            
            upx_zip_path = upx_dir / upx_filename
            
            # Download UPX
            if not self.download_file(upx_url, upx_zip_path):
                return False
            
            # Extract ZIP
            with zipfile.ZipFile(upx_zip_path, 'r') as zip_ref:
                zip_ref.extractall(upx_dir)
            
            # Move executable ke tools directory
            upx_exe_src = upx_dir / upx_folder / "upx.exe"
            upx_exe_dst = upx_dir / "upx.exe"
            
            if upx_exe_src.exists():
                shutil.move(str(upx_exe_src), str(upx_exe_dst))
                
                # Add to PATH untuk current session
                current_path = os.environ.get('PATH', '')
                if str(upx_dir) not in current_path:
                    os.environ['PATH'] = f"{upx_dir};{current_path}"
                
                logging.info(f"✅ UPX installed: {upx_exe_dst}")
                
                # Test installation
                result = subprocess.run([str(upx_exe_dst), '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logging.info("✅ UPX installation verified")
                    return True
                else:
                    logging.error("❌ UPX verification failed")
                    return False
            else:
                logging.error(f"❌ UPX executable not found: {upx_exe_src}")
                return False
                
        except Exception as e:
            logging.error(f"❌ UPX Windows installation failed: {e}")
            return False
    
    def install_upx_linux(self, upx_dir):
        """Install UPX untuk Linux"""
        try:
            # Try package manager first
            package_managers = [
                ['apt', 'install', '-y', 'upx'],
                ['yum', 'install', '-y', 'upx'],
                ['dnf', 'install', '-y', 'upx'],
                ['pacman', '-S', '--noconfirm', 'upx']
            ]
            
            for pm_cmd in package_managers:
                try:
                    result = subprocess.run(['sudo'] + pm_cmd, 
                                          capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        logging.info(f"✅ UPX installed via {pm_cmd[0]}")
                        return True
                except Exception:
                    continue
            
            # Fallback to manual installation
            upx_url = "https://github.com/upx/upx/releases/download/v4.2.1/upx-4.2.1-amd64_linux.tar.xz"
            upx_filename = "upx-4.2.1-amd64_linux.tar.xz"
            upx_folder = "upx-4.2.1-amd64_linux"
            
            upx_tar_path = upx_dir / upx_filename
            
            if not self.download_file(upx_url, upx_tar_path):
                return False
            
            # Extract tar.xz
            with tarfile.open(upx_tar_path, 'r:xz') as tar_ref:
                tar_ref.extractall(upx_dir)
            
            # Move executable
            upx_exe_src = upx_dir / upx_folder / "upx"
            upx_exe_dst = upx_dir / "upx"
            
            if upx_exe_src.exists():
                shutil.move(str(upx_exe_src), str(upx_exe_dst))
                os.chmod(upx_exe_dst, 0o755)  # Make executable
                
                # Add to PATH
                current_path = os.environ.get('PATH', '')
                if str(upx_dir) not in current_path:
                    os.environ['PATH'] = f"{upx_dir}:{current_path}"
                
                logging.info(f"✅ UPX installed: {upx_exe_dst}")
                return True
            else:
                logging.error(f"❌ UPX executable not found: {upx_exe_src}")
                return False
                
        except Exception as e:
            logging.error(f"❌ UPX Linux installation failed: {e}")
            return False
    
    def install_upx_macos(self, upx_dir):
        """Install UPX untuk macOS"""
        try:
            # Try Homebrew first
            try:
                result = subprocess.run(['brew', 'install', 'upx'], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    logging.info("✅ UPX installed via Homebrew")
                    return True
            except Exception:
                pass
            
            # Fallback to manual installation
            upx_url = "https://github.com/upx/upx/releases/download/v4.2.1/upx-4.2.1-amd64_macos.tar.xz"
            upx_filename = "upx-4.2.1-amd64_macos.tar.xz"
            upx_folder = "upx-4.2.1-amd64_macos"
            
            upx_tar_path = upx_dir / upx_filename
            
            if not self.download_file(upx_url, upx_tar_path):
                return False
            
            # Extract tar.xz
            with tarfile.open(upx_tar_path, 'r:xz') as tar_ref:
                tar_ref.extractall(upx_dir)
            
            # Move executable
            upx_exe_src = upx_dir / upx_folder / "upx"
            upx_exe_dst = upx_dir / "upx"
            
            if upx_exe_src.exists():
                shutil.move(str(upx_exe_src), str(upx_exe_dst))
                os.chmod(upx_exe_dst, 0o755)  # Make executable
                
                # Add to PATH
                current_path = os.environ.get('PATH', '')
                if str(upx_dir) not in current_path:
                    os.environ['PATH'] = f"{upx_dir}:{current_path}"
                
                logging.info(f"✅ UPX installed: {upx_exe_dst}")
                return True
            else:
                logging.error(f"❌ UPX executable not found: {upx_exe_src}")
                return False
                
        except Exception as e:
            logging.error(f"❌ UPX macOS installation failed: {e}")
            return False
    
    def verify_installations(self):
        """Verify all installations setelah setup"""
        logging.info("🔍 Verifying installations...")
        
        verifications = []
        
        # Verify PyInstaller
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                verifications.append(('PyInstaller', True, result.stdout.strip()))
            else:
                verifications.append(('PyInstaller', False, 'Command failed'))
        except Exception as e:
            verifications.append(('PyInstaller', False, str(e)))
        
        # Verify Nuitka
        try:
            result = subprocess.run([self.python_executable, '-m', 'nuitka', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                verifications.append(('Nuitka', True, result.stdout.strip()))
            else:
                verifications.append(('Nuitka', False, 'Command failed'))
        except Exception as e:
            verifications.append(('Nuitka', False, str(e)))
        
        # Verify UPX
        try:
            upx_exe = self.tools_dir / "upx" / ("upx.exe" if self.platform == 'windows' else "upx")
            if upx_exe.exists():
                result = subprocess.run([str(upx_exe), '--version'], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(['upx', '--version'], 
                                      capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                verifications.append(('UPX', True, version_line))
            else:
                verifications.append(('UPX', False, 'Command failed'))
        except Exception as e:
            verifications.append(('UPX', False, str(e)))
        
        # Print verification results
        print("\n" + "="*60)
        print("🔍 INSTALLATION VERIFICATION RESULTS")
        print("="*60)
        
        success_count = 0
        for tool, success, details in verifications:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {tool:12} - {details}")
            if success:
                success_count += 1
        
        print(f"\n📊 Success Rate: {success_count}/{len(verifications)} tools verified")
        
        return success_count == len(verifications)
    
    def create_build_script(self):
        """Create convenience build script"""
        script_content = f'''#!/usr/bin/env python3
"""
Convenience build script untuk research
Auto-generated pada {logging.time.strftime('%Y-%m-%d %H:%M:%S')}
"""

import subprocess
import sys
from pathlib import Path

def build_with_pyinstaller():
    """Quick build dengan PyInstaller"""
    cmd = [
        'pyinstaller',
        '--onefile',
        '--noconsole',
        '--name=SystemProcess',
        'agent_improved.py'
    ]
    
    print("🔨 Building dengan PyInstaller...")
    result = subprocess.run(cmd)
    return result.returncode == 0

def build_with_nuitka():
    """Quick build dengan Nuitka"""
    cmd = [
        '{self.python_executable}', '-m', 'nuitka',
        '--standalone',
        '--onefile',
        '--assume-yes-for-downloads',
        '--output-filename=AdvancedProcess.exe',
        'agent_improved.py'
    ]
    
    print("🔨 Building dengan Nuitka...")
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    print("🛠️ Quick Build Script")
    print("1. PyInstaller build")
    print("2. Nuitka build")
    print("3. Comprehensive comparison")
    
    choice = input("Select option (1-3): ")
    
    if choice == "1":
        build_with_pyinstaller()
    elif choice == "2":
        build_with_nuitka()
    elif choice == "3":
        # Run comprehensive comparison
        subprocess.run(['{self.python_executable}', 'build_comparison.py'])
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
'''
        
        script_path = Path.cwd() / "quick_build.py"
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            if self.platform != 'windows':
                os.chmod(script_path, 0o755)  # Make executable
            
            logging.info(f"📝 Build script created: {script_path}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to create build script: {e}")
            return False
    
    def comprehensive_setup(self):
        """Run comprehensive setup process"""
        print("\n" + "="*60)
        print("🔧 BUILD TOOLS COMPREHENSIVE SETUP")
        print("="*60)
        print("🎓 Academic Research: Malware Analysis S2")
        print("🛠️ Installing: PyInstaller, Nuitka, UPX")
        print("="*60)
        
        # Step 1: Check current status
        print("\n🔍 Step 1: Checking Current Installations")
        current_status = self.check_current_installations()
        
        # Step 2: Install Python packages
        print("\n📦 Step 2: Installing Python Packages")
        python_success = self.install_python_packages()
        
        # Step 3: Install UPX
        print("\n📦 Step 3: Installing UPX")
        upx_success = self.install_upx()
        
        # Step 4: Verify installations
        print("\n🔍 Step 4: Verifying Installations")
        verification_success = self.verify_installations()
        
        # Step 5: Create convenience scripts
        print("\n📝 Step 5: Creating Build Scripts")
        script_success = self.create_build_script()
        
        # Summary
        print("\n" + "="*60)
        print("📊 SETUP SUMMARY")
        print("="*60)
        
        steps = [
            ("Python Packages", python_success),
            ("UPX Installation", upx_success),
            ("Verification", verification_success),
            ("Build Scripts", script_success)
        ]
        
        success_count = 0
        for step_name, success in steps:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{status} {step_name}")
            if success:
                success_count += 1
        
        overall_success = success_count == len(steps)
        
        if overall_success:
            print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
            print("🚀 Ready untuk build comparison research!")
            print("\n📋 Next Steps:")
            print("1. Run: python build_comparison.py")
            print("2. Or use: python quick_build.py")
            print("3. Check builds/ directory untuk outputs")
        else:
            print("\n⚠️ SETUP COMPLETED WITH ISSUES")
            print("🔍 Review failed steps above")
            print("💡 You may need to install some tools manually")
        
        return overall_success

def main():
    """Main function untuk setup"""
    print("🎓 BUILD TOOLS SETUP - MALWARE RESEARCH S2")
    print("=" * 50)
    print("⚠️  FOR ACADEMIC RESEARCH PURPOSES ONLY")
    print("📚 Installing PyInstaller, Nuitka, dan UPX")
    print("=" * 50)
    
    # Confirm academic purpose
    confirm = input("\n❓ Confirm academic research purpose (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Academic confirmation required")
        return
    
    # Initialize dan run setup
    try:
        setup = BuildToolsSetup()
        success = setup.comprehensive_setup()
        
        if success:
            print("\n✅ All tools ready untuk research!")
        else:
            print("\n❌ Setup completed dengan issues")
            
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        logging.error(f"Setup failed: {e}")

if __name__ == "__main__":
    main()
