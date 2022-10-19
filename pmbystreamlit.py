# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
import json
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


def get_data(station_name = '종로구',
             ApiKey = '6RVOGGZcTp3G0jdog5E8DjFgsN3hd8p2nauoISfqMn9uJG+yvF4cKkdkDWKJONMQ9pqLGIHQoL3igJsqWTUyPQ=='):
    url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
    params = {'stationName':station_name,
            'dataTerm':'month',
            'pageNo':'1',
            'numOfRows':'100',
            'returnType':'json',
            'serviceKey':ApiKey,
            'ver':'1.1'}
    
    response = requests.get(url, params = params)
    data = json.loads(response.content)
    data = data['response']['body']['items']    

    name_list = []
    value_list = []
    
    for i in range(len(data)):
        if i == 0:name_list = list(data[i].keys())
        value_list.append(list(data[i].values()))
    
    env_df = pd.DataFrame(value_list, columns=name_list)
    
    env_df['pm10Value'] = env_df['pm10Value'].astype('int')
    env_df['pm25Value'] = env_df['pm25Value'].astype('int')
    env_df['pm10Value24'] = env_df['pm10Value24'].astype('int')
    env_df['pm25Value24'] = env_df['pm25Value24'].astype('int')
    
    env_df[['date','time']] = env_df['dataTime'].str.split(expand=True)
    env_df['dataTime'] = (pd.to_datetime(env_df.pop('date'), format='%Y/%m/%d') + 
                  pd.to_timedelta(env_df.pop('time') + ':00'))
    
    return env_df.sort_values(by = 'dataTime').reset_index()

def draw_chart(data):
    st.dataframe(data)
    
    chart = alt.Chart(data).mark_line().encode(x = 'dataTime', y = 'pm10Value')
    st.altair_chart(chart, use_container_width=True)
    
    
def get_chart(data):
    hover = alt.selection_single(
        fields=["dataTime"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="Particulate Matter Values Chart")
        .mark_line()
        .encode(
            x="dataTime",
            y="Value",
            color = "classify"
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="dataTime",
            y="Value",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("Value", title="pmValue"),
                alt.Tooltip("dataTime", title="Date"),
                
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

    
station_list = ['마포구', '종로구']

selected_station = st.selectbox("Select Station", station_list)


## streamlit 구성.
st.title('Particulate Matter Now')

data_load_state = st.text('Loading data')
data = get_data(station_name=selected_station)
data_load_state.text("Done! (using st.cache)")

## 오늘의 미세먼지


col1, col2 = st.columns(2)

with col1:
    st.subheader("Today's pm10 Value")
    st.info("{}".format(data["pm10Value"].iloc[-1]))
    
    st.subheader("Today's pm25 Value")
    st.warning("{}".format(data["pm25Value"].iloc[-1]))
    

with col2:
    st.subheader("Today's pm10 24avg Value")
    st.success("{}".format(data["pm10Value24"].iloc[-1]))
    
    st.subheader("Today's pm25 24avg Value")
    st.error("{}".format(data["pm25Value24"].iloc[-1]))


st.subheader("PM Value Now Chart")
# st.line_chart(data[['pm10Value', 'pm25Value']])


# get pm10 and pm25 data
clear_data1 = data[['dataTime','pm10Value']].rename(columns = {'pm10Value' : 'Value'})
clear_data1['classify'] = 'pm10Value'
clear_data2 = data[['dataTime','pm25Value']].rename(columns = {'pm25Value' : 'Value'})
clear_data2['classify'] = 'pm25Value'


clear_data = pd.concat([clear_data1, clear_data2], axis = 0).reset_index(drop=True)

# draw pm10 and pm25 chart
chart = get_chart(clear_data)
st.altair_chart(chart, use_container_width=True)


# avg chart
avg_data1 = data[['dataTime','pm10Value24']].rename(columns = {'pm10Value24' : 'Value'})
avg_data1['classify'] = 'pm10Value24'
avg_data2 = data[['dataTime','pm25Value24']].rename(columns = {'pm25Value24' : 'Value'})
avg_data2['classify'] = 'pm25Value24'

avg_data = pd.concat([avg_data1, avg_data2], axis = 0).reset_index(drop=True)

# draw pm10 and pm25 avg chart
st.subheader("PM Value 24 Chart")

avg_chart = get_chart(avg_data)
st.altair_chart(avg_chart, use_container_width=True)

# all pm chart
st.subheader("All pm Chart Display")

all_data = pd.concat([clear_data,avg_data], axis = 0)
all_chart = get_chart(all_data)
st.altair_chart(all_chart, use_container_width=True)