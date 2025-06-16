import pytest
from fastapi import status
from sqlalchemy import select, insert
from app.models import ASIC, MWHRevenue
from uuid import uuid4
from datetime import datetime, timedelta

class TestMwhRevenue:

    @pytest.mark.asyncio(loop_scope="function")
    async def test_read_mwh_revenue(self, test_client, db_session):
        """Test reading mwh revenue."""

        # Create an ASIC and mwh revenue entries for it.
        asic_data = {
            "id": uuid4(),
            "asic_slug": "test-asic",
            "asic_name": "Test ASIC",
            "asic_power": 1000,
            "asic_hash_rate": 1000,
        }
        await db_session.execute(insert(ASIC).values(**asic_data))

        mwh_revenue_data = [
            {
                "id": uuid4(),
                "asic_id": asic_data["id"],
                "mwh_usd_revenue": 1000,
                "mwh_btc_revenue": 0.00001,
                "block_number": 1000,
                "mwh_revenue_timestamp": datetime.now(),
            },
            {
                "id": uuid4(),
                "asic_id": asic_data["id"],
                "mwh_usd_revenue": 1000,
                "mwh_btc_revenue": 0.00001,
                "block_number": 1000,
                "mwh_revenue_timestamp": datetime.now(),
            }
        ]
        for mwh_revenue in mwh_revenue_data:
            await db_session.execute(insert(MWHRevenue).values(**mwh_revenue))

        # Read mwh_revenue
        read_response = await test_client.get(
            "/mwh_revenue/?asic_id=" + str(asic_data["id"]) + "&timestamp_start=" + (datetime.now() - timedelta(days=1)).isoformat() + "&timestamp_end=" + datetime.now().isoformat()
        )
        assert read_response.status_code == status.HTTP_200_OK
        mwh_revenue = read_response.json()

        assert len(mwh_revenue) == 2
        assert any(str(asic_data["id"]) == str(row["asic_id"]) for row in mwh_revenue)
