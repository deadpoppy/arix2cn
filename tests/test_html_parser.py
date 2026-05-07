"""Tests for arXiv HTML parsing."""

from __future__ import annotations

from arxiv2md.html_parser import parse_arxiv_html


def test_extracts_metadata_and_sections() -> None:
    html = """
    <html>
      <body>
        <article class="ltx_document">
          <h1 class="ltx_title ltx_title_document">Sample Title</h1>
          <div class="ltx_authors">
            <span class="ltx_text ltx_font_bold">Alice<sup>1</sup></span>
            <span class="ltx_text ltx_font_bold">Bob<sup>2</sup></span>
          </div>
          <div class="ltx_abstract">
            <p>Abstract text.</p>
          </div>
          <section class="ltx_section" id="S1">
            <h2 class="ltx_title ltx_title_section">1 Intro</h2>
            <div class="ltx_para"><p>Intro text.</p></div>
          </section>
        </article>
      </body>
    </html>
    """

    parsed = parse_arxiv_html(html)

    assert parsed.title == "Sample Title"
    assert parsed.authors == ["Alice", "Bob"]
    assert parsed.abstract == "Abstract text."
    assert parsed.sections
    assert parsed.sections[0].title == "1 Intro"
    assert parsed.sections[0].html and "Intro text." in parsed.sections[0].html


def test_extracts_affiliations_and_emails_in_authors_block() -> None:
    """Authors block should preserve affiliations and emails (arXiv issue)."""
    html = """
    <html>
      <body>
        <article class="ltx_document">
          <h1 class="ltx_title ltx_title_document">Sample Title</h1>
          <div class="ltx_authors">
            <span class="ltx_creator ltx_role_author">
              <span class="ltx_personname">Alice</span>
            </span>
            <span class="ltx_author_before">\u2003\u2003</span>
            <span class="ltx_creator ltx_role_author">
              <span class="ltx_personname">Bob</span>
              <span class="ltx_author_notes">
                <span class="ltx_contact ltx_role_address">
                  <sup class="ltx_sup">1</sup> Example University, USA
                </span>
                <span class="ltx_contact ltx_role_email">
                  <a href="mailto:bob@example.edu">bob@example.edu</a>
                </span>
              </span>
            </span>
          </div>
          <div class="ltx_abstract">
            <p>Abstract text.</p>
          </div>
        </article>
      </body>
    </html>
    """

    parsed = parse_arxiv_html(html)

    assert parsed.authors == ["Alice", "Bob"]
    assert parsed.authors_block is not None
    assert "Alice" in parsed.authors_block
    assert "Bob" in parsed.authors_block
    assert "Example University, USA" in parsed.authors_block
    assert "bob@example.edu" in parsed.authors_block
    # Footnote markers should be stripped
    assert "1" not in parsed.authors_block or parsed.authors_block.count("1") == 0


def test_extracts_contact_from_footnote_and_drops_contribution_statement() -> None:
    """Footnotes may contain contact info *or* long contribution statements."""
    html = """
    <html>
      <body>
        <article class="ltx_document">
          <h1 class="ltx_title ltx_title_document">Sample Title</h1>
          <div class="ltx_authors">
            <span class="ltx_creator ltx_role_author">
              <span class="ltx_personname">
                Alice
                <span class="ltx_note ltx_role_footnote" id="fn1">
                  <sup class="ltx_note_mark">1</sup>
                  <span class="ltx_note_outer">
                    <span class="ltx_note_content">
                      <span class="ltx_tag ltx_tag_note">1</span>
                      Example Institute. email: alice@example.edu
                    </span>
                  </span>
                </span>
                and Bob
                <span class="ltx_note ltx_role_footnote" id="fn2">
                  <sup class="ltx_note_mark">2</sup>
                  <span class="ltx_note_outer">
                    <span class="ltx_note_content">
                      <span class="ltx_tag ltx_tag_note">2</span>
                      Equal contribution. Listing order is random.
                      Bob designed the experiments and Alice wrote the code.
                      This is a long multi-sentence author contribution statement
                      that should not appear in the authors block.
                    </span>
                  </span>
                </span>
              </span>
            </span>
          </div>
          <div class="ltx_abstract">
            <p>Abstract text.</p>
          </div>
        </article>
      </body>
    </html>
    """

    parsed = parse_arxiv_html(html)

    assert parsed.authors_block is not None
    assert "Alice" in parsed.authors_block
    assert "Bob" in parsed.authors_block
    # Contact info from the first footnote should be preserved
    assert "Example Institute" in parsed.authors_block
    assert "alice@example.edu" in parsed.authors_block
    # The contribution statement must be stripped
    assert "Equal contribution" not in parsed.authors_block
    assert "designed the experiments" not in parsed.authors_block
    # Footnote markers should be stripped
    assert parsed.authors_block.count("1") == 0
