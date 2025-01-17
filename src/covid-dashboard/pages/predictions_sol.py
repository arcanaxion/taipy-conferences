from taipy.gui import Markdown, invoke_long_callback
from taipy.config import Config
import taipy as tp 
import pandas as pd

import datetime as dt

Config.load('config/config.toml')
scenario_cfg = Config.scenarios['scenario']

scenario_selector = [(s.id, s.name) for s in tp.get_scenarios()]
selected_scenario = None
selected_date = dt.datetime(2020,10,1)

scenario_country = "No selected scenario"
scenario_date = "No selected scenario"
scenario_name = ""

result = pd.DataFrame({"Date":[dt.datetime(2020,1,1)],
                       "Deaths_x":[0],"Deaths_y":[0],
                       "Predictions_x":[0],"Predictions_y":[0]})

def create_new_scenario(state):
    if state.scenario_name is not None or state.scenario_name == "":
        scenario = tp.create_scenario(scenario_cfg, name=state.scenario_name)
        state.scenario_selector += [(scenario.id, scenario.name)]
        state.selected_scenario = scenario.id
        actualize_graph(state)
        

def submit_scenario(state):
    # 1) get the selected scenario
    # 2) write in country Data Node, the selected country
    # 3) submit the scenario
    # 4) actualize le graph avec actualize_graph
    if state.selected_scenario is not None:
        scenario = tp.get(state.selected_scenario)
        scenario.country.write(state.selected_country)
        scenario.date.write(state.selected_date.replace(tzinfo=None))
        tp.submit(scenario)
        actualize_graph(state)

def actualize_graph(state):
    # 1) update the result dataframe
    # 2) change selected_country with the predicted country of the scenario
    if state.selected_scenario is not None:
        scenario = tp.get(state.selected_scenario)
        result_arima = scenario.res_ar.read()
        result_linear = scenario.res_lin.read()
        if result_arima is not None and result_linear is not None:
            state.result = result_linear.merge(result_arima, on="Date", how="outer").sort_values(by='Date')
        else:
            state.result = result
        state.scenario_country = scenario.country.read()
        state.scenario_date = scenario.date.read().strftime("%d %B %Y")

predictions_md = Markdown("""
# Prediction page
  
## Scenario Creation
  
<|layout|columns=5 5 5 5|
**Scenario Name** <br/>
<|{scenario_name}|input|label=Name|> <br/> <|Create|button|on_action=create_new_scenario|>

**Prediction Date** <br/>
<|{selected_date}|date|label=Prediction date|>
<br/>
<|Submit|button|on_action=submit_scenario|>

<|{selected_country}|selector|lov={selector_country}|dropdown|on_change=on_change_country|label=Country|>
|>

---------------------------------------

## Result

<|layout|columns=2 3 3|
<|{selected_scenario}|selector|lov={scenario_selector}|on_change=actualize_graph|dropdown|value_by_id|label=Scenario|> 

### Country of prediction : <|{scenario_country}|>

### Date of prediction : <|{scenario_date}|>

|>
<br/>

<|{result}|chart|x=Date|y[1]=Deaths_x|type[1]=bar|y[2]=Predictions_x|y[3]=Predictions_y|>
""")