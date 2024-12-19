# # 국가별 ODA사업 현황

import pandas as pd
import re
import numpy as np
import streamlit as st
from streamlit_jupyter import StreamlitPatcher, tqdm
from PIL import Image
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

pd.set_option('future.no_silent_downcasting', True)

# ## 1. 데이터불러오기

# ### 1-1. ODA 필요 데이터 목록 확인

# #### (1) 필요 데이터 목록

# - 수원국 데이터 : country_info
# - 시범마을사업데이터(사업) : pilot_village
# - 시범마을사업데이터(마을사업) : pilot_business
# - 초청연수프로그램 데이터 : invited_train
# - 기준연도 데이터 : standard_year
# - 국가목록 데이터 : country_list
# - 지역목록 데이터 : region_list
# - 사업시행기관목록 데이터 : business_list
# - 마을사업목록 : village_business

# ## 2. 데이터 전처리

# ### 2-1. 대시보드 표현 데이터로 변경

from excel_data import country_info, country_list, pilot_village, pilot_business, region_list, village_business, invited_train, standard_data, business_list


# ## 3. 국가별 데이터 넣기

def country_total_data():
    country_info1 = country_info.copy()
    country_info1['국가'] = country_list['국가명'] + '(' + country_list['국가영문명'] + ')'
    # 면적컬럼 변경
    country_info1['면적'] = country_info1['면적'].astype(int)
    country_info1['면적'] = country_info1['면적']/10000
    country_info1['면적'] = country_info1['면적'].apply(lambda x: f"{x:.2f}")
    country_info1['면적'] = country_info1['면적'].astype(str) + "만"
    # 인구 컬럼변경
    country_info1['인구'] = country_info1['인구'].astype(int)
    country_info1['인구'] = country_info1['인구'].apply(lambda x: f"{x:,}")
    country_info1['인구'] = country_info1['인구'].astype(str) + "만"
    # 인당GDP 컬럼변경
    country_info1['인당GDP'] = country_info1['인당GDP'].astype(int)
    country_info1['인당GDP'] = country_info1['인당GDP'].apply(lambda x: f"{x:,}")
    country_info1['인당GDP'] = "$" + country_info1['인당GDP'].astype(str)
    # 중점협력기간 데이터 추가
    country_info1['중점협력국기간_시작연도'] = country_info1['중점협력국기간_시작연도'].astype(str)
    country_info1['중점협력국기간_종료연도'] = country_info1['중점협력국기간_종료연도'].astype(str)
    country_info1['중점협력국기간'] = np.where(
        (country_info1['중점협력국기간_시작연도'] != '-') & (country_info1['중점협력국기간_종료연도'] != '-'),
        "'" + country_info1['중점협력국기간_시작연도'].str[2:] + '~' + "'" + country_info1['중점협력국기간_종료연도'].str[2:],
        '-'
    )
    return country_info1


# ### 3-1. 국기이미지 변경

# base_path 설정 : 실행 파일 디렉토리를 기준으로 설정
def get_base_path():
    # PyInstaller로 패키징된 실행 파일인 경우
    if getattr(sys, 'frozen', False):
        # 실행 파일의 디렉토리
        return os.path.dirname(sys.executable)
    # 로컬 개발 환경
    else:
        return os.getcwd()    


def image_data(country_name):
    base_path = os.path.join(get_base_path(), 'screen_display_data', '국기이미지')
    country_data = re.sub(r'\(.*?\)', '', country_name)
    image_path = os.path.join(base_path, f'{country_data}.jpg')
    try:
        if os.path.isfile(image_path):
            icon = Image.open(image_path)
            icon = icon.convert('RGB')
            buffered = BytesIO()
            icon.save(buffered, format='JPEG')
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        else:
            print(f"{country_name}의 이미지를 찾을 수 없습니다")
            
    except:
        print("이미지의 형식이 png 파일이 아닙니다")


# ### 3-2. 국가데이터 데이터프레임 넣기

