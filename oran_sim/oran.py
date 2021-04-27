import docker
import multiprocessing
import os

from collections import OrderedDict

class NearRealTimeRIC():
    
    def __init__(self, docker_socket, docker_api_version):
        self.client = docker.DockerClient(base_url=docker_socket,
                                 version=docker_api_version)
        self.NearRealTimeRIC_list = self.get_NearRealTimeRIC_instance_list()
        self.NearRealTimeRIC_scale = self.get_NearRealTimeRIC_scale()

    def get_NearRealTimeRIC_instance_list(self):
        return self.client.containers.list()

    def get_NearRealTimeRIC_scale(self):
        try:
            services = self.client.services.list(filters={'name': 'orion_orion'})
            service_inspector = self.client.api.inspect_service(services[0].id)
            scale = service_inspector['Spec']['Mode']['Replicated']['Replicas']
        except:
            return -1
        
        return scale

    def set_NearRealTimeRIC_scale(self, scale):
        '''
        # TODO: Scaling the service through the api didnt work
        try:
            services = self.client.services.list(filters={'name': 'orion_orion'})
            service_inspector = self.client.api.inspect_service(services[0].id)
            mode = {'replicated': {'replicas': scale}}
            ret = self.client.api.update_service(service=services[0].id, version=services[0].version, mode=mode)
            print(ret)
        except docker.errors.APIError as e:
            print(e)
            return -1
        '''
        stream = os.popen('docker service scale orion_orion={scale}'.format(scale=scale))
        
        return True

    def get_NearRealTimeRIC_info(self):
        self.NearRealTimeRIC_scale = self.get_NearRealTimeRIC_scale()
        self.NearRealTimeRIC_list = self.get_NearRealTimeRIC_instance_list()

        # get multiprocessing manager to return collected info
        # in a parallel fashion
        manager = multiprocessing.Manager()
        NearRealTimeRIC_info = manager.dict()

        proc_list = []
        for NearRealTimeRIC_instance in self.NearRealTimeRIC_list:
            # run in processes fashion to collect info faster
            p = multiprocessing.Process(target=self.__parse_NearRealTimeRIC_info,
                                        args=(NearRealTimeRIC_instance, NearRealTimeRIC_info))
            proc_list.append(p)
            p.start()

        for proc in proc_list:
            # join and kill the process
            proc.join()
            proc.terminate()
        
        #NearRealTimeRIC_info['scale'] = self.NearRealTimeRIC_scale

        return NearRealTimeRIC_info.copy()

    def __parse_NearRealTimeRIC_info(self, container, ret):

        try:
            # get container status dict
            container_stats = container.stats(stream=False)

            container_status = OrderedDict()

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

            # scale
            container_status[container_name]['scale'] = self.NearRealTimeRIC_scale

            # create a entry in the return dictionary with the container name
            # and pass all info
            ret[container_name] = container_status[container_name]
        except:
            pass