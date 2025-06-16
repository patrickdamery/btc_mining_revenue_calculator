from fastapi.routing import APIRoute
from app.utils import simple_generate_unique_route_id, block_subsidy, walk_chain, amap
import pytest

def test_simple_generate_unique_route_id(mocker):
    mock_route = mocker.Mock(spec=APIRoute)

    mock_route.tags = ["auth"]
    mock_route.name = "authenticate_user"

    unique_id = simple_generate_unique_route_id(mock_route)

    assert unique_id == "auth-authenticate_user"


def test_block_subsidy():
    # No halving
    assert block_subsidy(0) == 50.0
    # First halving at 210_000
    assert block_subsidy(210_000) == 25.0
    # After 64 halvings, subsidy is zero
    assert block_subsidy(210_000 * 64) == 0.0


@pytest.mark.asyncio
async def test_walk_chain_and_amap():
    # walk_chain: doubles until next is None
    async def fetch(x):
        return x * 2
    def nxt(x):
        return x + 1 if x < 3 else None

    agen = walk_chain(1, fetch, nxt)
    results = []
    async for v in agen:
        results.append(v)
    # Should yield for heights: fetch(1)=2 -> nxt(2)=3; fetch(3)=6 -> nxt(6)=None
    assert results == [2, 6]

    # amap: square each value
    async def base_gen():
        for i in [1, 2, 3]:
            yield i
    async def square(x):
        return x * x

    mapped = amap(square, base_gen())
    squares = []
    async for v in mapped:
        squares.append(v)
    assert squares == [1, 4, 9]
