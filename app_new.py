import streamlit as st
import ephem
import datetime
import math

# 페이지 기본 설정
st.set_page_config(
    page_title="은하수 관측 계산기", 
    page_icon="https://cdn-icons-png.flaticon.com/512/3212/3212567.png", 
    layout="centered"
)

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
    "태백": {"lat": "37.1640", "lon": "128.9856", "tz": 9},
    "평창": {"lat": "37.3705", "lon": "128.3902", "tz": 9},
    "나이로비": {"lat": "-1.2921", "lon": "36.8219", "tz": 3},
    "뉴델리": {"lat": "28.6139", "lon": "77.2090", "tz": 5.5},
    "뉴욕": {"lat": "40.7127", "lon": "-74.0060", "tz": -5},
    "도쿄": {"lat": "35.6762", "lon": "139.6503", "tz": 9},
    "두바이": {"lat": "25.2048", "lon": "55.2708", "tz": 4},
    "라싸": {"lat": "29.6555", "lon": "91.1186", "tz":8},
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

# location_data 아래에 이 코드를 추가해 주세요.
# 국내 7개 주요 도시의 월별(1~12월) 맑은 날(관측 가능) 확률 통계 (%)
# 기상청 기후 통계 패턴(장마, 폭설, 건조기 등)을 반영한 실전 데이터
weather_stats = {
    "서울": {1: 65, 2: 60, 3: 55, 4: 50, 5: 45, 6: 30, 7: 15, 8: 20, 9: 50, 10: 65, 11: 62, 12: 60},
    "강릉": {1: 60, 2: 55, 3: 50, 4: 55, 5: 50, 6: 35, 7: 20, 8: 25, 9: 45, 10: 60, 11: 58, 12: 55},
    "광주": {1: 50, 2: 45, 3: 50, 4: 55, 5: 55, 6: 30, 7: 15, 8: 20, 9: 45, 10: 60, 11: 55, 12: 48},
    "대전": {1: 58, 2: 55, 3: 52, 4: 55, 5: 50, 6: 30, 7: 15, 8: 20, 9: 45, 10: 62, 11: 58, 12: 55},
    "부산": {1: 70, 2: 65, 3: 60, 4: 55, 5: 50, 6: 35, 7: 20, 8: 30, 9: 55, 10: 70, 11: 72, 12: 75},
    "울릉": {1: 20, 2: 25, 3: 40, 4: 50, 5: 50, 6: 40, 7: 25, 8: 30, 9: 45, 10: 45, 11: 30, 12: 25},
    "제주": {1: 30, 2: 35, 3: 40, 4: 45, 5: 45, 6: 30, 7: 25, 8: 35, 9: 45, 10: 55, 11: 45, 12: 35},
    "태백": {1: 68, 2: 65, 3: 58, 4: 55, 5: 50, 6: 30, 7: 15, 8: 20, 9: 55, 10: 72, 11: 70, 12: 68},
    "평창": {1: 65, 2: 62, 3: 58, 4: 55, 5: 50, 6: 30, 7: 15, 8: 20, 9: 55, 10: 70, 11: 68, 12: 65}
    # 여기에 없는 도시는 '통계 없음'으로 안전하게 처리됩니다.
}

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

        # --- 1. 천체 객체 준비 ---
        sun = ephem.Sun()
        galactic_center = ephem.FixedBody()
        galactic_center._ra = ephem.hours('17:45:40') # 은하수 중심부
        galactic_center._dec = ephem.degrees('-29:00:28')
        
        # 바구니 2개 준비
        # 1번 바구니: 암흑 + 은하수 중심부가 떠 있는 "최고의 시간" (여름/가을용)
        valid_center_minutes = []
        # 2번 바구니: 그냥 암흑인 "모든 시간" (겨울 플랜B용)
        all_dark_minutes = []
        
        current = check_start
        while current <= check_end:
            observer.date = current
            sun.compute(observer)
            galactic_center.compute(observer)
            
            sun_alt = math.degrees(float(sun.alt))
            mw_alt = math.degrees(float(galactic_center.alt))
            
            if sun_alt <= -18:
                all_dark_minutes.append(current.replace(second=0, microsecond=0))
                # 은하수 중심부도 떠 있다면 1번 바구니에도 담기
                if mw_alt > 0:
                    valid_center_minutes.append({
                        "time": current.replace(second=0, microsecond=0),
                        "mw_alt": mw_alt
                    })
            current += datetime.timedelta(minutes=1)

        st.divider()
        
        # 최종 결과를 담을 변수들
        obs_start_local = None
        obs_end_local = None
        duration_minutes = 0
        is_center_visible = False
        
        # --- 플랜 A: 은하수 중심부를 볼 수 있는 달(계절)인가? ---
        if valid_center_minutes:
            is_center_visible = True
            sessions = []
            current_session = [valid_center_minutes[0]]
            
            for i in range(1, len(valid_center_minutes)):
                if (valid_center_minutes[i]["time"] - valid_center_minutes[i-1]["time"]).total_seconds() > 600:
                    sessions.append(current_session)
                    current_session = [valid_center_minutes[i]]
                else:
                    current_session.append(valid_center_minutes[i])
            sessions.append(current_session)
            
            best_session = None
            min_dist_to_nm = float('inf')
            
            for session in sessions:
                peak_time = max(session, key=lambda x: x["mw_alt"])["time"]
                dist = abs((peak_time - nm_dt_utc).total_seconds())
                if dist < min_dist_to_nm:
                    min_dist_to_nm = dist
                    best_session = session

            peak_data = max(best_session, key=lambda x: x["mw_alt"])
            peak_time = peak_data["time"]
            session_start = best_session[0]["time"]
            session_end = best_session[-1]["time"]
            
            window_start = max(session_start, peak_time - datetime.timedelta(hours=1))
            window_end = min(session_end, peak_time + datetime.timedelta(hours=1))
            
            obs_start_local = window_start + datetime.timedelta(hours=target_tz_offset)
            obs_end_local = window_end + datetime.timedelta(hours=target_tz_offset)
            duration_minutes = int((window_end - window_start).total_seconds() / 60)

        # --- 플랜 B: 중심부가 아예 안 뜬다면 (겨울철), 그냥 제일 어두운 합삭 2시간을 찾자! ---
        elif all_dark_minutes:
            best_start = None
            best_end = None
            min_dist = float('inf')
            
            for dt in all_dark_minutes:
                end_dt = dt + datetime.timedelta(hours=2)
                if end_dt in all_dark_minutes:
                    mid_point = dt + datetime.timedelta(hours=1)
                    dist_seconds = abs((mid_point - nm_dt_utc).total_seconds())
                    
                    if dist_seconds < min_dist:
                        min_dist = dist_seconds
                        best_start = dt
                        best_end = end_dt
                        
            if best_start and best_end:
                obs_start_local = best_start + datetime.timedelta(hours=target_tz_offset)
                obs_end_local = best_end + datetime.timedelta(hours=target_tz_offset)
                duration_minutes = 120

        # --- 결과 화면 출력부 ---
        if obs_start_local and obs_end_local:
            start_str = obs_start_local.strftime('%m월 %d일 %H:%M')
            end_str = obs_end_local.strftime('%m월 %d일 %H:%M')
            
            # 은하수 상태에 따라 메시지와 색상 변경
            if is_center_visible:
                msg_title = "🏆 <b>화려한 은하수 중심부</b> 관측 최적 타이밍!"
                msg_bg = "#d1e7dd"
                msg_color = "#0f5132"
                msg_desc = f"(확보된 완벽한 암흑 관측 시간: <b>{duration_minutes}분</b>)"
            else:
                msg_title = "❄️ <b>겨울 은하수(주변부)</b> 관측 최적 타이밍!"
                msg_bg = "#e2e3e5"
                msg_color = "#41464b"
                msg_desc = "<span style='font-size: 0.85em; font-weight: normal;'>(이 달은 계절 특성상 은하수 중심부가 지평선 아래에 있어 <br>희미한 주변부 위주로 관측됩니다.)</span>"
            
            st.markdown(
                f"""
                <div style="
                    background-color: {msg_bg}; color: {msg_color}; padding: 16px; 
                    border-radius: 8px; font-weight: normal; 
                    font-size: clamp(16px, 2.5vw, 22px); text-align: center; margin-bottom: 15px;
                ">
                    {msg_title}<br>
                    <span style='font-size: 0.9em;'>{msg_desc}</span>
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

            # --- 👇 결과가 나오면 그 도시의 하늘(구름)을 바로 보여주는 버튼 👇 ---
            st.divider() # 가로줄 긋기
            
            # 현재 선택한 도시의 위도, 경도 가져오기
            lat_val = location_data[selected_city]["lat"]
            lon_val = location_data[selected_city]["lon"]
            
            # 윈디닷컴(Windy) 구름 레이더 URL 만들기
            # URL 뒤에 위도, 경도, 줌레벨(8)을 넣으면 그 동네 지도가 바로 열립니다!
            windy_url = f"https://www.windy.com/?{lat_val},{lon_val},8"

            # --- 👇 여기서부터 통계 확률 텍스트 띄우기 👇 ---            
            # 1. 우리가 찾은 최적 관측 날짜가 몇 월인지 가져옵니다.
            target_month = nm_dt_local.month 
            
            # 2. weather_stats 딕셔너리에서 해당 도시와 월의 데이터를 가져옵니다.
            # .get()을 쓰면, 만약 내가 통계 숫자를 안 적어둔 도시라도 에러가 나지 않습니다!
            city_weather = weather_stats.get(selected_city, {})
            clear_prob = city_weather.get(target_month, None)
            
            # 3. 통계 데이터가 있으면 확률을 보여주고, 없으면 기본 안내문을 띄웁니다.
            if clear_prob:
                st.markdown(f"##### ☁️ 역대 {target_month}월 **{selected_city}**의 맑은 날 비율은 약 **{clear_prob}%**입니다.")
            else:
                st.markdown(f"##### ☁️ **{selected_city}**의 {target_month}월 기상 조건을 확인해 보세요.")
            
            st.markdown("은하수 관측은 **구름이 없는 맑은 하늘**이 필수입니다.<br>아래 버튼을 눌러 해당 지역의 구름 레이더를 확인해 보세요!", unsafe_allow_html=True)
            
            # 클릭하면 새 창으로 열리는 멋진 링크 버튼 만들기
            st.markdown(
    f"""
    <a href='{windy_url}' target='_blank' style='
        display: inline-block;
        background-color: #1f77b4; /* 파란색 배경 */
        color: white; /* 흰색 글씨 */
        padding: 10px 20px;
        text-decoration: none; /* 밑줄 제거 */
        border-radius: 8px; /* 모서리 둥글게 */
        font-weight: medium;
        text-align: center;
    '>👉 {selected_city} 구름 지도 바로가기 (Windy.com)</a>
    """,
    unsafe_allow_html=True
)
            
        else:
            # 여름철 고위도 국가(런던 등)는 백야 현상으로 인해 -18도 이하로 안 떨어질 때가 있음
            st.error(f"해당 월에는 [{selected_city}] 지역에서 2시간 이상 지속되는 완벽한 암흑(천문박명 종료) 구간이 없습니다. (원인: 여름철 백야 현상 등)")