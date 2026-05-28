from api.router.device import router as device_router
from api.router.policy import router as policy_router
from api.router.address_group import router as address_group_router
from api.router.port_group import router as port_group_router
from api.router.log import router as log_router

__all__ = ['device_router', 'policy_router', 'address_group_router', 'port_group_router', 'log_router']
