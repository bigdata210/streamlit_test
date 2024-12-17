# %% [markdown]
# # 새마을ODA_메인화면구성

# %%
import streamlit as st

# %%
st.set_page_config(layout='wide')

# %%
import pandas as pd
import re
import numpy as np
from streamlit_jupyter import StreamlitPatcher, tqdm
from streamlit_option_menu import option_menu
from streamlit_extras.stylable_container import stylable_container
from PIL import Image
import folium
from folium import plugins
import os
import sys
import base64

# %%
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# %% [markdown]
# #### (2) 기능별 페이지

# %%
from map_data import *
from country_oda import *
from statistics_data import *
from actionplan import *
from excel_data import *

# %% [markdown]
# #### (3) 폰트 설정

# %%
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


# %% [markdown]
# ### 1-2) 메인메뉴 구성

# %% [markdown]
# #### (1) 홈탭 설정

# %%
def main():
    with st.sidebar:
        option = option_menu("Menu", ["새마을ODA 지도", "국가별 ODA사업 현황", "새마을ODA 마을사업 현황", "새마을ODA 사업통계"],
                         icons=['bi bi-globe-asia-australia', "bi bi-pin-map-fill", "bi bi-map", "bi bi-bar-chart-line"],
                         menu_icon ='bi bi-justify', default_index=0,
                         styles ={
                             "container": {"padding": "4!important", "background-color":"#fafafa"},
                             "icon":{"color":"black", "font-size":"18px"},
                             "nav-link":{"font-size":"13px", "text-align":"left", "margin":"0px",
                                         "--hover-color":"#fafafa", "font-weight":"bold", "font-family": "'MyCustomFont', sans-serif"},
                             "nav-link-selected": {"background-color":"lightblue"},
                         }
                        )
    return option


# %% [markdown]
# #### (2) 세부메뉴 구성

# %%
def menu_option(option):
    if option == "새마을ODA 지도":
        reset_multiselect()
        st.markdown("""<h3 style='text-align: left; color: #333333; margin-botton: 0px; font-family: "MyCustomFont", sans-serif;'> 새마을ODA 지도 </h3>""", unsafe_allow_html= True)
        oda_map_data()    
    elif option == "국가별 ODA사업 현황":
        st.markdown("""<h3 style='text-align: left; color: #333333; margin-bottom: 0px; font-family: "MyCustomFont", sans-serif;'> 국가별 ODA 사업 현황 </h3>""", unsafe_allow_html= True)
        countries_oda_data()
    elif option == '새마을ODA 마을사업 현황':
        reset_multiselect()
        st.markdown("""<h3 style='text-align: left; color: #333333; margin-bottom: 0px font-family: "MyCustomFont", sans-serif;'> 새마을ODA 마을사업 현황 </h3>""", unsafe_allow_html= True)
        oda_village_business_data()
    elif option == '새마을ODA 사업통계':
        reset_multiselect()
        st.markdown("""<h3 style='text-align: left; color: #333333; margin-botton: 0px; font-family: "MyCustomFont", sans-serif'> 새마을ODA 사업 통계 </h3>""", unsafe_allow_html= True)
        oda_statistics_data()


# %% [markdown]
# ### 1-3) 새마을ODA 지도

