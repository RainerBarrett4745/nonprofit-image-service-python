from pathlib import Path

from nonprofit_images import ImageRequest, build_prompt


def test_campaign_report_uses_a_report_prompt_for_the_named_audience() -> None:
    request = ImageRequest(
        kind="report",
        audience="monthly donors",
        message="March campaign reached 80 percent of its target.",
    )

    prompt = build_prompt(request)

    assert "campaign reporting" in prompt
    assert "monthly donors" in prompt
    assert "March campaign" in prompt
