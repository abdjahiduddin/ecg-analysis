import os
import ast
import json
import psutil
import logging
from datetime import datetime
from flask import Flask, render_template, request, session, url_for, redirect, jsonify
from visualizer import main_process as create_graph
from cloud import authenticate_users
from mongodb import connections

# Define web application
app = Flask("Web Apps")
app.secret_key = "always secret"
host = '0.0.0.0'
port = 8888

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

authorized_page = {
    "not logged in": ["default", "login", "register"],
    "logged in": {
        "admin": ["admin"],
        "user": ["home", "edit_profile", "change_password", "article_summary"]
    }
}
api_folder = os.getcwd() + "/static/api/"
except_id = {"_id": 0}

this_process = psutil.Process()
attribute_list = ["pid", "create_time", "cpu_percent", "memory_percent", "disk_read", "disk_write"]


# Main process for web server component
# Start web server
def main_process():
    # Run web application in port 8888 of all interface
    print("[Web Server] * Flask server run on http://" + host + ":" + str(port) + "/ (Press CTRL+C to quit)")
    app.run(host=host, port=port)


# Index path
@app.route("/", methods=["GET"])
def index():
    # If logged in
    if "user" in session:
        # If admin
        if session["user"]["profile"]["username"] == "admin":
            return redirect_page("admin", {})
        # Other user (not admin)
        else:
            return redirect_page("home", {})
    # Not Logged in
    else:
        return redirect_page("default", {})


# Landing zone for template
@app.route("/<string:page>", methods=["GET"])
def landing(page):
    cookies = validate_cookies(page)
    # If logged in
    if "user" in session:
        user = session["user"]
        # If admin
        if user["profile"]["username"] == "admin":
            # If admin access non authorized page
            if page not in authorized_page["logged in"]["admin"]:
                # Redirect to admin's home
                return redirect_page("admin", {})
            else:
                users_list = get_users()
                return render_template(page + ".html", user=user, users_list=users_list, cookies=cookies)
        # Other user (not admin)
        else:
            # If user access non authorized page
            if page not in authorized_page["logged in"]["user"]:
                # Redirect to default home or non admin's home
                return redirect_page("home", {})
            else:
                return render_template(page + ".html", user=user, cookies=cookies)
    # Not Logged in
    else:
        # If non user access non authorized page
        if page not in authorized_page["not logged in"]:
            # Redirect to default index
            return redirect_page("default", {})
        else:
            return render_template(page + ".html", cookies=cookies)


# Route for register process
@app.route("/register/process", methods=["POST"])
def register():
    # Get form
    form = form_to_dict([])

    # Check possible error field
    error = {
        "username": check_user({"username": form["username"]}),
        "email": check_user({"email": form["email"]}),
        "password_match": validate_password(form["password"], form["password_confirmation"])
    }

    # If nothing error
    if not any(error.values()):
        # Prepare new user structure
        new_user = form_to_dict(["password_confirmation"])
        new_user["created"] = datetime.now()
        # Insert new user: User
        connections["user"].insert_one(new_user)
        # Authenticate users again
        authenticate_users()
        # Redirect to login page with cookies (user registered)
        return redirect_page("login", {"register": True})
    else:
        # Prepare previous form structure
        prev_form = form_to_dict(["password", "password_confirmation"])
        # Redirect back to register page with cookies (previous form and error warning)
        return redirect_page("register", {"prev_form": prev_form, "error": error})


# Route for login process
@app.route("/login/process", methods=["POST"])
def login():
    # Get form
    form = form_to_dict([])

    # Check user in database
    user_exist = connections["user"].find_one(form, except_id)

    # If user found
    if user_exist:
        user = user_exist
        # If user logged in as admin
        if user["username"] == "admin":
            # Save admin information to session
            session["user"] = {
                "profile": user
            }
            # Redirect to admin's home page with cookies (user logged in)
            return redirect_page("admin", {"login": True})
        # Logged in as other user (not admin)
        else:
            # Save other user information to session
            session["user"] = {
                "profile": user,
                "time": {
                    "created": user["created"].strftime("%Y-%m-%d"),
                    "now": datetime.now().strftime("%Y-%m-%d")
                },
                "divider_range": {
                    "resting": create_divider(0, int(user["age"])),
                    "exercising": create_divider(1, int(user["age"]))
                }
            }
            # Redirect to non admin's home page with cookies (user logged in)
            return redirect_page("home", {"login": True})
    # If user not found
    else:
        # Redirect back to login page with cookies (previous username and error warning)
        return redirect_page("login", {"username": form["username"], "error": True})


