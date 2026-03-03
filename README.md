# 🎵 CPU Symphony: The Sound of Processing

> **"당신의 컴퓨터가 연주하는 실시간 제너레이티브 재즈 앙상블"**
> 
> 컴퓨터의 연산 부하(CPU)와 메모리(RAM) 사용량을 실시간으로 분석하여, 그루브 넘치는 6인조 밴드 사운드로 변환하는 제너레이티브 아트(Generative Art) 프로젝트입니다.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Verdent](https://img.shields.io/badge/Vibe_Coding-Verdent-7000FF?style=flat&logo=openai)
![Model](https://img.shields.io/badge/Model-Gemini_3.1_Pro-4EBAE1?style=flat&logo=google-gemini)

## 🎹 프로젝트 소개 (Overview)

이 프로젝트는 정적인 시스템 모니터링을 청각적인 경험으로 바꿉니다. 작업 관리자의 그래프를 멍하니 바라보는 대신, 내 컴퓨터가 얼마나 바쁘게 일하고 있는지 **소리**로 들어보세요.

단순한 비프음이 아닙니다. **6개의 주요 논리 프로세서 리듬**과 **RAM 사용량**을 분석하여 기타, 건반, 베이스, 드럼이 어우러진 6인조 앙상블을 실시간으로 지휘하고 공간감(Reverb)을 부여합니다.

## 🛠️ 사용된 라이브러리 (Tech Stack)

이 프로젝트의 핵심은 파이썬 생태계의 강력한 패키지들입니다.

-   **🎼 [SCAMP](http://scamp.marcevanstein.com/) (Suite for Computer-Assisted Music in Python)**
    -   이 프로젝트의 **심장(Audio Engine)**입니다.
    -   단순 MIDI 재생을 넘어, 실시간으로 음악적 객체(음표, 화음, 템포)를 다루고 오디오 렌더링까지 담당합니다.
    -   비동기(Fork) 처리를 통해 로직 연산과 6개 파트의 음악 재생이 서로 딜레이 없이 흐르도록 구현했습니다.

-   **📊 [Rich](https://github.com/Textualize/rich)**
    -   이 프로젝트의 **얼굴(UI)**입니다.
    -   지루한 터미널 출력을 아름다운 **실시간 대시보드**로 탈바꿈시켰습니다.
    -   Sparkline(미니 차트)을 통해 코어별 CPU 흐름을 시각적으로 모니터링할 수 있습니다.

-   **📈 [psutil](https://github.com/giampaolo/psutil)**
    -   이 프로젝트의 **눈(Sensor)**입니다.
    -   시스템의 프로세서(CPU) 상태와 RAM 점유율을 정밀하게 읽어옵니다.

## 🎛️ 앙상블 구성 및 작동 원리 (How it works)

시스템은 6개의 코어 프로세서를 모니터링하며, 각기 다른 악기와 역할을 수행합니다.

| Core (Logical) | Role | Instrument | Behavior |
| :--- | :--- | :--- | :--- |
| **Core 1** | **Guitar Melody** | Electric Guitar (Jazz) | CPU 극대/극소점(Local Max/Min)에서 멜로디 연주 |
| **Core 3** | **Guitar Chord** | Classical Guitar | 부하량에 따라 정해진 텐션의 코드 스트로크 |
| **Core 5** | **Keys Melody** | Electric Piano 1 | 기타와 대선율(Counter-melody)을 이루는 건반 라인 |
| **Core 7** | **Keys Chord** | Electric Piano 2 | 리듬감을 더해주는 컴핑(Comping) 연주 |
| **Core 9** | **Drum Kit** | Standard Drum Kit | 킥, 스네어, 하이햇을 조합하여 리듬(Groove) 생성 |
| **Core 11** | **Bass** | Electric Bass (Pick) | 코드의 근음(Root)과 리듬을 탄탄하게 받쳐주는 베이스 |

### 🎼 음악적 특징 (Musical Features)
- **RAM Reverb Control**: 시스템의 현재 RAM 사용량(%)이 오디오의 **리버브(잔향) 이펙트 강도**로 직결됩니다. 메모리를 많이 쓸수록 음악의 공간감이 넓어집니다!
- **Dynamic Harmony**: 전체 CPU 평균 부하에 따라 메인 진행 코드가 바뀝니다. (Idle=C Maj7 -> Busy=Am7 -> Heavy=Bdim)
- **Quantized Mapping**: 완전 랜덤이 아닌, 지정된 코드 톤과 스케일 내에서 연주하여 화성적 안정감을 유지합니다.

## 🚀 실행 방법 (Getting Started)

### 1. 환경 설정
Windows 환경에서 실행하는 것을 권장합니다. (키보드 실시간 입력을 위해 내장 모듈인 `msvcrt` 사용)

```bash
# 필수 라이브러리 설치
pip install scamp scamp_extensions rich psutil
```

### 2. 실행
```bash
python cpu_music.py
```
*(실행 시 SCAMP의 오디오 드라이버 설정 로그가 표시될 수 있습니다. 자동으로 최적 드라이버를 탐색합니다.)*

### 3. 라이브 믹싱 컨트롤 (Controls)
실행 중인 터미널에서 키보드를 눌러 실시간으로 음악을 믹싱할 수 있습니다.

- **`1` ~ `6`** : 각 악기 트랙 **Mute / Unmute** 토글 (1:기타멜로디, 2:기타코드, 3:건반멜로디, 4:건반코드, 5:드럼, 6:베이스)
- **`Q`** : 마스터 볼륨 감소 (-)
- **`W`** : 마스터 볼륨 증가 (+)

## 🧑‍💻 Credits & Vibe Coding

이 프로젝트는 **Verdent** (AI Software Engineer Agent)와 **Gemini 3.1 Pro** 모델을 사용하여 **바이브 코딩(Vibe Coding)** 방식으로 설계 및 개발되었습니다.

-   **Prompt Engineering, Concept & Direction**: [User]
-   **Code Generation & Architecture**: Verdent (Powered by Gemini 3.1 Pro)

---
*Enjoy the music of your logic.* 🎶