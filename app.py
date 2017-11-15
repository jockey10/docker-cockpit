# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Text
from markupsafe import escape

from .forms import SignupForm
from .nav import nav

import docker
import pipes
from subprocess32 import STDOUT, call

app = Blueprint('app', __name__)
client = docker.from_env(version="auto")
# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top', Navbar(
    View('Docker Cockpit', '.index'),
    View('Home', '.index'),
    View('Kill Container', '.example_form'),
    Text('Using Flask-Bootstrap {}'.format(FLASK_BOOTSTRAP_VERSION)), ))

def kill_container( containerId, remove = False ):
    """
    Kill the container given by containerId.

    Optional: remove. If remove=True, container will also be deleted.
    """

    for action in ( 'kill', 'rm' ):
        if action == 'rm' and not remove:
            break

        # Here we're using the subprocess32 module backported for 2.7.x, which
        # provides support for a timeout provided to the call command
        # https://stackoverflow.com/questions/1191374/using-module-subprocess-with-timeout

        # we could also use the check_output command here - though we don't
        # really need to check the output for the application

        # NB: use shell=False to avoid vulnerabilities
        # https://stackoverflow.com/questions/3172470/actual-meaning-of-shell-true-in-subprocess
        call(['docker',action,containerId], stderr=STDOUT, timeout=5, shell=False )

# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@app.route('/')
def index():
    return render_template('index.html')

# Shows a long signup form, demonstrating form rendering.
@app.route('/example-form/', methods=('GET', 'POST'))
def example_form():
    form = SignupForm()

    # I couldn't get this working with 'form.validate_on_submit()'
    if form.validate_on_submit():
        container_name = pipes.quote(form.name.data)
        kill_and_rm = True if form.submit_killrm.data else False

        kill_container( container_name, remove=kill_and_rm )

        # We don't have anything fancy in our application, so we are just
        # flashing a message when a user completes the form successfully.
        #
        # Note that the default flashed messages rendering allows HTML, so
        # we need to escape things if we input user values:
        if kill_and_rm:
            flash('Container "{}" has gone to the great farm in the sky'
                  .format(escape(form.name.data)))
        else:
            flash('Container "{}" has "gone to the farm"'
                  .format(escape(form.name.data)))

        # In a real application, you may wish to avoid this tedious redirect.
        return redirect(url_for('.index'))

    return render_template('signup.html', form=form, client=client)