# Route for logout process
@app.route("/logout/process", methods=["POST"])
def logout():
    # Clear session
    session.clear()
    # Redirect to default index page with cookies (user logged out)
    return redirect_page("default", {"logout": True})


# Route for edit profile process
@app.route("/edit_profile/process", methods=["POST"])
def edit_profile():
    # Get form
    form = form_to_dict([])

    # Check email (except logged in user)
    check_email = {
        "$and": [
            {"username": {"$ne": session["user"]["profile"]["username"]}},
            {"email": form["email"]}
        ]
    }

    # Check email field error
    error = check_user(check_email)

    # If nothing error
    if not error:
        # Define new profile
        new_profile = form_to_dict([])
        # Update user profile
        filter_profile = {
            "username": session["user"]["profile"]["username"]
        }
        updated_profile = {
            "$set": new_profile
        }
        connections["user"].update(filter_profile, updated_profile)
        # Update user information in session
        user = connections["user"].find_one(filter_profile, except_id)
        session["user"] = {
            "profile": user,
            "time": {
                "created": user["created"].strftime("%Y-%m-%d"),
                "now": datetime.now().strftime("%Y-%m-%d")
            },
            "divider_range": {
                "resting": create_divider(0, int(user["age"])),
                "exercising": create_divider(1, int(user["age"]))
            }
        }
        # Authenticate users again
        authenticate_users()
        # Redirect to non admin's home page with cookies (profile updated)
        return redirect_page("home", {"edit_profile": True})
    else:
        # Define previous form
        prev_form = form_to_dict([])
        # Redirect back to edit profile page with cookies (previous form and error warning)
        return redirect_page("edit_profile", {"prev_form": prev_form, "error": error})


# Route for change password process
@app.route("/change_password/process", methods=["POST"])
def change_password():
    # Get form
    form = form_to_dict([])

    # Check password field error
    error = validate_password(form["password"], form["password_confirmation"])

    # If not error
    if not error:
        # Update user's password
        filter_profile = {
            "username": session["user"]["profile"]["username"]
        }
        updated_profile = {
            "$set": {"password": form["password"]}
        }
        connections["user"].update(filter_profile, updated_profile)
        # Redirect to non admin's home page with cookies (password changed)
        return redirect_page("home", {"change_password": True})
    else:
        # Redirect back to change_password page with cookies (error warning)
        return redirect_page("change_password", {"error": error})


# Route for find trend process
@app.route("/trend/process", methods=["POST"])
def find_trend():
    # Get HTML form
    form = form_to_dict([])

    # Define some necessaries
    info = {
        "trend": {
            "type": form["type"]
        },
        "user": {
            "username": session["user"]["profile"]["username"],
            "age": session["user"]["profile"]["age"],
            "device": session["user"]["profile"]["device"],
            "divider_range": session["user"]["divider_range"]
        }
    }

    # Define trend result
    trend_result = {
        "detail": {},
        "filename": {},
        "access_time": str(datetime.now()),
        "type": info["trend"]["type"],
        "html_format": {
            "div": {},
            "illustration": {}
        }
    }

    # If looking for trend type track
    if info["trend"]["type"] == "track":
        # Define track type query
        check_trend = {
            "profile.username": info["user"]["username"],
            "profile.device": info["user"]["device"],
            "trend.type": info["trend"]["type"]
        }

        # Check trend
        trend_exist = connections["trend"].find_one(check_trend, except_id, sort=[("trend.time", -1)])

        # If trend exist
        if trend_exist:
            # Define trend
            trend = trend_exist

            # Define trend date and date format
            info["trend"]["date"] = trend["trend"]["time"]
            info["trend"]["date_format"] = "%a, %d %b %Y %H:%M:%S"

            # Add trend result
            activity = parse_activity(trend["trend"]["activity"])
            divider_range = session["user"]["divider_range"][activity]
            trend_result["detail"][activity], trend_result["html_format"]["illustration"][activity] = explore_trend(divider_range, trend)
        # If trend not found
        else:
            # Define trend date and date format
            info["trend"]["date"] = datetime.now()
            info["trend"]["date_format"] = "Not Found"

            # Add trend not found result
            trend_result["detail"]["not found"] = "No data could be found."

        # Define track type div format
        div_format = {
            "outer": "col-sm-12",
            "inner1": "col-sm-3",
            "inner2": "col-sm-9"
        }
    # If looking for trend type other than track (yearly, monthly, or daily)
    else:
        # Split by "-" --> parse to int --> create list -> define date
        form_date = list(map(int, form['date'].split("-")))

        # Define trend date, date_format, and file_format by trend_type
        if info["trend"]["type"] == "yearly":
            info["trend"]["date"] = datetime(form_date[0], 1, 1)
            info["trend"]["date_format"] = "%Y"
        elif info["trend"]["type"] == "monthly":
            info["trend"]["date"] = datetime(form_date[0], form_date[1], 1)
            info["trend"]["date_format"] = "%b %Y"
        else:
            info["trend"]["date"] = datetime(form_date[0], form_date[1], form_date[2])
            info["trend"]["date_format"] = "%a, %d %b %Y"

        # Define other than track type query
        check_trend = {
            "profile.username": info["user"]["username"],
            "profile.device": info["user"]["device"],
            "trend.type": info["trend"]["type"],
            "trend.time": info["trend"]["date"]
        }

        # For resting (0) and excercising (1) activity
        for activity in [0, 1]:
            # Define activity in number and string
            info["trend"]["act(num)"] = activity
            info["trend"]["act(str)"] = parse_activity(activity)
            check_trend["trend.activity"] = info["trend"]["act(num)"]

            # Check trend
            trend_exist = connections["trend"].find_one(check_trend, except_id)

            # If trend exist
            if trend_exist:
                # Define trend
                trend = trend_exist
                # Add trend result
                divider_range = session["user"]["divider_range"][info["trend"]["act(str)"]]
                trend_result["detail"][info["trend"]["act(str)"]], trend_result["html_format"]["illustration"][info["trend"]["act(str)"]] = explore_trend(divider_range, trend)
                # Define and add trend filename
                trend_result["filename"][info["trend"]["act(str)"]] = "visual/" + info["user"]["username"] + "_" + info["trend"]["act(str)"] + ".svg"
                # Create visualization
                create_graph(info)
            else:
                # Add trend not found result
                trend_result["detail"][info["trend"]["act(str)"]] = "No data could be found for " + info["trend"]["act(str)"] + " activity."

        # Define other than track type div format
        div_format = {
            "outer": "col-sm-5",
            "inner1": "col-sm-12",
            "inner2": "col-sm-12"
        }

    # Add trend time range and div format
    trend_result["time_range"] = info["trend"]["date"].strftime(info["trend"]["date_format"])
    trend_result["html_format"]["div"] = div_format
    return redirect_page("home", {"trend": trend_result})


