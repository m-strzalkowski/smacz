ping -c 2 -b 192.168.1.255 >/dev/null
piip=`ip neigh show | grep b8:27:eb:72:1f:1e | awk '{print $1}' | head -n 1`
echo $piip