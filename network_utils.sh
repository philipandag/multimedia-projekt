#!/bin/bash

# $1 - network name
setup_network() {
	if [ "$#" -ne 1 ]; then
    		echo "Error: Network name not provided"
    		exit 1
	fi

	teardown_network $1 > /dev/null 2>&1

	ip link add $1_br0 type bridge
	ip link add $1_vth1 type veth peer $1_vth_1
	ip link add $1_vth2 type veth peer $1_vth_2
	ip netns add $1_ns1
	ip netns add $1_ns2
	ip link set dev $1_vth_1 netns $1_ns1
	ip link set dev $1_vth_2 netns $1_ns2
	ip netns exec $1_ns1 ip address add 192.168.10.1/24 dev $1_vth_1
	ip netns exec $1_ns1 ip link set dev $1_vth_1 up
	ip netns exec $1_ns2 ip address add 192.168.10.2/24 dev $1_vth_2
	ip netns exec $1_ns2 ip link set dev $1_vth_2 up
	ip link set dev $1_vth1 master $1_br0
	ip link set dev $1_vth2 master $1_br0
	ip link set dev $1_br0 up
	ip link set dev $1_vth1 up
	ip link set dev $1_vth2 up
	ip netns exec $1_ns1 ip link set dev lo up
	ip netns exec $1_ns2 ip link set dev lo up
	
	echo "Network $1 set up"
}

# $1 - network name
reset_tc_settings() {
	if [ "$#" -ne 1 ]; then
    		echo "Error: Network name not provided"
    		exit 1
	fi

	tc qdisc del dev $1_vth1 root || true
	tc qdisc del dev $1_vth2 root || true
}

# Tc netem qdisc settings are set to both interfaces in the network,
# meaning that real values will be 2 times bigger than values passed.
# e.g. setting delay here to 20 ms will result in delays being actually ~40ms
# $1 - network name
# $2 - rate (unit needs to be specified)
# $3 - delay (ms)
# $4 - jitter (ms)
# $5 - correlation (%)
# $6 - duplicate rate (%)
# $7 - corrupt rate (%)
# $8 - reorder rate (%)
setup_tc_netem() {
	if [ "$#" -ne 8 ]; then
    		echo "Error: Exactly 8 arguments are required: network name, rate, \
delay, jitter, correlation, duplicate rate, corrupt rate, reorder rate"
    		exit 1
	fi
	
	if lsmod | grep -wq sch_netem; then
		echo "sch_netem is already loaded, all good"
	else
		echo "sch_netem is not loaded, loading..."
		modprobe sch_netem
	fi

	reset_tc_settings $1
	
	tc qdisc add dev $1_vth1 root netem \
		rate $2 delay $3ms $4ms $5% duplicate $6% corrupt $7% reorder $8%
	tc qdisc add dev $1_vth2 root netem \
		rate $2 delay $3ms $4ms $5% duplicate $6% corrupt $7% reorder $8%
		3
	echo "qdisc set up"
}

# $1 - network name
teardown_network() {
	if [ "$#" -ne 1 ]; then
    		echo "Error: Network name not provided"
    		exit 1
	fi

	if ip link show $1_br0 > /dev/null 2>&1; then
		ip link del $1_br0
	fi
	
	if ip link show $1_vth1 > /dev/null 2>&1; then
		ip link del $1_vth1
	fi
	
	if ip link show $1_vth2 > /dev/null 2>&1; then
		ip link del $1_vth2
	fi
	
	if ip netns show $1_ns1 > /dev/null 2>&1; then
		ip netns del $1_ns1
	fi
	
	if ip netns show $1_ns2 > /dev/null 2>&1; then
		ip netns del $1_ns2
	fi
	
	echo "Network $1 torn down"
}

# $1 - network name
from_ns1_ping_ns2() {
	if [ "$#" -ne 1 ]; then
    		echo "Error: Network name not provided"
    		exit 1
	fi

	ip netns exec $1_ns1 ping 192.168.10.2
}

# $1 - network name
from_ns2_ping_ns1() {
	if [ "$#" -ne 1 ]; then
    		echo "Error: Network name not provided"
    		exit 1
	fi
	
	ip netns exec $1_ns2 ping 192.168.10.1
}

# $1 - network name
# $2 - address to ping
from_ns1_ping() {
	if [ "$#" -ne 2 ]; then
			echo "Error: You need to provide network name as the first \
argument and the host to ping as the second"
			exit 1
	fi

	ip netns exec $1_ns1 ping $2
}

# $1 - network name
# $2 - address to ping
from_ns2_ping() {
	if [ "$#" -ne 2 ]; then
			echo "Error: You need to provide network name as the first \
argument and the host to ping as the second"
			exit 1
	fi

	ip netns exec $1_ns2 ping $2
}

# $1 - network name
ns1_ping_self() {
	if [ "$#" -ne 1 ]; then
    		echo "Error: Network name not provided"
    		exit 1
	fi

	ip netns exec $1_ns1 ping 192.168.10.1
}

# $1 - network name
ns2_ping_self() {
	if [ "$#" -ne 1 ]; then
    		echo "Error: Network name not provided"
    		exit 1
	fi

	ip netns exec $1_ns2 ping 192.168.10.2
}

# $1 - network name
# $2 - path to app binary and app arguments. Quotes ("") may be used to pass
# command ./this.sh ns1_run_app net_name "ping some arguments here"
ns1_run_app() {
	if [ "$#" -ne 2 ]; then
			echo "Error: You need to provide network name as the first
argument and the command line to run as the second"
			exit 1
	fi

	sudo ip netns exec $1_ns1 $2
}

# $1 - network name
# $2 - path to app binary and app arguments. Quotes ("") may be used to pass
# command ./this.sh ns2_run_app net_name "ping some arguments here"
ns2_run_app() {
	if [ "$#" -ne 2 ]; then
			echo "Error: You need to provide network name as the first
argument and the command line to run as the second"
			exit 1
	fi

	sudo ip netns exec $1_ns2 $2
}

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ -z "$1" ]; then
	echo "You need to provide subcommand argument"
else
  "$@"
fi

# Written by Maciej Krzyżanowski
# Created using:
# * https://man7.org/linux/man-pages/man8/tc-netem.8.html
# * https://dev.to/stanleyogada/demystifying-linux-network-bridging-and-network-namespaces-19ap
# * https://www.baeldung.com/linux/bridging-network-interfaces
# * https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script

