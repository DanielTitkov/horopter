import dash_core_components as dcc
import dash_html_components as html
# from dash.dependencies import Input, Output

# from server import app

markdown_text = '''
### Horopter

Кажинный раз на этом самом месте я вспоминаю о своей невесте.
Вхожу в шалман, заказываю двести. 
'''

layout = html.Div([
    dcc.Markdown(markdown_text)
])
