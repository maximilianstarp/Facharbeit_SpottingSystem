# import libraries
import pandas as pd
import re
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from functools import wraps
import sacn

# import scripts
from calculations import DMXCalculator
from hashing import Hasher

class SpottingSystemServerHelper():
    def __init__(self) -> None:
        self.hasher = Hasher()
        self.dmx_calculator = DMXCalculator()

        self.csv_settings_data_path = "./database/settings_data.csv"
        self.csv_shows_data_path = "./database/shows_data.csv"
        self.csv_default_show_path = "./database/default_show.csv"

        try:
            self.default_show = pd.read_csv(self.csv_default_show_path)
            open(self.csv_settings_data_path).close()
            open(self.csv_shows_data_path).close()
        except:
            print("Crucial database error. Server can not start.")
            exit()
        
        try:
            self.sacn_sender = sacn.sACNsender()
            self.sacn_sender.start()
        except:
            print("Crucial sACN Error. Server can not start.")
    
    def get_settings_data(self):
        return pd.read_csv(self.csv_settings_data_path, dtype=str)

    def get_shows_data(self):
        return pd.read_csv(self.csv_shows_data_path, dtype=str)
    
    def validate_ip_address(self, value:str) -> bool:
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', value):
            return True
        return False
    
    def validate_number_range(self, value:int, min_val:int, max_val:int) -> bool:
        try:
            num = int(value)
            if min_val <= num <= max_val:
                return True
        except ValueError:
            pass
        return False
    
    def validate_utf8(self, string:str) -> bool:
        try:
            string.encode('utf-8').decode('utf-8')
            return True
        except UnicodeDecodeError:
            print("Error: Invalid UTF-8 encoding")
            return False
    
    @staticmethod
    def login_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                abort(403)

        return decorated
    
    def toggle_theme(self, theme:str) -> str:
        return "light" if theme == "dark" else "dark"
    
    def delete_show(self, show_name:str) -> bool:
        try:
            dataframe = self.get_shows_data()
            dataframe = self.get_shows_data()[self.get_shows_data().show_name != show_name]
            dataframe.to_csv(self.csv_shows_data_path, index=False)
            return True
        except:
            print("Error: Unable to delete show.")
            return False
    
    def add_show(self, show_name:str) -> bool:
        try:
            if not self.validate_utf8(show_name):
                return False
            if show_name in self.get_shows_data()['show_name'].values:
                return False
            if show_name == "":
                return False
            new_show = self.default_show.loc[0].to_frame().transpose()
            new_show["show_name"] = show_name
            shows_data = pd.concat([self.get_shows_data(), new_show], ignore_index=True)
            shows_data.to_csv(self.csv_shows_data_path, index=False)
            return True
        except:
            return False

app = Flask(__name__)
server_helper = SpottingSystemServerHelper()
app.secret_key = server_helper.hasher.generate_api_token()

    
@app.route("/controller/input", methods=['POST'])
def api_handler_controller_input():
    token = request.headers.get('Authorization')
    show_name = request.args.get('show_name')
    data_input = request.args.getlist('data_input')

    if not token or not show_name or not data_input:
        return jsonify({'error': 'Missing required parameters!'}), 400
    if token != server_helper.get_settings_data()["controller_token"].to_list()[0]:
        return jsonify({'error': 'Unauthorized access!'}), 401
    try:
        show_id = server_helper.get_shows_data().index[server_helper.get_shows_data()["show_name"] == show_name][0]
    except:
        return jsonify({'error': 'Show not found!'}), 405
    
    if request.remote_addr != server_helper.get_shows_data()['ip_ctrl'].loc[server_helper.get_shows_data().index[show_id]]:
        return jsonify({'error': 'Unauthorized access! Wrong IP'}), 402
    
    universe, distance, x, y, z, movinghead_pan, movinghead_tilt, camera_pan, camera_tilt = server_helper.dmx_calculator.calculate_dmx_universe(values=data_input, shows_data=server_helper.get_shows_data().loc[server_helper.get_shows_data().index[show_id]])

    universe_number = int(server_helper.get_shows_data()["universe"].loc[server_helper.get_shows_data().index[show_id]])
    server_helper.sacn_sender.activate_output(universe_number)
    server_helper.sacn_sender[universe_number].multicast = True # unicast ??
    universe = tuple(universe)
    server_helper.sacn_sender[universe_number].dmx_data = universe

    return jsonify({'Distance': distance, 'Point': {'x':x,'y':y,'z':z}, 'Pan-MH': movinghead_pan, 'Tilt-MH': movinghead_tilt, 'Pan-Cam': camera_pan, 'Tilt-Cam': camera_tilt})

