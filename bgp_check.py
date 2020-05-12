from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
# from nornir.plugins.functions.text import print_result
from tabulate import tabulate
from colorama import Fore, Style


# empty list for appending
table = []
headers = [
    "IP Address",
    "Hostname",
    "Description",
    "Neighbor Address",
    "Remote-AS",
    "Prefix",
    "Uptime",
    "BGP Status",
    "Ping P2P Result",
    "Ping P2P Summary",
]


def bgp_check(task):
    """will execute command: show ip bgp in all hosts included in hosts.yaml"""
    showbgp = task.run(
        netmiko_send_command, command_string="show ip bgp summary", use_textfsm=True
    )
    task.host["bgp_sum"] = showbgp.result
    bgp_sums = task.host["bgp_sum"]
    ipaddress = task.host.hostname
    # bgp states for "up" or "down" status

    bgp_down_states = ["Idle (Admin)", "Idle (PfxCt)", "Idle", "Active", "Connect"]
    bgp_peer_states = ["Open Sent", "Open Confirm"]
    up = Fore.GREEN + Style.BRIGHT + ("UP") + Fore.RESET
    down = Fore.RED + Style.BRIGHT + ("DOWN") + Fore.RESET
    waiting = Fore.YELLOW + Style.BRIGHT + ("WAITING") + Fore.RESET

    for bgp_sum in bgp_sums:
        neighbor = bgp_sum["bgp_neigh"]
        neigh_as = bgp_sum["neigh_as"]
        # router_id = bgp_sum["router_id"]
        prefix = bgp_sum["state_pfxrcd"]
        up_down = bgp_sum["up_down"]
        # assigning hostname based on ip address
        if ipaddress == "192.168.1.1":
            host = "CORE-R1"
        elif ipaddress == "192.168.1.5":
            host = "CORE-R2"
        else:
            host = ipaddress
        # R2 assigning description base on bgp neighbors
        if neighbor == "120.89.30.27":
            desc = "EASTERN BACKUP"
            source = "180.232.122.14"
            destination = "120.89.30.27"
        elif neighbor == "120.89.30.28":
            desc = "EASTERN MAIN"
            source = " 180.232.122.14"
            destination = " 120.89.30.28"
        elif neighbor == "172.17.32.165":
            desc = "INCAPSULA HONGKONG"
            source = "180.232.122.14"
            destination = "107.154.26.52"
        elif neighbor == "172.17.160.13":
            desc = "INCAPSULA OSAKA"
            source = "180.232.122.14"
            destination = "107.154.33.5"
        elif neighbor == "192.168.88.1":
            desc = "iBGP CORE-R1"
            source = "192.168.88.2"
            destination = "192.168.88.1"
        # R1 assigning description base on bgp neighbors
        elif neighbor == "121.58.215.185":
            desc = "CONVERGE"
            source = "121.58.215.186"
            destination = "121.58.215.185"
        elif neighbor == "203.177.110.117":
            desc = "GLOBE"
            source = "203.177.110.118"
            destination = "203.177.110.117"
        elif neighbor == "172.17.32.161":
            desc = "INCAPSULA HONGKONG"
            source = "121.58.215.186"
            destination = "107.154.26.52"
        elif neighbor == "172.17.160.9":
            desc = "INCAPSULA OSAKA"
            source = "121.58.215.186"
            destination = "107.154.33.5"
        elif neighbor == "192.168.88.2":
            desc = "iBGP CORE-R2"
            source = "192.168.88.1"
            destination = "192.168.88.2"
        else:
            desc = "BGP NEIGHBOR ROUTER"

        ping_cmd = task.run(
            netmiko_send_command,
            command_string=f"ping {destination} repeat 20 source {source}",
        )
        task.host["ping"] = ping_cmd.result
        ping_results = task.host["ping"]
        ping_results = ping_results.split()
        ping = ping_results[24]
        # print(ping_results)

        if not "!!!!!!!!!!!!!!!!!!!!" in ping:
            ping_sum = Fore.red + Style.BRIGHT + "INTERMITTENT" + Fore.RESET
        else:
            ping_sum = Fore.GREEN + Style.BRIGHT + "OK! No RTO" + Fore.RESET

        if prefix not in bgp_down_states:
            table.append(
                [
                    ipaddress,
                    host,
                    desc,
                    neighbor,
                    neigh_as,
                    prefix,
                    up_down,
                    up,
                    ping,
                    ping_sum,
                ]
            )
        elif prefix in bgp_down_states:
            table.append(
                [
                    ipaddress,
                    host,
                    desc,
                    neighbor,
                    neigh_as,
                    prefix,
                    up_down,
                    down,
                    ping,
                    ping_sum,
                ]
            )
        elif prefix in bgp_peer_states:
            table.append(
                [
                    ipaddress,
                    host,
                    desc,
                    neighbor,
                    neigh_as,
                    prefix,
                    up_down,
                    waiting,
                    ping,
                    ping_sum,
                ]
            )


def main() -> None:
    """Will execute the bgp_check"""
    bgp = InitNornir(config_file="config.yml")
    bgp.run(task=bgp_check)
    # int_res = nr.run(task=interface_check)
    # print_result(bgp_res)
    # print_result(int_res)
    print(tabulate(sorted(table), headers, tablefmt="rst", colalign="right"))


if __name__ == "__main__":
    main()
