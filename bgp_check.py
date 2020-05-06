from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command, netmiko_send_config
from nornir.plugins.functions.text import print_result
from tabulate import tabulate
from colorama import Fore

table = []
headers = ["IP Address","Hostname","Description","Neighbor Address",
            "Remote-AS", "Prefix", "Uptime", "BGP Status"]
def bgp_check(task):
    r = task.run(netmiko_send_command,
                 command_string="show ip bgp summary", use_textfsm=True)
    task.host['bgp_sum'] = r.result
    bgp_sums = task.host['bgp_sum']
    ipaddress = task.host.hostname

    bgp_down_states = ["Idle (Admin)","Idle (PfxCt)", "Idle", "Active", "Connect"]
    bgp_peer_states = ["Open Sent", "Open Confirm"]
    
    for bgp_sum in bgp_sums:
        neighbor = bgp_sum['bgp_neigh']
        neigh_as = bgp_sum['neigh_as']
        router_id = bgp_sum['router_id']
        prefix = bgp_sum['state_pfxrcd']
        up_down = bgp_sum['up_down']
        
        if ipaddress =="192.168.1.1":
            host = "CORE-R1"
        elif ipaddress=="192.168.1.5":
            host ="CORE-R2"
        #setup descriptions
        if neighbor == "120.89.30.27":
            desc = "EASTERN BACKUP"
        elif neighbor =="120.89.30.28":
            desc = "EASTERN MAIN"
        elif neighbor =="172.17.32.165":
            desc = "INCAPSULA HONGKONG"
        elif neighbor =="172.17.160.13":
            desc = "INCAPSULA OSAKA"
        elif neighbor =="192.168.88.1":
            desc = "iBGP CORE-R1"
        #R1
        elif neighbor =="121.58.215.185":
            desc = "CONVERGE"
        elif neighbor== "203.177.110.117":
            desc ="GLOBE"
        elif neighbor == "172.17.32.161":
            desc ="INCAPSULA HONGKONG"
        elif neighbor =="172.17.160.9":
            desc ="INCAPSULA OSAKA"  
        elif neighbor =="192.168.88.2":
            desc ="iBGP CORE-R2"
            
        if prefix not in bgp_down_states:
            table.append([ipaddress,host,desc,neighbor, neigh_as, prefix, up_down,
                           Fore.GREEN+("UP")+Fore.RESET])
        elif prefix in bgp_down_states:
            table.append([ipaddress,host,desc,neighbor, neigh_as, prefix, up_down,
                           Fore.RED+("DOWN")+Fore.RESET])
        elif prefix in bgp_peer_states:
            table.append([ipaddress,host,desc,neighbor, neigh_as, prefix, up_down,
                           Fore.YELLOW+("WAITING")+Fore.RESET])
            
def interface_check(task):
    r = task.run(netmiko_send_command,
                 command_string="show ip int br", use_textfsm=True)


def main() -> None:
    nr = InitNornir(config_file="config.yml")
    bgp_res = nr.run(task=bgp_check)
    # int_res = nr.run(task=interface_check)
    # print_result(bgp_res)
    # print_result(int_res)
    print(tabulate(table, headers, tablefmt="rst",colalign="center"))

if __name__ == '__main__':
    main()
