from pathlib import Path
from io import BytesIO
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parent
SUMMARY_DIR=ROOT/'data'/'processed_data'/'cities'
CITIES={
'Pune':(18.5204,73.8567),'Mumbai':(19.0760,72.8777),'Kolhapur':(16.7050,74.2433),'Sangli':(16.8524,74.5815),'Nashik':(19.9975,73.7898),'Nagpur':(21.1458,79.0882),'Solapur':(17.6599,75.9064),'Satara':(17.6805,74.0183),'Thane':(19.2183,72.9781),'Chhatrapati Sambhajinagar':(19.8762,75.3433),'Bengaluru':(12.9716,77.5946),'Hyderabad':(17.3850,78.4867),'New Delhi':(28.6139,77.2090),'Chennai':(13.0827,80.2707),'Ahmedabad':(23.0225,72.5714),'Kolkata':(22.5726,88.3639),'Jaipur':(26.9124,75.7873),'Surat':(21.1702,72.8311),'Indore':(22.7196,75.8577),'Bhopal':(23.2599,77.4126)}
ALIASES={'bangalore':'Bengaluru','delhi':'New Delhi','aurangabad':'Chhatrapati Sambhajinagar','bombay':'Mumbai'}
st.set_page_config(page_title='Urban Expansion Analytics',page_icon='🌍',layout='wide')
st.markdown('''<style>.stApp{background:linear-gradient(145deg,#0b1020,#14112e 58%,#1b1031);color:#f5f2ff}section[data-testid="stSidebar"]{background:#100f24;border-right:1px solid #30284f}.block-container{max-width:1600px;padding-top:1.2rem}h1,h2,h3{color:#f6f2ff}div[data-testid="stMetric"]{background:linear-gradient(135deg,#1b1b3a,#28204a);padding:17px;border:1px solid #39315f;border-radius:16px}div[data-testid="stMetricLabel"]{color:#b8b4dc}div[data-testid="stMetricValue"]{color:#fff}</style>''',unsafe_allow_html=True)
def norm_city(s):
 t=str(s).strip().replace('_',' ').title(); return ALIASES.get(t.lower(),t)
def load_data():
 rows=[]
 for p in SUMMARY_DIR.rglob('*.csv') if SUMMARY_DIR.exists() else []:
  try: df=pd.read_csv(p)
  except Exception: continue
  cols={str(c).lower().strip():c for c in df.columns}
  cc=next((cols[n] for n in ['class_name','land_cover','land_use','class','category'] if n in cols),None)
  ac=next((cols[n] for n in ['area_square_km','area_km2','area_sq_km','area_km_sq','area'] if n in cols),None)
  dc=next((cols[n] for n in ['date','observation_date','acquisition_date','timestamp'] if n in cols),None)
  yc=next((cols[n] for n in ['city','city_name'] if n in cols),None)
  sc=next((cols[n] for n in ['data_status','provenance','source_type'] if n in cols),None)
  if not cc or not ac: continue
  city=norm_city(df[yc].dropna().iloc[0]) if yc and not df[yc].dropna().empty else ''
  if not city:
   try: city=norm_city(p.parts[[x.lower() for x in p.parts].index('cities')+1])
   except Exception: city=norm_city(p.parent.parent.name)
  for _,r in df.iterrows():
   try: area=float(r[ac])
   except Exception: continue
   if pd.isna(area): continue
   dt=pd.to_datetime(r[dc],errors='coerce') if dc else pd.NaT
   if pd.isna(dt): dt=pd.Timestamp(p.stat().st_mtime,unit='s').normalize()
   status=str(r[sc]) if sc and pd.notna(r[sc]) else 'UNVERIFIED SOURCE — verify whether these are measured observations'
   is_demo='demo' in status.lower() or 'synthetic' in status.lower() or 'illustrative' in status.lower()
   rows.append({'city':city,'date':pd.Timestamp(dt).normalize(),'class_name':str(r[cc]).replace('_',' ').title(),'area_square_km':area,'source_file':str(p.relative_to(ROOT)),'data_status':status,'is_demo':is_demo})
 return pd.DataFrame(rows)
