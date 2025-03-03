# Gemini 2.0 Live API를 활용한 프로젝트입니다!
 1. 사용한 파이썬 버전: Python 3.10
 2. 설치한 패키지: pyserial, google-genai==0.2.2
 3. (혹시) 실행도중 SSL 에러를 만나면 https://curryyou.tistory.com/179를 참고하세요!
 4. 파이썬 파일은 모두 서버파일입니다! 파이썬 파일을 먼저 실행하고 html 파일을 로컬 호스트로 열어주세요!
 

# 코드 설명
  1. Live API를 활용해 영상+소리로 Gemini와 채팅하기
  2. Live API를 활용해 영상+소리로 Gemini와 대화하기
  3. Live API에 함수 기능을 활용해 특정 명령에 Gemini Agent로 써보기
  4. 3에서 생성한 Gemini Agent의 명령을 라즈베리파이 피코로 전송하기
  5. Thonny IDE를 활용해 라즈베리파이 피코 코드에 넣고 실행(반드시 실행 후 종료하여야 시리얼 포트를 파이참이 가져갈 수 있습니다)

# 4번 실습을 실행한 결과

 i2c_lcd.py 파일과 lcd_api.py 파일은 반드시 라즈베리파이 피코 내부에 생성해야합니다.
 5. thonny_main.py 파일도 내부에 생성하고 실행해주세요!

![image](https://github.com/user-attachments/assets/ebc71189-b433-474f-a850-17d308ab1ddb)
Gemini를 활용하여 팬 스피드를 70으로 설정해달라고 함수를 호출시키면
라즈베리파이 피코에 시리얼 통신 방식으로 값을 전송하고 그 값을 LCD에 출력하도록 설정하여 아래와 같은 결과를 얻을 수 있음
![image](https://github.com/user-attachments/assets/2a6fdf1b-5c35-4b9e-a784-c77d274d441e)
