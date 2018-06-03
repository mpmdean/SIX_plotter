import numpy as np
import pandas as pd
from collections import OrderedDict
import datetime, time

import matplotlib.pyplot as plt

from databroker import get_events, get_table, DataBroker as DB

import ipywidgets as widgets

# Functions
def stopped(header):
    try:
        status = header.stop['exit_status']
    except KeyError:
        status = 'Python crash before exit'
    
    if status == 'success':
        return True
    else:
        return False
    
    
def get_scan_id_dict(headers):
    return OrderedDict([(get_scan_desc(header), header) for header in headers if stopped(header)])

def get_keys(header):
    try:
        keys = header.table().keys()
        key_list = sorted(list(keys))
        return key_list
    except:
        return []

def get_scanned_motor(header):
    try:
        return ' '.join(header.start['motors'])
    except:
        return ''

def get_scan_desc(header):
    return '{} {} {}'.format(header.start['scan_id'], header.start['plan_name'], get_scanned_motor(header))

# Widgets

today_string = str(datetime.datetime.now().date())
DB_search_widget = widgets.Text(description='Database search',
                                value='since=\'{}\''.format(today_string))
refresh_headers_widget = widgets.Button(description='Refresh')

select_scan_id_widget = widgets.Select(description='Select scan id')

select_x_widget = widgets.Dropdown(description='x')

select_y_widget = widgets.Dropdown(description='y')

select_mon_widget = widgets.Dropdown(description='mon')

use_mon_widget = widgets.Checkbox(description='Normalize')

plot_button = widgets.Button(description='Plot')

clear_button = widgets.Button(description='Clear')

starting_values_display = widgets.Textarea(width='500px')

# bindings

def wrap_refresh(change):
    try:
        query = eval("dict({})".format(DB_search_widget.value))
        headers = DB(**query)
    except NameError:
        headers = []
        DB_search_widget.value += " -- is an invalid search"
    
    scan_id_dict = get_scan_id_dict(headers)
    select_scan_id_widget.options = scan_id_dict

    
refresh_headers_widget.on_click(wrap_refresh)
    
def wrap_select_scan_id(change):
    keys = get_keys(select_scan_id_widget.value)
    select_x_widget.options = keys
    scanned_motor = get_scanned_motor(select_scan_id_widget.value)
    try:
        usekey =  next((key for key in keys if scanned_motor in key), keys[0])
        select_x_widget.value = usekey
    except:
        pass
    
    select_y_widget.options = keys
    default_y = 'fccd_stats1_total'
    select_mon_widget.options = keys
    try:
        select_y_widget.value = default_y
    except:
        pass

select_scan_id_widget.observe(wrap_select_scan_id)

def wrap_plotit(change):
    header = select_scan_id_widget.value
    table = header.table()
    x = table[select_x_widget.value].values
    if use_mon_widget.value:
        y = table[select_y_widget.value].values / table[select_mon_widget.value].values
    else:
        y = table[select_y_widget.value].values
    
    label= header.start['scan_id']
    #print("x is {}".format(x))
    plt.plot(x, y, label=label)
    plt.xlabel(select_x_widget.value)
    plt.ylabel(select_y_widget.value)
    plt.legend()
    
    baseline_table = header.table(stream_name='baseline')
    start_values = pd.Series([getattr(baseline_table, key).values[0] for key in baseline_table.keys()], index=baseline_table.keys())
    starting_values_display.value = start_values.sort_index().to_string()

plot_button.on_click(wrap_plotit)

def wrap_clearit(change):
    plt.cla()
    
clear_button.on_click(wrap_clearit)

