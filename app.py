# 주석 내용 정리
# //#1 User 등록 페이지
# //#2 수분 섭취 페이지
# //#3 입력 정보를 csv파일로 저장
# //#4 찰랑이는 물결 효과
#
import pandas as pd
import requests
import json
import math
# //#1 User 등록 페이지
from flask import Flask, render_template, request, redirect, url_for, jsonify

# //#2 수분 섭취 페이지
import csv
import datetime
import os # //#3 입력 정보를 csv파일로 저장

app = Flask(__name__)


# //#1 User 등록 페이지
@app.route('/')
def index():
    return redirect(url_for('registerGet'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         gender = request.form['gender']
#         age = request.form['age']
#         weight = request.form['weight']
#         wake_time = request.form['wake_time']
#         bed_time = request.form['bed_time']
#         exercise_type = request.form['exercise_type']
#         exercise_env = request.form['exercise_env']
#         exercise_time = request.form['exercise_time']
#         exercise_duration = request.form['exercise_duration']
#         coffee_intake = request.form['coffee_intake']


#         return f"""
#         <div class="container">
#             <h1>회원가입 성공</h1>
#             <p>성별: {gender}</p>
#             <p>나이: 만 {age}세</p>
#             <p>체중: {weight}kg</p>
#             <p>운동 종류: {exercise_type}</p>
#             <p>운동 환경: {exercise_env}</p>
#             <p>운동 시간대: {exercise_time}</p>
#             <p>운동 시간: {exercise_duration}</p>
#             <p>평균 하루 카페인 섭취량: {coffee_intake}</p>
#         </div>
#         """
#     return render_template('register.html')

# 사용자 register 페이지
@app.route('/register', methods=['GET'])
def registerGet():
    return render_template('register.html')


# //#3 입력 정보를 csv파일로 저장
@app.route('/register', methods=['POST'])
def registerPost():
    # Get form data
    gender = request.form['gender']
    age = request.form['age']
    weight = request.form['weight']
    wake_time = request.form['wake_time']
    bed_time = request.form['bed_time']
    exercise_type = request.form['exercise_type']
    exercise_env = request.form['exercise_env']
    exercise_time = request.form['exercise_time']
    exercise_duration = request.form['exercise_duration']
    coffee_intake = request.form['coffee_intake']

    # Define the path for the CSV file
    csv_file_path = os.path.join('static', 'user_data.csv')

    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_file_path)

    # Open the CSV file in append mode
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['gender', 'age', 'weight', 'wake_time', 'bed_time', 'exercise_type', 'exercise_env', 'exercise_time', 'exercise_duration', 'coffee_intake']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file doesn't exist
        if not file_exists:
            writer.writeheader()

        # Write the user data
        writer.writerow({
            'gender': gender,
            'age': age,
            'weight': weight,
            'wake_time': wake_time,
            'bed_time': bed_time,
            'exercise_type': exercise_type,
            'exercise_env': exercise_env,
            'exercise_time': exercise_time,
            'exercise_duration': exercise_duration,
            'coffee_intake': coffee_intake
        })
        # == 의진
        info_df= pd.read_csv("static/user_data.csv")
        # 현재 시간 불러오기
        def weather_now():
            now = datetime.now()
            # 현재위치 좌표 얻기


            def current_location():
                here_req = requests.get("http://www.geoplugin.net/json.gp")

                if (here_req.status_code != 200):
                    print("현재좌표를 불러올 수 없음")
                else:
                    location = json.loads(here_req.text)
                    crd = {"lat": str(location["geoplugin_latitude"]), "lng": str(location["geoplugin_longitude"])}

                return crd

            crd = current_location()


            # 원하는 형식으로 변환
            formatted_time = now.strftime("%Y%m%d%H%M")

            print(formatted_time)
            yyyyMMdd = formatted_time[:8]
            HH = formatted_time[8:10]
            HH_00 = int(HH) * 100

            url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
            params = {
                'serviceKey': 'Jh8gMjcJB2/c87a9lWgb0/uxDLf0pk756QwV8p0Rcu5ySVrZZLV0Y43KoesUbUTPD/+ZDXBp/amEtbhM7ZYquw==',
                'pageNo': '1',
                'numOfRows': '1000',
                'dataType': 'JSON',
                'base_date': f'{yyyyMMdd}',
                'base_time': f'{HH_00:04d}',
                'nx': str(crd['lat']),
                'ny': str(crd['long']),
            }

            response = requests.get(url, params=params)
            text_content = response.content.decode('utf-8')
            # JSON 문자열을 파싱하여 딕셔너리로 변환
            data = json.loads(text_content)
            # 필요한 데이터 추출
            items = data["response"]["body"]["items"]["item"]

            # 데이터 프레임으로 변환
            df = pd.DataFrame(items)

            # 데이터 프레임 출력
            RH = float(df[df['category'] == 'REH']['obsrValue'].iloc[0])
            TA = float(df[df['category'] == 'T1H']['obsrValue'].iloc[0])
            return RH, TA

        def cal_water(kg, coffee, ex, ex_hour):
            ex_list = {
                '걷기': 0.9, '빨리걷기': 1.2, '달리기': 2,
                '계단오르기': 1.6, '자전거': 1.8, '줄넘기': 2.6, '등산': 1.5,
                '수영': 2.0, '에어로빅': 1.5, '체조': 1, '테니스': 1.9, '스케이트': 1.8,
                '스키': 1.6, '권투': 2.4, '농구': 2.1, '배구': 1, '축구': 2.5
            }

            lost_weight_w = ex_list[ex] * (1 / 15) * ex_hour

            coffee_w = coffee * 2 * 300
            base_w = kg * 30

            return (coffee_w + base_w) / 200, lost_weight_w / 200

        def upper_round(value):
            return math.ceil(value)

        def celsius_to_fahrenheit(celsius):
            return (celsius * 9 / 5) + 32

        def heat_index(T, R):
            # 상수 정의
            c1 = -42.379
            c2 = 2.04901523
            c3 = 10.14333127
            c4 = -0.22475541
            c5 = -0.00683783
            c6 = -0.05481717
            c7 = 0.00122874
            c8 = 0.00085282
            c9 = -0.00000199

            HI = (c1 + (c2 * T) + (c3 * R) + (c4 * T * R) +
                (c5 * T**2) + (c6 * R**2) +
                (c7 * T**2 * R) + (c8 * T * R**2) +
                (c9 * T**2 * R**2))
            return HI

        def calculate_heat_index(celsius, humidity):
            fahrenheit = celsius_to_fahrenheit(celsius)
            hi_fahrenheit = heat_index(fahrenheit, humidity)
            hi_celsius = (hi_fahrenheit - 32) * 5 / 9
            return hi_celsius

        # 예제 사용법
        # RH, TA = weather_now()

        # hi = calculate_heat_index(TA, RH)a

        # if hi > 35:
        #     duration = 15
        # elif hi > 31:
        #     duration = 20
        # else:
        #     duration = None

        # print(f"체감 온도는 {hi:.2f}°C 입니다. 휴식 시간: {duration}분")

        total_water, ex_water = cal_water(float(info_df['weight'].iloc[-1]), int(info_df['coffee_intake'].iloc[-1]),
                                        str(info_df['exercise_type'].iloc[-1]),  float(info_df['exercise_duration'].iloc[-1])*60,)

        active_time_start = int(info_df['wake_time'].iloc[-1][:-3])+1
        active_time_end = int(info_df['bed_time'].iloc[-1][:-3])-1

        activate_time = active_time_end - active_time_start

        if total_water / activate_time - total_water // activate_time >= 0.4:
            res = 0.5
        else:
            res = 0

        total_cup = total_water // activate_time + res

        # cup 사전 초기화
        cup = {}

        # 루프를 통해 각 시간대에 total_cup 값 추가
        for i in range(active_time_start, active_time_end + 1):
            cup[i - active_time_start] = [f"{i:02d}:00", total_cup]

        # 결과 출력
        last_df = pd.DataFrame(cup).T

        last_df.columns = ['time', 'amount']

        # start_hour 값을 사용하여 시간 계산
        start_hour = int(info_df['wake_time'].iloc[-1][:2])
        end_hour = int(info_df['bed_time'].iloc[-1][:2])


        target_hour_start = f"{int(info_df['exercise_time'].iloc[-1][:-3]) - 2:02d}:00"
        target_hour_end = f"{int(info_df['exercise_time'].iloc[-1][:-3]) + int(info_df['exercise_duration'].iloc[-1]):02d}:00"

        # 조건을 만족하는 행의 'cup' 값을 증가
        last_df.loc[last_df['time'] == target_hour_start, 'amount'] += 2
        last_df.loc[last_df['time'] == target_hour_end, 'amount'] += upper_round(ex_water)


        last_df.to_csv("static/intake_data.csv", index=False)
        goal_df = pd.DataFrame({'goal' :[sum(last_df['amount'])]})
        goal_df.to_csv("static/intakeGoal_data.csv", index=False)

        # ==================================================================================================



    return redirect(url_for('water_intake'))


# //#2 수분 섭취 페이지
@app.route('/water-intake')
def water_intake():
#    goal_intake = 3200
#    current_intake = 2400
#    intake_data = []
    intake_file_name = 'static/intake_data.csv'
    goal_file_name = 'static/intakeGoal_data.csv'

    # with open(intake_file_name, newline='') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         intake_data.append({
    #             'time': row['time'],
    #             'amount': int(row['amount'])
    #         })

    # with open(goal_file_name, newline='') as csvfile:
    #     reader = csv.reader(csvfile)
    #     next(reader)  # Skip header
    #     goal_intake = int(next(reader)[0])


#    return render_template('water_intake.html', goal_intake=goal_intake, current_intake=current_intake, intake_data=intake_data)
    return render_template('water_intake.html')

# //#2 섭취한 수분 데이터 가져와서 .html 파일에서 이용
@app.route('/api/intake-data')
def intake_data():
    intake_data = []
    with open('static/intake_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            intake_data.append({
                'time': row['time'],
                'amount': float(row['amount'])
            })
    return jsonify(intake_data)

