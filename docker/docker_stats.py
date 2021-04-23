import docker
import json
import multiprocessing


def get_container_info(container, ret):

    # get container status dict
    container_stats = container.stats(stream=False)

    container_status = dict()

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

    container_status[container_name]['perc_cpu_usage'] = round(
        perc_cpu_usage, 2)

    # calc memory usage
    cur_mem_usage = container_stats['memory_stats']['usage'] - container_stats[
        'memory_stats']['stats']['cache']
    max_memory_available = container_stats['memory_stats']['limit']

    perc_mem_usage = (cur_mem_usage / max_memory_available) * 100

    container_status[container_name]['perc_mem_usage'] = round(
        perc_mem_usage, 2)

    # calc net traffic
    container_status[container_name]['rx_bytes'] = container_stats['networks'][
        'eth0']['rx_bytes']
    container_status[container_name]['tx_bytes'] = container_stats['networks'][
        'eth0']['tx_bytes']

    # create a entry in the return dictionary with the container name
    # and pass all info
    ret[container_name] = container_status[container_name]

if __name__ == '__main__':

    # instatiate Docker Client
    client = docker.DockerClient(base_url='unix://var/run/docker.sock',
                                 version='1.40')

    # retrieve list of containers
    container_list = client.containers.list()

    # get multiprocessing manager to return collected info
    # in a parallel fashion
    manager = multiprocessing.Manager()
    container_info = manager.dict()

    while (True):

        proc_list = []
        for container in container_list:
            # run in processes fashion to collect info faster
            p = multiprocessing.Process(target=get_container_info,
                                        args=(container, container_info))
            proc_list.append(p)
            p.start()

        for proc in proc_list:
            # join and kill the process
            proc.join()
            proc.terminate()

        print(json.dumps(container_info.copy(), indent=4))
