import docker
import json
import time
import subprocess
import io
import multiprocessing


def get_container_info(container, container_status_ret):

    # get container status dict
    container_stats = container.stats(stream=False)

    container_status = dict()
    #container_status['name'] = container_stats['name']
    #container_status['id'] = container_status['id']

    container_name = container_stats['name']
    container_status[container_name] = dict()
    container_status[container_name]['id'] = container_stats['id']

    # calc cpu usage
    cur_cpu_usage = container_stats['cpu_stats']['cpu_usage']['total_usage']
    prev_cpu_usage = container_stats['precpu_stats']['cpu_usage'][
        'total_usage']
    delta_cpu_usage = cur_cpu_usage - prev_cpu_usage

    cur_system_cpu_usage = container_stats['cpu_stats']['system_cpu_usage']
    prev_system_cpu_usage = container_stats['precpu_stats']['system_cpu_usage']
    delta_system_cpu_usage = cur_system_cpu_usage - prev_system_cpu_usage

    per_cpu_usage_len = len(
        container_stats['cpu_stats']['cpu_usage']['percpu_usage'])

    perc_cpu_usage = (delta_cpu_usage /
                      delta_system_cpu_usage) * per_cpu_usage_len * 100

    #container_status['perc_cpu_usage'] = round(perc_cpu_usage, 2)
    container_status[container_name]['perc_cpu_usage'] = round(
        perc_cpu_usage, 2)

    # calc memory usage
    cur_mem_usage = container_stats['memory_stats']['usage'] - container_stats[
        'memory_stats']['stats']['cache']
    max_memory_available = container_stats['memory_stats']['limit']

    perc_mem_usage = (cur_mem_usage / max_memory_available) * 100

    #container_status['perc_mem_usage'] = round(perc_mem_usage, 2)
    container_status[container_name]['perc_mem_usage'] = round(
        perc_mem_usage, 2)

    # calc net traffic
    #container_status['rx_bytes'] = container_stats['networks']['eth0']['rx_bytes']
    container_status[container_name]['rx_bytes'] = container_stats['networks'][
        'eth0']['rx_bytes']
    #container_status['tx_bytes'] = container_stats['networks']['eth0']['tx_bytes']
    container_status[container_name]['tx_bytes'] = container_stats['networks'][
        'eth0']['tx_bytes']

    container_status_ret[container_name] = container_status[container_name]

    #return container_status


if __name__ == '__main__':

    # instatiate Docker Client
    client = docker.DockerClient(base_url='unix://var/run/docker.sock',
                                 version='1.40')

    # retrieve list of containers
    container_list = client.containers.list()

    # get multiprocessing manager to return collected info
    # in a threaded fashion
    manager = multiprocessing.Manager()
    container_info = manager.dict()

    while (True):

        thread_list = []
        for container in container_list:
            # run in thread fashion to collect info faster
            p = multiprocessing.Process(target=get_container_info,
                                        args=(container, container_info))
            thread_list.append(p)
            p.start()

        for thread in thread_list:
            p.join()

        print(json.dumps(container_info.copy(), indent=4))

    #print(json.dumps(client.containers.list()[3].stats(stream=False), indent=4))
