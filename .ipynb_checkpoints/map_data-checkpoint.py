# # 새마을ODA 지도

import pandas as pd
import re
import os
import sys
import base64
import numpy as np
import streamlit as st
import folium
import json
from PIL import Image
from io import BytesIO
from folium import plugins
from streamlit_jupyter import StreamlitPatcher, tqdm
from streamlit_option_menu import option_menu
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

st.markdown(
    """
    <style>
    @font-face {
        font-family: 'MyCustomFont';
        src: url('./fonts/KoPubDotumMedium.ttf') format('truetype');
    }

    body {
        font-family: 'MyCustomFont', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'MyCustomFont', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# ## 1. 데이터불러오기

# ### 1-1. ODA 필요 데이터 목록 확인

# #### (1) 필요 데이터 목록

# - 수원국 데이터 : country_info
# - 시범마을사업데이터(사업) : pilot_village
# - 초청연수프로그램 데이터 : invited_train
# - 기준연도 데이터 : standard_year
# - 국가목록 데이터 : country_list
# - 국가면적 데이터 : country_map

# ### 1-2. 수원국 데이터 및 국가목록 데이터 결합

from excel_data import country_info, country_list, pilot_village, invited_train, standard_data

country_data = pd.merge(country_info, country_list, left_on=['국가명', '대륙'], right_on=['국가명', '대륙명'], how='left')


# ### 1-3. 필요 색상 데이터

# #### (1) GDP별 색추가
# - 상위소득국 : 연한 초록색
# - 하위중소득국 : 하늘색
# - 최저개발국 : 파란색

def gdp_color(df):
    for data in df['features']:
        result = data['properties'].get('GDP구분', '')
        if result == '상위중소득국':
            data['properties']['gdp색상'] = 'lightblue'
        elif result == '하위중소득국':
            data['properties']['gdp색상'] = '#3284c7'
        elif result == '최저개발국':
            data['properties']['gdp색상'] = 'darkblue'
    return df


# #### (2) SGL회원 구분별 색추가

def sgl_color(row):
    if row['SGL회원국구분'] == '정회원국':
        return 'green'
    elif row['SGL회원국구분'] == '준회원국':
        return 'red'
    elif row['SGL회원국구분'] == '비회원국':
        return 'purple'
    else:
        return 'gray'


# #### (3) 새마을ODA 중점협력국여부 색추가

def prioirty_color(row):
    if row['중점협력국여부'] == '해당':
        return 'purple'
    elif row['중점협력국여부'] == '비해당':
        return 'green'
    else:
        return 'gray'


# ### 1-4. 새마을ODA지도를 위한 데이터 결합

# #### (1) 사업시작연도, 사업종료연도 데이터 저장

# #### (2) 사업종료연도가 최신인 데이터만 추가로 저장

def pilot_invited_filter():
    pilot_data = pilot_village[['대상국가', '사업시작연도', '사업종료연도']]
    invited_data = invited_train[['초청연수_국가명1', '초청연수_국가명2', '초청연수_국가명3', '초청연수_국가명4', '초청연수_국가명5', '사업연도']]
    ### 시범마을 데이터 ###
    # 시범마을 데이터에 존재하는 국가만 필터링
    country_info_data = pilot_data[pilot_data['대상국가'].isin(country_data['국가명'])]

    # 종료연도 기준으로 최신데이터 선택
    latest_data = country_info_data.loc[country_info_data.groupby('대상국가')['사업종료연도'].idxmax()]
    
    # 수원국 데이터에 추가
    for index,row in latest_data.iterrows():
        country_data.loc[country_data['국가명'] == row['대상국가'], '사업시작연도'] = row['사업시작연도']
        country_data.loc[country_data['국가명'] == row['대상국가'], '사업종료연도'] = row['사업종료연도']
        
    # 사업시작연도, 사업종료연도 타입 변경
    country_data['사업시작연도'] = country_data['사업시작연도'].astype('Int64')
    country_data['사업종료연도'] = country_data['사업종료연도'].astype('Int64')
    
    # 사업시작연도, 사업종료연도 이름 변경
    country_data.rename(columns={'사업시작연도':'시범마을시작연도', '사업종료연도':'시범마을종료연도'}, inplace=True)
    
    ### 초청연수 데이터 ###
    # 각 국가별로 단일로 저장
    single_country = invited_data.melt(id_vars=['사업연도'],
                                       value_vars=['초청연수_국가명1', '초청연수_국가명2', '초청연수_국가명3', 
                                                   '초청연수_국가명4', '초청연수_국가명5'],
                                       var_name = 'source', value_name='국가명')
    
    # NaN 값 제거 및 인덱스 초기화
    single_country = single_country.dropna(subset=['국가명'])
    
    # 종료연도 기준으로 최신데이터 선택
    latest_data = single_country.loc[single_country.groupby('국가명')['사업연도'].idxmax()]
    
    # 수원국 데이터에 추가
    for index, row in latest_data.iterrows():
        country_data.loc[country_data['국가명'] == row['국가명'], '사업연도'] = row['사업연도']
        
    # 사업시작연도, 사업종료연도 타입 변경
    country_data['사업연도'] = country_data['사업연도'].astype('Int64')
    
    # 사업시작연도, 사업종료연도 이름 변경
    country_data.rename(columns={'사업연도':'초청연수연도'}, inplace=True)
    return country_data


# ### 2-2. 국가면적데이터

# +
# PyInstaller로 빌드된 실행 파일에서 파일 경로를 찾을 때
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 경우, sys._MEIPASS로 압축 해제된 경로를 얻을 수 있어
    current_directory = sys._MEIPASS
else:
    # 개발 중일 때 (로컬에서 실행)
    current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

# dist 폴더 내의 countries_data.json 경로 만들기
json_file_path = os.path.join(current_directory, 'screen_display_data', 'countries_data.json')

# JSON 파일 열기
try: 
    with open(json_file_path, "r", encoding='utf-8') as f:
        country_map = json.load(f)
except FileNotFoundError as e:
    print(f"파일을 찾을 수 없습니다: {e}")
    sys.exit(1)


# -

def country_map_data():
    for i in range(len(country_map['features'])):
        total_info = country_map['features'][i]
        country_nm = total_info['properties']['NAME_KO']
        country_code = total_info['properties']['ISO_A3']
    
    # NAME_KO: 국가명 , 국가코드 3자리 이외 데이터 제거
    for feature in country_map['features']:
        properties = feature['properties']
        keys_to_keep = ['NAME_KO', 'ISO_A3']
        properties = {key: properties[key] for key in keys_to_keep if key in properties}
        feature['properties'] = properties
    return country_map


# ## 3. 새마을ODA 사업분포 지도

# ### 3-1. 새마을ODA 사업분포 지도시각화

# 57개국 Marker 표시
# popup 내용변경 필요
def oda_country57(country_data):
    if 'oda_map' not in st.session_state:
        # 중심지표시
        m = folium.Map(location=[13.318817, 20.631133],
                       max_bound=True,
                       tiles="Cartodb Positron",
                       zoom_start=3
                      )
    
        # 클릭시 텍스트
        for index, row in country_data.iterrows():
            try:
                if not pd.isna(row['초청연수연도']) and not pd.isna(row['시범마을시작연도']):
                    # 두 데이터 모두 존재할 경우
                    popup_content = f"""
                    <div style = "font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                    {row['국가명']} ({row['국가영문명']})
                    </div>
                    <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
                    <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                    초청연수: {row['초청연수연도']}  <br>
                    시범마을: {row['시범마을시작연도']}-{row['시범마을종료연도']} <br>
                    </div>
                    """
                elif not pd.isna(row['초청연수연도']):
                    # 초청연수만 존재할 경우
                    popup_content = f"""
                    <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                    {row['국가명']} ({row['국가영문명']})
                    </div>
                    <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
                    <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                    초청연수: {row['초청연수연도']}
                    </div>
                    """
                elif not pd.isna(row['시범마을시작연도']):
                    # 시범마을만 존재할 경우
                    popup_content = f"""
                    <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                    {row['국가명']} ({row['국가영문명']})
                    </div>
                    <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
                    <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                    시범마을: {row['시범마을시작연도']}-{row['시범마을종료연도']}
                    </div>
                    """
                    
                tooltip = folium.Tooltip(popup_content)
                folium.CircleMarker(
                    location=[row['위도'], row['경도']],
                    radius=7,   # 원의 크기
                    color='lightgray',  # 테두리색
                    weight=0.5,   # 테두리 굵기
                    fill=True,  # 채우기 여부
                    fill_color='blue',  # 채우기색
                    fill_opacity=0.8 # 투명도 (높아질수록 투명도 내려감)
                ).add_child(tooltip).add_to(m)
            except Exception as e:
                print(f"오류 발생: {e}, 행번호 : {index}, 데이터 : {row}")
                
        st.session_state.oda_map = m
    else:
        m = st.session_state.oda_map

    return m


# ## 4. 새마을ODA 국가 인당 GDP 지도

# ### 4-1. 새마을ODA 국가 인당 GDP 지도

# #### (1) 국가면적 데이터에서 57개국 이외 면적제거

def country_size(country_data):
    country_code = dict(zip(country_data['고유코드'], zip(country_data['GDP구분'], country_data['인당GDP'])))
    filtered_data = []
    country_nameko_iso = country_map_data()
    for feature in country_nameko_iso['features']:
        feature_id = feature['properties'].get('ISO_A3')
        if feature_id in country_code:
            gdf_info = country_code[feature_id]  # 튜플 언팩킹
            gdp_category, per_capita_gdp = gdf_info  # GDP구분과 인당GDP(달러) 분리
    
            # properties 업데이트
            feature['properties'].update({
                'GDP구분': gdp_category,
                '인당GDP(달러)': per_capita_gdp
            })
            filtered_data.append(feature)

    filtered_country_map = {
    'type': 'FeatureCollection',
    'features': filtered_data
    }
    filtered_country_map = gdp_color(filtered_country_map)
    return filtered_country_map


# + active=""
# len(filtered_data) # 57개국
# -

# #### (2) GDP별 지도시각화

# popup 내용변경 필요
def oda_gdp_map(filtered_country_map):
    # 중심지표시
    m = folium.Map(location=[13.318817, 20.631133], #34.7626, -35.3273
                   tiles="Cartodb Positron",
                   zoom_start=3
                  )

    # 면적표시
    folium.GeoJson(
        filtered_country_map,
        style_function= lambda features : {
            'fillColor': features['properties']['gdp색상'],
                                    'color':'black',
                                    'weight':0.1,
                                    'fillOpacity':0.9
                                   },
        tooltip=folium.GeoJsonTooltip(
            fields=['NAME_KO', '인당GDP(달러)', 'GDP구분'],
            aliases=['국가명:', '인당 GDP: $', 'GDP 분류:'],
            localize=True,
            style="""
            font-size: 14px;
            font-family: 'Nanum Gothic', sans-serif;
            white-space: nowrap;
            """
        )
    ).add_to(m)

    return m  # folium.Map 객체 반환


# ### 5-2. SGL회원 구분별 지도시각화

# 57개국 Marker 표시
def sgl_member(option):
    country_data = pilot_invited_filter()    
    # 색추가
    country_data['sgl색상'] = country_data.apply(sgl_color, axis=1)
    sgl_green = country_data[country_data['SGL회원국구분'] == '정회원국']
    sgl_red = country_data[country_data['SGL회원국구분'] == '준회원국']
    sgl_purple = country_data[country_data['SGL회원국구분'] == '비회원국']
    
    # 지도 초기화
    m = folium.Map(location=[13.318817, 20.631133],
                   max_bound=True,
                   tiles="Cartodb Positron",
                   zoom_start=3)

    if option == "회원국전체":
        for index, row in country_data.iterrows():
            popup_content = f"""
            <div style = "font-size: 14px;, sans-serif; white-space: nowrap;">
            {row['국가명']} ({row['국가영문명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px;, sans-serif; white-space: nowrap;">
            SGL 회원국 구분: {row['SGL회원국구분']} 
            </div>
            """
            tooltip = folium.Tooltip(popup_content)
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=7,
                color='lightgray',
                weight=0.5,
                fill=True,
                fill_color=row['sgl색상'],
                fill_opacity=0.8
            ).add_child(tooltip).add_to(m)

    elif option == "정회원국":
        for index, row in sgl_green.iterrows():
            popup_content = f"""
            <div style = "font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            {row['국가명']} ({row['국가영문명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            SGL 회원국 구분: {row['SGL회원국구분']}
            </div>
            """
            tooltip = folium.Tooltip(popup_content)
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=7,
                color='lightgray',
                weight=0.5,
                fill=True,
                fill_color=row['sgl색상'],
                fill_opacity=0.8
            ).add_child(tooltip).add_to(m)

    elif option == "준회원국":
        for index, row in sgl_red.iterrows():
            popup_content = f"""
            <div style = "font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            {row['국가명']} ({row['국가영문명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            SGL 회원국 구분: {row['SGL회원국구분']}
            </div>
            """
            tooltip = folium.Tooltip(popup_content)
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=7,
                color='lightgray',
                weight=0.5,
                fill=True,
                fill_color=row['sgl색상'],
                fill_opacity=0.8
            ).add_child(tooltip).add_to(m)

    elif option == "비회원국":
        for index, row in sgl_purple.iterrows():
            popup_content = f"""
            <div style = "font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            {row['국가명']} ({row['국가영문명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            SGL 회원국 구분: {row['SGL회원국구분']}
            </div>
            """
            tooltip = folium.Tooltip(popup_content)
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=7,
                color='lightgray',
                weight=0.5,
                fill=True,
                fill_color=row['sgl색상'],
                fill_opacity=0.8
            ).add_child(tooltip).add_to(m)

    return m 


# ## 6. 새마을ODA 중점협력국 지도

# ### 6-1. 중점협력국여부 지도시각화

def proy_member(option):
    country_data = pilot_invited_filter()
    country_data['proy색상'] = country_data.apply(prioirty_color, axis=1)
    country_data['중점협력국여부'] = country_data['중점협력국여부'].str.replace('Y', '해당')
    country_data['중점협력국여부'] = country_data['중점협력국여부'].str.replace('N', '비해당')  
    proy_o = country_data[country_data['중점협력국여부'] == '해당']
    proy_x = country_data[country_data['중점협력국여부'] == '비해당']
    
    # 중심지표시
    m = folium.Map(location=[13.318817, 20.631133],
                   max_bound=True,
                   tiles="Cartodb Positron",
                   zoom_start=3
                  )
    
    if option == "중점협력국전체":
        for index, row in country_data.iterrows():  
            popup_content = f"""
            <div style = "font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            {row['국가명']} ({row['국가영문명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            중점협력국: {row['중점협력국여부']} 
            </div>
            """
            # 마커표시
            tooltip = folium.Tooltip(popup_content)
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=7,   # 원의 크기
                color='lightgray',  # 테두리색
                weight=0.5,   # 테두리 굵기
                fill=True,  # 채우기 여부
                fill_color=row['proy색상'],  # 채우기색
                fill_opacity=0.8 # 투명도 (높아질수록 투명도 내려감)
            ).add_child(tooltip).add_to(m)

    elif option == "중점협력국_해당":
        for index, row in proy_o.iterrows():
            popup_content = f"""
            <div style = "font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            {row['국가명']} ({row['국가영문명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            중점협력국: {row['중점협력국여부']}
            </div>
            """
            # 마커표시
            tooltip = folium.Tooltip(popup_content)
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=7,   # 원의 크기
                color='lightgray',  # 테두리색
                weight=0.5,   # 테두리 굵기
                fill=True,  # 채우기 여부
                fill_color=row['proy색상'],  # 채우기색
                fill_opacity=0.8 # 투명도 (높아질수록 투명도 내려감)
            ).add_child(tooltip).add_to(m)
            
    elif option == "중점협력국_비해당":
        for index, row in proy_x.iterrows():
            popup_content = f"""
            <div style = "font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            {row['국가명']} ({row['국가영문명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            중점협력국: {row['중점협력국여부']}
            </div>
            """
            # 마커표시
            tooltip = folium.Tooltip(popup_content)
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=7,   # 원의 크기
                color='lightgray',  # 테두리색
                weight=0.5,   # 테두리 굵기
                fill=True,  # 채우기 여부
                fill_color=row['proy색상'],  # 채우기색
                fill_opacity=0.8 # 투명도 (높아질수록 투명도 내려감)
            ).add_child(tooltip).add_to(m)
    return m


# ## 7.새마을ODA 신규요청국 지도

# ### 7-1. 새마을ODA 신규요청국 지도시각화

def new_request(country_data):
    # 기준연도 저장 
    year = standard_data['기준연도'][0]

    # 신규요청국 저장
    new_ox = country_data[country_data['신규요청국여부'] == 'Y']
    new_ox = new_ox.copy()
    new_ox.loc[:, '신규요청국'] = 'ODA 요청'
    # 중심지표시
    m = folium.Map(location=[13.318817, 20.631133],
                   max_bound=True,
                   tiles="Cartodb Positron",
                   zoom_start=3
                  )
    
    for index, row in new_ox.iterrows():         
        popup_content = f"""
        <div style = "font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
        {row['국가명']} ({row['국가영문명']})
        </div>
        <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
        <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
        {year} {row['신규요청국']} 
        </div>
        """
        # 마커표시
        tooltip = folium.Tooltip(popup_content)
        folium.CircleMarker(
            location=[row['위도'], row['경도']],
            radius=7,   # 원의 크기
            color='lightgray',  # 테두리색
            weight=0.1,   # 테두리 굵기
            fill=True,  # 채우기 여부
            fill_color='blue',  # 채우기색
            fill_opacity=0.8 # 투명도 (높아질수록 투명도 내려감)
        ).add_child(tooltip).add_to(m)
        
    return m 


# ## 8. 새마을ODA 연락소분포 지도

# ### 8-1. 새마을ODA 연락소별 저장

# +
# base_path 설정 : 실행 파일 디렉토리를 기준으로 설정
def get_base_path():
    # PyInstaller로 패키징된 실행 파일인 경우
    if getattr(sys, 'frozen', False):
        # 실행 파일의 디렉토리
        return os.path.dirname(sys.executable)
    # 로컬 개발 환경
    else:
        return os.getcwd()
try:
    base_path = os.path.join(get_base_path(), 'screen_display_data', '연락소로고')
    image_paths = {
        "대한민국대사관": os.path.join(base_path, "대한민국대사관로고.png"),
        "KOICA": os.path.join(base_path, "KOICA로고.png"),
        "새마을회": os.path.join(base_path, "새마을회로고.png"),
    }
    # 각 파일의 존재 여부 확인
    for name, path in image_paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"{name}의 로고 파일을 찾을 수 없습니다: {path}")

except FileNotFoundError as e:
    print(f"파일을 찾을 수 없습니다: {e}")
    sys.exit(1)
except Exception as e:
    print(f"알 수 없는 에러가 발생했습니다: {e}")
    sys.exit(1)


# -

# 각 요소에 따라 값을 변경하는 함수 정의
def map_values():
    country_data = pilot_invited_filter() 
    country_data['연락소'] = country_data['대한민국대사관_유무'] + ',' + country_data['재단사무소_유무'] + ',' + country_data['KOICA사무소_유무']
    country_data['연락소'] = country_data['연락소'].replace('N', '', regex=True)
    
    country_data.loc[country_data['대한민국대사관_유무'] == 'Y', '연락소_아이콘'] = image_paths['대한민국대사관']
    country_data.loc[country_data['KOICA사무소_유무'] == 'Y', '연락소_아이콘'] = image_paths['KOICA']
    country_data.loc[country_data['재단사무소_유무'] == 'Y', '연락소_아이콘'] = image_paths['새마을회']
    country_data['연락소'] = country_data['연락소'].str.split(',')
    result = []
    
    # 각 리스트의 요소를 확인하며 값 추가
    for parts in country_data['연락소']:
        temp_result = []  # 각 행별 결과를 저장할 임시 리스트
        if isinstance(parts, list):
            if len(parts) > 0 and parts[0].strip() == 'Y':  # 첫 번째 요소 확인
                temp_result.append('대한민국대사관')
            if len(parts) > 1 and parts[1].strip() == 'Y':  # 두 번째 요소 확인
                temp_result.append('재단사무소')
            if len(parts) > 2 and parts[2].strip() == 'Y':  # 세 번째 요소 확인
                temp_result.append('KOICA사무소')
        result.append(', '.join(temp_result))  # 결과를 쉼표로 연결하여 문자열로 저장

    # 결과를 새로운 열에 추가
    country_data['연락소_결과'] = result

    return country_data


# ### 8-2. 새마을ODA 연락소분포 지도시각화

def contact_member(option):   
    country_data= map_values()
    korea_mofa = country_data[country_data['대한민국대사관_유무'] == 'Y']
    foundation = country_data[country_data['재단사무소_유무'] == 'Y'] 
    koica = country_data[country_data['KOICA사무소_유무'] == 'Y']
    # 중심지표시
    m = folium.Map(location=[13.318817, 20.631133],
                   max_bound=True,
                   tiles="Cartodb Positron",
                   zoom_start=3
                  )

    marker_cluster =MarkerCluster().add_to(m)
    if option == "연락소전체":
        for index, row in country_data.iterrows():
            popup_content = f"""
                <div style = "font-size: 15px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                {row['연락소_결과']}
                </div>
                <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
                <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                • 대상국가: {row['국가명']}
                </div>
                """
            
            icon_custom = folium.CustomIcon(icon_image=row['연락소_아이콘'], icon_size=(25,25))
            # 마커표시
            tooltip = folium.Tooltip(popup_content)
            folium.Marker(location=[row['위도'], row['경도']], tooltip=tooltip,
                          icon=icon_custom
                         ).add_to(m)
        
    elif option == "대한민국대사관":
        for index, row in korea_mofa.iterrows():
            popup_content = f"""
            <div style = "font-size: 15px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            {row['국가명']} 대한민국대사관
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            • 대상국가: {row['국가명']}
            </div>
            """

            icon_custom = folium.CustomIcon(icon_image=image_paths['대한민국대사관'], icon_size=(25,25))
            # 마커표시
            tooltip = folium.Tooltip(popup_content)
            folium.Marker(location=[row['위도'], row['경도']], tooltip=tooltip,
                          icon=icon_custom
                         ).add_to(m)

    elif option == "재단사무소":
        for index, row in foundation.iterrows():
            popup_content = f"""
            <div style = "font-size: 15px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            새마을재단사무소
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            • 대상국가: {row['국가명']}
            </div>
            """
            
            icon_custom = folium.CustomIcon(icon_image=image_paths['새마을회'], icon_size=(25,25))
            # 마커표시
            tooltip = folium.Tooltip(popup_content)
            folium.Marker(location=[row['위도'], row['경도']], tooltip=tooltip,
                          icon=icon_custom
                         ).add_to(m)

    elif option == "KOICA사무소":
        for index, row in koica.iterrows():
            popup_content = f"""
            <div style = "font-size: 15px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            kOICA 사무소
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
            • 대상국가: {row['국가명']}
            </div>
            """
            
            icon_custom = folium.CustomIcon(icon_image=image_paths['KOICA'], icon_size=(25,25))
            # 마커표시
            tooltip = folium.Tooltip(popup_content)
            folium.Marker(location=[row['위도'], row['경도']], tooltip=tooltip,
                          icon=icon_custom
                         ).add_to(m)
    return m


def logo_data(contact_name):
    base_path = os.path.join(get_base_path(), 'screen_display_data', '연락소로고')
    # 이미지 경로 설정 (screen_display_data 디렉토리 내의 로고 이미지)
    image_path = os.path.join(base_path, f'{contact_name}.png')
    
    try:
        # 이미지 열기
        icon = Image.open(image_path)
        
        # 'RGBA' 모드이면 투명 배경을 흰색으로 채운 후 'RGB'로 변환
        if icon.mode == 'RGBA':
            # 새 흰색 배경 이미지 만들기
            background = Image.new('RGB', icon.size, (255, 255, 255))  # 흰색 배경
            background.paste(icon, (0, 0), icon.split()[3])  # alpha 채널을 마스크로 사용하여 붙여넣기
            icon = background
        else:
            icon = icon.convert('RGB')  # 이미 RGB 모드라면 그대로 진행

        # JPEG로 저장하기
        buffered = BytesIO()
        icon.save(buffered, format='JPEG')
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return img_str
    
    except FileNotFoundError:
        print(f"Error: The image {image_path} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
