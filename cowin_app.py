# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 12:17:39 2021

@author: CSU5KOR
"""

from cowin_api import CoWinAPI
import pandas as pd 
import streamlit as st
import base64

#states = cowin.get_states()
#print(states)

#pin_code = "700029"
#date = '03-05-2021'  # Optional. Default value is today's date
#min_age_limit = 18  # Optional. By default returns centers without filtering by min_age_limit
#the function download_link is taken from streamlit discussions
def download_link(object_to_download, download_filename, download_link_text):
    
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'



pin_code = st.sidebar.text_input('Enter Pin code',value='700032',max_chars=6)#"700029"
age_group=st.sidebar.radio('Select age group',('All','18-45'))
vaccine=st.sidebar.radio('Select Vaccine',('COVAXIN','COVISHIELD'))

cowin = CoWinAPI()
available_centers = cowin.get_availability_by_pincode(pin_code)
available_centers.keys()

data_vals=available_centers['centers']

if len(data_vals)>0:
    len_data_vals=len(data_vals)
    final_data=pd.DataFrame()
    for d in range(len_data_vals):
        vac_schedule=data_vals[d]
        keys=list(vac_schedule.keys())
        target_keys=['center_id','name','address','state_name','district_name','pincode','fee_type','from','to']
        if vac_schedule['fee_type']!='Free':
            vaccine_info=vac_schedule['vaccine_fees']
            vaccine_info_len=len(vaccine_info)
            
            
            vaccine_info_dat=pd.DataFrame()
            for i in range(len(vaccine_info)):
                vaccine_dat=vaccine_info[i]
                vaccine_name=vaccine_dat['vaccine']
                vaccine_fee=vaccine_dat['fee']
                vaccine_array=pd.DataFrame([vaccine_name,vaccine_fee]).T
                vaccine_info_dat=pd.concat([vaccine_info_dat,vaccine_array],axis=0)
            vaccine_info_dat.columns=['Vaccine','fee']
        else:
            vaccine_info_dat=pd.DataFrame(['NULL','0']).T
            vaccine_info_dat.columns=['Vaccine','fee']
            
            
        json_keys=['sessions','vaccine_fees']
        target_vals=[]
        for t in target_keys:
            data_row=vac_schedule[t]
            target_vals.append(data_row)
        target_vals=pd.DataFrame(target_vals).T
        target_vals.columns=target_keys
        target_vals=pd.concat([target_vals,vaccine_info_dat],axis=1)
        
        session_info=vac_schedule['sessions']
        len_sessions=len(session_info)
        
        full_session_info=pd.DataFrame()
        for s in range(len_sessions):
            session_vals=session_info[s]
            session_keys=list(session_vals.keys())
            session_list=[]
            session_vals_data='x'
            for k in session_keys:
                if k=='session_id':
                    session_vals_data='0'
                else:
                    session_vals_data=session_vals[k]
                    #print(k)
                session_list.append(session_vals_data)
            session_list=pd.DataFrame(session_list).T
            full_session_info=pd.concat([full_session_info,session_list],axis=0)
        
        #session_keys.remove(session_keys[0])
        
        full_session_info.columns=session_keys
        full_session_info=full_session_info.drop('session_id',axis=1)
        
        all_data=pd.concat([target_vals,full_session_info],axis=1)
        final_data=pd.concat([final_data,all_data],axis=0)
    final_data=final_data.drop('Vaccine',axis=1)
else:
    final_data=pd.DataFrame(['Rsult','Notfound']).T
if len(data_vals)>0:
    if age_group=='All':
        final_data_subset=final_data
    else:
        final_data_subset=final_data[final_data['min_age_limit']<=18]
    final_data_subset=final_data_subset[final_data_subset['vaccine']==vaccine]
    st.dataframe(final_data_subset,height=1500,width=1000)
    if st.button('Download vaccine information as csv'):
        tmp_download_link = download_link(final_data_subset, pin_code+'.csv', 'Click here to download your data!')
        st.markdown(tmp_download_link, unsafe_allow_html=True)
else:
    st.dataframe(final_data,height=1500,width=1000)


#all_data.drop_duplicates()

