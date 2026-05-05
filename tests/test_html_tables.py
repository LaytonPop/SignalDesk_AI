from intel_analyst.processing.html_tables import extract_tables_from_html


def test_extract_tables_from_html():
    html = """
    <html>
      <body>
        <table>
          <tr><th>公司</th><th>营收</th></tr>
          <tr><td>A</td><td>100</td></tr>
          <tr><td>B</td><td>200</td></tr>
        </table>
      </body>
    </html>
    """
    result = extract_tables_from_html(html=html, source_name="demo", article_title="Quarterly Report")
    assert len(result.tables) == 1
    assert result.tables[0].row_count == 2
    assert result.table_paths