# //#의진 체감온도 불러오기
# 체감 온도 계산을 위한 API 엔드포인트 추가
@app.route('/api/heat-index', methods=['GET'])
def get_heat_index():
    info_df = pd.read_csv("static/user_data.csv")

    def weather_now():
        now = datetime.datetime.now()
        formatted_time = now.strftime("%Y%m%d%H%M")
        yyyyMMdd = formatted_time[:8]
        HH = formatted_time[8:10]
        HH_00 = int(HH) * 100

        url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
        params = {
            'serviceKey': 'Jh8gMjcJB2/c87a9lWgb0/uxDLf0pk756QwV8p0Rcu5ySVrZZLV0Y43KoesUbUTPD/+ZDXBp/amEtbhM7ZYquw==',
            'pageNo': '1',
            'numOfRows': '1000',
            'dataType': 'JSON',
            'base_date': f'{yyyyMMdd}',
            'base_time': f'{HH_00:04d}',
            'nx': '55',  # 현재 유저의 위치 정보가 없으므로 임의로 설정
            'ny': '127'
        }

        response = requests.get(url, params=params)
        text_content = response.content.decode('utf-8')
        data = json.loads(text_content)
        items = data["response"]["body"]["items"]["item"]
        df = pd.DataFrame(items)
        RH = float(df[df['category'] == 'REH']['obsrValue'].iloc[0])
        TA = float(df[df['category'] == 'T1H']['obsrValue'].iloc[0])
        return RH, TA

    def celsius_to_fahrenheit(celsius):
        return (celsius * 9 / 5) + 32

    def heat_index(T, R):
        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -0.22475541
        c5 = -0.00683783
        c6 = -0.05481717
        c7 = 0.00122874
        c8 = 0.00085282
        c9 = -0.00000199
        HI = (c1 + (c2 * T) + (c3 * R) + (c4 * T * R) +
              (c5 * T**2) + (c6 * R**2) +
              (c7 * T**2 * R) + (c8 * T * R**2) +
              (c9 * T**2 * R**2))
        return HI

    def calculate_heat_index(celsius, humidity):
        fahrenheit = celsius_to_fahrenheit(celsius)
        hi_fahrenheit = heat_index(fahrenheit, humidity)
        hi_celsius = (hi_fahrenheit - 32) * 5 / 9
        return hi_celsius

    RH, TA = weather_now()
    try:
        hi = calculate_heat_index(TA, RH)
    except:
        hi = -1

    if hi > 0:
        duration = "안전"
    elif hi > 31:
        duration = "관심"

    elif hi > 33:
        duration = "주의"

    elif hi > 35:
        duration = "경고"

    elif hi > 38:
        duration = "위험"
    else:
        duration = "api 오류"

    return jsonify({
        'heat_index': hi,
        'duration': duration
    })

#======================================체감온도
if __name__ == '__main__':
    app.run(debug=False,host="0.0.0.0",)
    # app.run(host="0.0.0.0", port=5004,debug=True)
    # app.run(host="0.0.0.0", port=5004,debug=True)