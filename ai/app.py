# Import the Flask class from the flask module
from flask import Flask, render_template

# Create an instance of the Flask class
# __name__ is a special variable that gets the name of the current file
# This helps Flask find resources like templates and static files
app = Flask(__name__)

# Define a route for the homepage
# The @app.route decorator binds a URL to a function
@app.route('/')
def index():
    """
    This function is called when a user navigates to the root URL (/) of the app.
    It returns a simple string that will be displayed in the browser.
    """
    return "Hello, World!"

# Another route with a variable part
# <name> is a dynamic part of the URL
@app.route('/hello/<name>')
def hello_name(name):
    """
    This function takes the dynamic part of the URL (name) as an argument.
    It returns a personalized greeting.
    """
    return f"Hello, {name}!"

# A route that renders an HTML template
# This is useful for building web pages with more structure
# You would need to create a 'templates' folder and an 'about.html' file
@app.route('/about')
def about():
    """
    This function renders an HTML template.
    You can pass data to the template using keyword arguments.
    """
    return render_template('about.html', title='About Us', content='This is the about page.')

# ------------------------------------------
# Real Endpoints and Logic would go below
# ------------------------------------------

@app.route('/admin/run-bot-user-check', methods=['POST'])
def run_bot_user_check():
    """
    This endpoint would contain logic to check for bot users.
    For now, it just returns a placeholder message.
    """
    # Placeholder for actual bot user check logic
    return "Bot user check initiated."



# This conditional block ensures the web server runs only when the script is executed directly
# The debug=True flag enables the debugger and reloader, which are very useful during development
if __name__ == '__main__':
    app.run(debug=True)