def demo_data():
 rows=[]
 for dt, vals in [('2025-10-20',{'Built-Up':28.7,'Vegetation':51.8,'Agriculture':73.9,'Water':8.4,'Bare Land':12.1}),('2026-10-05',{'Built-Up':32.4,'Vegetation':48.7,'Agriculture':71.2,'Water':8.5,'Bare Land':13.0})]:
  for cls,area in vals.items(): rows.append({'city':'Pune','date':pd.Timestamp(dt),'class_name':cls,'area_square_km':area,'source_file':'DEMO VALUES','data_status':'DEMO — illustrative values, not satellite-derived','is_demo':True})
 return pd.DataFrame(rows)
data=load_data(); demo=data.empty
if demo: data=demo_data()
if not data.empty and 'is_demo' not in data.columns: data['is_demo']=False
if not data.empty and 'data_status' not in data.columns: data['data_status']='UNVERIFIED SOURCE — verify before reporting'
with st.sidebar:
 st.markdown('## 🌍 Urban Analytics'); page=st.radio('Navigation',['Overview','Land-Use Analysis','Urban Expansion','Data Explorer','Reports'],label_visibility='collapsed'); st.divider(); st.markdown('### Analysis Controls')
 cities=sorted(set(CITIES)|set(data.city.dropna().unique())); city=st.selectbox('Choose city',cities,index=cities.index('Pune') if 'Pune' in cities else 0)
 cd=data[data.city.str.casefold()==city.casefold()].copy()
 low,high=(cd.date.min().date(),cd.date.max().date()) if not cd.empty else (date(2025,1,1),date(2026,12,31))
 period=st.date_input('Choose analysis period',value=(low,high),min_value=date(2000,1,1),max_value=date(2100,12,31)); st.divider(); st.caption('Data source: local processed summaries')
 lat, lon = CITIES.get(city, (None, None))
 if lat is not None: st.caption(f'📍 Location: {lat:.4f}° N, {lon:.4f}° E')
start,end=period if len(period)==2 else (period[0],period[0])
cd=data[data.city.str.casefold()==city.casefold()].copy(); filtered=cd[(cd.date.dt.date>=start)&(cd.date.dt.date<=end)].copy()
st.title('🌍 Urban Expansion & Land-Use Analytics'); st.caption('Satellite observations • Land-cover classification • Change detection • Reports')
if filtered.empty:
 st.warning(f'No observations found for {city} in the selected date range. Try a wider date range or add a compatible CSV under data/processed_data/cities/<city>/classification/.')
 lat, lon = CITIES.get(city, (20.5937, 78.9629))
 st.markdown('### 📍 Selected city location')
 st.metric('Latitude', f'{lat:.4f}°'); st.metric('Longitude', f'{lon:.4f}°')
 locdf=pd.DataFrame([{'City':name,'Latitude':coord[0],'Longitude':coord[1],'Selected':name==city} for name,coord in CITIES.items()])
 figloc=px.scatter_geo(locdf,lat='Latitude',lon='Longitude',hover_name='City',color='Selected',color_discrete_map={True:'#f15bb5',False:'#8b7cf6'},projection='natural earth',scope='asia')
 figloc.update_geos(lataxis_range=[5,38],lonaxis_range=[65,100],showland=True,landcolor='#17172f',showocean=True,oceancolor='#0b1020', showcountries=True,countrycolor='#65558b')
 figloc.update_layout(paper_bgcolor='#17172f',plot_bgcolor='#17172f',font_color='#f5f2ff',height=420,margin=dict(l=0,r=0,t=10,b=0),legend_title_text='Selected city')
 st.plotly_chart(figloc,use_container_width=True)
 st.info('Location markers show approximate city-centre coordinates. They are not land-use boundaries or classified satellite pixels.')
 st.stop()