@app.route("/", methods=['GET', 'POST'])
@SpottingSystemServerHelper.login_required
def web_ui_handler_homepage():
    try:
        if request.method == "POST":
            form_name = request.form.get('btn-name')
            theme = server_helper.get_settings_data().at[0, "theme"]

            if form_name == 'theme-form':
                new_theme = server_helper.toggle_theme(theme)
                settings_data = server_helper.get_settings_data()
                settings_data.at[0, "theme"] = new_theme
                settings_data.to_csv(server_helper.csv_settings_data_path, index=False)
            
            if form_name == 'load':
                show_name = request.form.get('btn-index')
                return redirect(f'/show/{show_name}')
            
            if "btn-delete" in request.form:
                show_name = request.form.get('btn-delete')
                if server_helper.delete_show(show_name):
                    return redirect('/')
                else:
                    abort(500)
            
            if form_name == 'add-show':
                show_name = request.form['show-name']
                if server_helper.add_show(show_name):
                    return redirect('/')
                else:
                    abort(500)
    
        theme = server_helper.get_settings_data().at[0, "theme"]
        shows = server_helper.get_shows_data()['show_name'].tolist()
        return render_template('home_page_template.html', theme=theme, shows=shows)
    except:
        abort(500)

@app.route("/settings", methods=['GET', 'POST'])
@server_helper.login_required
def web_ui_handler_settingspage():
    general_settings_data = server_helper.get_settings_data()
    error_msgs = {'current_username': "", 'new_username': "", 'repnew_username': "", 'current_psw': "", 'new_psw': "", 'repnew_psw': "", 'port': ""}
    new_username = ""
    new_password = ""

    try:
        if request.method == 'POST':
            form_name = request.form.get('btn-name')
            if form_name == "Save":
                try:
                    input_data = {
                        'current_username': request.form.get('current-username'),
                        'new_username': request.form.get('new-username'),
                        'repnew_username': request.form.get('repnew-username'),
                        'current_psw': request.form.get('current-psw'),
                        'new_psw': request.form.get('new-psw'),
                        'repnew_psw': request.form.get('repnew-psw'),
                        'new_port': request.form.get('new-port'),
                    }
                except:
                    error_msgs.update({key: "Could not read in Data. Make Sure all Data is written in utf-8." for key in error_msgs})
                    return render_template('settings_page_template.html', theme=server_helper.get_settings_data().at[0, "theme"], error_msgs=error_msgs, placeholders=general_settings_data.transpose()[0].to_dict())
                
                input_data = pd.DataFrame([input_data]).transpose()
                input_data = input_data.loc[input_data.ne("").any(axis=1)]

                if not input_data.empty:
                    input_data = input_data.transpose()
                    for key in input_data:
                        data = input_data[key].to_list()[0]
                        if key == 'new_username':
                            if ('current_username' in input_data and 'current_psw' in input_data):
                                if server_helper.hasher.check_hashed_credentials(input_data['current_username'].to_list()[0], input_data['current_psw'].to_list()[0], server_helper.get_settings_data().at[0,"username"], server_helper.get_settings_data().at[0,"password"]):
                                    if input_data[key].values == input_data['repnew_username'].values:
                                        new_username = data
                                    else:
                                        error_msgs['repnew_username'] = "Validation does not match"
                                else:
                                    error_msgs.update({'current_username': "Username and/or Password is not correct", 'current_psw': "Username and/or Password is not correct"})
                            else:
                                error_msgs.update({'current_username': "Username and/or Password is not correct", 'current_psw': "Username and/or Password is not correct"})
                            continue
                        if key == 'new_psw':
                            if ('current_username' in input_data and 'current_psw' in input_data):
                                if server_helper.hasher.check_hashed_credentials(input_data['current_username'].to_list()[0], input_data['current_psw'].to_list()[0], server_helper.get_settings_data().at[0,"username"], server_helper.get_settings_data().at[0,"password"]):
                                    if input_data[key].values == input_data['repnew_psw'].values:
                                        new_password = data
                                    else:
                                        error_msgs['repnew_psw'] = "Validation does not match"
                                else:
                                    error_msgs.update({'current_username': "Username and/or Password is not correct", 'current_psw': "Username and/or Password is not correct"})
                            else:
                                error_msgs.update({'current_username': "Username and/or Password is not correct", 'current_psw': "Username and/or Password is not correct"})
                            continue
                        if key == 'new_port':
                            if data.isdigit() and 1 <= int(input_data[key].to_list()[0]) <= 65535:
                                general_settings_data['port'] = input_data[key]
                                error_msgs['port'] = "Warning: To change the port you have to restart the server"
                            else:
                                error_msgs['port'] = "Value must be a number between 1 and 65,535"
                            continue
                    if new_username:
                        general_settings_data["username"] = server_helper.hasher.genenrate_hash(str(new_username))
                    if new_password:
                        general_settings_data["password"] = server_helper.hasher.genenrate_hash(str(new_password))
                    general_settings_data.to_csv(server_helper.csv_settings_data_path, index=False)

                return render_template('settings_page_template.html', theme=server_helper.get_settings_data().at[0, "theme"], error_msgs=error_msgs, placeholders=general_settings_data.transpose()[0].to_dict())

        return render_template('settings_page_template.html', theme=server_helper.get_settings_data().at[0, "theme"], error_msgs=error_msgs, placeholders=general_settings_data.transpose()[0].to_dict())
    except Exception as e:
       abort(500)