def select_country_info(country_name):
    country_data = re.sub(r'\(.*?\)', '', country_name)
    country_info = country_total_data()
    if country_data in country_info['국가명'].values:
        # 국가 이름 및 국가명 넣기 
        area_info = country_info.loc[country_info['국가명'] == country_data, '면적'].values[0]
        population_info = country_info.loc[country_info['국가명'] == country_data, '인구'].values[0]
        gdp_info = country_info.loc[country_info['국가명'] == country_data, '인당GDP'].values[0]  #인당GPD
        gdp_split =country_info.loc[country_info['국가명'] == country_data, 'GDP구분'].values[0]  #인당GDP구분
        sql_info = country_info.loc[country_info['국가명'] == country_data, 'SGL회원국구분'].values[0]  #SGL회원국구분
        pcc_ox = country_info.loc[country_info['국가명'] == country_data, '중점협력국여부'].values[0]  #중점협력국여부
        pcc_period = country_info.loc[country_info['국가명'] == country_data, '중점협력국기간'].values[0] 
        pcc_part = country_info.loc[country_info['국가명'] == country_data, '중점협력분야'].values[0]  #중점협력분야
        new_ox = country_info.loc[country_info['국가명'] == country_data, '신규요청국여부'].values[0]  #신규요청국여부
        bie_ox = country_info.loc[country_info['국가명'] == country_data, 'BIE회원국여부'].values[0]  #BIE회원국여부
        mou_ox = country_info.loc[country_info['국가명'] == country_data, 'MOU여부'].values[0]  #MOU체결여부
        
        # 데이터프레임으로 변환
        data = {
            '면적' : [area_info],
            '인구' : [population_info],
            '인당GDP' : [gdp_info],
            'GDP 분류' : [gdp_split],
            'SGL회원국 분류' : [sql_info],
            '중점협력국 여부' : [pcc_ox],
            '중점협력국 기간' : [pcc_period],
            '중점협력분야' : [pcc_part],
            '신규요청 여부' : [new_ox],
            'BIE국 여부' : [bie_ox],
            'MOU체결 여부' : [mou_ox]
        }
        df = pd.DataFrame(data, index=[0])
        df1 = df.T
        df1.index.name = '항목'
        df1.columns= ['정보']
        styled_df = df1.style.set_table_attributes('style="border: 1px solid gray; border-collapse: collapse; margin: auto; width:100%; height: auto; overflow: auto;"') \
            .set_properties(**{'text-align': 'center', 'font-weight': 'bold', 'font-family': 'Malgun Gothic'}) \
            .set_table_styles([
                {
                    'selector': 'thead th',
                    'props': [('background-color', 'darknavy !important'), ('color', 'white')]
                },
                {
                    'selector': 'td',
                    'props': [('border', '1px solid gray'), ('background-color', 'white !important'), ('color', 'black')]
                },
                {
                    'selector': 'th',
                    'props': [('border', '1px solid gray')]
                },
                {
                    'selector': 'td:first-child',
                    'props': [('background-color', 'lightgray'),  # 옅은 회색
                              ('text-align', 'center'),  # 가운데 정렬
                              ('font-weight', 'bold')]  # 굵은 글씨
                },
                {
                    'selector': 'td:last-child',
                    'props': [('background-color', 'skyblue !important')]
                },
                # 인덱스를 숨기기 위한 스타일
                {
                    'selector': 'thead tr th:first-child',
                    'props': [('display', 'none')]
                },
                {
                    'selector': 'tbody th',
                    'props': [('display', 'none')]
                }
            ])
        
        return styled_df


# ### 3-3. 국가사진 넣기

def wiki_picture(country_name):
    base_path = os.path.join(get_base_path(), 'screen_display_data', '나라별사진') 
    country_data = re.sub(r'\(.*?\)', '', country_name)
    img_path = os.path.join(base_path, f'{country_data}.png')
    
    try:
        # 파일존재여부확인
        if os.path.isfile(img_path):
            img = Image.open(img_path)
            img = img.resize(size=(200,200))
            st.image(img)
        else:
            print(f"{country_name}의 이미지를 찾을 수 없습니다")
    except:
        print("이미지의 형식이 png 파일이 아닙니다")


# ### 3-3. 국가지도 넣기

# #### (1) 기관별 색추가

def orgin_color(row):
    if row['시행기관'] == '새마을운동중앙회':
        return 'gray'
    elif row['시행기관'] == '새마을재단':
        return 'orange'
    elif row['시행기관'] == 'KOICA':
        return 'skyblue'
    else:
        return ''


# #### (2) 추진상황별 색추가

def process_color(row):
    if row['추진상황'] == '진행':
        return 'green'
    elif row['추진상황'] == '신규':
        return 'blue'
    elif row['추진상황'] == '종료':
        return 'black'
    elif row['추진상황'] == '예정':
        return 'purple'
    else:
        return 'gray'


# #### (1) 시범마을사업데이터 중 사업, 마을사업 결합 

def village_map():
    # 시범마을사업데이터 중 사업, 마을사업 결합
    pilot = pd.merge(pilot_business, pilot_village, on='사업식별번호', how='left')
    pilot.drop(columns=['사업식별번호', '사업명_국문_x', '사업명_국문_y', '사업명_영문', '사업유형', '사업분야', '대상지역1', '대상지역2', '대상지역3', '대상지역4', '대상지역5', '대상지역6', '대상지역7', '대상지역8', '대상지역9', '대상지역10'],
                    inplace=True)

    # 결합데이터에 지역 위도, 경도 추가
    pilot_region = pd.merge(pilot, region_list, on = '지역명', how='left')
    pilot_region = pilot_region.drop(columns=['순번', '국가코드', '지역코드', '행번호'])
    pilot_region = pilot_region.dropna(how='all')
    pilot_region = pilot_region.rename(columns={'위도':'지역위도', '경도':'지역경도'})
    pilot_info = pd.merge(pilot_region, country_list, on =['국가명'], how='left')
    pilot_info['국가명'] = pilot_info['국가명'].fillna(pilot_info['대상국가'])
    # 중복값 제거
    pilot_info = pilot_info.drop_duplicates()

    # 마을사업을 모두 포함하는 컬럼 추가
    pilot_info['마을사업_통합'] = pilot_info[['마을사업1', '마을사업2', '마을사업3', '마을사업4', '마을사업5', '마을사업6', '마을사업7', '마을사업8', '마을사업9', '마을사업10']].fillna('').astype(str).agg(','.join, axis=1)
    pilot_info.drop(columns=['마을사업1', '마을사업2', '마을사업3', '마을사업4', '마을사업5', '마을사업6', '마을사업7', '마을사업8', '마을사업9', '마을사업10', '순번', '위도', '경도'], inplace=True)
    pilot_info['마을사업_통합'] = pilot_info['마을사업_통합'].str.replace(r',+', ',', regex=True)
    pilot_info['마을사업_통합'] = pilot_info['마을사업_통합'].str.rstrip(',')

    # 마을사업별 액션플랜 컬럼 추가
    business_category = dict(zip(village_business['마을사업'], village_business['대분류']))
    pilot_info['마을정비'] = pilot_info['마을사업_통합'].apply(
        lambda x: ', '.join([business.strip() for business in x.split(',') if business_category.get(business.strip()) == '마을정비'])
    )
    pilot_info['소득증대'] = pilot_info['마을사업_통합'].apply(
        lambda x: ', '.join([business.strip() for business in x.split(',') if business_category.get(business.strip()) == '소득증대'])
    )
    
    # 컬럼별 타입변경
    pilot_info['사업시작연도'] = pilot_info['사업시작연도'].astype('Int64')
    pilot_info['사업종료연도'] = pilot_info['사업종료연도'].astype('Int64')
    pilot_info['지역위도'] = pd.to_numeric(pilot_info['지역위도'], errors='coerce')
    pilot_info['지역경도'] = pd.to_numeric(pilot_info['지역경도'], errors='coerce')

    # NaN 값을 빈 문자열로 대체하기 전에 데이터 타입 변환
    excluded_columns = ['지역위도', '지역경도', '사업시작연도', '사업종료연도']
    for col in pilot_info.columns:
        if col not in excluded_columns:
            pilot_info[col] = pilot_info[col].astype(str)  # 문자열로 변환
    # NaN 값을 빈 문자열로 대체하기
    pilot_info.loc[:, ~pilot_info.columns.isin(excluded_columns)] = pilot_info.loc[:, ~pilot_info.columns.isin(excluded_columns)].fillna('')

    # 불필요 컬럼 제거
    pilot_info.drop(columns=['대상지역수', '고유코드'], inplace=True)
    pilot_info['orgin색상'] = pilot_info.apply(orgin_color, axis=1)
    pilot_info['process색상'] = pilot_info.apply(process_color, axis=1)
    return pilot_info


