from flask import Flask



def create_app():
    app= Flask(__name__)
    
    
    from .views import app as appBlueprint
    app.register_blueprint(appBlueprint)
    
    
    return app