import json
import os
import stopit
import sys
import cherrypy
import cherrypy_cors
from pymongo import MongoClient
import time
import pandas as pd

from src.api import *
from src.utils import *



CONTACT = "If you continue to encounter this issue, please contact us at " \
          "support_team@becool.com."
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
        # print("YO")
        # print(cherrypy.request.method)
        if cherrypy.request.method == 'OPTIONS':
        #     # This is a request that browser sends in CORS prior to sending a real request.
        #
        #     # Set up extra headers for a pre-flight OPTIONS request.
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
            return {"ALLOW:": 'POST',
                    "Access-Control-Allow-Origin:": 'https://danielaleite.github.io'}


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

    @cherrypy.expose
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
                # print("VPATH")
                # for v in vpath:
                #     print(v)
                # Compulsory parameters
                method = vpath[0]  # Access the prototype module
                rounding = vpath[1]  # Number of decimals
                print(f'Rounding: {rounding}')
                # tree = vpath[-3]  # Dummy parameter
                user_key = vpath[-2]  # User Key
                api_method = vpath[-1]  # Which function in module to be accessed
                print(f'User Key: {user_key}"')
                print(f'API Method: {api_method}')
                # Additional parameters (the order of URL input matters!)
                # Casting to other data types is done within the functions that
                # use these parameters
                parameters = [item for item in vpath[2:-2]]
                print(f'parameters: {parameters}')
                # Add user key
                try:
                    log_dict["user_id"] = jsonData["userkey"]
                except:
                    status = "We encountered a problem with the inputs " \
                             "from our app, please try again."
                    store_log(db.request_log, log_dict, status=status)

                    cherrypy.response.status = 403
                    return json.dumps(status + " " + CONTACT)



                """ Reading Prototype parameters """
                if method == "prototype":
                    try:
                        method_tic = time.time()

                        print(f'JsonData.keys: {jsonData.keys()}')

                        if "cost_threshold" in jsonData.keys():
                            params["cost_threshold"] = jsonData["cost_threshold"]
                        cost_threshold = params["cost_threshold"]
                        print(f'Loading Thresh: {cost_threshold}')
                        timer["Reading parameters"] = time.time() - method_tic

                    except:
                        status = "There was an issue with the API input " \
                                 "(reading parameters) Please contact " \
                                 "us at support_team@becool.com."
                        store_log(db.request_log, log_dict, status=status)
                        cherrypy.response.status = 403
                        return json.dumps(status)

                else:  # Different module, not yet implemented
                    status = "The module you wanteed to access hasn't been implemented yet. Please contact " \
                             "us at support_team@becool.com."
                    store_log(db.request_log, log_dict, status=status)
                    cherrypy.response.status = 403
                    return json.dumps(status)
                # Last input parameter
                try:
                    round_param = int(rounding)
                except:
                    status = "There was an issue with the API input " \
                             "(rounding parameter). Please contact us at " \
                             "support_team@becool.com"
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
                    "status": None,
                    "user_id": None,
                })

                try:
                    location = jsonData["location"]
                except:
                    status = "No Location Field in Body!" \
                             "Please contact us at " \
                             "support_team@becool.com"
                    store_log(db.request_log, log_dict, status=status)
                    cherrypy.response.status = 403
                    return json.dumps(status)

                # Update last modified
                log_dict["lm"] = jsonData["updated"]

                log_dict["location"] = location

                # Store time: reading parameters
                timer["Reading parameters"] = time.time() - tic

                # Start timer: parsing current intentions
                tic = time.time()

                # Parse current intentions
                try:
                    parsed_dict = parse_current_items_list(db,
                        jsonData["shopping_list"], location)
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
                log_dict["current_categories"] = jsonData["shopping_list"]

                # Store time: parsing current intentions
                timer["Parsing current items"] = time.time() - tic


                if method == "prototype":
                    search_space = list(parsed_dict["search"])
                    print(f'Search: {search_space}')
                    units = np.array(parsed_dict["units"])
                    target_amounts = list(parsed_dict["amounts"])
                    prices = np.array(parsed_dict["prices"])
                    co2_emissions = np.array(parsed_dict["carbons"])

                    if api_method == "optimal_price":
                        tic_function = time.time()
                        try:
                            output = function_call(
                                flag=api_method, search_space=search_space, target_amounts=target_amounts, units=units,
                                prices=prices, co2_emissions=co2_emissions
                            )
                            log_dict["cheap_price"] = output["price"]
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

                    elif api_method == "optimal_co2":
                        tic_function = time.time()
                        try:
                            output = function_call(
                                flag="optimal_price", search_space=search_space, target_amounts=target_amounts,
                                units=units,
                                prices=prices, co2_emissions=co2_emissions
                            )
                            cheap_price = output["price"]
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
                        try:
                            output = function_call(
                                flag=api_method,search_space=search_space, target_amounts=target_amounts, units=units,
                                prices=prices, co2_emissions=co2_emissions, cost_threshold=cost_threshold/100.0, cheap_price=cheap_price)
                            print(f'Before Final Output: {output}')
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

                    else:
                        status = "API method (in Prototype module) does not exist. Please contact us " \
                                 "at support_team@becool.com."
                        store_log(db.request_log, log_dict, status=status)
                        cherrypy.response.status = 403
                        return json.dumps(status)
                    timer["Run Function"] = time.time() - tic_function

                    # Start timer: Anonymizing data
                    tic_anon = time.time()


                    if api_method in \
                            {"optimal_price", "optimal_co2"}:
                        try:

                            # Start timer: Storing human-readable output
                            tic = time.time()

                            # TODO:
                            final_shopping_list = get_final_output(search_space, output, api_method, rounding)
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


                        if api_method == "speedTest":

                            status = f"The procedure took " \
                                     f"{time.time() - main_tic:.3f} seconds!"

                            # Stop timer: Complete SMDP procedure
                            timer["Complete Optimization procedure"] = \
                                time.time() - main_tic

                            return json.dumps({
                                "status": status,
                                "timer":  timer
                            })

                        else:
                            # Return scheduled tasks
                            print(f'Final List')
                            for f_item in final_shopping_list:
                                print(f_item)
                            return json.dumps(final_shopping_list)

                else:
                    status = "API Method not implemented. Please contact us " \
                             "at support_team@becool.com."
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