# #### (6) 나라별 지역표시

def lat_lon(country_name):
    country_list_info = country_list.copy()
    pilot_info = village_map()
    # 국가명일 경우
    if country_name in country_list_info['국가명'].values:
        lat = country_list_info.loc[country_list_info['국가명'] == country_name, "위도"].values[0]
        lon = country_list_info.loc[country_list_info['국가명'] == country_name, "경도"].values[0]
        return lat, lon


def country_map(country_name):
    # 국가 위도, 경도 추출하기
    country_data = re.sub(r'\(.*?\)', '', country_name)
    center = lat_lon(country_data)
    m = folium.Map(location=center,
                   max_bound=True,
                   tiles="Cartodb Positron",
                   zoom_start=7
                  )
    pilot_info = village_map()
    pilot_data = pilot_info[pilot_info['국가명'] == country_data] 
    has_valid_coords = False
    
    for index, row in pilot_data.iterrows():  
        # 지역 위,경도 없을 경우 패스
        if pd.isna(row['지역위도']) or pd.isna(row['지역경도']):
            continue

        has_valid_coords = True

        if row['마을정비'] != '' and row['소득증대'] != '':
            # 마을정비, 소득증대 모두 존재할 경우
            popup_content = f"""
            <div style="font-size: 18px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                {row['지역명']} ({row['국가명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif;">
                <div style="white-space: nowrap;">• 사업시행기관: {row['시행기관']}</div>
                <div style="white-space: nowrap;">• 사업예산: {row['총사업예산(백만원)']}</div>
                <div style="white-space: nowrap;">• 사업추진상황: {row['추진상황']}</div>
                <div style="white-space: nowrap;">• 사업기간: {row['사업시작연도']} ~ {row['사업종료연도']}</div>
                <div style="white-space: nowrap;">• 마을사업(마을정비): {row['마을정비']}</div>
                <div style="white-space: nowrap;">• 마을사업(소득증대): {row['소득증대']}</div>
            </div>
            """
        elif row['마을정비'] != '':
            # 마을정비만 존재할 경우
            popup_content = f"""
            <div style="font-size: 18px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                {row['지역명']} ({row['국가명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif;">
                <div style="white-space: nowrap;">• 사업시행기관: {row['시행기관']}</div>
                <div style="white-space: nowrap;">• 사업예산: {row['총사업예산(백만원)']}</div>
                <div style="white-space: nowrap;">• 사업추진상황: {row['추진상황']}</div>
                <div style="white-space: nowrap;">• 사업기간: {row['사업시작연도']} ~ {row['사업종료연도']}</div>
                <div style="white-space: nowrap;">• 마을사업(마을정비): {row['마을정비']}
            </div>
            """
        elif row['소득증대'] != '':
            # 마을정비만 존재할 경우
            popup_content = f"""
            <div style="font-size: 18px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                {row['지역명']} ({row['국가명']})
            </div>
            <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
            <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif;">
                <div style="white-space: nowrap;">• 사업시행기관: {row['시행기관']}</div>
                <div style="white-space: nowrap;">• 사업예산: {row['총사업예산(백만원)']}</div>
                <div style="white-space: nowrap;">• 사업추진상황: {row['추진상황']}</div>
                <div style="white-space: nowrap;">• 사업기간: {row['사업시작연도']} ~ {row['사업종료연도']}</div>
                <div style="white-space: nowrap;">• 마을사업(소득증대): {row['소득증대']}
            </div>
            """
        
    # 마커표시
        tooltip = folium.Tooltip(popup_content)
        folium.CircleMarker(
            location=[row['지역위도'], row['지역경도']],
            radius=6,   # 원의 크기
            color='lightgray',  # 테두리색
            weight=0.5,   # 테두리 굵기
            fill=True,  # 채우기 여부
            fill_color=row['orgin색상'],  # 채우기색
            fill_opacity=0.8 # 투명도 (높아질수록 투명도 내려감)
        ).add_child(tooltip).add_to(m)

    if not has_valid_coords:
        m = folium.Map(location=center,
               max_bound=True,
               tiles="Cartodb Positron",
               zoom_start=7
              )

    st_folium(m, width=1300, height=600, key="country_map_key")   


