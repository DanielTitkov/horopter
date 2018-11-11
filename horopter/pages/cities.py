# from database import Session, City, Result
from ..utils.helpers import value_from_json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

import sys
sys.path.append('../../')
import config

from server import app, Session, Result, City, Article
from sqlalchemy import func
from datetime import datetime
import pandas as pd
import json

config = config.Config
mapbox_access_token = config.MAPBOX_ACCESS_TOKEN

markdown_intro = '''
### Города

Здесь можно посмотреть, в каком городе больше каких новостей - хороших, плохих, нейтральных. 
* К **хорошим** новостям в основном относятся новости, в которых говорится о научных открытиях,
о спасениях, ремонте дорог и строительстве новых объектов, иногда о праздниках.
* В список **нейтральных** в основном попадают новости касающиется отдельных лиц
(события "из жизни звезд", например) и не имеющие влияния на состояния и настроение общества,
не связанные со смертью и серезными проблемами, а также новости о большинстве спортивных событий и т.д.
* К **плохим** относятся новости о преступлениях, смертях, ДТП и стихийных бедствиях. 

Размер отметки города на карте соотвестует стандартизованому
*количеству новостей* из этого города за анализируемый период 
(может не соответствовать размеру города с точки зрения территории и населения).
'''

markdown_method = '''
### Метод

Сбор новостей производится каждую неделю. 
Оценка тональности новостей производится автоматически, 
поэтому в некоторых случаях приведенная тональность может быть некорректной. 
Однако в целом точность оценок не менее 80%.

Оценка производится с помощью предобученной модели. 
'''

GOOD_COLOR = '#5df322'
BAD_COLOR = '#e84a5f'
NEUTRAL_COLOR = '#5f5f5f'
polarity_alias = {'pos':'Хорошие новости', 
                  'net': 'Нейтральные новости', 
                  'neg': 'Плохие новости'}
labels = polarity_alias.keys()

session = Session()
city_data = session.query(func.max(Result.timestamp), 
                  Result.summary, 
                  City.city_name, 
                  City.coordinates).\
        join(City, Result.city_id == City.city_id).\
        group_by(City.city_id).all()


columns=['timestamp', 'summary', 'city', 'coordinates']
city_df = pd.DataFrame.from_records(city_data, columns=columns)
city_df[['lat', 'lon']] = city_df['coordinates'].str.split(',', expand=True)

city_df['pos'] = city_df.summary.apply(value_from_json, path='polarity.positive')
city_df['neg'] = city_df.summary.apply(value_from_json, path='polarity.negative')
city_df['net'] = city_df.summary.apply(value_from_json, path='polarity.neutral')

city_df['P'] = city_df.pos / (city_df.pos + city_df.neg + city_df.net)
city_df['desc'] = city_df.city + '<br>' + \
                    'Хорошие: ' + city_df.pos.astype(str) + \
                    '<br>Нейтральные: ' + city_df.net.astype(str) + \
                    '<br>Плохие: ' + city_df.neg.astype(str)
city_df['amount'] = city_df.pos + city_df.neg + city_df.net
city_df['std_amount'] = 2*(city_df.amount - city_df.amount.mean()) / city_df.amount.std() + 5.5 


scl = [ [0, GOOD_COLOR], [1, BAD_COLOR] ]

city_graph_data = [
    go.Scattermapbox(
        lat=city_df['lat'],
        lon=city_df['lon'],
        mode='markers',
        marker = dict(
            size = city_df['std_amount'].dropna()*1.75,
            opacity = 0.8,
            reversescale = True,
            autocolorscale = False,
            symbol = 'circle',
            colorscale = scl,
            cmin = 0,
            color = city_df['P'],
            cmax = city_df['P'].max(),
        ),
        text=city_df['desc'],
        hoverinfo='text'
    )]

city_graph_layout = go.Layout(
    title='Nuclear Waste Sites on Campus',
    autosize=True,
    hovermode='closest',
    showlegend=False,
    margin = go.layout.Margin(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0
    ),
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=60,
            lon=80,
        ),
        pitch=0,
        zoom=2,
        style='dark'
    ),
)

city_graph_fig = dict(data=city_graph_data, layout=city_graph_layout)   