def update(db):
    stock_list = pd.read_csv('./data_gen/StockInfo.csv')
    converted_stock_dict = pd.DataFrame.to_dict(stock_list, orient="records")
    # # To add data
    # db.stock_table.insert_many(converted_stock_dict)

    for item in converted_stock_dict:
        db.stock_table.update_one({
            "$and": [
                {"Location": item["Location"]},
                {"Product Name": item["Product Name"]}
            ]
        }, {"$set": {"Price": item["Price"]}})
    return 0


if __name__ == '__main__':
    uri = "mongodb+srv://cool_usr:cool_pwd@becoolcluster.xv0y0.mongodb.net/BeCool"
    client = MongoClient(uri)
    # Creating database if it does not exist
    db = client["BeCool"]
    # Creating a collection (aka table)
    stock_table = db["Inventory"]

    # update the Inventory
    update(db)
    cherrypy_cors.install()
    conf = {
        '/':       {
            # 'tools.sessions.on': True,
            'tools.response_headers.on':      True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain'),
                                               ('Access-Control-Allow-Origin', 'https://danielaleite.github.io')]},
        '/static': {
            'tools.staticdir.on':    True,
            'cors.expose.on': True,
            'tools.staticdir.dir':   os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'static'),
            'tools.staticdir.index': 'urlgenerator.html'
        }
    }

    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update(
        {'server.socket_port': int(os.environ.get('PORT', '8080'))})
    cherrypy.quickstart(Root(), '/', conf)
