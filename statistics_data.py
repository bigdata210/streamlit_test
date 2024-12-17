# + active=""
# !pip install folium

# + active=""
# pip install xlsxwriter
# -

import pandas as pd
import re
import numpy as np
import streamlit as st
import folium
import json
from streamlit_jupyter import StreamlitPatcher, tqdm
from streamlit_option_menu import option_menu
from io import BytesIO

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

pd.set_option('future.no_silent_downcasting', True)

# # 새마을ODA 사업통계

# ## 1. 데이터불러오기

# - 수원국데이터 : country_info
# - 시범마을사업데이터(사업) : pilot_village
# - 초정연수프로그램데이터 : invited_train

from excel_data import country_info, invited_train, pilot_village

# ## 2. 데이터 전처리

# ### 2-1. 수원국데이터, 시범마을사업 데이터 결합

# +
# 수원국데이터 전처리
country_info1 = country_info.drop(columns=['면적', '인구', '인당GDP', '중점협력분야', '중점협력국기간_시작연도', '중점협력국기간_종료연도',
                  'BIE회원국여부', 'MOU여부'], inplace=False, axis=1, errors='ignore')

# 시범마을데이터 전처리
pilot_data = pilot_village[['시행기관', '대상국가']].drop_duplicates().dropna()

# 수원국데이터, 시범마을데이터 결합
country_data = pd.merge(country_info1, pilot_data, left_on = '국가명', right_on = '대상국가', how='outer')

# 불필요 컬럼 제거 
country_data = country_data.drop(columns=['GDP구분', 'SGL회원국구분', '중점협력국여부', '신규요청국여부',
                       '대한민국대사관_유무', '재단사무소_유무', 'KOICA사무소_유무',
                       '중앙회협력관_유무', '새마을회_유무', '대상국가'], axis=1, errors='ignore')


# -

# ### 2-2. 초청연수 데이터 결합

def process_invited():
    # 초청연수 데이터 전처리
    rows = []
    for index, row in invited_train.iterrows():
        for i in range(1,6):
            country_name = row[f'초청연수_국가명{i}']
            rows.append({'국가명': country_name,
                    '초청연수': 'Y'})

    invite_count = pd.DataFrame(rows) 
    # 초청연수 중복값 및 NaN값 제거
    invite_count = invite_count.drop_duplicates()
    invite_count = invite_count.dropna()

    # 데이터 전처리값 결합
    country_total = pd.merge(country_data, invite_count, on = '국가명', how='outer')
    return country_total


# ## 3. 통계집계 데이터 수집

# ### 3-1 대륙의 값이 없는 것은 0으로 채우는 함수

def fill_zero(df, col_name):
    continents = ['아프리카', '아시아', '태평양도서', '중남미']
    frames = [df]
    for continent in continents:
        if continent not in df['대륙'].values:
            frames.append(pd.DataFrame({'대륙': [continent], col_name: [0]}))
    return pd.concat(frames, ignore_index=True).copy()


# ### 3-2. 수원국데이터 중 통계 데이터 수집

grouping_info = [
    ('신규요청국여부', 'Y', '신규요청국'),
    ('중점협력국여부', 'Y', '중점협력국(해당)'),
    ('중점협력국여부', 'N', '중점협력국(비해당)'),
    ('SGL회원국구분', '정회원국', '정회원국'),
    ('SGL회원국구분', '준회원국', '준회원국'),
    ('SGL회원국구분', '비회원국', '비회원국'),
    ('GDP구분', '상위중소득국', '상위중소득국'),
    ('GDP구분', '하위중소득국', '하위중소득국'),
    ('GDP구분', '최저개발국', '최저개발국'),
    ('중앙회협력관_유무', 'Y', '새마을운동중앙회협력관'),
    ('새마을회_유무', 'Y', '새마을회 활동'),
    ('재단사무소_유무', 'Y', '새마을재단사무소 운영'),
    ('KOICA사무소_유무', 'Y', 'KOICA사무소 운영'),
    ('대한민국대사관_유무', 'N', '대한민국대사관 미설치')
]


def country_info_stat():
    country_total = process_invited()
    country_df = []

    for col_name, filter_value, new_col_name in grouping_info:
        filtered_df = country_info[country_info[col_name] == filter_value].copy()
        grouped_df = filtered_df.groupby('대륙')['국가명'].count().reset_index(name=new_col_name)
        filled_df = fill_zero(grouped_df, new_col_name)
        country_df.append(filled_df.set_index('대륙'))    
    
    country_df1 = pd.concat(country_df, axis=1)
    country_df1.reset_index(inplace=True)

    # 초청연수 중 통계 데이터 수집
    ## 초청연수만 있는 국가 필터링
    invite_country = country_total[(country_total['초청연수'] == 'Y') & (country_total['시행기관'].isna())] 
    
    # 초청연수만 있는 국가 데이터프레임
    invite_oda = invite_country.groupby('대륙')['국가명'].count().reset_index(name='초청연수만 실시')
    invite_oda = fill_zero(invite_oda, '초청연수만 실시')
    invite_oda.set_index('대륙', inplace=True)
    invite_oda = invite_oda.reset_index()

    # 데이터 결합
    result = pd.merge(country_df1, invite_oda, on='대륙', how='left')
    return result


# ### 3-4. 시범마을 중 통계 데이터 수집

pilot_info = [
    ('시범마을', '중앙회', '시범마을(중앙회)'),
    ('시범마을', '재단', '시범마을(재단)'),
    ('시범마을', 'KOICA', '시범마을(KOICA)'),
    ('시범마을', '중앙회+재단', '시범마을(중앙회 + 재단)'),
    ('시범마을', '재단+KOICA', '시범마을(재단 + KOICA)'),
    ('시범마을', '중앙회+재단+KOICA', '시범마을(중앙회 + 재단 + KOICA)')
]   