@app.callback(Output('balance-graph', 'figure'), [Input('select-city', 'value')])
def balance_graph(city):
    balance_graph_data = [dict(
        x = [city], 
        y = [int(city_df[city_df.city == city][k[0]])],
        type = 'bar', 
        name = polarity_alias[k[0]], 
        hoverinfo="skip",
        marker = dict(
            color=k[1]
        )
    ) for k in list(zip(labels, [GOOD_COLOR, NEUTRAL_COLOR, BAD_COLOR]))]

    balance_graph_layout = dict(
        title=city,
        xaxis=dict(
            autorange=True,
            showticklabels=False
        ),
        yaxis=dict(
            title = 'Количество новостей',
            autorange=True,
        ),
        legend=dict(
            orientation="h"
        )
    )

    return dict(data=balance_graph_data, layout=balance_graph_layout)   


@app.callback(Output('timeline-graph', 'figure'), [Input('select-city', 'value')])
def get_latest_articles(city):
    session = Session()
    single_data = session.query(Result.timestamp, Result.summary, City.city_name).\
                        join(City, Result.city_id == City.city_id).\
                        filter(City.city_name == city).\
                        order_by(Result.timestamp.desc()).\
                        limit(10).from_self().\
                        order_by(Result.timestamp.asc()).all()
        
    single_df = pd.DataFrame.from_records(single_data, columns=['timestamp', 'summary', 'city'])
    single_df['pos'] = single_df.summary.apply(value_from_json, path='polarity.positive')
    single_df['neg'] = single_df.summary.apply(value_from_json, path='polarity.negative')
    single_df['net'] = single_df.summary.apply(value_from_json, path='polarity.neutral')
    single_df['date'] = single_df.timestamp.apply(lambda x: datetime.fromtimestamp(x).strftime('%d.%m.%Y'))

    timeline_graph_data = [
        go.Scatter(
            x = single_df['date'],
            y = single_df[i[0]],
            mode = 'lines+markers',
            name = polarity_alias[i[0]],
            connectgaps=True,
            line = dict(
                color = i[1]
            ),
        ) for i in zip(['pos', 'net', 'neg'], [GOOD_COLOR, NEUTRAL_COLOR, BAD_COLOR])
    ]

    timeline_graph_layout = dict(
        title=city,
        yaxis=dict(
            title = 'Количество новостей',
            autorange=True,
        ),
        legend=dict(
            orientation="h"
        )
    )
    
    session.close()
    return dict(data=timeline_graph_data, layout=timeline_graph_layout)


@app.callback(Output('latest-articles', 'children'), [Input('select-city', 'value')])
def get_latest_articles(city):
    session = Session()
    articles = session.query(
        Article.title, 
        Article.text, 
        Article.timestamp,
        Article.analysis).\
    join(City, Article.city_id == City.city_id).\
    filter(City.city_name == city).\
    order_by(Article.timestamp.desc()).\
    limit(6).all()

    latest_articles = [
        html.Div([
            html.Div([
                html.Div([
                    html.P([
                        datetime.fromtimestamp(a.timestamp).strftime('%d.%m.%Y')
                    ], className='date'),
                ], className='col'),
                html.Div([
                    html.P([json.loads(a.analysis)['polarity']], className='article-polarity')
                ], className='col')
            ], className='row'),
            html.H5([a.title], className='article-title'),
            html.P([a.text], className='article-text'),
            html.Hr(),
        ], className='article-teaser') for a in articles
    ]

    session.close()
    return latest_articles


layout = html.Div([
    html.Div([
        html.Div([
            html.Div([], className='gap-blank'),
            dcc.Markdown(markdown_intro),
            dcc.Graph(id='city-graph', figure=city_graph_fig),
            html.Div([], className='gap-blank'),            
        ], className='col')
    ], className='row'),
    html.Div([
        html.Div([
            html.H4('Выберите город'),
            dcc.Dropdown(
                options=[dict(label=c, value=c) for c in city_df.city.unique()],
                value='Москва',
                id='select-city'
            ),
            dcc.Graph(id='balance-graph'),
        ], className='col-md-4'),
        html.Div([
            html.Div(id='latest-articles')
        ], className='col-md-8'),
    ], className='row'),
    html.Div([
        html.Div([
            dcc.Markdown(markdown_method)
        ], className='col'),
        html.Div([
            dcc.Graph(id='timeline-graph'),
        ], className='col'),
    ], className='row')
])

