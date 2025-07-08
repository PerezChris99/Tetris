"""
Network Connection Test Utility
Test network connectivity and troubleshoot connection issues
"""
import socket
import threading
import time
import sys

def test_port_open(host: str, port: int, timeout: float = 5.0) -> bool:
    """Test if a port is open on a host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_local_ip() -> str:
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def test_server_creation(port: int = 0) -> tuple[bool, int]:
    """Test if we can create a server on a port"""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', port))
        actual_port = server_socket.getsockname()[1]
        server_socket.close()
        return True, actual_port
    except Exception as e:
        return False, 0

def run_connectivity_test():
    """Run a comprehensive connectivity test"""
    print("=== Tetris Battle Network Connectivity Test ===\\n")
    
    # Test 1: Local IP
    print("1. Getting local IP address...")
    local_ip = get_local_ip()
    print(f"   Local IP: {local_ip}")
    
    # Test 2: Server creation
    print("\\n2. Testing server creation...")
    can_create, port = test_server_creation(0)
    if can_create:
        print(f"   ✓ Can create server on port {port}")
    else:
        print("   ✗ Cannot create server (firewall/permissions issue)")
    
    # Test 3: Loopback connection
    print("\\n3. Testing loopback connection...")
    if can_create:
        # Start a temporary server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', 0))
        test_port = server_socket.getsockname()[1]
        server_socket.listen(1)
        
        def accept_connection():
            try:
                client, addr = server_socket.accept()
                client.close()
            except:
                pass
        
        accept_thread = threading.Thread(target=accept_connection, daemon=True)
        accept_thread.start()
        
        # Test connection
        if test_port_open("127.0.0.1", test_port, 2.0):
            print("   ✓ Loopback connection successful")
        else:
            print("   ✗ Loopback connection failed")
        
        server_socket.close()
    else:
        print("   ⚠ Skipped (cannot create server)")
    
    # Test 4: Internet connectivity
    print("\\n4. Testing internet connectivity...")
    if test_port_open("8.8.8.8", 53, 3.0):  # DNS
        print("   ✓ Internet connection available")
    else:
        print("   ✗ No internet connection detected")
    
    # Test 5: Common port availability
    print("\\n5. Testing common port availability...")
    test_ports = [12345, 25565, 7777, 8080]
    available_ports = []
    
    for port in test_ports:
        can_use, _ = test_server_creation(port)
        if can_use:
            available_ports.append(port)
    
    if available_ports:
        print(f"   ✓ Available ports: {', '.join(map(str, available_ports))}")
    else:
        print("   ⚠ No common ports available (try random port)")
    
    print("\\n=== Summary ===")
    print(f"Local IP Address: {local_ip}")
    print("Status: ", end="")
    
    if can_create:
        print("✓ Ready for hosting games")
        print(f"\\nTo host a game, share this information:")
        print(f"  IP Address: {local_ip}")
        print(f"  Port: <will be assigned when you start hosting>")
        print(f"\\nNote: Players outside your local network may need")
        print(f"      port forwarding configured on your router.")
    else:
        print("⚠ Network setup needed")
        print("\\nTroubleshooting tips:")
        print("- Check firewall settings")
        print("- Try running as administrator")
        print("- Contact your network administrator")
    
    print("\\n=== Connection Guide ===")
    print("To play online:")
    print("1. HOST: Run the game and select 'Host Game'")
    print("2. HOST: Share your IP address and port with the other player")
    print("3. JOINER: Select 'Join Game' and enter the host's IP and port")
    print("4. Both players should be connected automatically")
    print("\\nLocal Network (same WiFi/LAN):")
    print(f"- Use the local IP: {local_ip}")
    print("\\nInternet (different networks):")
    print("- Host needs to configure port forwarding on their router")
    print("- Use the host's public IP address")
    print("- Consider using online services like Hamachi for easier setup")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_connectivity_test()
        elif sys.argv[1] == "ip":
            print(get_local_ip())
        elif len(sys.argv) >= 4 and sys.argv[1] == "check":
            host = sys.argv[2]
            port = int(sys.argv[3])
            if test_port_open(host, port):
                print(f"✓ {host}:{port} is reachable")
            else:
                print(f"✗ {host}:{port} is not reachable")
        else:
            print("Usage:")
            print("  python network_test.py test     - Run full connectivity test")
            print("  python network_test.py ip       - Show local IP address")
            print("  python network_test.py check <host> <port> - Test specific connection")
    else:
        run_connectivity_test()

if __name__ == "__main__":
    main()
