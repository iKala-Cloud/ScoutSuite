from ScoutSuite.providers.gcp.resources.cloudrun.cloudrun_services import Services
from ScoutSuite.providers.gcp.resources.cloudrun.cloudrun_jobs import Jobs
from ScoutSuite.providers.gcp.resources.projects import Projects

class Run(Projects):
    _children = [
        (Services, 'services'),
        #(Jobs, 'jobs')
    ]
