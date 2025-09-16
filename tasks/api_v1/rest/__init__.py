from fastapi import APIRouter

from .tasks.views import router as tasks_router
from .tasks.views import router_list as tasks_list_router


router = APIRouter()


router.include_router(router=tasks_router, prefix='/task')
router.include_router(router=tasks_list_router, prefix='/tasks')




