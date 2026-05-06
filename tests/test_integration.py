"""Integration tests that hit real arXiv HTML and verify image URLs."""

from __future__ import annotations

import re

import httpx
import pytest

from arxiv2md.ingestion import ingest_paper


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.asyncio
async def test_2602_23765_image_urls_are_reachable() -> None:
    """Regression test for doubled image path segments.

    Paper 2602.23765 (v2) uses image paths like ``2602.23765v2/x3.png``.
    When the input arXiv ID does not include a version number, the old code
    produced URLs such as
    ``https://arxiv.org/html/2602.23765/2602.23765v2/x3.png`` (404).
    This test fetches the real HTML, runs the full pipeline, and HEAD-requests
    every image URL to make sure they are all reachable.
    """
    result, _metadata = await ingest_paper(
        arxiv_id="2602.23765",
        version=None,
        html_url="https://arxiv.org/html/2602.23765",
        remove_refs=True,
        remove_toc=True,
        remove_inline_citations=False,
        section_filter_mode="exclude",
        sections=[],
    )

    md = result.content
    # Extract image URLs from markdown: ![alt](url).
    # We restrict to URLs ending with a known image extension so that nested
    # markdown links inside figure alt text (e.g.
    # ``![caption [Section](url1).](url2)``) do not pollute the list.
    image_urls = re.findall(
        r"!\[.*?\]\((https?://[^\s)]+\.(?:png|jpe?g|gif|svg))\)", md, re.IGNORECASE
    )

    assert image_urls, "No image URLs found in the generated markdown"

    # Filter out data URIs just in case
    image_urls = [u for u in image_urls if not u.startswith("data:")]

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for url in image_urls:
            # Skip non-arxiv URLs (e.g. static logos)
            if "arxiv.org" not in url:
                continue
            response = await client.head(url)
            assert response.status_code == 200, (
                f"Image URL returned {response.status_code}: {url}\n"
                f"If the path contains a duplicated segment like "
                f"'/2602.23765/2602.23765v2/', the bug is not fixed."
            )


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.asyncio
async def test_2501_11120v1_standard_relative_image_urls() -> None:
    """Test that standard relative image paths are also resolved correctly.

    Paper 2501.11120v1 uses paths like ``x1.png`` and
    ``extracted/6141037/figures/...`` which are standard directory-relative
    paths and should still work after the fix.
    """
    result, _metadata = await ingest_paper(
        arxiv_id="2501.11120v1",
        version="v1",
        html_url="https://arxiv.org/html/2501.11120v1",
        remove_refs=True,
        remove_toc=True,
        remove_inline_citations=False,
        section_filter_mode="exclude",
        sections=[],
    )

    md = result.content
    image_urls = re.findall(
        r"!\[.*?\]\((https?://[^\s)]+\.(?:png|jpe?g|gif|svg))\)", md, re.IGNORECASE
    )
    image_urls = [u for u in image_urls if not u.startswith("data:")]

    assert image_urls, "No image URLs found in the generated markdown"

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for url in image_urls:
            if "arxiv.org" not in url:
                continue
            response = await client.head(url)
            assert response.status_code == 200, (
                f"Image URL returned {response.status_code}: {url}"
            )
