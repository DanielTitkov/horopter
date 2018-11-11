from horopter.database import Session, City, Result, Article
import dash

app = dash.Dash()
server = app.server
app.config.suppress_callback_exceptions = True
app.css.append_css({'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css'})


