import streamlit as st
import ephem
import datetime
import math

# 페이지 기본 설정
st.set_page_config(page_title="은하수 관측 계산기", page_icon="🌌", layout="centered")

# '시각'을 '시점'으로 변경
st.markdown(
    """
    <h1 style='font-size: clamp(20px, 4vw, 42px);'>🌌 은하수 최적 관측 시점 계산기</h1>
    """, 
    unsafe_allow_html=True
)
st.markdown("은하수를 관측할 수 있는 **가장 완벽한 약 3시간의 관측 타이밍**을 찾아줍니다.")

# 1. 설정 입력
col1, col2 = st.columns(2)
with col1:
    target_year = st.selectbox("연도", range(2024, 2031), index=2)
with col2:
    target_month = st.selectbox("월", range(1, 13), index=9)

# 버튼 이름 변경
if st.button("최적 시점 계산하기", type="primary"):
    with st.spinner('최적의 관측 범위를 계산 중입니다...'):
        
        # 관측자 설정 (서울 기준)
        observer = ephem.Observer()
        observer.lat = '37.5665'
        observer.lon = '126.9780'
        observer.elevation = 50

        # 해당 월 1일 기준 다음 합삭(New Moon) 시점 찾기
        start_date = datetime.datetime(target_year, target_month, 1)
        next_new_moon_ephem = ephem.next_new_moon(start_date)
        
        # 한국 시간(KST)으로 변환 (+9시간)
        nm_dt_utc = next_new_moon_ephem.datetime()
        nm_dt_kst = nm_dt_utc + datetime.timedelta(hours=9)

        # 분석 범위 설정: 합삭 시점 전후 3일
        check_start = nm_dt_utc - datetime.timedelta(days=3)
        check_end = nm_dt_utc + datetime.timedelta(days=3)

        sun = ephem.Sun()
        results = []

        # 10분 단위로 루프 돌며 태양 고도 체크
        current = check_start
        while current <= check_end:
            observer.date = current
            sun.compute(observer)
            
            alt_deg = math.degrees(float(sun.alt))
            
            # 태양 고도가 -18도 이하 (완전 암흑)일 때만 수집
            if alt_deg <= -18:
                dist_seconds = abs((current - nm_dt_utc).total_seconds())
                current_kst = current + datetime.timedelta(hours=9)
                
                results.append({
                    "time": current_kst,
                    "distance_to_newmoon": dist_seconds
                })
            
            current += datetime.timedelta(minutes=10)

        st.divider()
        
        if results:
            # 합삭 시점과 가장 가까운 암흑 시간 찾기
            results.sort(key=lambda x: x["distance_to_newmoon"])
            best_time = results[0]['time']
            
            # 기준 시점으로부터 ±90분(총 3시간) 범위 설정
            obs_start = best_time - datetime.timedelta(minutes=90)
            obs_end = best_time + datetime.timedelta(minutes=90)
            
            # 출력용 문자열 포맷팅
            start_str = obs_start.strftime('%m월 %d일 %H:%M')
            end_str = obs_end.strftime('%m월 %d일 %H:%M')
            
            st.markdown(
    """
    <div style="
        background-color: #d1e7dd; /* 연한 초록색 배경 (st.success와 비슷함) */
        color: #0f5132;            /* 진한 초록색 글씨 */
        padding: 16px;             /* 박스 안쪽 여백 */
        border-radius: 8px;        /* 박스 모서리 둥글게 */
        font-weight: bold;         /* 글씨 굵게 */
        font-size: clamp(20px, 3vw, 28px); /* 창 크기에 따라 글자 크기 유연하게 조절! */
    ">
        🏆 최적 관측 타이밍을 찾았습니다!
    </div>
    """,
    unsafe_allow_html=True
)
            
            # 창 크기에 맞춰 글씨가 줄어들도록 HTML/CSS 직접 적용
            st.markdown(f"""
                <div style="margin-bottom: 1.5rem; padding: 10px; background-color: #f8f9fa; border-radius: 10px;">
                    <div style="font-size: 1rem; color: #555; margin-bottom: 5px;">✨ 최적 관측 시점</div>
                    <div style="font-size: clamp(20px, 4vw, 42px); font-weight: bold; color: #1f77b4; line-height: 1.2;">
                        {start_str} ~ {end_str}
                    </div>
                </div>
                <div style="margin-bottom: 1rem; padding: 10px;">
                    <div style="font-size: 1rem; color: #555; margin-bottom: 5px;">🌑 해당월 합삭(KST)</div>
                    <div style="font-size: clamp(1.5rem, 4vw, 2.5rem); font-weight: bold; color: #333; line-height: 1.2;">
                        {nm_dt_kst.strftime('%m월 %d일 %H:%M')}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        else:
            st.error("해당 기간에 완전한 암흑 조건이 없습니다.")