def select_country_map(country_name, village_name_list=None):
    # 국가 위도, 경도 추출하기
    country_data = re.sub(r'\(.*?\)', '', country_name)
    center = lat_lon(country_data)
    m = folium.Map(location=center,
                   max_bound=True,
                   tiles="Cartodb Positron",
                   zoom_start=7
                  )

    if village_name_list:
        pilot_info = village_map()
        
        for village_data in village_name_list:
            village_data = re.sub(r'\s+', '', village_data)
            pilot_data = pilot_info[pilot_info['지역명'] == village_data]
            for index, row in pilot_data.iterrows():      
                if row['마을정비'] != '' and row['소득증대'] != '':
                    # 마을정비, 소득증대 모두 존재할 경우
                    popup_content = f"""
                    <div style="font-size: 18px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                        {row['지역명']} ({row['국가명']})
                    </div>
                    <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
                    <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif;">
                        <div style="white-space: nowrap;">• 사업시행기관: {row['시행기관']}</div>
                        <div style="white-space: nowrap;">• 사업예산: {row['총사업예산(백만원)']}</div>
                        <div style="white-space: nowrap;">• 사업추진상황: {row['추진상황']}</div>
                        <div style="white-space: nowrap;">• 사업기간: {row['사업시작연도']} ~ {row['사업종료연도']}</div>
                        <div style="white-space: nowrap;">• 마을사업(마을정비): {row['마을정비']}</div>
                        <div style="white-space: nowrap;">• 마을사업(소득증대): {row['소득증대']}</div>
                    </div>
                    """
                elif row['마을정비'] != '':
                    # 마을정비만 존재할 경우
                    popup_content = f"""
                    <div style="font-size: 18px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                        {row['지역명']} ({row['국가명']})
                    </div>
                    <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
                    <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif;">
                        <div style="white-space: nowrap;">• 사업시행기관: {row['시행기관']}</div>
                        <div style="white-space: nowrap;">• 사업예산: {row['총사업예산(백만원)']}</div>
                        <div style="white-space: nowrap;">• 사업추진상황: {row['추진상황']}</div>
                        <div style="white-space: nowrap;">• 사업기간: {row['사업시작연도']} ~ {row['사업종료연도']}</div>
                        <div style="white-space: nowrap;">• 마을사업(마을정비): {row['마을정비']}
                    </div>
                    """
                elif row['소득증대'] != '':
                    # 마을정비만 존재할 경우
                    popup_content = f"""
                    <div style="font-size: 18px; font-family: 'Nanum Gothic', sans-serif; white-space: nowrap;">
                        {row['지역명']} ({row['국가명']})
                    </div>
                    <hr style="border: none; border-top: 1px solid #000; margin: 10px 0;">
                    <div style="font-size: 14px; font-family: 'Nanum Gothic', sans-serif;">
                        <div style="white-space: nowrap;">• 사업시행기관: {row['시행기관']}</div>
                        <div style="white-space: nowrap;">• 사업예산: {row['총사업예산(백만원)']}</div>
                        <div style="white-space: nowrap;">• 사업추진상황: {row['추진상황']}</div>
                        <div style="white-space: nowrap;">• 사업기간: {row['사업시작연도']} ~ {row['사업종료연도']}</div>
                        <div style="white-space: nowrap;">• 마을사업(소득증대): {row['소득증대']}
                    </div>
                    """
                
                tooltip = folium.Tooltip(popup_content)
                folium.CircleMarker(
                    location=[row['지역위도'], row['지역경도']],
                    radius=6,   # 원의 크기
                    color='lightgray',  # 테두리색
                    weight=0.5,   # 테두리 굵기
                    fill=True,  # 채우기 여부
                    fill_color=row['orgin색상'],  # 채우기색
                    fill_opacity=0.8 # 투명도 (높아질수록 투명도 내려감)
                ).add_child(tooltip).add_to(m)

    st_folium(m, width=1300, height=600, key="select_country_map_key")


# ### 3-4. 시범마을 시행기관별 개소수

# #### (1) 기관별 개소수(기존 개소수)

def contact_count1(orgin, country_name):
    country_data = re.sub(r'\(.*?\)', '', country_name)
    pilot_data = village_map()    
    year_data = standard_data['기준연도'].iloc[0]
    pilot_data['기준연도' ] = year_data
    
    contact_data = pilot_data[(pilot_data['국가명'] == country_data) & (pilot_data['시행기관'] == orgin)]
    condition = (contact_data['사업시작연도'].astype(int) < contact_data['기준연도'].astype(int))
    filtered_data = contact_data[condition]
    filtered_count = filtered_data['시행기관'].count()
    return filtered_count


# #### (3) 기관별 개소수(예정 개소수)

def contact_count2(orgin, country_name):
    country_data = re.sub(r'\(.*?\)', '', country_name)
    pilot_data = village_map()    
    year_data = standard_data['기준연도'].iloc[0]
    pilot_data['기준연도' ] = year_data
    
    contact_data = pilot_data[(pilot_data['국가명'] == country_data) & (pilot_data['시행기관'] == orgin)]
    condition = (contact_data['사업시작연도'].astype(int) >= contact_data['기준연도'].astype(int))
    filtered_data = contact_data[condition]
    filtered_count = filtered_data['시행기관'].count()
    return filtered_count