@app.route("/article_summary/<string:status>", methods=["GET"])
def summary(status):
    return redirect_page("article_summary", {"status": status})


# Route for web server API
@app.route("/api/<string:filename>", methods=["GET"])
def api(filename):
    if os.path.exists(api_folder + filename):
        # Open and read corresponding file
        with open(api_folder + filename, 'r') as file:
            trend = json.load(file)
        # Change timestamp to datetime
        trend["trend"]["time"] = datetime.fromtimestamp(trend["trend"]["time"])
    else:
        trend = {"data": "Not Found"}
    return jsonify(trend)


# Route for web server monitor
@app.route("/monitor/<string:attribute>", methods=["GET"])
def monitor(attribute):
    # If PID
    if attribute == "pid":
        # Direct attribute value
        value = getattr(this_process, attribute)
    # Elseif Disk I/O
    elif attribute == "disk_read" or attribute == "disk_write":
        # Get value (by attribute method)
        get_value = getattr(this_process, "io_counters")
        value = get_value()
        # Bytes to Mega Bytes
        # If disk read (index = 2)
        if attribute == "disk_read":
            value = round(value[2] / 1048576, 1)
        # Else - if disk write (index = 3)
        else:
            value = round(value[3] / 1048576, 1)
    # Elseif create time or cpu + memory usage (in percent)
    elif attribute in attribute_list:
        # Get value (by attribute method)
        get_value = getattr(this_process, attribute)
        value = get_value()
        # If create time
        if attribute == "create_time":
            # Timestamp to Datetime
            value = datetime.fromtimestamp(value)
        # Else - if cpu + memory usage (in percent)
        else:
            value = round(value, 1)
    # Else - not a registered service
    else:
        value = "Not available"
    return str(value)

# Redirect page with cookies function
def redirect_page(page, variables_to_cookies):
    # Define location to landing zone
    response = redirect(url_for("landing", page=page))
    # Change all needed variables to cookies
    for key, value in variables_to_cookies.items():
        response.set_cookie(key, str(value), max_age=1)
    # Return redirect function and it's cookies
    return response


# Explore request to get all cookies (cookies to dictionary)
def explore_cookies():
    cookies = {}
    # Save cookies to dictionary
    for cookie in request.cookies:
        cookies[cookie] = request.cookies.get(cookie)
    return cookies