agg=filtered.groupby(['date','class_name'],as_index=False).area_square_km.sum(); obs=sorted(agg.date.unique()); latest=agg[agg.date==max(obs)]; prev=agg[agg.date==max([d for d in obs if d<max(obs)])] if len(obs)>1 else pd.DataFrame(columns=agg.columns)
built=latest[latest.class_name.str.contains('built|urban',case=False,regex=True)].area_square_km.sum(); veg=latest[latest.class_name.str.contains('vegetation|forest|green',case=False,regex=True)].area_square_km.sum(); agri=latest[latest.class_name.str.contains('agri|crop',case=False,regex=True)].area_square_km.sum()
if page=='Overview':
 st.subheader(f'📍 {city} — Selected Period'); st.caption(f'{start:%d %B %Y} to {end:%d %B %Y} • {len(obs)} observation date(s)'); lat,lon=CITIES.get(city,(None,None)); st.markdown(f'**City-centre coordinates:** {lat:.4f}° N, {lon:.4f}° E' if lat is not None else '**City-centre coordinates:** unavailable'); a,b,c,d=st.columns(4); a.metric('Built-up area',f'{built:.2f} km²' if built else 'Not classified'); b.metric('Vegetation',f'{veg:.2f} km²' if veg else 'Not classified'); c.metric('Agriculture',f'{agri:.2f} km²' if agri else 'Not classified'); d.metric('Observation dates',len(obs))
 st.markdown('### 📍 City locations across India')
 locdf=pd.DataFrame([{'City':name,'Latitude':coord[0],'Longitude':coord[1],'Selected':name==city} for name,coord in CITIES.items()])
 figloc=px.scatter_geo(locdf,lat='Latitude',lon='Longitude',hover_name='City',color='Selected',color_discrete_map={True:'#f15bb5',False:'#8b7cf6'},projection='natural earth',scope='asia')
 figloc.update_geos(lataxis_range=[5,38],lonaxis_range=[65,100],showland=True,landcolor='#17172f',showocean=True,oceancolor='#0b1020',showcountries=True,countrycolor='#65558b')
 figloc.update_layout(paper_bgcolor='#17172f',plot_bgcolor='#17172f',font_color='#f5f2ff',height=420,margin=dict(l=0,r=0,t=10,b=0),legend_title_text='Selected city')
 st.plotly_chart(figloc,use_container_width=True)
 st.caption('City-centre markers are approximate reference locations; this is not a classified satellite raster map.')
 left,right=st.columns([1.2,1])
 with left:
  st.markdown('### 🛰️ Land-cover composition'); fig=px.treemap(latest,path=['class_name'],values='area_square_km',color='class_name',color_discrete_sequence=['#9b5de5','#00bbf9','#00f5d4','#fee440','#f15bb5','#f8961e']); fig.update_layout(paper_bgcolor='#17172f',plot_bgcolor='#17172f',font_color='#f5f2ff',height=340,margin=dict(l=5,r=5,t=10,b=5),showlegend=False); st.plotly_chart(fig,use_container_width=True); st.caption('Summary visualization only. A true raster overlay requires georeferenced classification data.')
 with right:
  st.markdown('### 🥧 Land-use distribution'); fig=px.pie(latest,names='class_name',values='area_square_km',hole=.58,color_discrete_sequence=['#9b5de5','#00bbf9','#00f5d4','#fee440','#f15bb5','#f8961e']); fig.update_layout(paper_bgcolor='#17172f',font_color='#f5f2ff',height=340,margin=dict(l=5,r=5,t=10,b=5),legend=dict(orientation='h',y=-.2)); st.plotly_chart(fig,use_container_width=True)
 st.markdown('### 📊 Land-use area by class and observation'); fig=px.bar(agg,x='date',y='area_square_km',color='class_name',barmode='group',labels={'date':'Observation date','area_square_km':'Area (km²)','class_name':'Land-use class'},color_discrete_sequence=['#9b5de5','#00bbf9','#00f5d4','#fee440','#f15bb5','#f8961e']); fig.update_layout(paper_bgcolor='#17172f',plot_bgcolor='#17172f',font_color='#f5f2ff',height=360); st.plotly_chart(fig,use_container_width=True)
 st.markdown('### 🔎 Change between observations')
 if prev.empty: st.info('A second observation date is needed for change detection.')
 else:
  ch=latest[['class_name','area_square_km']].merge(prev[['class_name','area_square_km']],on='class_name',how='outer',suffixes=('_later','_earlier')).fillna(0); ch['Change (km²)']=ch.area_square_km_later-ch.area_square_km_earlier; ch['Change (%)']=ch.apply(lambda r:100*r['Change (km²)']/r.area_square_km_earlier if r.area_square_km_earlier else None,axis=1); ch=ch.rename(columns={'class_name':'Land-use class','area_square_km_earlier':'Earlier area (km²)','area_square_km_later':'Later area (km²)'}); st.dataframe(ch.round(2),use_container_width=True,hide_index=True)
