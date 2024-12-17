# # 새마을ODA 사업통계

import pandas as pd
import re
import numpy as np
import streamlit as st
import folium
import json
from streamlit_jupyter import StreamlitPatcher, tqdm
from streamlit_option_menu import option_menu
import os
import sys
from PIL import Image
from io import BytesIO
import base64

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

pd.set_option('future.no_silent_downcasting', True)

# ## 1. 데이터불러오기

# - 시범마을사업데이터(마을사업) : pilot_business
# - 마을사업목록 데이터 : village_business
# - 국가목록 데이터 : country_list
# - 지역목록 데이터 : region_list

# ## 2. 데이터 전처리

# ### 2-1. 국가별 마을사업 전처리

from excel_data import pilot_business, village_business, country_list, region_list


def village_business_data():
    # 국가별 시범마을사업 및 지역목록 데이터 결합
    df = pd.merge(pilot_business, region_list, on ='지역명', how='left')
    df.drop(columns =['지역명', '사업식별번호', '사업명_국문', '순번', '국가코드', '지역코드', '위도', '경도'], inplace=False, axis=1, errors='ignore')
    df = df.drop_duplicates()
    
    # 마을사업별로 행분리
    rows = []
    for index, row in df.iterrows():
        for i in range(1,11):
            village_data = row[f'마을사업{i}']
            rows.append({
                '국가명': row['국가명'],
                '마을사업':village_data
            })
    village_business_data = pd.DataFrame(rows)
    vibu = village_business_data.dropna(subset=['마을사업'])
    vibu = vibu.dropna(subset=['국가명'])
    # 국가별 마을사업 및 마을사업 분류 데이터 결합
    total_data = pd.merge(vibu, village_business, on ='마을사업', how='left')
    total_data = total_data.drop(columns=['순번', '코드'], axis=1, errors='ignore')
    total_data = total_data.drop_duplicates()

    # 마을사업 및 대륙명 데이터 결합
    total_data = pd.merge(total_data, country_list, on='국가명', how='left')
    total_data = total_data.drop(columns=['순번', '국가영문명', '고유코드', '위도', '경도'],  axis=1, errors='ignore')
    return total_data


# #### (1) 국가별 국가이미지를 가져오는 함수

# base_path 설정 : 실행 파일 디렉토리를 기준으로 설정
def get_base_path():
    # PyInstaller로 패키징된 실행 파일인 경우
    if getattr(sys, 'frozen', False):
        # 실행 파일의 디렉토리
        return os.path.dirname(sys.executable)
    # 로컬 개발 환경
    else:
        return os.getcwd()


def img_data(country_name):
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


# ## 3. 데이터 저장

# ### 3-1. 세션 저장

# #### (1) 마을정비

water_options = ['공동우물', '식수사업', '수도개선', '정수시설', '주택상수도']
building_options = ['어린이집', '새마을시장', '학교건축', '학교화장실', '학교담장', '놀이터', '도서관', '쓰레기분리장']
general_options = ['주택건축', '주택개량', '마을회관', '다목적회관', '보건소', '목욕탕개선']
infrastructure_options = ['진입로', '마을거리', '마을안길', '도로포장', '가로등', '울타리', '교량설치점검', '섬이동보트']

# #### (2) 소득증대

commerical_options = ['제빵점', '텐트대여', '커피브랜드', '팜유사업', '채소판매대', '비즈니스센터', '급식사업', '미용실사업']
manufacturing_options = ['퇴비제조', '만두사업', '과일주스', '당면제빵', '타작장', '화덕사업', '봉제사업', '벽돌제조']
purpose_options = ['벼건조기', '변압기', '정미소', '곡물저장소', '자재보관소', '연료보급소', '축사개량', '채소농장']
livestock_options = ['양계', '돼지사육', '소사육', '낙공', '가축은행', '양어장', '참게개구리', '양봉']
forestry_options = ['버섯', '나무심기', '조림사업', '묘목장', '양묘식재', '숲가꾸기', '과수원']
agricultural_options = ['벼카사바', '영농채소', '양파고추', '옥수수감자', '멜론바나나', '아보카도', '커피카카오', '화훼']
agrfacillity_options = ['농수로배수', '양수기', '농업용수', '저수지댐', '농지개간', '비가림하우스', '온실하우스', '비닐하우스']
education_options = ['재봉', '용접', '농업기술', '병충해방지', '한글', '컴퓨터', '보건', '도자기수공예']
financial_options = ['농장대출', '소액대출', '가축은행', '영농사업', '구판장', '쓰레기은행', '협동조합', '농자재구매']


# ### 3-2. 스타일 설정 함수

def get_checkbox_style(title):
    return f"""
        <style>
            .green-background {{
                padding: 5px;
                text-align: left;
                margin-top: -10px;
                margin-bottom: 5px;
                border-bottom: 1px solid gray;
                font-size: 15px;
                font-weight: bold;
            }}
        </style>
        <div class="green-background">{title}</div>
    """


# ### 3-2 모든 체크박스 선택 및 해제

def update_all_checkboxes():
    # 선택된 버튼에 따라서 다르게 처리
    if st.session_state['village_selected_button'] == '마을정비':
        # '마을정비'에 대한 전체선택/해제
        for option in water_options + building_options + general_options + infrastructure_options:
            st.session_state[option] = st.session_state.select_all  # select_all의 상태로 체크박스 선택/해제

    elif st.session_state['village_selected_button'] == '소득증대':
        # '소득증대'에 대한 전체선택/해제
        for option in commerical_options + manufacturing_options + purpose_options + livestock_options + \
                       forestry_options + agricultural_options + agrfacillity_options + education_options + financial_options:
            st.session_state[option] = st.session_state.select_all  # select_all의 상태로 체크박스 선택/해제


def income_increase(middle_option):
    selected_data = []
    checkbox_cols = st.columns(8)
    for i, option in enumerate(middle_option[:8]):
        with checkbox_cols[i]:
            is_checked = st.session_state.get(option, False)
            if st.checkbox(option, value=is_checked, key=f"{option}_{i}"):
                selected_data.append(option)
    return selected_data


# #### (3) 초기화함수

def reset_checkboxes():
    if st.session_state['village_selected_button'] == '마을정비':
        # 마을정비로 넘어갈 때는 소득증대 체크박스 상태 초기화
        for option in commerical_options + manufacturing_options + purpose_options + livestock_options + \
                       forestry_options + agricultural_options + agrfacillity_options + education_options + financial_options:
            st.session_state[option] = False
    elif st.session_state['village_selected_button'] == '소득증대':
        # 소득증대로 넘어갈 때는 마을정비 체크박스 상태 초기화
        for option in water_options + building_options + general_options + infrastructure_options:
            st.session_state[option] = False