@app.route("/tokens", methods=['GET', 'POST'])
@server_helper.login_required
def web_ui_handler_tokenspage():
    settings_data = server_helper.get_settings_data()

    if request.form == 'POST':
        form_name = request.form.get('btn-name')
        if form_name == "New Controller-Token":
            settings_data["controller_token"] = server_helper.hasher.generate_api_token()
        settings_data.to_csv(server_helper.csv_settings_data_path, index=False)

        return render_template("tokens_page_template.html", controller_token=settings_data['controller_token'][0], theme=server_helper.get_settings_data().at[0, "theme"])
    
    return render_template("tokens_page_template.html", controller_token=settings_data['controller_token'][0], theme=server_helper.get_settings_data().at[0, "theme"])

@app.route("/show/<show_name>", methods=['GET', 'POST'])
@server_helper.login_required
def web_ui_handler_showpages(show_name):
    shows_data = server_helper.get_shows_data()
    error_msgs = {field: "" for field in ['cam_addr', 'mh_addr', 'univers', 'xdist', 'ydist', 'zdist', 'panrot', 'tiltrot', 'ip_ctrl', 'ip_cam', 'port_cam', 'show_name']}

    try:
        show_id = shows_data.index[shows_data['show_name'] == show_name][0]
    except:
        abort(500)

    try:
        if request.method == 'POST':
            form_name = request.form.get('btn-name')
            if form_name == 'Cancel':
                return redirect("/")
            elif form_name == "Save":
                try:
                    input_data = {
                        'cam_addr': request.form['cam-addr'],
                        'mh_addr': request.form['mh-addr'],
                        'universe': request.form['universe'],
                        'xdist': request.form['x-dist'],
                        'ydist': request.form['y-dist'],
                        'zdist': request.form['z-dist'],
                        'panrot': request.form['pan-rot'],
                        'tiltrot': request.form['tilt-rot'],
                        'ip_ctrl': request.form['ip-ctrl'],
                        'ip_cam': request.form['ip-cam'],
                        'port_cam': request.form['port-cam'],
                        'show_name': request.form['show-name']
                    }
                except:
                    error_msgs.update({key: "Could not read in Data. Make Sure all Data is written in utf-8." for key in error_msgs})
                    return render_template('shows_page_template.html', theme=server_helper.get_settings_data().at[0, "theme"], show_name=show_name, error_msgs=error_msgs, shows_data=shows_data.transpose()[show_id])

                input_data = pd.DataFrame([input_data]).transpose()
                input_data = input_data.loc[input_data.ne("").any(axis=1)]

                if not input_data.empty:
                    input_data = input_data.transpose()
                    for key in input_data:
                        data = input_data[key].to_list()[0]
                        if key in ['cam_addr', 'mh_addr', 'universe', 'port_cam'] and not server_helper.validate_number_range(data, *{'cam_addr': (0, 512), 'mh_addr': (0, 512), 'universe': (1, 32768), 'port_cam': (1, 65535)}[key]):
                            error_msgs[key] = "Number not within valid number range"
                            break
                        if key in ['ip_ctrl', 'ip_cam'] and not server_helper.validate_ip_address(data):
                            error_msgs[key] = "No valid IP-Address"
                            break
                        if key == 'show_name' and data in shows_data['show_name'].values:
                            error_msgs['show_name'] = "Name already in use"
                            break

                        shows_data.at[shows_data.index[show_id], key] = str(data)

                shows_data.to_csv(server_helper.csv_shows_data_path, index=False)

                if show_name != server_helper.get_shows_data().at[0, "show_name"]:
                    return redirect(url_for('web_ui_handler_showpages', show_name=data))

                return render_template('shows_page_template.html', theme=server_helper.get_settings_data().at[0, "theme"], show_name=server_helper.get_shows_data().at[0, "show_name"], error_msgs=error_msgs, shows_data=shows_data.transpose()[show_id])

        return render_template('shows_page_template.html', theme=server_helper.get_settings_data().at[0, "theme"], show_name=server_helper.get_shows_data().at[0, "show_name"], error_msgs=error_msgs, shows_data=shows_data.transpose()[show_id])
    except:
        abort(500)

