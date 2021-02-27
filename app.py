import json
import os
import stopit
import sys
import cherrypy
from pymongo import MongoClient
import time

frmo src.apis import *
from src.utils import *


CONTACT = "If you continue to encounter this issue, please contact us at " \
          "sakshamconsul@gmail.com."
TIMEOUT_SECONDS = 28

# Extend recursion limit
sys.setrecursionlimit(10000)


class RESTResource(object):
    """
    Base class for providing a RESTful interface to a resource.
    From https://stackoverflow.com/a/2831479

    To use this class, simply derive a class from it and implement the methods
    you want to support.  The list of possible methods are:
    handle_GET
    handle_PUT
    handle_POST
    handle_DELETE
    """

    @cherrypy.expose
    @cherrypy.tools.accept(media='application/json')
    def default(self, *vpath, **params):
        method = getattr(self, "handle_" + cherrypy.request.method, None)
        if not method:
            methods = [x.replace("handle_", "") for x in dir(self)
                       if x.startswith("handle_")]
            cherrypy.response.headers["Allow"] = ",".join(methods)
            cherrypy.response.status = 405
            status = "Method not implemented."
            return json.dumps(status)

        # Can we load the request body (json)
        try:
            rawData = cherrypy.request.body.read()
            jsonData = json.loads(rawData)
        except:
            cherrypy.response.status = 403
            status = "No request body"
            return json.dumps(status)

        return method(jsonData, *vpath, **params)


