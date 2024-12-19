import subprocess
import os

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
NETWORK_UTILS_SCRIPT=os.path.join(SCRIPT_DIR, "..", "network_utils.sh")
IP_1="192.168.10.1/24"
IP_2="192.168.10.1/24"


def setup_network(network_name):
    subprocess.run([NETWORK_UTILS_SCRIPT, "setup_network", network_name])
    
def clear_tc_netem(network_name):
    subprocess.run([NETWORK_UTILS_SCRIPT, "reset_tc_settings", network_name])
    
def setup_tc_netem(network_name, rate="1Gbps", delay_ms="0", jitter_ms="0", correlation_percent="0", loss_percent="0", duplicate_percent="0", corrupt_percent="0", reorder_percent="0"):
    clear_tc_netem(network_name)
    subprocess.run([NETWORK_UTILS_SCRIPT, "setup_tc_netem", network_name, rate, delay_ms, jitter_ms, correlation_percent, loss_percent, duplicate_percent, corrupt_percent, reorder_percent])

def run_ns1(network_name, command_to_execute: str) -> str:
    """
    returns the stdout of the command
    """
    return subprocess.run([NETWORK_UTILS_SCRIPT, "ns1_run_app", network_name, command_to_execute], stdout=subprocess.PIPE).stdout.decode().strip()

def run_ns2(network_name, command_to_execute: str) -> str:
    """
    returns the stdout of the command
    """
    return subprocess.run([NETWORK_UTILS_SCRIPT, "ns2_run_app", network_name, command_to_execute], stdout=subprocess.PIPE).stdout.decode().strip()
    
    
if __name__ == "__main__":
    name="test-net"
    setup_network(name)
    setup_tc_netem(name, rate="1Gbps", delay_ms="500", jitter_ms="500", correlation_percent="0", duplicate_percent="0", corrupt_percent="0", reorder_percent="0")
    print(run_ns1(name, "ping -c 3 192.168.10.2"))
    print(run_ns2(name, "ping -c 3 192.168.10.1"))
