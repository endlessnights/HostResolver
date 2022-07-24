import time
import socket
from icmplib import ping
from columnar import columnar
from icmplib import NameLookupError

start_time = time.time()
# get data from file (hosts)
file1 = open('source.txt', 'r')
Lines = file1.readlines()
count = 0
all_data = []
# open socket for check opened port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for line in Lines:
    try:
        count += 1
        # print("{}: {}".format(count, line.strip()))
        hostname = line.strip()
        # check is 443 port opened
        try:
            result = sock.connect_ex((hostname, 443))
            if result == 0:
                portcheck = 'Ok'
            else:
                portcheck = 'Bad'
        except:
            pass
        # icmplib ping
        host = ping(hostname, count=5, interval=0.1, privileged=False)
        headers = ['Name', 'Address', 'MIN', 'AVG', 'MAX', 'rtts', 'Jitter', 'Port 443']
        rtts = [round(num, 2) for num in host.rtts]
        # if host doesn't ping, drop or reject ICMP reply
        if (str(host.min_rtt or host.avg_rtt or host.max_rtt)) == '0.0' or str(host.rtts) == '[]':
            all_data.append(
                ['{}'.format(hostname), '{}'.format(host.address),
                 'ICMP DROP', 'ICMP DROP', 'ICMP DROP', 'ICMP DROP', 'ICMP DROP',
                 '{}'.format(portcheck)]
            )
        else:
            all_data.append(
                ['{}'.format(hostname), '{}'.format(host.address),
                 '{}'.format(host.min_rtt), '{}'.format(host.avg_rtt),
                 '{}'.format(host.max_rtt), '{}'.format(rtts), '{}'.format(host.jitter), '{}'.format(portcheck)]
            )
    except NameLookupError:
        # if host address couldn't be resolved (no IP address on domain A-record)
        all_data.append(
            ['{}'.format(hostname), 'Not resolved', '-', '-', '-', '-', '-', 'Bad']
        )
sock.close()
# print table
table = columnar(all_data, headers=headers, min_column_width=18, terminal_width=200)
print(table)
# count time took for program runtime
print("Took %s seconds" % (time.time() - start_time))
