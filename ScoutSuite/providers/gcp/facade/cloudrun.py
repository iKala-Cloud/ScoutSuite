from ScoutSuite.core.console import print_exception
from ScoutSuite.providers.gcp.facade.basefacade import GCPBaseFacade
from ScoutSuite.providers.gcp.facade.utils import GCPFacadeUtils
from ScoutSuite.providers.utils import map_concurrently, run_concurrently, get_and_set_concurrently

import json
class CloudrunFacade(GCPBaseFacade):
    def __init__(self):
        # The version needs to be set per-function
        super().__init__('run', 'v1')  # API Client

    async def get_run_services(self, project_id: str):
        return await self._get_services("v1", project_id)
    
    async def get_run_jobs(self, project_id: str):
        return await self._get_jobs("v2", project_id)


    async def _get_services(self, api_version: str, project_id: str):
        try:
            # get list of cloud run services
            list_results = await self._list_services_version(project_id, api_version)
            # get list of cloud run names
            # projects/{project_id_or_number}/regions/{region}/services/
            service_list = [
                f"projects/{run.get('metadata').get('namespace')}/locations/{run.get('metadata').get('labels').get('cloud.googleapis.com/location')}/services/{run.get('metadata').get('name')}" for run in list_results]
        except Exception as e:
            print_exception(f'Failed to list Cloud run (Services) ({api_version}): {e}')
            return []
        else:
            run = await map_concurrently(self._get_services_version, service_list, api_version=api_version)
            # print(run)
            await get_and_set_concurrently([self._get_and_set_services_iam_policy],
                                           run,
                                           api_version=api_version)
            return run
    
    async def _get_jobs(self, api_version: str, project_id: str):
        try:
            # get list of cloud run jobs
            list_results = await self._list_jobs_version(project_id, api_version)
            # get list of cloud run names
            # projects/{project_id_or_number}/regions/{region}/jobs/
            print(list_results)
            service_list = [
                f"projects/{run.get('metadata').get('namespace')}/locations/{run.get('metadata').get('labels').get('cloud.googleapis.com/location')}/jobs/{run.get('metadata').get('name')}" for run in list_results]
        except Exception as e:
            print_exception(f'Failed to list Cloud run (Jobs) ({api_version}): {e}')
            return []
        else:
            run = await map_concurrently(self._get_jobs_version, service_list, api_version=api_version)
            # print(run)
            await get_and_set_concurrently([self._get_and_set_jobs_iam_policy],
                                           run,
                                           api_version=api_version)
            return run

    async def _list_services_version(self, project_id: str, api_version: str):
        run_client = self._build_arbitrary_client(self._client_name, api_version, force_new=True)
        parent = f'projects/{project_id}/locations/-'
        services = run_client.projects().locations()
        services_tmp = run_client.projects().locations().services()
        
        request = services_tmp.list(parent=parent)
        
        results = await GCPFacadeUtils.get_all('items', request, services)
        return results
    
    async def _list_jobs_version(self, project_id: str, api_version: str):
        run_client = self._build_arbitrary_client(self._client_name, "v1", force_new=True)

        parent = f'namespaces/{project_id}'
        jobs = run_client.namespaces().jobs()
        request = jobs.list(parent=parent)
        
        results = await GCPFacadeUtils.get_all('items', request, jobs)
        return results

    async def _get_services_version(self, name: str, api_version: str):
        try:
            run_client = self._build_arbitrary_client(self._client_name, api_version, force_new=True)
            services = run_client.projects().locations().services()
            request = services.get(name=name)
            return await run_concurrently(lambda: request.execute())
        except Exception as e:
            print_exception(f'Failed to get Cloud run (Services) ({api_version}): {e}')
            return {}
        
    async def _get_jobs_version(self, name: str, api_version: str):
        try:
            run_client = self._build_arbitrary_client(self._client_name, api_version, force_new=True)
            jobs = run_client.projects().locations().jobs()
            request = jobs.get(name=name)
            return await run_concurrently(lambda: request.execute())
        except Exception as e:
            print_exception(f'Failed to get Cloud run (Jobs) ({api_version}): {e}')
            return {}

    async def _get_and_set_services_iam_policy(self, run, api_version: str):
        try:
            run_client = self._build_arbitrary_client(self._client_name, api_version, force_new=True)
            runs = run_client.projects().locations().services()
            request = runs.getIamPolicy(resource=f"projects/{run.get('metadata').get('namespace')}/locations/{run.get('metadata').get('labels').get('cloud.googleapis.com/location')}/services/{run.get('metadata').get('name')}")
            policy = await run_concurrently(lambda: request.execute())
            run['bindings'] = policy.get('bindings', [])
        except Exception as e:
            print_exception(f'Failed to get bindings for Cloud run (Services) error'
                            f'({api_version}): {e}')
            run['bindings'] = []

    async def _get_and_set_jobs_iam_policy(self, run, api_version: str):
        try:
            run_client = self._build_arbitrary_client(self._client_name, api_version, force_new=True)
            jobs = run_client.projects().locations().jobs()
            request = jobs.getIamPolicy(resource=f"projects/{run.get('metadata').get('namespace')}/locations/{run.get('metadata').get('labels').get('cloud.googleapis.com/location')}/jobs/{run.get('metadata').get('name')}")
            policy = await run_concurrently(lambda: request.execute())
            run['bindings'] = policy.get('bindings', [])
        except Exception as e:
            print_exception(f'Failed to get bindings for Cloud run (Jobs) error'
                            f'({api_version}): {e}')
            run['bindings'] = []
