from fastapi import APIRouter
from src.endpoints import users,etc,agency,assets,branch,repair,doc,license,manage

router = APIRouter()
router.include_router(users.router)
router.include_router(assets.router)
router.include_router(etc.router)
router.include_router(agency.router)
router.include_router(branch.router)
router.include_router(repair.router)
router.include_router(doc.router)
router.include_router(license.router)
router.include_router(manage.router)