# ### 3-5. 시범마을별 기관 필터

# #### (1) 기관별/추진상황별 필터기능

def total_filter(orgin, state, country_name):
    texts = []
    orgin_data = orgin.replace('재단', '새마을재단').replace('중앙회', '새마을운동중앙회')
    country_name = re.sub(r'\(.*?\)', '', country_name)
    pilot_data = village_map()   
    total_data = pilot_data[(pilot_data['국가명'] == country_name) & (pilot_data['시행기관'] == orgin_data) & (pilot_data['추진상황'] == state)]

    for index, row in total_data.iterrows():
        if row['마을정비'] != '' and row['소득증대'] != '':
            text = f"""
                <div style="border: 1px solid #ccc; padding: 8px; margin-bottom: 8px; border-radius: 5px; position: relative;">
                    <div style="display: flex; justify-content: flex-end; position: absolute; top: 8px; right: 8px;">
                        <div style="background-color: {row['orgin색상']}; color: white; padding: 5px 5px; margin-right: 5px; border-radius: 5px;">
                            <span style="font-size: 12px;">{orgin}</span>
                        </div>
                        <div style="background-color: {row['process색상']}; color: white; padding: 5px 5px; border-radius: 5px;">
                            <span style="font-size: 12px;">{state}</span>
                        </div>
                    </div>
                <div style="white-space: normal;">
                    <strong style="font-size: 12px;">지역명:</strong>  
                    <span style="font-size: 13px;">{row['지역명']}</span> <br>
                    <strong style="font-size: 12px;">사업 기간:</strong>  
                    <span style="font-size: 13px;">{row['사업시작연도']} - {row['사업종료연도']}</span> <br> 
                    <strong style="font-size: 12px;">마을정비:</strong>  
                    <span style="font-size: 13px;">{row['마을정비']}</span> <br>
                    <strong style="font-size: 12px;">소득증대:</strong>  
                    <span style="font-size: 13px;">{row['소득증대']}</span>
                </div>
            """
        elif row['마을정비'] != '':
            text = f"""
                <div style="border: 1px solid #ccc; padding: 8px; margin-bottom: 8px; border-radius: 5px; position: relative;">
                    <div style="display: flex; justify-content: flex-end; position: absolute; top: 8px; right: 8px;">
                        <div style="background-color: {row['orgin색상']}; color: white; padding: 5px 5px; margin-right: 5px; border-radius: 5px;">
                            <span style="font-size: 12px;">{orgin}</span>
                        </div>
                        <div style="background-color: {row['process색상']}; color: white; padding: 5px 5px; border-radius: 5px;">
                            <span style="font-size: 12px;">{state}</span>
                        </div>
                    </div>
                <div style="white-space: normal;">
                    <strong style="font-size: 12px;">지역명:</strong>  
                    <span style="font-size: 13px;">{row['지역명']}</span> <br>
                    <strong style="font-size: 12px;">사업 기간:</strong>  
                    <span style="font-size: 13px;">{row['사업시작연도']} - {row['사업종료연도']}</span> <br> 
                    <strong style="font-size: 12px;">마을정비:</strong>  
                    <span style="font-size: 13px;">{row['마을정비']}</span>
                </div>
            """
        elif row['소득증대'] != '':
            text = f"""
                <div style="border: 1px solid #ccc; padding: 8px; margin-bottom: 8px; border-radius: 5px; position: relative;">
                    <div style="display: flex; justify-content: flex-end; position: absolute; top: 8px; right: 8px;">
                        <div style="background-color: {row['orgin색상']}; color: white; padding: 5px 5px; margin-right: 5px; border-radius: 5px;">
                            <span style="font-size: 12px;">{orgin}</span>
                        </div>
                        <div style="background-color: {row['process색상']}; color: white; padding: 5px 5px; border-radius: 5px;">
                            <span style="font-size: 12px;">{state}</span>
                        </div>
                    </div>
                <div style="white-space: normal;">
                    <strong style="font-size: 12px;">지역명:</strong>  
                    <span style="font-size: 13px;">{row['지역명']}</span> <br>
                    <strong style="font-size: 12px;">사업 기간:</strong>  
                    <span style="font-size: 13px;">{row['사업시작연도']} - {row['사업종료연도']}</span> <br> 
                    <strong style="font-size: 12px;">소득증대:</strong>  
                    <span style="font-size: 13px;">{row['소득증대']}</span>
                </div>
            """
        texts.append(text)
    return texts


# #### (4) 개소 및 기관별/추친상황별 종합 함수

