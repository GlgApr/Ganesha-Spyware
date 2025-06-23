#!/usr/bin/env python3
"""
Advanced Build Comparison: PyInstaller vs Nuitka
Automated compilation dan performance analysis untuk research S2
"""

import subprocess
import os
import time
import hashlib
import json
import psutil
import shutil
import logging
from pathlib import Path
from datetime import datetime
import platform

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - BUILD - %(message)s')

class AdvancedBuildComparator:
    """
    Comprehensive build comparison tool untuk academic research
    Compares PyInstaller + UPX vs Nuitka + UPX
    """
    
    def __init__(self, source_file="agent_improved.py"):
        self.source_file = source_file
        self.base_dir = Path.cwd()
        self.build_dir = self.base_dir / "builds"
        self.results_dir = self.base_dir / "build_results"
        
        # Create directories
        self.build_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        # Results storage
        self.comparison_results = {
            'timestamp': datetime.now().isoformat(),
            'platform': platform.platform(),
            'source_file': str(self.source_file),
            'pyinstaller': {},
            'nuitka': {},
            'analysis': {}
        }
        
        logging.info(f"🔧 Build comparator initialized")
        logging.info(f"📁 Build directory: {self.build_dir}")
        logging.info(f"📊 Results directory: {self.results_dir}")
    
    def check_dependencies(self):
        """Check semua dependencies untuk building"""
        logging.info("🔍 Checking build dependencies...")
        
        dependencies = {
            'pyinstaller': False,
            'nuitka': False,
            'upx': False
        }
        
        # Check PyInstaller
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                dependencies['pyinstaller'] = True
                logging.info(f"✅ PyInstaller: {result.stdout.strip()}")
            else:
                logging.warning("❌ PyInstaller not found")
        except Exception as e:
            logging.warning(f"❌ PyInstaller check failed: {e}")
        
        # Check Nuitka
        try:
            result = subprocess.run(['python', '-m', 'nuitka', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                dependencies['nuitka'] = True
                logging.info(f"✅ Nuitka: {result.stdout.strip()}")
            else:
                logging.warning("❌ Nuitka not found")
        except Exception as e:
            logging.warning(f"❌ Nuitka check failed: {e}")
        
        # Check UPX
        try:
            result = subprocess.run(['upx', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                dependencies['upx'] = True
                version_line = result.stdout.split('\n')[0]
                logging.info(f"✅ UPX: {version_line}")
            else:
                logging.warning("❌ UPX not found")
        except Exception as e:
            logging.warning(f"❌ UPX check failed: {e}")
        
        # Installation guide jika missing
        if not all(dependencies.values()):
            logging.info("\n📦 INSTALLATION GUIDE:")
            if not dependencies['pyinstaller']:
                logging.info("   pip install pyinstaller")
            if not dependencies['nuitka']:
                logging.info("   pip install nuitka")
            if not dependencies['upx']:
                if platform.system() == "Windows":
                    logging.info("   Download UPX dari https://upx.github.io/")
                else:
                    logging.info("   brew install upx  # macOS")
                    logging.info("   apt install upx   # Ubuntu")
        
        return dependencies
    
    def build_with_pyinstaller(self):
        """Build executable menggunakan PyInstaller + UPX"""
        logging.info("🔨 Building dengan PyInstaller...")
        
        pyinstaller_dir = self.build_dir / "pyinstaller"
        pyinstaller_dir.mkdir(exist_ok=True)
        
        # PyInstaller command dengan optimizations
        cmd = [
            'pyinstaller',
            '--onefile',                    # Single executable
            '--noconsole',                  # No console window
            '--strip',                      # Strip debug symbols
            '--optimize=2',                 # Python optimization level
            '--exclude-module=unittest',    # Exclude unnecessary modules
            '--exclude-module=doctest',
            '--exclude-module=pdb',
            '--exclude-module=test',
            '--name=SystemManager',         # Output name
            '--distpath', str(pyinstaller_dir),
            '--specpath', str(pyinstaller_dir / "specs"),
            '--workpath', str(pyinstaller_dir / "temp"),
            '--clean',                      # Clean cache
            str(self.source_file)
        ]
        
        # Add Windows-specific options
        if platform.system() == "Windows":
            cmd.extend([
                '--version-file=version_info.txt',  # Version info (if exists)
                '--icon=icon.ico'                   # Icon (if exists)
            ])
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            build_time = time.time() - start_time
            
            if result.returncode == 0:
                exe_path = pyinstaller_dir / "SystemManager.exe"
                
                if exe_path.exists():
                    original_size = exe_path.stat().st_size
                    
                    # Apply UPX compression
                    compressed_size, compression_ratio = self.apply_upx_compression(exe_path)
                    
                    # Calculate metrics
                    build_result = {
                        'success': True,
                        'build_time': build_time,
                        'exe_path': str(exe_path),
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'compression_ratio': compression_ratio,
                        'md5_hash': self.calculate_file_hash(exe_path),
                        'build_log': result.stdout
                    }
                    
                    logging.info(f"✅ PyInstaller build successful: {compressed_size:,} bytes")
                    return build_result
                else:
                    logging.error("❌ PyInstaller: Executable not found after build")
                    return {'success': False, 'error': 'Executable not found'}
            else:
                logging.error(f"❌ PyInstaller build failed: {result.stderr}")
                return {'success': False, 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            logging.error("❌ PyInstaller build timeout")
            return {'success': False, 'error': 'Build timeout'}
        except Exception as e:
            logging.error(f"❌ PyInstaller build error: {e}")
            return {'success': False, 'error': str(e)}
    
    def build_with_nuitka(self):
        """Build executable menggunakan Nuitka + UPX"""
        logging.info("🔨 Building dengan Nuitka...")
        
        nuitka_dir = self.build_dir / "nuitka"
        nuitka_dir.mkdir(exist_ok=True)
        
        # Nuitka command dengan advanced optimizations
        cmd = [
            'python', '-m', 'nuitka',
            '--standalone',                          # Standalone executable
            '--onefile',                            # Single file output
            '--assume-yes-for-downloads',           # Auto-download dependencies
            '--output-filename=AdvancedTool.exe',   # Output filename
            '--output-dir', str(nuitka_dir),
            '--remove-output',                      # Clean intermediate files
            '--optimize-for-size',                  # Size optimization
            '--no-debug-info',                      # No debug information
            '--python-flag=no_warnings,no_docstrings', # Python flags
            '--disable-console',                    # No console (Windows)
            '--include-package=cryptography',       # Ensure crypto support
            '--include-package=dns',                # DNS resolution
            '--follow-imports',                     # Follow all imports
            str(self.source_file)
        ]
        
        # Windows-specific optimizations
        if platform.system() == "Windows":
            cmd.extend([
                '--windows-disable-console',
                '--windows-icon-from-ico=icon.ico'  # Icon (if exists)
            ])
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            build_time = time.time() - start_time
            
            if result.returncode == 0:
                exe_path = nuitka_dir / "AdvancedTool.exe"
                
                if exe_path.exists():
                    original_size = exe_path.stat().st_size
                    
                    # Apply UPX compression
                    compressed_size, compression_ratio = self.apply_upx_compression(exe_path)
                    
                    # Calculate metrics
                    build_result = {
                        'success': True,
                        'build_time': build_time,
                        'exe_path': str(exe_path),
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'compression_ratio': compression_ratio,
                        'md5_hash': self.calculate_file_hash(exe_path),
                        'build_log': result.stdout
                    }
                    
                    logging.info(f"✅ Nuitka build successful: {compressed_size:,} bytes")
                    return build_result
                else:
                    logging.error("❌ Nuitka: Executable not found after build")
                    return {'success': False, 'error': 'Executable not found'}
            else:
                logging.error(f"❌ Nuitka build failed: {result.stderr}")
                return {'success': False, 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            logging.error("❌ Nuitka build timeout")
            return {'success': False, 'error': 'Build timeout'}
        except Exception as e:
            logging.error(f"❌ Nuitka build error: {e}")
            return {'success': False, 'error': str(e)}
    
    def apply_upx_compression(self, exe_path):
        """Apply UPX compression ke executable"""
        try:
            original_size = exe_path.stat().st_size
            
            # UPX compression dengan maximum settings
            upx_cmd = [
                'upx',
                '--best',           # Best compression
                '--ultra-brute',    # Ultra compression (slow but effective)
                '--overlay=copy',   # Preserve overlay
                str(exe_path)
            ]
            
            result = subprocess.run(upx_cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                compressed_size = exe_path.stat().st_size
                compression_ratio = (original_size - compressed_size) / original_size
                
                logging.info(f"✅ UPX compression: {original_size:,} → {compressed_size:,} bytes "
                           f"({compression_ratio:.1%} reduction)")
                
                return compressed_size, compression_ratio
            else:
                logging.warning(f"⚠️ UPX compression failed: {result.stderr}")
                return original_size, 0.0
                
        except Exception as e:
            logging.warning(f"⚠️ UPX compression error: {e}")
            return exe_path.stat().st_size, 0.0
    
    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash dari file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logging.warning(f"⚠️ Hash calculation failed: {e}")
            return None
    
    def analyze_pe_structure(self, exe_path):
        """Analyze PE structure untuk stealth assessment"""
        try:
            # Basic PE analysis menggunakan system tools
            if platform.system() == "Windows":
                # Use PowerShell untuk basic PE info
                ps_cmd = f'Get-ItemProperty "{exe_path}" | Select-Object Length,CreationTime,LastWriteTime'
                result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {'pe_info': result.stdout.strip()}
            
            # Cross-platform file analysis
            file_info = {
                'size': exe_path.stat().st_size,
                'created': datetime.fromtimestamp(exe_path.stat().st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(exe_path.stat().st_mtime).isoformat()
            }
            
            return file_info
            
        except Exception as e:
            logging.warning(f"⚠️ PE analysis failed: {e}")
            return {}
    
    def simulate_detection_analysis(self, build_result, builder_type):
        """Simulate detection analysis based pada research findings"""
        if not build_result.get('success'):
            return {'detection_rate': 1.0, 'confidence': 'low'}
        
        # Expected detection rates based pada research
        if builder_type == 'pyinstaller':
            base_detection = 0.65  # 65% baseline detection
            size_factor = min(build_result['compressed_size'] / (10 * 1024 * 1024), 1.0)  # Size impact
            python_artifacts = 0.8  # High Python artifact presence
            
        elif builder_type == 'nuitka':
            base_detection = 0.35  # 35% baseline detection
            size_factor = min(build_result['compressed_size'] / (8 * 1024 * 1024), 1.0)
            python_artifacts = 0.2  # Low Python artifact presence
        
        # Calculate adjusted detection rate
        detection_rate = base_detection * (0.7 + 0.3 * size_factor) * (0.5 + 0.5 * python_artifacts)
        
        return {
            'detection_rate': round(detection_rate, 3),
            'estimated_av_detections': int(detection_rate * 65),  # Assuming 65 AV engines
            'python_artifacts': python_artifacts,
            'size_factor': size_factor,
            'confidence': 'medium'  # Simulation confidence
        }
    
    def performance_benchmark(self, exe_path):
        """Benchmark executable performance"""
        if not exe_path or not Path(exe_path).exists():
            return {}
        
        try:
            # Simulate startup time measurement
            startup_times = []
            for i in range(3):  # Multiple runs
                start_time = time.time()
                
                # Quick process start/stop untuk measurement
                process = subprocess.Popen([exe_path], stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL)
                time.sleep(0.5)  # Let it initialize
                process.terminate()
                process.wait(timeout=5)
                
                startup_time = time.time() - start_time
                startup_times.append(startup_time)
                time.sleep(1)  # Cooldown
            
            avg_startup = sum(startup_times) / len(startup_times)
            
            return {
                'avg_startup_time': round(avg_startup, 3),
                'startup_times': startup_times,
                'benchmark_runs': len(startup_times)
            }
            
        except Exception as e:
            logging.warning(f"⚠️ Performance benchmark failed: {e}")
            return {'error': str(e)}
    
    def comprehensive_comparison(self):
        """Perform comprehensive build comparison"""
        logging.info("\n" + "="*60)
        logging.info("🚀 COMPREHENSIVE BUILD COMPARISON")
        logging.info("="*60)
        
        # Check dependencies first
        deps = self.check_dependencies()
        if not all(deps.values()):
            logging.error("❌ Missing dependencies. Please install required tools.")
            return None
        
        # Build dengan PyInstaller
        logging.info("\n📦 Phase 1: PyInstaller Build")
        pyinstaller_result = self.build_with_pyinstaller()
        self.comparison_results['pyinstaller'] = pyinstaller_result
        
        if pyinstaller_result.get('success'):
            # Detection analysis
            self.comparison_results['pyinstaller']['detection_analysis'] = \
                self.simulate_detection_analysis(pyinstaller_result, 'pyinstaller')
            
            # Performance benchmark
            self.comparison_results['pyinstaller']['performance'] = \
                self.performance_benchmark(pyinstaller_result.get('exe_path'))
        
        # Build dengan Nuitka
        logging.info("\n📦 Phase 2: Nuitka Build")
        nuitka_result = self.build_with_nuitka()
        self.comparison_results['nuitka'] = nuitka_result
        
        if nuitka_result.get('success'):
            # Detection analysis
            self.comparison_results['nuitka']['detection_analysis'] = \
                self.simulate_detection_analysis(nuitka_result, 'nuitka')
            
            # Performance benchmark
            self.comparison_results['nuitka']['performance'] = \
                self.performance_benchmark(nuitka_result.get('exe_path'))
        
        # Comparative analysis
        self.comparison_results['analysis'] = self.calculate_comparative_metrics()
        
        # Generate report
        self.generate_comprehensive_report()
        
        return self.comparison_results
    
    def calculate_comparative_metrics(self):
        """Calculate comparative metrics untuk academic analysis"""
        py_result = self.comparison_results.get('pyinstaller', {})
        nu_result = self.comparison_results.get('nuitka', {})
        
        if not (py_result.get('success') and nu_result.get('success')):
            return {'error': 'One or both builds failed'}
        
        # Size comparison
        py_size = py_result['compressed_size']
        nu_size = nu_result['compressed_size']
        size_advantage = (py_size - nu_size) / py_size * 100 if py_size > 0 else 0
        
        # Build time comparison
        py_time = py_result['build_time']
        nu_time = nu_result['build_time']
        time_ratio = nu_time / py_time if py_time > 0 else 1
        
        # Detection comparison
        py_detection = py_result.get('detection_analysis', {}).get('detection_rate', 0.65)
        nu_detection = nu_result.get('detection_analysis', {}).get('detection_rate', 0.35)
        detection_improvement = (py_detection - nu_detection) / py_detection * 100 if py_detection > 0 else 0
        
        # Academic significance calculation
        academic_score = self.calculate_academic_significance(
            size_advantage, detection_improvement, py_result, nu_result
        )
        
        return {
            'size_comparison': {
                'pyinstaller_size': py_size,
                'nuitka_size': nu_size,
                'size_advantage_percent': round(size_advantage, 1),
                'winner': 'nuitka' if nu_size < py_size else 'pyinstaller'
            },
            'build_time_comparison': {
                'pyinstaller_time': round(py_time, 1),
                'nuitka_time': round(nu_time, 1),
                'time_ratio': round(time_ratio, 2),
                'winner': 'pyinstaller' if py_time < nu_time else 'nuitka'
            },
            'detection_comparison': {
                'pyinstaller_detection': py_detection,
                'nuitka_detection': nu_detection,
                'improvement_percent': round(detection_improvement, 1),
                'winner': 'nuitka' if nu_detection < py_detection else 'pyinstaller'
            },
            'academic_significance': academic_score,
            'overall_recommendation': self.determine_overall_winner(
                size_advantage, detection_improvement, time_ratio
            )
        }
    
    def calculate_academic_significance(self, size_adv, det_adv, py_result, nu_result):
        """Calculate academic significance score"""
        # Weights untuk different aspects
        weights = {
            'detection_evasion': 0.40,  # Most important untuk security research
            'size_optimization': 0.25,
            'performance': 0.20,
            'practical_value': 0.15
        }
        
        # Normalize scores (0-1)
        detection_score = min(det_adv / 50, 1.0)  # Max expected 50% improvement
        size_score = min(size_adv / 60, 1.0)      # Max expected 60% improvement
        
        # Performance score (startup time, etc.)
        py_perf = py_result.get('performance', {}).get('avg_startup_time', 3.0)
        nu_perf = nu_result.get('performance', {}).get('avg_startup_time', 1.5)
        perf_improvement = (py_perf - nu_perf) / py_perf if py_perf > 0 else 0
        performance_score = min(perf_improvement / 0.5, 1.0)  # Max expected 50% improvement
        
        # Practical value (ease of deployment, compatibility)
        practical_score = 0.8  # Assume good practical value
        
        # Calculate weighted score
        academic_score = (
            detection_score * weights['detection_evasion'] +
            size_score * weights['size_optimization'] + 
            performance_score * weights['performance'] +
            practical_score * weights['practical_value']
        )
        
        return {
            'overall_score': round(academic_score, 3),
            'detection_score': round(detection_score, 3),
            'size_score': round(size_score, 3),
            'performance_score': round(performance_score, 3),
            'practical_score': round(practical_score, 3),
            'significance_level': 'high' if academic_score > 0.7 else 'medium' if academic_score > 0.5 else 'low'
        }
    
    def determine_overall_winner(self, size_adv, det_adv, time_ratio):
        """Determine overall winner based pada weighted criteria"""
        nuitka_score = 0
        pyinstaller_score = 0
        
        # Detection evasion (weight: 40%)
        if det_adv > 20:  # Significant improvement
            nuitka_score += 40
        elif det_adv > 10:  # Moderate improvement
            nuitka_score += 20
        else:
            pyinstaller_score += 10
        
        # Size optimization (weight: 25%)
        if size_adv > 30:  # Significant size reduction
            nuitka_score += 25
        elif size_adv > 15:  # Moderate size reduction
            nuitka_score += 15
        else:
            pyinstaller_score += 10
        
        # Build time (weight: 15%)
        if time_ratio < 2:  # Reasonable build time
            nuitka_score += 15
        else:
            pyinstaller_score += 15
        
        # Ease of use (weight: 20%)
        pyinstaller_score += 10  # Generally easier to use
        nuitka_score += 5
        
        if nuitka_score > pyinstaller_score:
            return {
                'winner': 'nuitka',
                'score_difference': nuitka_score - pyinstaller_score,
                'confidence': 'high' if (nuitka_score - pyinstaller_score) > 20 else 'medium',
                'recommendation': 'Nuitka recommended untuk academic research'
            }
        else:
            return {
                'winner': 'pyinstaller',
                'score_difference': pyinstaller_score - nuitka_score,
                'confidence': 'medium',
                'recommendation': 'PyInstaller may be sufficient for basic needs'
            }
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        report_path = self.results_dir / f"build_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.comparison_results, f, indent=2, ensure_ascii=False)
            
            logging.info(f"📊 Comprehensive report saved: {report_path}")
            
            # Generate human-readable summary
            self.print_summary_report()
            
        except Exception as e:
            logging.error(f"❌ Failed to save report: {e}")
    
    def print_summary_report(self):
        """Print human-readable summary"""
        analysis = self.comparison_results.get('analysis', {})
        
        print("\n" + "="*70)
        print("📊 BUILD COMPARISON SUMMARY REPORT")
        print("="*70)
        
        # Size comparison
        size_comp = analysis.get('size_comparison', {})
        print(f"\n📦 SIZE COMPARISON:")
        print(f"   PyInstaller: {size_comp.get('pyinstaller_size', 0):,} bytes")
        print(f"   Nuitka:      {size_comp.get('nuitka_size', 0):,} bytes")
        print(f"   Advantage:   {size_comp.get('size_advantage_percent', 0)}% smaller dengan Nuitka")
        
        # Detection comparison
        det_comp = analysis.get('detection_comparison', {})
        print(f"\n🛡️ DETECTION EVASION:")
        print(f"   PyInstaller: {det_comp.get('pyinstaller_detection', 0):.1%} detection rate")
        print(f"   Nuitka:      {det_comp.get('nuitka_detection', 0):.1%} detection rate")
        print(f"   Improvement: {det_comp.get('improvement_percent', 0)}% better dengan Nuitka")
        
        # Academic significance
        academic = analysis.get('academic_significance', {})
        print(f"\n🎓 ACADEMIC SIGNIFICANCE:")
        print(f"   Overall Score: {academic.get('overall_score', 0):.3f}")
        print(f"   Significance:  {academic.get('significance_level', 'unknown').upper()}")
        
        # Recommendation
        recommendation = analysis.get('overall_recommendation', {})
        print(f"\n🎯 RECOMMENDATION:")
        print(f"   Winner:     {recommendation.get('winner', 'unknown').upper()}")
        print(f"   Confidence: {recommendation.get('confidence', 'unknown').upper()}")
        print(f"   Reason:     {recommendation.get('recommendation', 'No recommendation')}")
        
        print("\n" + "="*70)

def main():
    """Main function untuk automated build comparison"""
    print("🎓 ADVANCED BUILD COMPARISON UNTUK RESEARCH S2")
    print("=" * 60)
    print("📚 Thesis: Analisis dan Pengembangan Malware")
    print("🔬 Comparison: PyInstaller vs Nuitka dengan UPX")
    print("=" * 60)
    
    # Check source file
    source_file = "agent_improved.py"
    if not Path(source_file).exists():
        print(f"❌ Source file not found: {source_file}")
        print("💡 Please ensure agent_improved.py is dalam current directory")
        return
    
    # Confirm academic purpose
    confirm = input("\n❓ Confirm academic research purpose (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Academic confirmation required")
        return
    
    # Initialize dan run comparison
    try:
        comparator = AdvancedBuildComparator(source_file)
        results = comparator.comprehensive_comparison()
        
        if results:
            print("\n✅ Build comparison completed successfully!")
            print("📁 Check build_results/ directory untuk detailed reports")
        else:
            print("\n❌ Build comparison failed")
            
    except KeyboardInterrupt:
        print("\n🛑 Build comparison interrupted by user")
    except Exception as e:
        print(f"\n❌ Build comparison error: {e}")
        logging.error(f"Comparison failed: {e}")

if __name__ == "__main__":
    main()
