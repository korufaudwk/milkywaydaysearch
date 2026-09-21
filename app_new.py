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
st.markdown("은하수를 관측할 수 있는 **가장 완벽한 약 2시간의 관측 타이밍**을 찾아줍니다.")

# 1. 설정 입력
col1, col2 = st.columns(2)
with col1:
    target_year = st.selectbox("연도", range(2024, 2031), index=2)
with col2:
    target_month = st.selectbox("월", range(1, 13), index=9)
# 1. 관측 위치별 위도, 경도, 시간대(UTC 기준) 데이터 준비
location_data = {
    "서울": {"lat": "37.5665", "lon": "126.9780", "tz": 9},
    "강릉": {"lat": "37.7518", "lon": "128.8760", "tz": 9},
    "광주": {"lat": "35.1595", "lon": "126.8526", "tz": 9},
    "대전": {"lat": "36.3504", "lon": "127.3845", "tz": 9},
    "부산": {"lat": "35.1795", "lon": "129.0756", "tz": 9},
    "울릉": {"lat": "37.4842", "lon": "130.8986", "tz": 9},    
    "제주": {"lat": "33.4996", "lon": "126.5311", "tz": 9},
    "나이로비": {"lat": "-1.2921", "lon": "36.8219", "tz": 3},
    "뉴델리": {"lat": "28.6139", "lon": "77.2090", "tz": 5.5},
    "뉴욕": {"lat": "40.7127", "lon": "-74.0060", "tz": -5},
    "도쿄": {"lat": "35.6762", "lon": "139.6503", "tz": 9},
    "두바이": {"lat": "25.2048", "lon": "55.2708", "tz": 4},
    "런던": {"lat": "51.5074", "lon": "-0.1278", "tz": 0},
    "로마": {"lat": "41.9028", "lon": "12.4964", "tz": 1},
    "로스앤젤레스": {"lat": "34.0522", "lon": "-118.2437", "tz": -8},
    "리스본": {"lat": "38.7223", "lon": "-9.1393", "tz": 0},
    "모스크바": {"lat": "55.7558", "lon": "37.6173", "tz": 3},
    "발리": {"lat": "-8.6705", "lon": "115.2126", "tz": 8},
    "방콕": {"lat": "13.7563", "lon": "100.5018", "tz": 7},
    "베이징": {"lat": "39.9042", "lon": "116.4074", "tz": 8},
    "상파울루": {"lat": "-23.5505", "lon": "-46.6333", "tz": -3},
    "스톡홀름": {"lat": "59.3293", "lon": "18.0686", "tz": 1},
    "시드니": {"lat": "-33.8688", "lon": "151.2093", "tz": 10},
    "아테네": {"lat": "37.9838", "lon": "23.7275", "tz": 2},
    "예루살렘": {"lat": "31.7683", "lon": "35.2137", "tz": 2},
    "울란바토르": {"lat": "47.9190", "lon": "106.9180", "tz": 8},
    "케이프타운": {"lat": "-33.9249", "lon": "18.4241", "tz": 2},
    "하와이": {"lat": "21.3069", "lon": "-157.8583", "tz": -10}
}

selected_city = st.selectbox("관측 위치", list(location_data.keys()))