@app.route('/login', methods=['GET', 'POST'])
def web_ui_handler_loginpage():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if server_helper.validate_utf8(username) and server_helper.validate_utf8(password):
                settings_data = server_helper.get_settings_data()
                if server_helper.hasher.check_hashed_credentials(username, password, settings_data.at[0, "username"], settings_data.at[0, "password"]):
                    session['logged_in'] = True
                    return redirect(url_for('web_ui_handler_homepage'))
                else:
                    msg = "Invalid credentials. Please try again."
            else:
                msg = "Credentials are not UTF-8."
            
            return render_template('login_page_template.html', msg=msg, theme=settings_data.at[0, "theme"])
        
        return render_template('login_page_template.html', theme=server_helper.get_settings_data().at[0, "theme"])
    except:
        abort(500)

@app.route("/logout")
@server_helper.login_required
def web_ui_handler_logout():
    try:
        session.pop('logged_in', None)
        return redirect(url_for('web_ui_handler_loginpage'))
    except:
        abort(500)

@app.errorhandler(403)
def error_handler_403(e):
    return redirect(url_for('web_ui_handler_loginpage'))
@app.errorhandler(404)
def error_handler_404(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def error_handler_500(e):
    return render_template('500.html'), 500

app.register_error_handler(404, error_handler_404)
app.register_error_handler(500, error_handler_500)
app.register_error_handler(403, error_handler_403)

if __name__ == '__main__':
    app.run("0.0.0.0", port=int(server_helper.get_settings_data()["port"].to_list()[0]), debug=True)