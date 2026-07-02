from validate_equity_report import validate_manifest


def _complete_manifest():
    return {
        "report": {
            "symbol": "603212.SH",
            "as_of": "2026-07-01T08:00:00Z",
            "status": "complete",
            "data_status": "complete",
        },
        "metrics": {
            "price": 45.0,
            "currency": "CNY",
            "volume": 2_000_000,
            "market_cap": 20_000_000_000,
        },
        "agents": [
            {"agent": name, "success": True, "degraded": False, "analysis": "ok"}
            for name in ("technical", "fundamental", "risk")
        ],
        "evidence": [
            {"kind": kind, "source": "provider", "as_of": "2026-07-01", "verified": True}
            for kind in ("market_data", "filing", "risk")
        ],
        "sections": [
            "executive_summary",
            "fundamentals",
            "valuation",
            "technical",
            "risk",
            "scenarios",
            "sources",
        ],
    }


def test_complete_manifest_passes():
    assert validate_manifest(_complete_manifest())["decision"] == "complete"


def test_missing_price_blocks():
    manifest = _complete_manifest()
    manifest["metrics"]["price"] = None

    result = validate_manifest(manifest)

    assert result["decision"] == "blocked"
    assert "reference price must be positive" in result["blocking_reasons"]


def test_missing_filing_is_partial():
    manifest = _complete_manifest()
    manifest["evidence"] = [
        item for item in manifest["evidence"] if item["kind"] != "filing"
    ]

    result = validate_manifest(manifest)

    assert result["decision"] == "partial"
    assert result["missing_evidence"] == ["filing"]
