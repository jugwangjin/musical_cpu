# 🎵 CPU Symphony: The Sound of Processing

> **"당신의 CPU가 연주하는 실시간 재즈 즉흥곡"**
>
> 컴퓨터의 연산 부하를 실시간으로 분석하여, 아름다운 선율과 화음으로 변환하는 제너레이티브 아트(Generative Art) 프로젝트입니다.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Verdent](https://img.shields.io/badge/Vibe_Coding-Verdent-7000FF?style=flat&logo=openai)
![Model](https://img.shields.io/badge/Model-Gemini_3_Pro-4EBAE1?style=flat&logo=google-gemini)

## 🎹 프로젝트 소개 (Overview)

이 프로젝트는 정적인 시스템 모니터링을 청각적인 경험으로 바꿉니다. 작업 관리자의 그래프를 멍하니 바라보는 대신, 내 컴퓨터가 얼마나 바쁘게 일하고 있는지 **소리**로 들어보세요.

단순한 비프음이 아닙니다. **12코어 프로세서의 리듬**을 분석하여 기타와 피아노가 어우러진 앙상블을 실시간으로 지휘합니다.

## 🛠️ 사용된 라이브러리 (Tech Stack)

이 프로젝트의 핵심은 파이썬 생태계의 강력한 라이브러리 3대장입니다.

-   **🎼 [SCAMP](http://scamp.marcevanstein.com/) (Suite for Computer-Assisted Music in Python)**
    -   이 프로젝트의 **심장**입니다.
    -   단순 MIDI 재생을 넘어, 실시간으로 음악적 객체(음표, 화음, 템포)를 다루고 오디오 렌더링까지 담당합니다.
    -   비동기(Fork) 처리를 통해 로직 연산과 음악 재생이 서로 방해받지 않고 매끄럽게 흐르도록 구현했습니다.

-   **📊 [Rich](https://github.com/Textualize/rich)**
    -   이 프로젝트의 **얼굴**입니다.
    -   지루한 터미널 출력을 아름다운 **실시간 대시보드**로 탈바꿈시켰습니다.
    -   Sparkline(미니 차트)을 통해 CPU 흐름을 시각적으로도 즐길 수 있습니다.

-   **📈 [psutil](https://github.com/giampaolo/psutil)**
    -   이 프로젝트의 **눈**입니다.
    -   시스템의 각 논리 프로세서(Logical Processor) 상태를 정밀하게 0.25초 단위로 스캔합니다.

## 🎛️ 작동 원리 (How it works)

시스템은 **Core 1, 4, 7, 10**번 프로세서를 모니터링하며, 각각 다른 악기와 역할을 맡습니다.

| Core Index | Role | Instrument | Logic (Algorithm) |
| :--- | :--- | :--- | :--- |
| **Core 1** | Chord | Classical Guitar | CPU 부하(0~100%)를 8개 코드로 매핑하여 1초마다 연주 |
| **Core 4** | Melody | Jazz Guitar | CPU 부하의 **변곡점(Peak/Valley)** 감지 시 즉흥 멜로디 연주 |
| **Core 7** | Chord | Piano | Guitar Chord와 옥타브/보이싱을 달리하여 풍성함 더함 |
| **Core 10** | Melody | Electric Piano | 고음역대에서 Guitar Melody와 주고받으며 화려함 장식 |

## 🚀 실행 방법 (Getting Started)

### 1. 환경 설정
`conda` 또는 `venv` 환경을 권장합니다.

```bash
# 필수 라이브러리 설치
pip install scamp scamp_extensions rich psutil
```

### 2. 실행
```bash
python cpu_music.py
```
*(실행 시 오디오 드라이버 설정 로그가 뜰 수 있으나, 자동으로 최적의 설정을 찾습니다.)*

## 🧑‍💻 Credits & Vibe Coding

이 프로젝트는 **Verdent** (AI Software Engineer Agent)와 **Gemini 3 Pro** 모델을 사용하여 **바이브 코딩(Vibe Coding)** 방식으로 개발되었습니다.

-   **Prompt Engineering & Direction**: [User]
-   **Code Generation & Architecture**: Verdent (Powered by Gemini 3 Pro)

---
*Enjoy the music of your logic.* 🎶