# 버튼 이름 변경
if st.button("최적 시점 계산하기", type="primary"):
    with st.spinner('최적의 관측 범위를 계산 중입니다...'):
        
        target_tz_offset = location_data[selected_city]["tz"]
        
        observer = ephem.Observer()
        observer.lat = location_data[selected_city]["lat"]
        observer.lon = location_data[selected_city]["lon"]
        
        # 합삭 시점 찾기
        start_date = datetime.datetime(target_year, target_month, 1)
        next_new_moon_ephem = ephem.next_new_moon(start_date)
        
        nm_dt_utc = next_new_moon_ephem.datetime()
        # 선택한 도시의 현지 시간으로 합삭 시간 변환
        nm_dt_local = nm_dt_utc + datetime.timedelta(hours=target_tz_offset)

        check_start = nm_dt_utc - datetime.timedelta(days=3)
        check_end = nm_dt_utc + datetime.timedelta(days=3)

        sun = ephem.Sun()
        
        # "완전 암흑"인 시간만 모아둘 바구니 (Set)
        valid_dark_times = set()
        
        current = check_start
        while current <= check_end:
            observer.date = current
            sun.compute(observer)
            alt_deg = math.degrees(float(sun.alt))
            
            # 태양 고도가 -18도 이하일 때만 수집 (초 단위는 깔끔하게 0으로 맞춤)
            if alt_deg <= -18:
                valid_dark_times.add(current.replace(second=0, microsecond=0))
            
            current += datetime.timedelta(minutes=1)

        st.divider()
        
        best_start = None
        best_end = None
        min_dist = float('inf')
        
        # 수집된 암흑 시간들을 시간순으로 정렬
        sorted_times = sorted(list(valid_dark_times))
        
        # 2시간(120분) 동안 '연속으로' 암흑이 유지되는 구간 찾기
        for dt in sorted_times:
            end_dt = dt + datetime.timedelta(hours=2)
            
            # 시작 시간으로부터 2시간 뒤의 시간도 '완전 암흑' 리스트에 있다면 (즉, 2시간 내내 밤이라면)
            if end_dt in valid_dark_times:
                # 그 2시간 구간의 '중간 지점'이 합삭과 얼마나 가까운지 계산
                mid_point = dt + datetime.timedelta(hours=1)
                dist_seconds = abs((mid_point - nm_dt_utc).total_seconds())
                
                # 가장 합삭과 가까운 2시간 구간을 저장
                if dist_seconds < min_dist:
                    min_dist = dist_seconds
                    best_start = dt
                    best_end = end_dt
                    
        if best_start and best_end:
            # 최종 찾은 UTC 시간을 선택한 도시의 현지 시간으로 변환
            obs_start_local = best_start + datetime.timedelta(hours=target_tz_offset)
            obs_end_local = best_end + datetime.timedelta(hours=target_tz_offset)
            
            start_str = obs_start_local.strftime('%m월 %d일 %H:%M')
            end_str = obs_end_local.strftime('%m월 %d일 %H:%M')
            
            st.markdown(
                """
                <div style="
                    background-color: #d1e7dd; color: #0f5132; padding: 16px; 
                    border-radius: 8px; font-weight: bold; 
                    font-size: clamp(20px, 3vw, 28px);
                ">
                    🏆 최적 관측 타이밍을 찾았습니다!
                </div>
                """, unsafe_allow_html=True
            )
            
            st.markdown(f"""
                <div style="margin-top: 1.5rem; margin-bottom: 1.5rem; padding: 10px; background-color: #f8f9fa; border-radius: 10px;">
                    <div style="font-size: 1rem; color: #555; margin-bottom: 5px;">✨ 최적 관측 시점 (현지 시간)</div>
                    <div style="font-size: clamp(20px, 4vw, 42px); font-weight: bold; color: #1f77b4; line-height: 1.2;">
                        {start_str} ~ {end_str}
                    </div>
                </div>
                <div style="margin-bottom: 1rem; padding: 10px;">
                    <div style="font-size: 1rem; color: #555; margin-bottom: 5px;">🌑 해당월 합삭 (현지 시간)</div>
                    <div style="font-size: clamp(1.5rem, 4vw, 2.5rem); font-weight: bold; color: #333; line-height: 1.2;">
                        {nm_dt_local.strftime('%m월 %d일 %H:%M')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            # 여름철 고위도 국가(런던 등)는 백야 현상으로 인해 -18도 이하로 안 떨어질 때가 있음
            st.error(f"해당 월에는 [{selected_city}] 지역에서 2시간 이상 지속되는 완벽한 암흑(천문박명 종료) 구간이 없습니다.")
