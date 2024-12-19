# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
css_code = """
@font-face {
    font-family: 'MyCustomFont';
    src: url('./KoPubDotumMedium.ttf') format('truetype');
}

body {
    font-family: 'MyCustomFont', sans-serif;
}
"""

# 파일 경로 설정
css_path = '../styles.css'

# 파일에 CSS 내용 쓰기
with open(css_path, 'w') as f:
    f.write(css_code)
