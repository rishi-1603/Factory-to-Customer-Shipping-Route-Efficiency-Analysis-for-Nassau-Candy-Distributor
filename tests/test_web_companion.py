"""Public browser export must agree with the existing Python analysis."""
import json
from pathlib import Path
import pytest
from src import kpis
ROOT=Path(__file__).resolve().parents[1]
def payload():return json.loads((ROOT/'docs/assets/data.json').read_text())

def test_web_export_matches_python_engine(df):
    data=payload();rows=data['rows'];expected=kpis.lead_time_overview(df)
    assert len(rows)==expected['shipments']
    assert sum(r[5] for r in rows)/len(rows)==pytest.approx(expected['avg_lead_days'],abs=.005)
    assert len({(r[0],r[1]) for r in rows})==len(kpis.route_table(df))
    assert sum(r[6] for r in rows)==pytest.approx(data['expected']['sales'],abs=.005)


def test_web_export_excludes_personal_fields():
    data=payload()
    assert data['columns']==['factory','state','region','mode','date','lead','sales','profit']
    assert all(len(row)==8 for row in data['rows'])


def test_public_reports_and_media_are_real_files():
    docs=ROOT/'docs'
    for name in ['index.html','project-explanation.html','internship-reflection.html','assets/app.js','assets/style.css','assets/plotly.min.js','.nojekyll']:
        assert (docs/name).is_file()
    assert (docs/'project-report.pdf').read_bytes().startswith(b'%PDF')
    for name in ['project-walkthrough.mp4','internship-reflection-draft.mp4']:
        assert b'ftyp' in (docs/name).read_bytes()[:32]
    assert 'draft' in (docs/'internship-reflection.html').read_text().lower()