# %%
def oda_map_data():
    country_data = pilot_invited_filter()
    col1, col2 = st.columns([1,2])
    with col1:
        selected_map = st.selectbox("지도선택", ["새마을ODA 사업분포 지도", "새마을ODA 국가 인당 GDP 지도", "새마을ODA SGL회원 구분지도",
                                           "새마을ODA 중점협력국 지도", "새마을ODA 당해요청국 지도", "새마을ODA 연락소분포 지도"],
                                    key = "map_selectbox", label_visibility='hidden'
                                   )

    if 'current_map' not in st.session_state or st.session_state.current_map != selected_map:
    # 맵 변경 시 기본값 초기화
        st.session_state.current_map = selected_map
        if selected_map == "새마을ODA SGL회원 구분지도":
            st.session_state.selected_button = '회원국전체'
        elif selected_map == "새마을ODA 중점협력국 지도":
            st.session_state.selected_button = '중점협력국전체'
        elif selected_map == "새마을ODA 연락소분포 지도":
            st.session_state.selected_button = '연락소전체'
            
    if selected_map == "새마을ODA 사업분포 지도":
        # 범례 추가
        st.markdown(
            """
            <div style="position: absolute; 
                        bottom: 5px; right: 30px; 
                        display: flex; 
                        align-items: center; 
                        background-color: white; 
                        font-size: 12px; 
                        padding: 12px; 
                        border: 1px solid black; 
                        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                        justify-content: space-between;">
                <div style="background-color: blue; width: 20px; height: 20px; margin-right: 5px;"></div> 새마을ODA 수행국가
            </div>
            """,
            unsafe_allow_html=True
        )
        oda_country =  oda_country57(country_data)
        st_folium(oda_country, width=1600, height=800)  
        
    elif selected_map == "새마을ODA 국가 인당 GDP 지도":
        # 범례 추가
        st.markdown(
            """
            <div style="position: absolute; 
                        bottom: 5px; right: 30px; 
                        display: flex; 
                        align-items: center; 
                        background-color: white; 
                        font-size: 12px; 
                        padding: 12px; 
                        border: 1px solid black; 
                        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                        justify-content: space-between;">
                <b style="margin-right: 10px;">GDP 구분:</b>
                <div style="background-color: lightblue; width: 20px; height: 20px; margin-right: 5px;"></div> 상위중소득국&nbsp;
                <div style="background-color: #3284c7; width: 20px; height: 20px; margin-right: 5px;"></div> 하위중소득국&nbsp;
                <div style="background-color: darkblue; width: 20px; height: 20px; margin-right: 5px"></div> 최저개발국&nbsp;
            </div>
            """,
            unsafe_allow_html=True
        )
        filtered_country_map = country_size(country_data)
        oda_gdp = oda_gdp_map(filtered_country_map)
        st_folium(oda_gdp, width=1600, height=800)

    elif selected_map == "새마을ODA 당해요청국 지도":
        # 범례 추가
        st.markdown(
            """
            <div style="position: absolute; 
                        bottom: 5px; right: 30px; 
                        display: flex; 
                        align-items: center; 
                        background-color: white; 
                        font-size: 12px; 
                        padding: 12px; 
                        border: 1px solid black; 
                        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                        justify-content: space-between;">
                <div style="background-color: blue; width: 20px; height: 20px; margin-right: 5px;"></div> 신규요청국가&nbsp;
            </div>
            """,
            unsafe_allow_html=True
        )
        new_m = new_request(country_data)
        st_folium(new_m, width=1600, height=800)

    elif selected_map == "새마을ODA SGL회원 구분지도":
        # 범례 추가
        st.markdown(
            """
            <div style="position: absolute; 
                        bottom: 5px; right: 30px; 
                        display: flex; 
                        align-items: center; 
                        background-color: white; 
                        font-size: 12px; 
                        padding: 12px; 
                        border: 1px solid black; 
                        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                        justify-content: space-between;">
                <b style="margin-right: 10px;">SGL회원 구분:</b>
                <div style="background-color: green; width: 20px; height: 20px; margin-right: 5px;"></div> 정회원국&nbsp;
                <div style="background-color: red; width: 20px; height: 20px; margin-right: 5px;"></div> 준회원국&nbsp;
                <div style="background-color: purple; width: 20px; height: 20px; margin-right: 5px"></div> 비회원국&nbsp;
            </div>
            """,
            unsafe_allow_html=True
        )
        # 버튼 상태 및 스타일 설정
        button_styles = {
            '회원국전체': 'background-color: navy; color: white;' if st.session_state.selected_button == '회원국전체' else 'background-color: #ebebeb; color: black;',
            '정회원국': 'background-color: navy; color: white;' if st.session_state.selected_button == '정회원국' else 'background-color: #ebebeb; color: black;',
            '준회원국': 'background-color: navy; color: white;' if st.session_state.selected_button == '준회원국' else 'background-color: #ebebeb; color: black;',
            '비회원국': 'background-color: navy; color: white;' if st.session_state.selected_button == '비회원국' else 'background-color: #ebebeb; color: black;',
        }

        st.markdown("""
            <style>
            .stButton >button {
                margin-top: -20px;
                padding: 5px 10px;
                border: none;
                }
            </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4= st.columns(4)        
        # '전체' 버튼
        with col1:
            with stylable_container("회원국전체", css_styles=f"button {{{button_styles['회원국전체']}}}"):
                if st.button("전체", key="회원국전체", use_container_width=True):
                    st.session_state.selected_button = '회원국전체'
        
        # '정회원국' 버튼
        with col2:
            with stylable_container("정회원국", css_styles=f"button {{{button_styles['정회원국']}}}"):
                if st.button("정회원국", key="정회원국", use_container_width=True):
                    st.session_state.selected_button = '정회원국'
        
        # '준회원국' 버튼
        with col3:
            with stylable_container("준회원국", css_styles=f"button {{{button_styles['준회원국']}}}"):
                if st.button("준회원국", key="준회원국", use_container_width=True):
                    st.session_state.selected_button= '준회원국'
        
        # '비회원국' 버튼
        with col4:
            with stylable_container("비회원국", css_styles=f"button {{{button_styles['비회원국']}}}"):
                if st.button("비회원국", key="비회원국", use_container_width=True):
                    st.session_state.selected_button = '비회원국'
        
        # 버튼 스타일 업데이트
        selected_button = st.session_state.selected_button
        
        # 선택된 옵션에 맞는 지도 출력
        map_result = sgl_member(selected_button)
        st.session_state.map_result = map_result
        
        # 저장된 맵 결과 출력
        if 'map_result' in st.session_state:
            st_folium(st.session_state.map_result, width=1600, height=800)

    elif selected_map == "새마을ODA 중점협력국 지도":
        # 범례 추가
        st.markdown(
            """
            <div style="position: absolute; 
                        bottom: 5px; right: 30px; 
                        display: flex; 
                        align-items: center; 
                        background-color: white; 
                        font-size: 12px; 
                        padding: 12px; 
                        border: 1px solid black; 
                        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                        justify-content: space-between;">
                <b style="margin-right: 10px;">중점협력국 구분:</b>
                <div style="background-color: purple; width: 20px; height: 20px; margin-right: 5px;"></div> 중점협력국(해당)&nbsp;
                <div style="background-color: green; width: 20px; height: 20px; margin-right: 5px;"></div> 중점협력국(비해당)&nbsp;
            </div>
            """,
            unsafe_allow_html=True
        )
        col1, col2, col3 = st.columns(3)
        
        # 버튼 상태 및 스타일 설정
        button_styles = {
            '중점협력국국전체': 'background-color: navy; color: white;' if st.session_state.selected_button == '중점협력국전체' else 'background-color: #ebebeb; color: black;',
            '중점협력국_해당': 'background-color: navy; color: white;' if st.session_state.selected_button == '중점협력국_해당' else 'background-color: #ebebeb; color: black;',
            '중점협력국_비해당': 'background-color: navy; color: white;' if st.session_state.selected_button == '중점협력국_비해당' else 'background-color: #ebebeb; color: black;',
        }
    
        st.markdown("""
            <style>
            .stButton > button {
                margin-top: -20px;
                padding: 5px 10px;
                border: none;
            }
            .stButton > button[data-baseweb="button"] {
                padding: 8px;
            }
            </style>
        """, unsafe_allow_html=True)
            
        # '전체' 버튼
        with col1:
            with stylable_container("중점협력국전체", css_styles=f"button {{{button_styles['중점협력국국전체']}}}"):
                if st.button("전체", key="중점협력국전체", use_container_width=True):
                    st.session_state.selected_button = '중점협력국전체'
        
        # '중점협력국(해당)' 버튼
        with col2:
            with stylable_container("중점협력국_해당", css_styles=f"button {{{button_styles['중점협력국_해당']}}}"):
                if st.button("중점협력국(해당)", key="중점협력국_해당", use_container_width=True):
                    st.session_state.selected_button = '중점협력국_해당'
        
        # '중점협력국(비해당)' 버튼
        with col3:
            with stylable_container("중점협력국_비해당", css_styles=f"button {{{button_styles['중점협력국_비해당']}}}"):
                if st.button("중점협력국(비해당)", key="중점협력국_비해당", use_container_width=True):
                    st.session_state.selected_button = '중점협력국_비해당'
    
        # 버튼 스타일 업데이트
        selected_button = st.session_state.selected_button
        
        # 선택된 옵션에 맞는 지도 출력
        map_result = proy_member(selected_button)
        st.session_state.map_result = map_result
    
        # 저장된 맵 결과 출력
        if 'map_result' in st.session_state:
            st_folium(st.session_state.map_result, width=1600, height=800)
            
    elif selected_map == "새마을ODA 연락소분포 지도":
        col1, col2= st.columns([6,4])
        with col2:
            korea_logo = '대한민국대사관로고'
            saemaul_logo = '새마을회로고'
            koica_logo = 'KOICA로고'
            st.markdown(f"""
                <div style="position: absolute; 
                            bottom: 5px; right: 30px; 
                            display: flex; 
                            align-items: center; 
                            background-color: white; 
                            font-size: 12px; 
                            padding: 12px; 
                            border: 1px solid black; 
                            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                            justify-content: flex-start;">
                    <span style="display: flex; align-items: center; margin-right: 10px;">
                        <strong>연락소 구분:</strong>
                    </span>
                    <div style="display: flex; align-items: center; font-size: 12px; margin-right: 10px;">
                        <img src="data:image/jpeg;base64, {logo_data(korea_logo)}" style="width: 20px; height: 20px; margin-right:5px;">
                        <span>{korea_logo}</span>
                    </div>
                    <div style="display: flex; align-items: center; font-size: 12px; margin-right: 10px;">
                        <img src="data:image/jpeg;base64, {logo_data(saemaul_logo)}" style="width: 20px; height: 20px; margin-right:5px;">
                        <span>{saemaul_logo}</span>
                    </div>
                    <div style="display: flex; align-items: center; font-size: 12px;">
                        <img src="data:image/jpeg;base64, {logo_data(koica_logo)}" style="width: 20px; height: 20px; margin-right:5px;">
                        <span>{koica_logo}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        col1, col2, col3, col4 = st.columns(4)
        # 버튼 상태 및 스타일 설정
        button_styles = {
            '연락소전체': 'background-color: navy; color: white;' if st.session_state.selected_button == '연락소전체' else 'background-color: #ebebeb; color: black;',
            '대한민국대사관': 'background-color: navy; color: white;' if st.session_state.selected_button == '대한민국대사관' else 'background-color: #ebebeb; color: black;',
            '재단사무소': 'background-color: navy; color: white;' if st.session_state.selected_button == '재단사무소' else 'background-color: #ebebeb; color: black;',
            'KOICA사무소': 'background-color: navy; color: white;' if st.session_state.selected_button == 'KOICA사무소' else 'background-color: #ebebeb; color: black;',
        }

        st.markdown("""
            <style>
            .stButton >button {
                margin-top: -20px;
                padding: 5px 10px;
                border: none;
                }
            </style>
        """, unsafe_allow_html=True)
                
        # '전체' 버튼
        with col1:
            with stylable_container("연락소전체", css_styles=f"button {{{button_styles['연락소전체']}}}"):
                if st.button("전체", key="연락소전체", use_container_width=True):
                    st.session_state.selected_button = '연락소전체'
        
        # '대한민국대사관' 버튼
        with col2:
            with stylable_container("대한민국대사관", css_styles=f"button {{{button_styles['대한민국대사관']}}}"):
                if st.button("대한민국대사관", key="대한민국대사관", use_container_width=True):
                    st.session_state.selected_button = '대한민국대사관'
        
        # '재단사무소' 버튼
        with col3:
            with stylable_container("재단사무소", css_styles=f"button {{{button_styles['재단사무소']}}}"):
                if st.button("재단사무소", key="재단사무소", use_container_width=True):
                    st.session_state.selected_button = '재단사무소'
        
        # 'KOICA사무소' 버튼
        with col4:
            with stylable_container("KOICA사무소", css_styles=f"button {{{button_styles['KOICA사무소']}}}"):
                if st.button("KOICA사무소", key="KOICA사무소", use_container_width=True):
                    st.session_state.selected_button = 'KOICA사무소'
          
        # 버튼 스타일 업데이트
        selected_button = st.session_state.selected_button
        
        # 선택된 옵션에 맞는 지도 출력
        map_result = contact_member(st.session_state.selected_button)
        st.session_state.map_result = map_result
        
        # 저장된 맵 결과 출력
        if 'map_result' in st.session_state:
            st_folium(st.session_state.map_result, width=1600, height=800)


# %% [markdown]
# ### 1-4) 국가별 ODA사업 현황

# %%
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


# %%
def countries_oda_data():
    # 기본값 설정
    if 'countries_selected_button' not in st.session_state or not st.session_state['countries_selected_button']:
        st.session_state['countries_selected_button'] = '시범마을사업_현황'
        reset_multiselect()
        
    country_result = country_total_data()
    selected_data = st.selectbox('국가선택', country_result['국가'], on_change=reset_multiselect, label_visibility='hidden')

    col1, col2, col3 = st.columns([2, 3, 3])
    
    # 버튼 상태 및 스타일 설정
    button_styles = {
        '시범마을사업_현황': 'background-color: navy; color: white; font-weight: bold;' if st.session_state['countries_selected_button'] == '시범마을사업_현황' else 'background-color: #ebebeb; color: black;',
        '초청연수프로그램_현황': 'background-color: navy; color: white; font-weight: bold;' if st.session_state['countries_selected_button'] == '초청연수프로그램_현황' else 'background-color: #ebebeb; color: black;'
    }
    
    st.markdown("""
        <style>
        .stButton > button {
            margin-top: -20px;
            padding: 5px 10px;
            border: none;
        }
        .stButton > button[data-baseweb="button"] {
            padding: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 국가정보 내용
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
        <img src="data:image/jpeg;base64, {image_data(selected_data)}" style="width: 60px; height: 40px; margin-right:10px;">
        <span style="font-size: 20px; font-weight: bold;">{selected_data}</span>
        </div>""", unsafe_allow_html=True)

   # '시범마을사업 현황' 버튼
    with col2:
        with stylable_container("시범마을사업_현황", css_styles=f"button {{{button_styles['시범마을사업_현황']}}}"):
            if st.button("시범마을사업 현황", key="시범마을사업_현황", use_container_width=True):
                st.session_state['countries_selected_button'] = '시범마을사업_현황'
                st.rerun()
                
    # '초청연수프로그램 현황' 버튼
    with col3:
        with stylable_container("초청연수프로그램_현황", css_styles=f"button {{{button_styles['초청연수프로그램_현황']}}}"):
            if st.button("초청연수프로그램 현황", key="초청연수프로그램_현황", use_container_width=True):
                st.session_state['countries_selected_button'] = '초청연수프로그램_현황'
                st.rerun()

    st.write("""
    <style>
        .custom-hr {
            margin-top: -5px;  /* 위쪽 간격 조정 (원하는 값으로 변경 가능) */
            margin-bottom: 5px; /* 아래쪽 간격 조정 */
            border: 0; /* 기본 경계 제거 */
            height: 1px; /* 구분선 두께 */
            background-color: rgba(0, 0, 0, 0.2); /* 구분선 색상 */
        }
    </style>
    <hr class="custom-hr">
    """, unsafe_allow_html=True)
                
    # 버튼 상태 확인 후, '시범마을사업_현황' 버튼이 눌린 상태로 초기화 되도록
    if st.session_state['countries_selected_button'] == '시범마을사업_현황':
        col11, col22 = st.columns([2, 8])
        with col11:
            df_data = select_country_info(selected_data)
            st.dataframe(df_data, width=440, height=430)
            wiki_picture(selected_data)

        if st.session_state['countries_selected_button'] == '시범마을사업_현황':       
            with col22:
                orgin_filter_total(selected_data)

    elif st.session_state['countries_selected_button'] == '초청연수프로그램_현황':
        col11, col22 = st.columns([2, 8])
        with col11:
            df_data = select_country_info(selected_data)
            st.dataframe(df_data, width=440, height=430)
            wiki_picture(selected_data)

        with col22:
            df = invite_df(selected_data)
            invite_df_result(df)
            st.write('')
            invite_barchart(df)


# %% [markdown]
# ### 1-5) 새마을ODA 마을사업 현황

# %%
def village_setting(selected_items):
    total_data = village_business_data()
    result = total_data[((total_data['대분류'] == '마을정비') &
                         (total_data['마을사업'].isin(selected_items)))]
    unique_countries = result[['국가명', '대륙명']].drop_duplicates()
    unique_countries = unique_countries.reset_index(drop=True)
    return unique_countries

def income_setting(selected_items):
    total_data = village_business_data()
    result= total_data[((total_data['대분류'] == '소득증대') &
                         (total_data['마을사업'].isin(selected_items)))]
    unique_countries = result[['국가명', '대륙명']].drop_duplicates()
    unique_countries = unique_countries.reset_index(drop=True)
    return unique_countries


# %%
def village_country_data(selected_items):
    # 국가명과 이미지 HTML 조합 생성
    html_content = ''
    for country in selected_items:
        img_data = image_data(country)
        if img_data:
            html_content += f"""
            <div style="display: inline-block; text-align: center; margin-right: 15px; padding: 5px; vertical-align: top;">
                <img src="data:image/jpeg;base64,{img_data}" style="width: 70px; height: 40px; margin-bottom: 5px; object-fit: contain;">
                <div style="margin-top: 5px;">
                    <span style="font-size: 10px; font-weight: bold;">{country}</span>
                    </div>
            </div>"""
    return html_content  # HTML 콘텐츠 반환


# %%
def get_continent_style(selected_items, continent):
    return f"""
        <div style="border: 1px solid #ccc; padding: 10px; border-radius: 5px; background-color: #fafafa;">
                <span style="font-size: 12px; font-weight: bold;">{continent}</span>
                <div>{village_country_data(selected_items)}</div>
            </div>
        """


# %%
def oda_village_business_data():
    # 세션상태 초기화
    if 'village_selected_button' not in st.session_state:
        st.session_state['village_selected_button'] = '마을정비'
    if 'select_all' not in st.session_state:
        st.session_state['select_all'] = False
    reset_checkboxes()
    update_all_checkboxes()
    # 버튼 상태 및 스타일 설정
    button_styles = {
        '마을정비': 'background-color: navy; color: white;' if st.session_state['village_selected_button'] == '마을정비' else 'background-color: #ebebeb; color: black;',
        '소득증대': 'background-color: navy; color: white;' if st.session_state['village_selected_button'] == '소득증대' else 'background-color: #ebebeb; color: black;',
    }
    st.markdown("""
    <style>
    .stButton >button {
        margin-top: -20px;
        padding: 5px 10px;
        border: none;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([4,4,2,1])
    # '마을정비' 버튼
    with col1:
        with stylable_container("마을정비", css_styles=f"button {{{button_styles['마을정비']}}}"):
            if st.button("마을정비", key="마을정비", use_container_width=True):
                st.session_state['village_selected_button'] = '마을정비'
                st.rerun()

    # '소득증대' 버튼
    with col2:
        with stylable_container("소득증대", css_styles=f"button {{{button_styles['소득증대']}}}"):
            if st.button("소득증대", key="소득증대", use_container_width=True):
                st.session_state['village_selected_button'] = '소득증대'
                st.rerun()

    with col3:
        st.checkbox('전체선택/해제', key='select_all', value=st.session_state.select_all, on_change=update_all_checkboxes)
    
    col11, col22 = st.columns([7,3])       
    selected_data = []
    if st.session_state['village_selected_button'] == '마을정비':
        reset_checkboxes()
        with col11:
            st.write(get_checkbox_style('물'), unsafe_allow_html=True)
            checkbox_cols = st.columns(5)
            for i, option in enumerate(water_options[:5]):
                with checkbox_cols[i]:
                    checked_is = st.session_state.get(option, False)              
                    if st.checkbox(option, value=checked_is):
                        selected_data.append(option)
            st.session_state['village_selected_data'] = selected_data
            
            st.write(get_checkbox_style('목적건물'), unsafe_allow_html=True)
            checkbox_cols = st.columns(8)
            for i, option in enumerate(building_options[:8]):
                with checkbox_cols[i]:
                    checked_is = st.session_state.get(option, False)
                    if st.checkbox(option, value=checked_is):
                        selected_data.append(option)
            st.session_state['village_selected_data'] = selected_data
            
            st.write(get_checkbox_style('일반건물'), unsafe_allow_html=True)
            checkbox_cols = st.columns(6)
            for i, option in enumerate(general_options[:6]):
                with checkbox_cols[i]:
                    checked_is = st.session_state.get(option, False)
                    if st.checkbox(option, value=checked_is):
                        selected_data.append(option)
            st.session_state['village_selected_data'] = selected_data
            
            st.write(get_checkbox_style('마을기반'), unsafe_allow_html=True)
            checkbox_cols = st.columns(8)
            for i, option in enumerate(infrastructure_options[:8]):
                with checkbox_cols[i]:
                    checked_is = st.session_state.get(option, False)
                    if st.checkbox(option, value=checked_is):
                        selected_data.append(option)
            st.session_state['village_selected_data'] = selected_data
            
        with col22:
            asia_data = []
            africa_data = []
            south_america_data = []
            pacific_data = []
            
            if selected_data:
                continent_data = village_setting(selected_data)
                
                if continent_data is not None and not continent_data.empty:
                    for index, row in continent_data.iterrows():
                        if row['대륙명'] == '아시아':
                            asia_data.append(row['국가명'])
                        elif row['대륙명'] == '아프리카':
                            africa_data.append(row['국가명'])
                        elif row['대륙명'] == '중남미':
                            south_america_data.append(row['국가명'])
                        elif row['대륙명'] == '태평양도서':
                            pacific_data.append(row['국가명'])

            # 각 대륙별 국가명 출력
            with st.container():
                st.markdown(get_continent_style(asia_data, '아시아'), unsafe_allow_html=True)
                st.markdown('<br>', unsafe_allow_html=True)  # 간격 추가
            
            with st.container():
                st.markdown(get_continent_style(africa_data, '아프리카'), unsafe_allow_html=True) 
                st.markdown('<br>', unsafe_allow_html=True)  # 간격 추가
                
            with st.container():
                st.markdown(get_continent_style(south_america_data, '중남미'), unsafe_allow_html=True) 
                st.markdown('<br>', unsafe_allow_html=True)  # 간격 추가
                
            with st.container():
                st.markdown(get_continent_style(pacific_data, '태평양도서'), unsafe_allow_html=True) 
                st.markdown('<br>', unsafe_allow_html=True)  # 간격 추가
        
    if st.session_state['village_selected_button'] == '소득증대':
        reset_checkboxes()
        with col11:
            selected_data = []
            st.write(get_checkbox_style('상업기타'), unsafe_allow_html=True)
            selected_data += income_increase(commerical_options)
            st.write(get_checkbox_style('제조가공'), unsafe_allow_html=True)
            selected_data += income_increase(manufacturing_options)
            st.write(get_checkbox_style('목적시설'), unsafe_allow_html=True)
            selected_data += income_increase(purpose_options)
            st.write(get_checkbox_style('가축사육'), unsafe_allow_html=True)
            selected_data += income_increase(livestock_options)
            st.write(get_checkbox_style('임업작물'), unsafe_allow_html=True)
            selected_data += income_increase(forestry_options)
            st.write(get_checkbox_style('농업작물'), unsafe_allow_html=True)
            selected_data += income_increase(agricultural_options)
            st.write(get_checkbox_style('농업시설'), unsafe_allow_html=True)
            selected_data += income_increase(agrfacillity_options)
            st.write(get_checkbox_style('기술교육'), unsafe_allow_html=True)
            selected_data += income_increase(education_options)
            st.write(get_checkbox_style('금융기타'), unsafe_allow_html=True)
            selected_data += income_increase(financial_options)
            st.session_state['village_selected_data'] = selected_data
            
        with col22:
            asia_data = []
            africa_data = []
            south_america_data = []
            pacific_data = []
            
            if selected_data:
                continent_data = income_setting(selected_data)

                if continent_data is not None and not continent_data.empty:
                    for index, row in continent_data.iterrows():
                        if row['대륙명'] == '아시아':
                            asia_data.append(row['국가명'])
                        elif row['대륙명'] == '아프리카':
                            africa_data.append(row['국가명'])
                        elif row['대륙명'] == '중남미':
                            south_america_data.append(row['국가명'])
                        elif row['대륙명'] == '태평양도서':
                            pacific_data.append(row['국가명'])
                            
            # 각 대륙별 국가명 출력
            with st.container():
                st.markdown(get_continent_style(asia_data, '아시아'), unsafe_allow_html=True)
                st.markdown('<br>', unsafe_allow_html=True)  # 간격 추가
            
            with st.container():
                st.markdown(get_continent_style(africa_data, '아프리카'), unsafe_allow_html=True) 
                st.markdown('<br>', unsafe_allow_html=True)  # 간격 추가
                
            with st.container():
                st.markdown(get_continent_style(south_america_data, '중남미'), unsafe_allow_html=True) 
                st.markdown('<br>', unsafe_allow_html=True)  # 간격 추가
                
            with st.container():
                st.markdown(get_continent_style(pacific_data, '태평양도서'), unsafe_allow_html=True) 
                st.markdown('<br>', unsafe_allow_html=True)  # 간격 추가


# %% [markdown]
# ### 1-6) 새마을ODA 사업통계

# %%
def oda_statistics_data():
    df2 = stat_data()
    excel = convert_df(df2)

    st.download_button(
        label="💾 엑셀 다운로드",
        data = excel,
        file_name="통계 집계 테이블.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    stat_data_result(df2) 


# %% [markdown]
# # 2. 함수 실행

# %%
if __name__ == "__main__":
    selected_data = main()
    menu_option(selected_data)
