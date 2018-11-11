from server import app, server

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

from horopter.pages import home, http404, cities

app.title = 'Horopter - Объективная информация'

header = html.Nav([
    html.H1('Horopter', className='navbar-brand mb-0 h1'),
    dcc.Link('Home', href='/', className='nav-item nav-link'),
    dcc.Link('Города', href='/cities', className='nav-item nav-link'),
], id='header', className='navbar navbar-expand-lg')


footer = html.Div([], id='footer')


app.layout = html.Div([
    header,
    dcc.Location(id='url', refresh=False),
    html.Div([], id='content', className='container-fluid'),
    footer
], id='layout', className='container-fluid')


@app.callback(Output('content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    routes = {
        '/': home,
        '/cities': cities
    }

    return routes.get(pathname, http404).layout


if __name__ == '__main__':
    app.server.run(debug=True)