def orgin_filter_total(selected_data):
    col1, col2 = st.columns([5,2])
    with col1:
        st.markdown(
            f"""
            <div style='display: flex; justify-content: center; align-items: center; flex-wrap: nowrap; margin-bottom: 10px;'>
                <div class='custom-font' style='background-color:gray; color: white; padding: 8px; margin-right:8px; border-radius: 8px;'>
                    새마을운동중앙회 
                </div>
                <div class='custom-font' style='padding: 6px; font-size: 15px; margin-right:20px;'>
                    {contact_count1('새마을운동중앙회', selected_data)}개소 (예정 {contact_count2('새마을운동중앙회', selected_data)}개소)
                </div>
                <div class='custom-font' style='background-color:orange; color: white; padding: 10px; margin-right:10px; border-radius: 10px;'>
                    새마을재단
                </div>
                <div class='custom-font' style='padding: 6px; font-size: 15px; margin-right:20px;'>
                    {contact_count1('새마을재단', selected_data)}개소 (예정 {contact_count2('새마을재단', selected_data)}개소)
                </div>
                <div class='custom-font' style= 'background-color:skyblue; color: white; padding: 10px; margin-right:10px; border-radius: 10px;'>
                    KOICA
                </div>
                <div class='custom-font' style='padding: 6px; font-size: 15px;'>
                    {contact_count1('KOICA', selected_data)}개소 (예정 {contact_count2('KOICA', selected_data)}개소)
                </div>
            </div>
            """,
            unsafe_allow_html=True)
#        country_map(selected_data)     
        
    with col2:
        # 초기 세션 상태 설정
        if 'selected_filter' not in st.session_state:
            st.session_state['selected_filter'] = []

        if 'stat_filter' not in st.session_state:
            st.session_state['stat_filter'] = []

        # 국가명 변경 시 초기화 설정
        if 'last_selected_data' not in st.session_state:
            st.session_state['last_selected_data'] = None

        if selected_data != st.session_state['last_selected_data']:
            st.session_state['selected_filter'] = []
            st.session_state['last_selected_data'] = selected_data 
        
        # 선택할 항목
        org_options = ['중앙회', '재단', 'KOICA']
        stat_options = ['신규', '진행', '종료', '예정'] 

        # 회색으로 변경
        st.markdown(
                """
            <style>
            span[data-baseweb="tag"] {
              background-color: gray !important;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <style>
            .filter-label {
                color: black;
                font-size: 16px;
                margin-bottom: -10px;
                }
            .stMultiSelect {
                margin-top: -30px;  /* '기관선택'과 'org_filters' 사이의 간격을 줄임 */
            }
            small {
                display: inline;  /* small 태그를 inline으로 설정 */
                margin-left: 5px;  /* 간격을 조금 추가 */
                font-size: 11px;  /* 글씨 크기 줄이기 */
            }
            </style>
            """, unsafe_allow_html=True,
        )
        st.markdown('<span class="filter-label">🔎기관선택</span><small>※기관을 먼저 선택해주세요.</small>', unsafe_allow_html=True)
        org_filters = st.multiselect('기관선택', org_options, default=None, key='org_select',
                                    label_visibility='hidden')

        st.markdown('<span class="filter-label">⏳추진현황</span>', unsafe_allow_html=True)
        stat_filters = st.multiselect('추진현황', stat_options, default=None, key='stat_select',
                                     label_visibility='hidden')

        # 선택된 기관에 따라 필터링
        filtered_data = []
        all_region_list = []

        # 기관명이 주어질 경우 데이터 필터링
        if org_filters:
            for org in org_filters:
                filtered_data.extend(total_filter(org, '신규', selected_data))
                filtered_data.extend(total_filter(org, '진행', selected_data))
                filtered_data.extend(total_filter(org, '종료', selected_data))
                filtered_data.extend(total_filter(org, '예정', selected_data))
            # 추진상황이 주어질 경우 데이터 필터링
            if stat_filters:
                filtered_data_stat = [
                    item for item in filtered_data if any(stat in item for stat in stat_filters)
                ]
                filtered_data = filtered_data_stat
        
            # filtered_data의 결과를 하나의 문자열로 이어붙임
            filtered_data_html = ""
            for result in filtered_data:
                filtered_data_html += f"<div>{result}</div>"
        
            # height=300으로 고정된 div 영역에 마크업 삽입
            st.markdown(
                f'<div style="height: 420px; overflow-y: auto;">{filtered_data_html}</div>',
                unsafe_allow_html=True
            )
        
            # 지역명 리스트 추출
            for result in filtered_data:
                match = re.search(r'<strong style="font-size: 12px;">지역명:</strong>\s*<span style="font-size: 13px;">(.*?)</span>', result)
                if match:
                    all_region_list.append(match.group(1))
        
        with col1:
            if org_filters or stat_filters:
                select_country_map(selected_data, all_region_list)
            else:
                country_map(selected_data)


def reset_multiselect():
    st.session_state['org_select'] = []
    st.session_state['stat_select'] = []
    st.session_state['selected_orgs'] = []
    st.session_state['filtered_data'] = []
    st.session_state['countries_selected_button'] = '시범마을사업_현황'
    if 'last_selected_data' not in st.session_state:
        st.session_state['last_selected_data'] = None


# ## 4. 초청연수 데이터 

# ### 4-1. 년도별 국가별 초청연수 인원 데이터 전처리

# #### (1) 기관컬럼 추가

def center_add(row):
    if row['기관분류'] == '중앙회':
        return '중앙회'
    elif row['기관분류'] == '재단':
        return '재단'
    elif row['기관분류'] == 'KOICA':
        return 'KOICA'
    elif row['기관분류'] == '공모기관':
        return f'공모기관({row['시행기관']})'


# #### (1) 년도, 국가, 초청인원별 저장

