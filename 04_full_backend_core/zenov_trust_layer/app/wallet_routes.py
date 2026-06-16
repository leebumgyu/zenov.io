from fastapi import APIRouter, HTTPException

from zenov_mobility.app.services.reward_service import RewardError, get_wallet_detail, list_wallet_details


router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])


@router.get("")
def list_wallets_view():
    return list_wallet_details()


@router.get("/{driver_id}")
def get_wallet_view(driver_id: str):
    try:
        return get_wallet_detail(driver_id)
    except RewardError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