# 시범마을별 구분하여 저장
def village_info_stat():
    pilot_df = []
    pilot_country = country_data[country_data['시행기관'].notna()].copy()

    pilot_country.loc[:, '시행기관'] = pilot_country['시행기관'].str.replace('새마을운동중앙회', '중앙회')
    pilot_country.loc[:, '시행기관'] = pilot_country['시행기관'].str.replace('새마을재단', '재단')
    order = ['중앙회', '재단', 'KOICA']
    pilot_join = pilot_country.groupby('국가명')['시행기관'].agg(
        lambda x: '+'.join(sorted(x, key=lambda v: order.index(v) if v in order else len(order)))).reset_index()
    pilot_country = pilot_country.merge(pilot_join.rename(columns={'시행기관': '시범마을'}), on='국가명', how='left')

    pilot_country.drop(columns=['시행기관'], inplace=True)
    pilot_country.drop_duplicates(inplace=True)

    # 시범마을 통계 데이터 수집
    for col_name, filter_value, new_col_name in pilot_info:
        filtered_df = pilot_country[pilot_country[col_name] == filter_value]
        grouped_df = filtered_df.groupby('대륙')['국가명'].count().reset_index(name=new_col_name)
        filled_df = fill_zero(grouped_df, new_col_name)
        pilot_df.append(filled_df.set_index('대륙')) 

    pilot_df1 = pd.concat(pilot_df, axis=1)
    pilot_df1.reset_index(inplace=True)
    return pilot_df1


# ## 4. 통계 집계데이터 병합

# ### 4-1. 통계 데이터 병합 및 데이터 타입 변경

def result_change():
    result1 = country_info_stat()
    result2 = village_info_stat()
    result = pd.merge(result1, result2, on='대륙', how='left')
    result = result.transpose()
    result.columns = ['아시아', '아프리카', '중남미', '태평양도서']
    result['총국가'] = result.sum(axis=1)
    result = result.iloc[1:]
    result['총국가'] = result['총국가'].astype(int)
    result['아시아'] = result['아시아'].astype(int)
    result['아프리카'] = result['아프리카'].astype(int)
    result['태평양도서'] = result['태평양도서'].astype(int)
    result['중남미'] = result['중남미'].astype(int)
    return result


# ### 4-2. 국가별 비율 구하기 

def add_percent():
    # 0으로 나누는 경우를 방지하기 위해 np.where 사용
    # 0인 경우는 그대로 두고, 0이 아닐 경우에만 비율 계산
    result = result_change()
    result['아시아비율'] = np.where(result['총국가'] != 0, 
                                     round(result['아시아'] / result['총국가'] * 100, 1), '-')
    result['아프리카비율'] = np.where(result['총국가'] != 0, 
                                        round(result['아프리카'] / result['총국가'] * 100, 1), '-')
    result['태평양도서비율'] = np.where(result['총국가'] != 0, 
                                          round(result['태평양도서'] / result['총국가'] * 100, 1), '-')
    result['중남미비율'] = np.where(result['총국가'] != 0, 
                                      round(result['중남미'] / result['총국가'] * 100, 1), '-')

    new_order = ['총국가', '아프리카', '아프리카비율', '아시아', '아시아비율',
             '태평양도서', '태평양도서비율', '중남미', '중남미비율']
    result = result[new_order]
    result_data = result.reset_index().rename(columns={'index': '상세내용'}).reset_index(drop=True)
    
    return result_data


# #### (6) 구분 컬럼추가

def stat_data():
    result = add_percent().copy()
    result['구분'] = ''
    result.loc[result['상세내용'] == '신규요청국', '구분'] = '신규요청국'
    result.loc[result['상세내용'] == '중점협력국(해당)', '구분'] = '중점협력국'
    result.loc[result['상세내용'] == '중점협력국(비해당)', '구분'] = '중점협력국'
    result.loc[result['상세내용'].isin(['정회원국', '준회원국', '비회원국']), '구분'] = 'SGL회원'
    result.loc[result['상세내용'].isin(['상위중소득국', '하위중소득국', '최저개발국']), '구분'] = 'GDP구분'
    result.loc[result['상세내용'].isin(['새마을운동중앙회협력관', '새마을회 활동', '새마을재단사무소 운영', 'KOICA사무소 운영', '대한민국대사관 미설치']), '구분'] = '연락소분포'
    result.loc[result['상세내용'].isin(['초청연수만 실시', '시범마을(중앙회)', '시범마을(재단)', '시범마을(KOICA)', '시범마을(중앙회 + 재단)', '시범마을(재단 + KOICA)', '시범마을(중앙회 + 재단 + KOICA)']), '구분'] = '사업분류'

    # '구분' 컬럼을 맨 앞으로 이동
    result = result[['구분'] + [col for col in result.columns if col != '구분']]
    return result


# #### (2) 통계 집계 스타일지정

def stat_data_result(df):
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
            height: 60%;
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
        }}
        table td:nth-child(2), table td:nth-child(3) {{
            background-color: #e1e9eb;
        }}
        table td:nth-child(4) {{
            background-color: #eff7d7;
        }}
        table td:nth-child(6), table td:nth-child(8), table td:nth-child(10), table td:nth-child(12) {{
            background-color: #b2daed;
        }}
        table thead tr th:first-child {{
            display: none;
        }}
        table tbody th {{
            display: none;
        }}
    </style>
    {html_content}
    """

    st.markdown(html_with_styles, unsafe_allow_html=True)


# ### 4-3. 엑셀로 다운로드 기능

def convert_df(result):
    output = BytesIO()
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        result.to_excel(writer, index=False, sheet_name='통계집계테이블')

    output.seek(0)
    return output