def invited_df(invited_train):
    invited_info = invited_train
    rows = []
    for index, row in invited_info.iterrows():
      for i in range(1,6):
        country_name = row[f'초청연수_국가명{i}']
        invite_count = row[f'국가{i}_초청인원(명)']
        rows.append({
            '사업연도': row['사업연도'],
            '시행기관': row['시행기관'],
            '국가명': country_name,
            '초청인원': invite_count
        })
    invite_count = pd.DataFrame(rows)   
    # NaN값 제거 
    invite_count.dropna(subset=['국가명'], inplace=True)
    # 사업연도, 초청인원 타입변경
    invite_count['사업연도'] = invite_count['사업연도'].astype(int)
    invite_count['초청인원'] = invite_count['초청인원'].astype(int)
    # 사업시행기관목록과 병합
    invite_total = pd.merge(invite_count, business_list, on='시행기관', how='left')
    invite_total.drop(columns=['순번', '기관코드'], inplace=True)

    # 기관 컬럼추가
    invite_total['기관'] = invite_total.apply(center_add, axis=1)

    # 기준연도 컬럼 추가
    year_data = standard_data['기준연도'].iloc[0]
    invite_total['기준연도'] = year_data
    invite_total['시작연도'] = year_data -15
    return invite_total


# ### 4-2 초청연수 데이터프레임

# #### (1) 공모기관별 합계 행 추가

def public_sum(pivoted_data):
    public_sum = pivoted_data[pivoted_data['기관'].str.contains('공모기관', na=False)]

    if not public_sum.empty:
        public_sum = public_sum.sum(numeric_only=True)
        public_sum['기관'] = '공모기관 합계'

        public_sum = pd.DataFrame([public_sum])
        return public_sum
    else:
        public_sum = pd.DataFrame({
            '기관': ['공모기관 합계'],
            **{year: [''] for year in pivoted_data.columns[1:]}  # 모든 년도 열에 값은 ''
        })
        return public_sum


# #### (2) 년도별 합계 행 추가

def year_sum(pivoted_data):
    # '기관', '합계' 제외 
    filtered_data = pivoted_data.drop(columns=['기관'], errors='ignore').sum()

    # 년도별 합계 계산
    year_total_df = pd.DataFrame([filtered_data])
    year_total_df['기관'] = '총합계'
    
    year_total_df = year_total_df[['기관'] + [col for col in year_total_df.columns if col != '기관']]
    return year_total_df


# #### (3) 국가별, 년도별 초청연수 데이터프레임

def invite_df(country_name):
    country_name = re.sub(r'\(.*?\)', '', country_name)
    invited_total = invited_df(invited_train)
    invite_data = invited_total[invited_total['국가명'] == country_name]
    year_data = standard_data['기준연도'].iloc[0]
    # 빈데이터 프레임일 경우
    if invite_data.empty:
        invite_data = pd.DataFrame({
            '사업연도': [None],
            '시행기관': [None],
            '국가명': [country_name],
            '초청인원': [None],
            '기관분류':[None],
            '기관':[None],
            '기준연도': [year_data -15],
            '시작연도': [year_data]
        })
        
        year_range = list(range(invite_data['기준연도'].iloc[0], invite_data['시작연도'].iloc[0]+1, 1))
        year_range = [str(year)[-2:] for year in year_range]
        pivoted_data = pd.DataFrame(columns=year_range)
        pivoted_data['기관'] = [None] * len(pivoted_data)
        pivoted_data['기관'] = ['중앙회', '재단', 'KOICA', '총합계']
        pivoted_data = pivoted_data[['기관'] + year_range]

        # '합계' 열 추가
        pivoted_data['합계'] = ''
        pivoted_data = pivoted_data.fillna('')

    else:
        # 시작연도/기준연도 설정
        start_year = invite_data['시작연도'].iloc[0]
        reference_year = invite_data['기준연도'].iloc[0]
        year_range = list(range(start_year, reference_year + 1))
    
        # 연도범위 고정
        invite_data = invite_data[(invite_data['사업연도'] >= start_year) & (invite_data['사업연도'] <= reference_year)]
        groupby_data = invite_data.groupby(['사업연도', '기관'])['초청인원'].sum().reset_index()
        pivoted_data = groupby_data.pivot(index='기관', columns='사업연도', values='초청인원')
        
        # 초청연수 int형으로 변환
        pivoted_data = pivoted_data.fillna(0).astype(int)
        # 년도 두자리로 변경
        pivoted_data.columns = [str(year)[-2:] for year in pivoted_data.columns]
        year_range = [str(year)[-2:] for year in year_range]
        pivoted_data = pivoted_data.reindex(columns=year_range, fill_value='')
        pivoted_data = pivoted_data.reset_index()
        # 기관별 합계 추가 (열)
        pivoted_data['합계'] = pivoted_data.loc[:, pivoted_data.columns != '기관'].replace('', 0).sum(axis=1)
        # 공모기관 합계 추가 (행)
        public_center_sum = public_sum(pivoted_data)
    
        # 년도별 합계 추가 (행)
        year_data_sum = year_sum(pivoted_data)
        pivoted_data = pd.concat([pivoted_data, public_center_sum, year_data_sum], ignore_index=True)
    
        # 값애 0이나 NaN은 ''로 변경
        pivoted_data.replace(0, '', inplace=True)
        pivoted_data = pivoted_data.fillna('')
        # 순서 고정
        fixed_order = ['중앙회', '재단', 'KOICA']
        institutions = pivoted_data['기관'].unique()
        desired_order = fixed_order + [inst for inst in institutions if inst not in fixed_order]
        
        pivoted_data['기관'] = pd.Categorical(pivoted_data['기관'], categories=desired_order, ordered=True)
        pivoted_data = pivoted_data.sort_values('기관').reset_index(drop=True)
    return pivoted_data


# ### 4-3. 초청연수 표 시각화

