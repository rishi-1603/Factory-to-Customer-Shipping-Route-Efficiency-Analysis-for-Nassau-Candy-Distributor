"""Export a de-identified browser companion dataset from the existing pipeline.
Run from the repository root: python scripts/build_web_data.py [--raw PATH]
The original Streamlit app and metric engine remain the primary Python implementation.
"""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src import config as C
from src.data_cleaning import load_raw,clean
from plotly.offline import get_plotlyjs
parser=argparse.ArgumentParser();parser.add_argument('--raw',default=str(C.RAW_CSV));args=parser.parse_args()
df,log=clean(load_raw(args.raw))
assets=ROOT/'docs/assets';assets.mkdir(exist_ok=True,parents=True)
from src.kpis import lead_time_overview,route_table
cols=[C.COL_FACTORY,C.COL_STATE,C.COL_REGION,C.COL_SHIP_MODE,'order_date_parsed',C.COL_LEAD,C.COL_SALES,C.COL_GROSS_PROFIT]
view=df[cols].copy();view['order_date_parsed']=view.order_date_parsed.dt.strftime('%Y-%m-%d')
result={'kind':'nassau','columns':['factory','state','region','mode','date','lead','sales','profit'],'rows':view.values.tolist(),'expected':{**lead_time_overview(df),'sales':round(float(df[C.COL_SALES].sum()),2),'profit':round(float(df[C.COL_GROSS_PROFIT].sum()),2),'routes':len(route_table(df))},'source_rows':len(df),'privacy':'Only analytical dimensions, dates and values; customer names, customer IDs, order IDs, cities and addresses excluded.'}
(assets/'data.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(assets/'plotly.min.js').write_text(get_plotlyjs(),encoding='utf-8')
print(json.dumps({'source_rows':len(df),'browser_rows':len(result['rows']),'expected':result['expected']},indent=2))