elif page=='Land-Use Analysis':
 st.subheader('🗺️ Land-Use Analysis'); fig=px.bar(latest.sort_values('area_square_km',ascending=False),x='class_name',y='area_square_km',color='class_name',text_auto='.2f',color_discrete_sequence=['#9b5de5','#00bbf9','#00f5d4','#fee440','#f15bb5','#f8961e']); fig.update_layout(paper_bgcolor='#17172f',plot_bgcolor='#17172f',font_color='#f5f2ff',showlegend=False,yaxis_title='Area (km²)',xaxis_title=''); st.plotly_chart(fig,use_container_width=True); st.dataframe(latest,use_container_width=True,hide_index=True)
elif page=='Urban Expansion':
 st.subheader('📈 Urban Expansion & Change Detection'); urban=agg[agg.class_name.str.contains('built|urban',case=False,regex=True)]
 if urban.empty: st.warning('No class labelled Built-Up or Urban was found in the processed summaries.')
 else:
  fig=px.line(urban,x='date',y='area_square_km',markers=True,labels={'date':'Observation date','area_square_km':'Built-up area (km²)'}); fig.update_traces(line_color='#c084fc',line_width=4,marker_size=10); fig.update_layout(paper_bgcolor='#17172f',plot_bgcolor='#17172f',font_color='#f5f2ff'); st.plotly_chart(fig,use_container_width=True)
  if len(urban)>1: st.metric('Built-up area change',f'{urban.iloc[-1].area_square_km-urban.iloc[0].area_square_km:+.2f} km²')
 if prev.empty: st.info('Select a period with at least two observation dates.')
 else:
  ch=latest[['class_name','area_square_km']].merge(prev[['class_name','area_square_km']],on='class_name',how='outer',suffixes=('_later','_earlier')).fillna(0); ch['Change (km²)']=ch.area_square_km_later-ch.area_square_km_earlier; st.dataframe(ch.round(2),use_container_width=True,hide_index=True)
elif page=='Data Explorer':
 st.subheader('📋 Data Explorer'); st.dataframe(filtered.sort_values(['date','class_name']),use_container_width=True,hide_index=True); st.download_button('⬇️ Download CSV',filtered.to_csv(index=False).encode(),f'{city.lower().replace(" ","_")}_land_use.csv','text/csv')
else:
 st.subheader('📄 Download analysis report'); st.write(f'**City:** {city}  \n**Period:** {start:%d %b %Y} – {end:%d %b %Y}  \n**Observation dates:** {len(obs)}'); st.download_button('⬇️ Export data as CSV',filtered.to_csv(index=False).encode(),f'{city.lower().replace(" ","_")}_analysis.csv','text/csv')
 try:
  from reportlab.lib.pagesizes import A4
  from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
  from reportlab.lib import colors
  from reportlab.lib.styles import getSampleStyleSheet
  buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4); styles=getSampleStyleSheet(); story=[Paragraph('Urban Expansion &amp; Land-Use Analytics Report',styles['Title']),Spacer(1,12),Paragraph(f'City: {city}',styles['Heading2']),Paragraph(f'Period: {start:%d %B %Y} to {end:%d %B %Y}',styles['Normal']),Paragraph(f'Observation dates: {len(obs)}',styles['Normal']),Spacer(1,12),Paragraph('Latest land-use summary',styles['Heading2'])]; table=[['Land-use class','Area (km²)']]+[[str(r.class_name),f'{r.area_square_km:.2f}'] for r in latest.itertuples()]; t=Table(table,repeatRows=1); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#30245b')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.grey),('PADDING',(0,0),(-1,-1),7)])); story += [t]; doc.build(story); st.download_button('⬇️ Download PDF report',buf.getvalue(),f'{city.lower().replace(" ","_")}_urban_expansion_report.pdf','application/pdf')
 except ImportError: st.warning('PDF library missing. Run: pip install reportlab')
st.divider(); st.caption('Urban Expansion Analytics • Local processed data • Verify coverage and classification accuracy before reporting.')