def invite_df_result(df):
     # Generate HTML with styles applied through Styler
    html_content = df.style.set_table_attributes(
        'style="border: 1px solid gray; border-collapse: collapse; margin: auto; width:100%; height: 80%; overflow: auto;"'
    ).set_properties(
        **{'text-align': 'center', 'font-weight': 'bold', 'font-family': 'Malgun Gothic', 'font-size': '12px', 'padding': '5px'}
    ).to_html(index=False)
    
    # Remove auto-generated cell-specific style blocks
    html_content = re.sub(r'<style type="text/css">.*?</style>', '', html_content, flags=re.DOTALL)
    
    # Add custom CSS to the resulting HTML
    html_with_styles = f"""
    <style>
        table {{
            border: 1px solid gray;
            border-collapse: collapse;
            margin: auto;
            width: 100%;
            height: 70%;
            overflow: auto;
        }}
        table thead th {{
            background-color: #061b42;
            color: white;
            font-weight: bold;
            text-align: center;
            font-family: Malgun Gothic;
            font-size: 13px;
            padding: 5px;
            border: 1px solid gray;
        }}
        table td {{
            border: 1px solid gray;
            background-color: white;
            color: black;
            text-align: center;
            font-weight: bold;
            font-family: Malgun Gothic;
            font-size: 13px;
            padding: 5px;
            border: 1px solid white;
        }}
        table td:nth-child(2) {{
            background-color: #e1e9eb;
        }}
        table td:last-child {{
            background-color: #b2daed;
        }}
        table thead tr th:first-child {{
            display: none;
        }}
        table tbody th {{
            display: none;
        }}
        table tbody tr:last-child td {{
            background-color: #b2daed;
        }}
    </style>
    {html_content}
    """

    st.markdown(html_with_styles, unsafe_allow_html=True)


# ### 4-4. 초청연수 막대그래프

def invite_barchart(pivoted_data):
    # 폰트설정
    # plt.rcParams['font.family'] = 'Malgun Gothic'
    # plt.rcParams['axes.unicode_minus'] = False

    st.markdown("""
        <style>
        @font-face {
            font-family: 'NanumGothic';
            src: url('streamlit_test/static/fonts/NanumGothic.ttf') format('truetype');
        }
        body {
            font-family: 'NanumGothic', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)
        
    # '합계'와 '기관'을 제외한 연도별 데이터를 추출
    year_columns = [col for col in pivoted_data.columns if col not in ['기관', '합계']]
    # '기관'을 인덱스로 설정하여 연도별로 그룹화
    pivoted_data.set_index('기관', inplace=True)
    
    # '총합계' 제거
    filtered_data = pivoted_data.drop(['총합계'], errors='ignore')
    
    # '공모기관 합계' 제거 로직 수정 (인덱스에서 '기관'을 참조)
    filtered_data = filtered_data[~(filtered_data.index.str.contains('공모기관') & (filtered_data.index != '공모기관 합계'))]
    
    # '공모기관 합계'를 '공모기관'으로 바꾸기
    filtered_data.rename(index={'공모기관 합계': '공모기관'}, inplace=True)

    # '합계' 열 제거
    filtered_data = filtered_data.drop(columns=['합계'], errors='ignore') 
    
    # 빈 값('')을 0으로 변환하고 숫자형으로 변환
    filtered_data[year_columns] = filtered_data[year_columns].replace('', 0).astype(int)


    # 연도 앞에 '20'을 붙임
    new_year_columns = ['20' + year for year in year_columns if year in filtered_data.columns]
    filtered_data.columns = new_year_columns
    
    #print(filtered_data.columns)
   # 색상 지정 (기관에 따라)
    color_map = {
        '중앙회': '#c4c4c4',
        '재단': 'orange',
        'KOICA': 'skyblue',
        '공모기관': 'lightgreen'
    }
    # 그래프 크기조절
    fig, ax = plt.subplots(figsize=(12,4))
    
    # 막대 그래프 그리기
    filtered_data[new_year_columns].T.plot(
        kind='bar', 
        ax=ax,
        stacked=True, 
        color=[color_map.get(idx, 'gray') for idx in filtered_data.index]
    )

    #각 막대 위에 값 추가
    for i in range(len(filtered_data[new_year_columns].T)):  # x축의 막대
        bottom = 0  # 막대의 시작점
        for j in range(len(filtered_data.index)):  # y축의 데이터 계층
            value = filtered_data[new_year_columns].T.values[i][j]  # 현재 값
            if value > 1:  # 값이 1보다 클 경우에만 표시
                ax.text(
                    i,  # x좌표
                    bottom + value /2,  # 막대 안의 중앙 위치
                    str(int(value)),  # 값을 정수로 표시
                    ha='center',  # 중앙정렬
                    va='center',  # 수직 중앙 정렬
                    fontsize=8,   # 글자크기
                    color ='black'
                )
            bottom += value
                
    # 범례 설정
    plt.legend(bbox_to_anchor=(0.5, -0.1), loc='upper center', ncol=len(filtered_data.index), frameon=True, edgecolor='gray')

    # x축 라벨 설정
    ax.set_xticklabels(new_year_columns, rotation=0)  # 연도 라벨을 수평으로 표시
               
    # 눈금선 추가
    ax.grid(axis='y', linestyle='-', color='gray', alpha=0.3)  # y축 눈금선 추가
    ax.grid(axis='x', linestyle='-', color='gray', alpha=0.3)  # x축 눈금선 추가
    # 그래프 표시
    st.pyplot(plt)
