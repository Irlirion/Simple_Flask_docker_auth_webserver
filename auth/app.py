import os
from server import create_app, config


app = create_app(mode=config.Development)

if __name__ == '__main__':
    app.run(debug=True)