class PostResource(RESTResource):

    @cherrypy.tools.json_out()
    def handle_POST(self, jsonData, *vpath, **params):

        # Start timer
        main_tic = time.time()

        with stopit.ThreadingTimeout(TIMEOUT_SECONDS) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING

            # Initialize log dictionary
            log_dict = {
                "start_time": datetime.now(),
            }

            # Initialize dictionary that inspects time taken by each method
            timer = dict()

            try:
                # Load fixed time if provided
                if "time" in jsonData.keys():
                    user_datetime = datetime.strptime(jsonData["time"],
                                                      "%Y-%m-%d %H:%M")
                else:
                    user_datetime = datetime.utcnow()

                # Start timer: reading parameters
                tic = time.time()

                # Compulsory parameters
                method = vpath[0]
                rounding = vpath[1]  # Number of decimals

                # tree = vpath[-3]  # Dummy parameter
                user_key = vpath[-2]
                api_method = vpath[-1]

                # Additional parameters (the order of URL input matters!)
                # Casting to other data types is done within the functions that
                # use these parameters
                parameters = [item for item in vpath[2:-3]]
                # print(f'parameters: {parameters}')
                # Is there a user key
                try:
                    log_dict["user_id"] = jsonData["userkey"]
                except:
                    status = "We encountered a problem with the inputs " \
                             "from our app, please try again."
                    store_log(db.request_log, log_dict, status=status)

                    cherrypy.response.status = 403
                    return json.dumps(status + " " + CONTACT)

                # Initialize SMDP parameters
                params = dict({
                    "cost_threshold": 1
                })

                """ Reading SMDP parameters """
                if method == "prototype":

                    try:
                        tic = time.time()

                        params.update({
                            "cost_threshold":            parameters[0]
                        })

                        # Get threshold from database (if available)
                        query = list(db.pr_transform.find(
                            {
                                "user_id": jsonData["userkey"]
                            }
                        ))
                        if len(query) > 0 and api_method == "previousThreshold":
                            query = query[-1]
                            params["cost_threshold"] = query["cost_threshold"]
                        else:
                            query = None

                        # Imposed bias value for f'(s, a) = m * f(s, a) + b
                        if "cost_threshold" in jsonData.keys():
                            params["cost_threshold"] = jsonData["cost_threshold"]
                        cost_threshold = params["cost_threshold"]
                        timer["Reading parameters"] = time.time() - tic

                    except:
                        status = "There was an issue with the API input " \
                                 "(reading parameters) Please contact " \
                                 "us at sakshamconsul@gmail.com."
                        store_log(db.request_log, log_dict, status=status)
                        cherrypy.response.status = 403
                        return json.dumps(status)


                # Last input parameter
                try:
                    round_param = int(rounding)
                except:
                    status = "There was an issue with the API input " \
                             "(rounding parameter). Please contact us at " \
                             "sakshamconsul@gmail.com"
                    store_log(db.request_log, log_dict, status=status)
                    cherrypy.response.status = 403
                    return json.dumps(status)

                # Update time with time zone
                log_dict["user_datetime"] = user_datetime

                log_dict.update({
                    "api_method": api_method,
                    "cost_threshold": cost_threshold,
                    "round_param": round_param,
                    "user_key": user_key,


                    # Must be provided on each store (if needed)
                    "lm": None,
                    "mixing_parameter": None,
                    "status": None,
                    "user_id": None,
                })

                # Update last modified
                log_dict["lm"] = jsonData["updated"]

                # Store time: reading parameters
                timer["Reading parameters"] = time.time() - tic

                # Start timer: parsing current intentions
                tic = time.time()

                # Parse current intentions
                try:
                    current_items = parse_current_items_list(
                        jsonData["currentItemsList"])
                except Exception as error:

                    status = str(error)

                    # Remove personal data
                    anonymous_error = parse_error_info(status)

                    # Store error in DB
                    store_log(db.request_log, log_dict, status=anonymous_error)

                    status += " Please take a look at your App inputs " \
                              "and then try again. "
                    cherrypy.response.status = 403
                    return json.dumps(status + CONTACT)


                # Store current intentions
                log_dict["current_intentions"] = current_items

                # Store time: parsing current intentions
                timer["Parsing current items"] = time.time() - tic



                if method == "prototype":

                    tic = time.time()

                    final_tasks = assign_points(
                        current_items, threshold=cost_threshold
                    )

                    # Add database entry if one does not exist
                    if query is None:
                        db.pr_transform.insert_one({
                            "user_id": jsonData["userkey"],
                            "cost_threshold":    params["cost_threshold"],
                        })


                    timer["Run Prototype"] = time.time() - tic

                else:
                    status = "API method does not exist. Please contact us " \
                             "at sakshamconsul@gmail.com."
                    store_log(db.request_log, log_dict, status=status)
                    cherrypy.response.status = 403
                    return json.dumps(status)

                # Start timer: Anonymizing data
                tic = time.time()

                # Update values in the tree
                log_dict["tree"] = delete_sensitive_data(projects)

                # Store time: Anonymizing date
                timer["Anonymize data"] = time.time() - tic

                print("aaa")

                print(api_method, scheduler)
                # TODO:
                print(scheduler == "basic")


                # Schedule tasks for today
                if scheduler == "basic":
                    try:
                        # Get task list from the tree
                        task_list = task_list_from_projects(projects)

                        print("bbb")

                        final_tasks = \
                            basic_scheduler(task_list,
                                            current_day=user_datetime,
                                            duration_remaining=today_minutes)
                    except Exception as error:
                        print("lol")
                        status = str(error) + ' '

                        # Store error in DB
                        store_log(db.request_log, log_dict, status=status)

                        cherrypy.response.status = 403
                        return json.dumps(status + CONTACT)



                if api_method in \
                        {"getBest"}:
                    try:

                        # Start timer: Storing human-readable output
                        tic = time.time()

                        # TODO:
                        final_tasks = get_final_output(
                            final_tasks, round_param, points_per_hour,
                            user_datetime=user_datetime)

                        # Store time: Storing human-readable output
                        timer["Storing human-readable output"] = time.time() - tic

                    except NameError as error:

                        store_log(db.request_log, log_dict,
                                  status="Task has no name!")
                        cherrypy.response.status = 403
                        return json.dumps(str(error) + " " + CONTACT)

                    except:
                        status = "Error while preparing final output."
                        store_log(db.request_log, log_dict, status=status)
                        cherrypy.response.status = 403
                        return json.dumps(status + " " + CONTACT)

                    # Start timer: Storing successful pull in database
                    tic = time.time()

                    store_log(db.request_log, log_dict, status="Successful pull!")

                    # Store time: Storing successful pull in database
                    timer["Storing successful pull in database"] = time.time() - tic

                    # print("\n===== Optimal items =====")
                    # for task in final_tasks:
                    #     # print(f"{task['nm']} & {task['val']} \\\\")
                    #     print(f"{task['nm']:100s} | {task['val']}")
                    # print()

                    if api_method == "speedTest":

                        status = f"The procedure took " \
                                 f"{time.time() - main_tic:.3f} seconds!"

                        # Stop timer: Complete SMDP procedure
                        timer["Complete SMDP procedure"] = \
                            time.time() - main_tic

                        return json.dumps({
                            "status": status,
                            "timer":  timer
                        })

                    else:
                        # Return scheduled tasks
                        return json.dumps(final_tasks)

                else:
                    status = "API Method not implemented. Please contact us " \
                             "at sakshamconsul@gmail.com."
                    store_log(db.request_log, log_dict, status=status)

                    cherrypy.response.status = 405
                    return json.dumps(status)

            except stopit.utils.TimeoutException:
                return json.dumps("Timeout!")

            except Exception as error:
                status = "The API has encountered an error, please try again."

                # status = str(error)

                # Store anonymous error info in DB collection
                anonymous_error = parse_error_info(str(error))
                try:
                    store_log(db.request_log, log_dict,
                              status=status + " " + anonymous_error)
                except:
                    store_log(
                        db.request_log,
                        {"start_time": log_dict["start_time"],
                         "status":
                             status + " " +
                             "Exception while storing anonymous error info."})

                cherrypy.response.status = 403
                return json.dumps(status + " " + CONTACT)


class Root(object):
    api = PostResource()

    @cherrypy.expose
    def index(self):
        return "Server is up!"
        # return "REST API for App Project"


if __name__ == '__main__':
    uri = "mongodb://climatechangers:climatechangers@127.0.0.1/climatechangers"
    client = MongoClient(uri)
    db = client["climatechangers"]
    collection = db["climatechangers"]
    # conn = MongoClient(os.environ['MONGODB_URI'] + "?retryWrites=false")
    # db = conn.heroku_g6l4lr9d

    conf = {
        '/':       {
            # 'tools.sessions.on': True,
            'tools.response_headers.on':      True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')]},
        '/static': {
            'tools.staticdir.on':    True,
            'tools.staticdir.dir':   os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'static'),
            'tools.staticdir.index': 'urlgenerator.html'
        }
    }

    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update(
        {'server.socket_port': int(os.environ.get('PORT', '6789'))})
    cherrypy.quickstart(Root(), '/', conf)
