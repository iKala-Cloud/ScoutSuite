from ScoutSuite.providers.base.resources.base import Resources
from ScoutSuite.providers.gcp.facade.base import GCPFacade
from ScoutSuite.providers.gcp.resources.cloudrun.utils import get_environment_secrets


class Jobs(Resources):
    def __init__(self, facade: GCPFacade, project_id: str):
        super().__init__(facade)
        self.project_id = project_id

    async def fetch_all(self):
        raw_functions = await self.facade.cloudrun.get_run_jobs(self.project_id)

        print(raw_functions)
        for raw_function in raw_functions:
            function_id, function = self._parse_function(raw_function)
            self[function_id] = function

    def _parse_function(self, raw_function):
        run_dict = {}

        run_dict['id'] = raw_function['metadata']['uid']
        run_dict['name'] = raw_function['metadata']['name']
        
        # run_dict['timeout'] = raw_function['spec']['template']['spec']['timeoutSeconds']
        # run_dict['max_instances'] = raw_function['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/maxScale']

        # run_dict['url'] = raw_function['status']['address']['url']
        # run_dict['ingress_settings'] = raw_function['metadata']['annotations']['run.googleapis.com/ingress-status']
        
        # run_dict['service_account'] = raw_function['spec']['template']['spec']['serviceAccountName']
        # run_dict['bindings'] = raw_function['bindings']
        
        # # valueFrom secret manager
        # run_dict['container'] = raw_function['spec']['template']['spec']['containers']
        # run_dict['environment_variables'] = {env.get('name'): env.get('value', '') 
        #                                      for container in raw_function['spec']['template']['spec']['containers'] 
        #                                      for env in container.get('env', {})
        #                                     }
        # run_dict['environment_variables_secrets'] = get_environment_secrets(run_dict['environment_variables'])
        
        return run_dict['id'], run_dict
