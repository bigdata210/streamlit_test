# %% [markdown]
# # 전체 데이터 가져오기

# %% [markdown]
# ## 1. 엑셀 데이터 가져오기

# %%
import pandas as pd
import os
import openpyxl as pyxl


# %%
def load_xlsx_data(directory_path):
    data = {}
    for filename in os.listdir(directory_path):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(directory_path, filename)
            try:
                total_data = pd.read_excel(file_path, sheet_name=None)
                return total_data
            except Exception as e:
                print(f"에러가 발생하였습니다.: {e}")


# %%
directory_path = os.getcwd()
total_data = load_xlsx_data(directory_path)

# %% [markdown]
# ### (1) 수원국 데이터

# %%
country_info = total_data['수원국데이터']

# %%
country_info = country_info.rename(columns={'면적(㎢)': '면적', '인구(만명)': '인구', '인당GDP(달러)':'인당GDP'})

# %% [markdown]
# #### (2) 시범마을사업데이터(사업)

# %%
pilot_village = total_data["시범마을사업데이터(사업)"]

# %%
pilot_village = pilot_village[pilot_village.drop(columns='행번호').notna().any(axis=1)]

# %% [markdown]
# #### (3) 시범마을사업데이터(마을사업)

# %%
pilot_business = total_data["시범마을사업데이터(마을사업)"]

# %% [markdown]
# #### (4) 초청연수프로그램 데이터

# %%
invited_train = total_data["초청연수프로그램데이터"]

# %%
invited_train = invited_train[invited_train.drop(columns='행번호').notna().any(axis=1)]

# %% [markdown]
# #### (5) 기준연도 데이터

# %%
standard_data = total_data["기준연도"]

# %% [markdown]
# #### (6) 국가목록 데이터

# %%
country_list = total_data["국가목록"]

# %%
country_list = country_list[country_list.drop(columns='순번').notna().any(axis=1)]

# %% [markdown]
# #### (7) 지역목록 데이터

# %%
region_list = total_data["지역목록"]

# %%
region_list = region_list[region_list.drop(columns='순번').notna().any(axis=1)]

# %% [markdown]
# #### (8) 사업시행기관목록 데이터

# %%
business_list = total_data["사업시행기관목록"]

# %%
business_list = business_list[business_list.drop(columns='순번').notna().any(axis=1)]

# %% [markdown]
# #### (9) 마을사업목록 데이터

# %%
village_business = total_data['마을사업목록']