# Validate cookies value
def validate_cookies(page):
    # Get cookies in dictionary
    cookies = explore_cookies()
    # If it's first time aceess register page
    if page == "register" and "prev_form" not in cookies:
        # Empty all input
        cookies["error"] = {}
        cookies["prev_form"] = {}
    # If it's first time aceess edit profile page
    elif page == "edit_profile" and "prev_form" not in cookies:
        # Use session value as input
        cookies["prev_form"] = session["user"]["profile"]
    # If previous form and trend (both is not dictionary)
    elif "prev_form" in cookies or "trend" in cookies:
        # For all cookies
        for key, cookie in cookies.items():
            # Except session
            if key != "session":
                # Change cookie value from string to dictionary
                cookies[key] = ast.literal_eval(cookie)
    return cookies


# Get all users list
def get_users():
    # Except Admin
    except_admin = {"username": {"$ne": "admin"}}
    # Exclude field (id, time account created, username, password)
    except_field = {"_id": 0, "created": 0, "username": 0, "password": 0}
    users = connections["user"].find(except_admin, except_field)
    return users


# Check user existence
def check_user(check_identity):
    # Check database
    user_exist = connections["user"].find_one(check_identity)
    # If user exist
    if user_exist:
        # Define error
        return True
    else:
        # Define not error
        return False


# Check password match
def validate_password(password, password_confirmation):
    # if password equal password confirmation
    if password == password_confirmation:
        # Define error
        return False
    else:
        # Define not error
        return True


# Change form to dictionary with exclude feature
def form_to_dict(excludes):
    form = request.form.to_dict()
    # Exclude some field in form
    for exclude in excludes:
        form.pop(exclude)
    return form


# Explore trend necessary information
def explore_trend(divider_range, trend):
    # Define necessaries
    avg_hr = trend["trend"]["heart_rate"]["average"]
    status = trend["trend"]["status"]
    space = "        "

    # Define trend detail
    color, condition, reason, solution = explore_detail(status)
    detail = {
        "status": status,
        "color": color,
        "condition": condition,
        "reason": reason,
        "solution": solution,
        "average": avg_hr
    }

    # Define trend illustration
    low, middle, high, info = illustrate(status, divider_range, avg_hr)
    illustration = {
        "line": low + space + middle + space + high,
        "info": info
    }
    # Return trend detail and illustration
    return detail, illustration


# Explore trend detail
def explore_detail(status):
    # Slow status trend detail
    if status == "slow":
        # Want to warn user (font color is red and condition not healthy)
        # that their heart rate is conditioned as slow heart rate
        solution = "is a article summary about slow heart rate, read it for better understanding."
        return "red", "may not healthy", "slower than", solution
    # Fast status trend detail
    elif status == "fast":
        # Want to warn user (font color is red and condition not healthy)
        # that their heart rate is conditioned as fast heart rate
        solution = "is a article summary about fast heart rate, read it for better understanding."
        return "red", "may not healthy", "faster than", solution
    # Normal status trend detail
    else:
        # Want to inform user (font color is green and condition healthy)
        # that their heart rate is conditioned as normal heart rate
        solution = "No treatment needed. Keep going!!!"
        return "green", "healthy", "within", solution


# Illustrate trend
def illustrate(status, divider_range, heart_rate):
    space = "                    "
    # Slow status trend illustration
    if status == "slow":
        # Initialize slow illustration
        # their heart rate -+- minimum divider -+- maximum divider
        #    [yours]
        return str(heart_rate), str(divider_range["low"]), str(divider_range["high"]), "[yours]" + space
    # Fast status trend illustration
    elif status == "fast":
        # Initialize fast illustration:
        # minimum divider -+- maximum divider -+- their heart rate
        #                                            [yours]
        return str(divider_range["low"]), str(divider_range["high"]), str(heart_rate), space + "[yours]"
    # Normal status trend illustration
    else:
        # Initialize fast illustration:
        # minimum divider -+- their heart rate -+- maximum divider
        #                          [yours]
        return str(divider_range["low"]), str(heart_rate), str(divider_range["high"]), "[yours]"


# Create divider range (low and high normal heart rate divider)
def create_divider(activity, age):
    divider_range = {}

    if activity == 0:
        divider_range["low"] = 60
        divider_range["high"] = 100
    else:
        # Calculate max heart rate
        heart_rate_max = 208 - (0.7 * int(age))

        divider_range["low"] = int(heart_rate_max * 0.5)
        divider_range["high"] = int(heart_rate_max * 0.9)

    return divider_range


# Parse activity in number to activity in string
# 0 for resting
# 1 for exercising
def parse_activity(activity_number):
    if activity_number == 0:
        return "resting"
    else:
        return "exercising"


if __name__ == "__main__":
    main_process()
