# -*- coding: utf-8 -*-
"""AuraSync | Luxury Ambient Intelligence - single-file Streamlit app.
Run with:  streamlit run app.py   (Streamlit >= 1.37 recommended)
Install:   pip install streamlit pandas requests deep-translator openai   (deep-translator = every language on every page)
"""
import ast
import calendar
import concurrent.futures
import hashlib
import html
import json
import math
import os
import random
import re
import socket
import sys
import threading
import time
import types
from datetime import date, datetime, timedelta, timezone
from datetime import time as dtime

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - openai is optional; the rule-based engine still works
    OpenAI = None

st.set_page_config(page_title="AuraSync | Luxury Ambient Intelligence",
                   page_icon="✨", layout="wide")

GOLD = "#D4AF37"
LANGS = ["English", "Tamil (தமிழ்)", "Korean (한국어)", "Thai (Thai)", "Spanish (Español)",
         "Hindi (हिन्दी)", "Arabic (العربية)", "Japanese (日本語)", "Chinese (中文)", "French (Français)",
         "German (Deutsch)", "Italian (Italiano)", "Portuguese (Português)", "Russian (Русский)",
         "Turkish (Türkçe)", "Dutch (Nederlands)", "Polish (Polski)", "Swedish (Svenska)",
         "Greek (Ελληνικά)", "Indonesian (Bahasa Indonesia)", "Vietnamese (Tiếng Việt)",
         "Malay (Bahasa Melayu)", "Filipino (Tagalog)"]

# ----------------------------------------------------------------------------
# Translations
# T: key -> (English, Tamil, Korean, Thai, Spanish)   [first five languages, every label]
# TX: extra languages -> tuple aligned with CORE_KEYS (other labels fall back to English)
# ----------------------------------------------------------------------------
T = {
    "sub": ("Luxury Ambient Intelligence", "ஆடம்பர சூழல் நுண்ணறிவு", "럭셔리 앰비언트 인텔리전스", "ระบบอัจฉริยะแวดล้อมระดับหรู", "Inteligencia Ambiental de Lujo"),
    "lang": ("Language", "மொழி", "언어", "ภาษา", "Idioma"),
    "nav": ("Navigate", "வழிசெலுத்தல்", "메뉴", "เมนู", "Navegación"),
    "p1": ("Live Dashboard", "நேரடி டாஷ்போர்டு", "라이브 대시보드", "แดชบอร์ดสด", "Panel en Vivo"),
    "p2": ("Moods, Routines & Settings", "மனநிலைகள், வழக்கங்கள் & அமைப்புகள்", "무드, 루틴 & 설정", "อารมณ์ กิจวัตร และการตั้งค่า", "Ambientes, Rutinas y Ajustes"),
    "p3": ("Inner Voice & Guide", "உள்மனக் குரல் & வழிகாட்டி", "내면의 목소리 & 가이드", "เสียงภายในและคู่มือ", "Voz Interior y Guía"),
    "p4": ("Device Fleet", "சாதனக் குழு", "디바이스 플릿", "กลุ่มอุปกรณ์", "Flota de Dispositivos"),
    "p5": ("System Settings", "கணினி அமைப்புகள்", "시스템 설정", "การตั้งค่าระบบ", "Ajustes del Sistema"),
    "p6": ("Room Settings, Remote Access & Smart Geofence", "அறை அமைப்புகள், தொலைதூர கட்டுப்பாடு & ஜியோஃபென்ஸ்", "방 설정, 원격 액세스 & 스마트 지오펜스", "การตั้งค่าห้อง การเข้าถึงระยะไกล & สมาร์ทจีโอเฟนซ์", "Configuración de Habitación, Acceso Remoto y Geocerca Inteligente"),
    "mode_sel": ("Control mode", "கட்டுப்பாட்டு முறை", "제어 모드", "โหมดควบคุม", "Modo de control"),
    "mode_manual": ("Manual Mode", "கைமுறை பயன்முறை", "수동 모드", "โหมดแมนนวล", "Modo Manual"),
    "mode_auto": ("Auto Mode (Wearable Biometric Sync)", "தானியங்கு பயன்முறை (அணிகலன் உயிரியல் ஒத்திசைவு)", "자동 모드 (웨어러블 바이오 동기화)", "โหมดอัตโนมัติ (ซิงค์ข้อมูลชีวภาพจากอุปกรณ์สวมใส่)", "Modo Automático (Sincronización Biométrica)"),
    "auto_hint": ("Manual Mode: your biometrics are shown below, but lights, AC, fan, curtains and audio stay under your control.", "கைமுறை பயன்முறை: உங்கள் உயிரியல் தரவு கீழே தெரியும்; விளக்கு, ஏசி, மின்விசிறி, திரைச்சீலை, ஒலி உங்கள் கட்டுப்பாட்டில் இருக்கும்.", "수동 모드: 바이오 데이터는 아래에 표시되며 조명, 에어컨, 팬, 커튼, 오디오는 직접 제어합니다.", "โหมดแมนนวล: แสดงข้อมูลชีวภาพด้านล่าง แต่ไฟ แอร์ พัดลม ม่าน และเสียงยังคงอยู่ในการควบคุมของคุณ", "Modo Manual: tus datos biométricos se muestran abajo, pero luces, A/C, ventilador, cortinas y audio los controlas tú."),
    "auto_on": ("Auto Mode: Aura reads your wearable and runs the lights, AC, fan, curtains, scent and audio in the room you are in.", "தானியங்கு பயன்முறை: AI உங்கள் அணிகலனைப் படித்து விளக்கு, ஏசி, மின்விசிறி, திரைச்சீலை, வாசனை, ஒலி மற்றும் இணைந்த சாதனங்களை இயக்குகிறது.", "자동 모드: AI가 웨어러블을 분석해 조명, 에어컨, 팬, 커튼, 향, 오디오와 연결된 모든 기기를 제어합니다.", "โหมดอัตโนมัติ: AI อ่านข้อมูลจากอุปกรณ์สวมใส่และควบคุมไฟ แอร์ พัดลม ม่าน กลิ่น เสียง และอุปกรณ์ที่เชื่อมต่อทั้งหมด", "Modo Automático: la IA lee tu wearable y controla luces, A/C, ventilador, cortinas, aroma, audio y todos los dispositivos conectados."),
    "atmos": ("One-Click Instant Atmosphere", "ஒரே கிளிக்கில் சூழல்", "원클릭 즉시 분위기", "เปลี่ยนบรรยากาศทันที", "Ambiente Instantáneo"),
    "timer": ("Auto-Stop / Sleep Timer", "தானியங்கு நிறுத்தம் / உறக்க நேரம்", "자동 종료 / 수면 타이머", "ตั้งเวลาปิดอัตโนมัติ / นอนหลับ", "Temporizador de Apagado / Sueño"),
    "off": ("Off", "நிறுத்து", "끄기", "ปิด", "Apagado"),
    "min": ("min", "நிமிடம்", "분", "นาที", "min"),
    "studio": ("Master Audio Studio (Procedural Synthesizer)", "மாஸ்டர் ஆடியோ ஸ்டுடியோ (செயற்கை ஒலி உருவாக்கி)", "마스터 오디오 스튜디오 (프로시저럴 신시사이저)", "สตูดิโอเสียงหลัก (ซินธ์สร้างเสียงอัตโนมัติ)", "Estudio de Audio Maestro (Sintetizador Procedural)"),
    "play": ("Play", "தொடங்கு", "재생", "เล่น", "Reproducir"),
    "stop": ("Stop", "நிறுத்து", "정지", "หยุด", "Detener"),
    "mixer": ("Multi-Layer Sound Studio Mixer", "பல அடுக்கு ஒலி கலவை", "멀티 레이어 사운드 믹서", "มิกเซอร์เสียงหลายชั้น", "Mezclador de Sonido Multicapa"),
    "bed": ("Base music volume (%)", "அடிப்படை இசை ஒலி (%)", "기본 음악 볼륨 (%)", "ระดับเสียงเพลงพื้นฐาน (%)", "Volumen de la música base (%)"),
    "bio": ("Real-Time Heart Rate & Biometric Telemetry", "நேரடி இதயத் துடிப்பு & உயிரியல் தரவு", "실시간 심박수 & 바이오메트릭", "อัตราการเต้นของหัวใจและข้อมูลชีวภาพแบบเรียลไทม์", "Frecuencia Cardíaca y Biometría en Vivo"),
    "source": ("Data source", "தரவு மூலம்", "데이터 소스", "แหล่งข้อมูล", "Fuente de datos"),
    "sim": ("Simulated", "உருவகப்படுத்தப்பட்டது", "시뮬레이션", "จำลอง", "Simulado"),
    "wear": ("Wearable API", "அணிகலன் API", "웨어러블 API", "API อุปกรณ์สวมใส่", "API de wearable"),
    "scn": ("Simulated scenario", "உருவகப்படுத்தப்பட்ட சூழல்", "시뮬레이션 시나리오", "สถานการณ์จำลอง", "Escenario simulado"),
    "offline": ("Wearable offline - using simulation", "அணிகலன் இணைப்பில் இல்லை - உருவகப்படுத்தல் பயன்படுத்தப்படுகிறது", "웨어러블 오프라인 - 시뮬레이션 사용 중", "อุปกรณ์สวมใส่ออฟไลน์ - ใช้ข้อมูลจำลอง", "Wearable sin conexión: usando simulación"),
    "state_lbl": ("Detected state", "கண்டறியப்பட்ட நிலை", "감지된 상태", "สถานะที่ตรวจพบ", "Estado detectado"),
    "st_relaxed": ("Relaxed", "அமைதி", "편안함", "ผ่อนคลาย", "Relajado"),
    "st_active": ("Active", "சுறுசுறுப்பு", "활동 중", "กระฉับกระเฉง", "Activo"),
    "st_stress": ("Stress", "மன அழுத்தம்", "스트레스", "เครียด", "Estrés"),
    "st_sleep": ("Asleep", "உறக்கம்", "수면 중", "หลับ", "Dormido"),
    "st_wake": ("Waking up", "எழுகிறார்", "기상 중", "ตื่นนอน", "Despertando"),
    "bpm": ("Heart rate (bpm)", "இதயத் துடிப்பு (bpm)", "심박수 (bpm)", "อัตราการเต้นหัวใจ (bpm)", "Pulso (lpm)"),
    "spo2": ("SpO2 (%)", "SpO2 (%)", "산소포화도 (%)", "ออกซิเจนในเลือด (%)", "SpO2 (%)"),
    "skin": ("Skin temp (°C)", "தோல் வெப்பம் (°C)", "피부 온도 (°C)", "อุณหภูมิผิว (°C)", "Temp. piel (°C)"),
    "active": ("Active atmosphere", "செயலில் உள்ள சூழல்", "현재 분위기", "บรรยากาศปัจจุบัน", "Ambiente activo"),
    "ai_auto": ("Aura Companion", "ஆரா துணை", "아우라 컴패니언", "ออร่า คอมพาเนียน", "Compañero Aura"),
    "ai_conf": ("confidence", "நம்பகத்தன்மை", "신뢰도", "ความมั่นใจ", "confianza"),
    "ai_log": ("Aura Diary", "ஆரா நாட்குறிப்பு", "아우라 다이어리", "ไดอารีออร่า", "Diario Aura"),
    "live_dev": ("Live device state", "நேரடி சாதன நிலை", "실시간 기기 상태", "สถานะอุปกรณ์สด", "Estado en vivo de dispositivos"),
    "save": ("Save", "சேமி", "저장", "บันทึก", "Guardar"),
    "saved": ("Saved ✔", "சேமிக்கப்பட்டது ✔", "저장됨 ✔", "บันทึกแล้ว ✔", "Guardado ✔"),
    "std_cfg": ("Standard Mode Configuration", "நிலையான பயன்முறை அமைப்பு", "표준 모드 설정", "การตั้งค่าโหมดมาตรฐาน", "Configuración de Modo Estándar"),
    "mode": ("Mode", "பயன்முறை", "모드", "โหมด", "Modo"),
    "bulb": ("Bulb color", "விளக்கு நிறம்", "전구 색상", "สีหลอดไฟ", "Color de la bombilla"),
    "bright": ("Brightness (%)", "ஒளிர்வு (%)", "밝기 (%)", "ความสว่าง (%)", "Brillo (%)"),
    "fan": ("Fan speed", "மின்விசிறி வேகம்", "팬 속도", "ความเร็วพัดลม", "Velocidad del ventilador"),
    "ac": ("AC temperature (°C)", "ஏசி வெப்பநிலை (°C)", "에어컨 온도 (°C)", "อุณหภูมิแอร์ (°C)", "Temperatura del A/C (°C)"),
    "curtain": ("Curtains open (%)", "திரைச்சீலை திறப்பு (%)", "커튼 열림 (%)", "ม่านเปิด (%)", "Cortinas abiertas (%)"),
    "genre": ("Base music genre", "அடிப்படை இசை வகை", "기본 음악 장르", "แนวเพลงพื้นฐาน", "Género musical base"),
    "bulb_pw": ("Smart bulb power (ON/OFF)", "ஸ்மார்ட் விளக்கு (ON/OFF)", "스마트 전구 전원 (ON/OFF)", "เปิด/ปิดหลอดไฟอัจฉริยะ", "Bombilla inteligente (ON/OFF)"),
    "fan_pw": ("Fan power (ON/OFF)", "மின்விசிறி (ON/OFF)", "팬 전원 (ON/OFF)", "เปิด/ปิดพัดลม", "Ventilador (ON/OFF)"),
    "ac_pw": ("AC power (ON/OFF)", "ஏசி (ON/OFF)", "에어컨 전원 (ON/OFF)", "เปิด/ปิดแอร์", "A/C (ON/OFF)"),
    "extras": ("Ambient devices ON in this mode", "இந்த பயன்முறையில் இயங்கும் சூழல் சாதனங்கள்", "이 모드에서 켜질 환경 기기", "อุปกรณ์บรรยากาศที่เปิดในโหมดนี้", "Dispositivos ambientales activos en este modo"),
    "custom": ("Custom Mode Creator", "தனிப்பயன் பயன்முறை உருவாக்கி", "커스텀 모드 만들기", "สร้างโหมดกำหนดเอง", "Creador de Modo Personalizado"),
    "cname": ("Custom mode name", "தனிப்பயன் பயன்முறை பெயர்", "커스텀 모드 이름", "ชื่อโหมดกำหนดเอง", "Nombre del modo"),
    "dev_bulb": ("Bulb scene", "விளக்கு காட்சி", "전구 장면", "ซีนหลอดไฟ", "Escena de bombilla"),
    "dev_ac": ("AC mode", "ஏசி பயன்முறை", "에어컨 모드", "โหมดแอร์", "Modo A/C"),
    "dev_fan": ("Fan mode", "மின்விசிறி பயன்முறை", "팬 모드", "โหมดพัดลม", "Modo del ventilador"),
    "intens": ("Instrument intensity", "இசைக்கருவி அளவு", "악기 강도", "ความเข้มของเครื่องดนตรี", "Intensidad de instrumentos"),
    "need_name": ("Please enter a mode name.", "பயன்முறை பெயரை உள்ளிடவும்.", "모드 이름을 입력하세요.", "กรุณาใส่ชื่อโหมด", "Introduce un nombre de modo."),
    "setup": ("Initial Profile Setup", "ஆரம்ப சுயவிவர அமைப்பு", "초기 프로필 설정", "ตั้งค่าโปรไฟล์เริ่มต้น", "Configuración Inicial del Perfil"),
    "name": ("Full Name", "முழு பெயர்", "이름", "ชื่อเต็ม", "Nombre completo"),
    "dob": ("Date of Birth", "பிறந்த தேதி", "생년월일", "วันเกิด", "Fecha de nacimiento"),
    "pob": ("Place of Birth (City/Town)", "பிறந்த இடம் (நகரம்/ஊர்)", "출생지 (도시/마을)", "สถานที่เกิด (เมือง/เมืองเล็ก)", "Lugar de nacimiento (Ciudad/Pueblo)"),
    "tob": ("Time of Birth", "பிறந்த நேரம்", "출생 시각", "เวลาเกิด", "Hora de nacimiento"),
    "hour": ("Hour", "மணி", "시", "ชั่วโมง", "Hora"),
    "minute": ("Minute", "நிமிடம்", "분", "นาที", "Minuto"),
    "need_fields": ("Please enter your name and place of birth.", "உங்கள் பெயர் மற்றும் பிறந்த இடத்தை உள்ளிடவும்.", "이름과 출생지를 입력하세요.", "กรุณากรอกชื่อและสถานที่เกิด", "Introduce tu nombre y lugar de nacimiento."),
    "welcome": ("✨ Welcome back, {n}!", "✨ மீண்டும் வருக, {n}!", "✨ 다시 오신 것을 환영합니다, {n}님!", "✨ ยินดีต้อนรับกลับ, {n}!", "✨ ¡Bienvenido de nuevo, {n}!"),
    "edit": ("✏️ Edit Birth Details", "✏️ பிறப்பு விவரங்களை திருத்து", "✏️ 출생 정보 수정", "✏️ แก้ไขข้อมูลการเกิด", "✏️ Editar datos de nacimiento"),
    "nudge": ("💛 Hey {n}! A friendly nudge: take one slow, deep breath. Your Do's, Don'ts and Caution for today are ready to keep you centered.",
              "💛 ஹே {n}! ஒரு அன்பான நினைவூட்டல்: ஒரு மெதுவான ஆழ்ந்த மூச்சு எடுங்கள். இன்று உங்களை சமநிலையில் வைக்க உங்கள் செய்ய வேண்டியவை, கூடாதவை, எச்சரிக்கை தயாராக உள்ளன.",
              "💛 {n}님, 다정한 알림이에요! 천천히 깊게 숨을 한 번 쉬어 보세요. 오늘 중심을 지켜줄 해야 할 일, 하지 말아야 할 일, 주의사항이 준비되어 있어요.",
              "💛 สวัสดี {n}! ขอเตือนเบา ๆ หายใจเข้าลึก ๆ ช้า ๆ สักครั้ง สิ่งที่ควรทำ ไม่ควรทำ และข้อควรระวังของวันนี้พร้อมแล้วเพื่อช่วยให้คุณมั่นคง",
              "💛 ¡Hola {n}! Un recordatorio amable: respira lento y profundo una vez. Tus Qué hacer, Qué evitar y Precaución de hoy están listos para mantenerte centrado."),
    "plan": ("Today's Strategic Action Plan", "இன்றைய உத்தி செயல் திட்டம்", "오늘의 전략 실행 계획", "แผนปฏิบัติการเชิงกลยุทธ์ของวันนี้", "Plan Estratégico de Hoy"),
    "do": ("✅ Do's", "✅ செய்ய வேண்டியவை", "✅ 해야 할 일", "✅ สิ่งที่ควรทำ", "✅ Qué hacer"),
    "dont": ("❌ Don'ts", "❌ கூடாதவை", "❌ 하지 말아야 할 일", "❌ สิ่งที่ไม่ควรทำ", "❌ Qué evitar"),
    "caution": ("⚠️ Caution", "⚠️ எச்சரிக்கை", "⚠️ 주의", "⚠️ ข้อควรระวัง", "⚠️ Precaución"),
    "deep": ("📖 Deep Explanation", "📖 ஆழமான விளக்கம்", "📖 심층 설명", "📖 คำอธิบายเชิงลึก", "📖 Explicación Profunda"),
    "chat": ("Speak to your Divine Compass", "உங்கள் தெய்வீக திசைகாட்டியுடன் பேசுங்கள்", "신성한 나침반과 대화하세요", "พูดคุยกับเข็มทิศศักดิ์สิทธิ์ของคุณ", "Habla con tu Brújula Divina"),
    "chat_ph": ("Ask your Inner Compass", "உங்கள் உள் திசைகாட்டியிடம் கேளுங்கள்", "내면의 나침반에게 물어보세요", "ถามเข็มทิศภายในของคุณ", "Pregunta a tu Brújula Interior"),
    "online": ("online", "இணைப்பில்", "온라인", "ออนไลน์", "en línea"),
    "need_profile": ("Save your birth details above to unlock your Divine Compass.", "உங்கள் தெய்வீக திசைகாட்டியைத் திறக்க மேலே பிறப்பு விவரங்களைச் சேமிக்கவும்.", "신성한 나침반을 사용하려면 위에 출생 정보를 저장하세요.", "บันทึกข้อมูลการเกิดด้านบนเพื่อปลดล็อกเข็มทิศศักดิ์สิทธิ์", "Guarda tus datos de nacimiento arriba para activar tu Brújula Divina."),
    "conn_hub": ("Device Connection Hub", "சாதன இணைப்பு மையம்", "기기 연결 허브", "ศูนย์เชื่อมต่ออุปกรณ์", "Centro de conexión de dispositivos"),
    "conn_all": ("🔗 Connect all devices", "🔗 அனைத்து சாதனங்களையும் இணை", "🔗 모든 기기 연결", "🔗 เชื่อมต่ออุปกรณ์ทั้งหมด", "🔗 Conectar todos los dispositivos"),
    "conn_setup": ("Connection setup", "இணைப்பு அமைப்பு", "연결 설정", "การตั้งค่าการเชื่อมต่อ", "Configuración de conexión"),
    "proto": ("Protocol", "நெறிமுறை", "프로토콜", "โปรโตคอล", "Protocolo"),
    "addr": ("IP address / URL", "IP முகவரி / URL", "IP 주소 / URL", "ที่อยู่ IP / URL", "Dirección IP / URL"),
    "conn_btn": ("Connect / Test", "இணை / சோதி", "연결 / 테스트", "เชื่อมต่อ / ทดสอบ", "Conectar / Probar"),
    "s_ok": ("Connected", "இணைந்தது", "연결됨", "เชื่อมต่อแล้ว", "Conectado"),
    "s_no": ("Not connected", "இணைக்கப்படவில்லை", "연결 안 됨", "ยังไม่เชื่อมต่อ", "No conectado"),
    "s_off": ("Offline", "ஆஃப்லைன்", "오프라인", "ออฟไลน์", "Sin conexión"),
    "dev_hint": ("Simulation works instantly. For real hardware choose Philips WiZ (UDP) with the bulb's IP, or Home Assistant / REST with a webhook URL.",
                 "உருவகப்படுத்தல் உடனே வேலை செய்யும். உண்மையான சாதனத்திற்கு விளக்கின் IP உடன் Philips WiZ (UDP) அல்லது Home Assistant / REST webhook URL தேர்வு செய்யவும்.",
                 "시뮬레이션은 즉시 작동합니다. 실제 기기는 전구 IP가 있는 Philips WiZ (UDP) 또는 웹훅 URL이 있는 Home Assistant / REST를 선택하세요.",
                 "โหมดจำลองใช้งานได้ทันที สำหรับอุปกรณ์จริงให้เลือก Philips WiZ (UDP) พร้อม IP ของหลอดไฟ หรือ Home Assistant / REST พร้อม URL ของ webhook",
                 "La simulación funciona al instante. Para hardware real elige Philips WiZ (UDP) con la IP de la bombilla, o Home Assistant / REST con una URL de webhook."),
    "dev_my": ("My Smart Devices", "என் ஸ்மார்ட் சாதனங்கள்", "내 스마트 기기", "อุปกรณ์อัจฉริยะของฉัน", "Mis dispositivos inteligentes"),
    "dev_add": ("Add a device", "சாதனத்தைச் சேர்", "기기 추가", "เพิ่มอุปกรณ์", "Añadir dispositivo"),
    "dev_pick": ("Device type", "சாதன வகை", "기기 종류", "ประเภทอุปกรณ์", "Tipo de dispositivo"),
    "dev_room": ("Room", "அறை", "방", "ห้อง", "Habitación"),
    "dev_name": ("Custom name (optional)", "தனிப்பயன் பெயர் (விருப்பம்)", "사용자 지정 이름 (선택)", "ชื่อกำหนดเอง (ไม่บังคับ)", "Nombre personalizado (opcional)"),
    "dev_btn": ("Add device", "சாதனத்தைச் சேர்", "기기 추가", "เพิ่มอุปกรณ์", "Añadir"),
    "power_lbl": ("Power", "மின்சாரம்", "전원", "เปิด/ปิด", "Encendido"),
    "summary": ("Fleet summary", "சாதன சுருக்கம்", "기기 요약", "สรุปอุปกรณ์", "Resumen de dispositivos"),
    "sync": ("Re-apply active atmosphere to all devices", "செயலில் உள்ள சூழலை அனைத்து சாதனங்களுக்கும் மீண்டும் பயன்படுத்து", "현재 분위기를 모든 기기에 다시 적용", "ใช้บรรยากาศปัจจุบันกับอุปกรณ์ทั้งหมดอีกครั้ง", "Volver a aplicar el ambiente a todos los dispositivos"),
    "synced": ("Devices synced.", "சாதனங்கள் ஒத்திசைக்கப்பட்டன.", "기기가 동기화되었습니다.", "ซิงค์อุปกรณ์แล้ว", "Dispositivos sincronizados."),
    "api": ("Biometrics API URL", "உயிரியல் தரவு API முகவரி", "바이오메트릭 API 주소", "URL ของ API ข้อมูลชีวภาพ", "URL de la API biométrica"),
    "thr": ("Stress threshold (bpm)", "மன அழுத்த வரம்பு (bpm)", "스트레스 임계값 (bpm)", "เกณฑ์ความเครียด (bpm)", "Umbral de estrés (lpm)"),
    "rel": ("Relaxed upper limit (bpm)", "அமைதி நிலை உச்ச வரம்பு (bpm)", "편안함 상한 (bpm)", "ขีดจำกัดบนของสถานะผ่อนคลาย (bpm)", "Límite superior de relajación (lpm)"),
    "rest": ("Resting heart rate (bpm)", "ஓய்வு இதயத் துடிப்பு (bpm)", "안정시 심박수 (bpm)", "อัตราการเต้นหัวใจขณะพัก (bpm)", "Pulso en reposo (lpm)"),
    "poll": ("Biometric refresh interval (s)", "உயிரியல் தரவு புதுப்பிப்பு இடைவெளி (வி)", "바이오 데이터 갱신 간격 (초)", "ช่วงเวลารีเฟรชข้อมูลชีวภาพ (วินาที)", "Intervalo de actualización biométrica (s)"),
    "notif": ("Friendly nudge banner", "நட்பு நினைவூட்டல் பதாகை", "친근한 알림 배너", "แบนเนอร์แจ้งเตือนแบบเป็นกันเอง", "Banner de recordatorio amable"),
    "chime": ("Ring alert on nudge", "நினைவூட்டலில் மணி ஒலி", "알림 시 벨 소리", "เสียงกระดิ่งเมื่อมีการแจ้งเตือน", "Alerta sonora en el recordatorio"),
    "test": ("Test connection", "இணைப்பைச் சோதி", "연결 테스트", "ทดสอบการเชื่อมต่อ", "Probar conexión"),
    "reset": ("Reset all data", "அனைத்து தரவையும் மீட்டமை", "모든 데이터 초기화", "รีเซ็ตข้อมูลทั้งหมด", "Restablecer todo"),
    # --- New keys merged from NEW_T with full 5-language tuples ---
    "day": ("Day", "நாள்", "일", "วัน", "Día"),
    "month": ("Month", "மாதம்", "월", "เดือน", "Mes"),
    "year": ("Year", "ஆண்டு", "년", "ปี", "Año"),
    "room_sel": ("Active room", "செயலில் உள்ள அறை", "활성 방", "ห้องที่ใช้งาน", "Habitación activa"),
    "add_space": ("➕ Add Custom Space", "➕ தனிப்பயன் இடத்தைச் சேர்", "➕ 사용자 공간 추가", "➕ เพิ่มพื้นที่กำหนดเอง", "➕ Añadir espacio personalizado"),
    "sp_name": ("Room name (e.g. Terrace Garden, Gaming Den)", "அறை பெயர் (எ.கா. டெரஸ் தோட்டம், கேமிங் டென்)", "방 이름 (예: 테라스 가든, 게이밍 덴)", "ชื่อห้อง (เช่น สวนดาดฟ้า, เกมมิ่งเดน)", "Nombre de la habitación (ej. Jardín Terraza, Sala de Juegos)"),
    "sp_icon": ("Icon", "சின்னம்", "아이콘", "ไอคอน", "Icono"),
    "sp_type": ("Room type", "அறை வகை", "방 유형", "ประเภทห้อง", "Tipo de habitación"),
    "sp_devs": ("Assign devices from your fleet to this space", "உங்கள் சாதனக் குழுவிலிருந்து இந்த இடத்திற்கு சாதனங்களை ஒதுக்குங்கள்", "이 공간에 기기 할당", "กำหนดอุปกรณ์ให้กับพื้นที่นี้", "Asignar dispositivos a este espacio"),
    "sp_btn": ("Create space", "இடத்தை உருவாக்கு", "공간 만들기", "สร้างพื้นที่", "Crear espacio"),
    "sp_need": ("Please enter a room name.", "அறை பெயரை உள்ளிடவும்.", "방 이름을 입력하세요.", "กรุณาใส่ชื่อห้อง", "Introduce un nombre de habitación."),
    "sp_dup": ("A space with this name already exists.", "இந்த பெயரில் ஒரு இடம் ஏற்கனவே உள்ளது.", "이 이름의 공간이 이미 있습니다.", "มีพื้นที่ชื่อนี้อยู่แล้ว", "Ya existe un espacio con este nombre."),
    "sp_made": ("Space created: {n}", "இடம் உருவாக்கப்பட்டது: {n}", "공간 생성됨: {n}", "สร้างพื้นที่แล้ว: {n}", "Espacio creado: {n}"),
    "here": ("📍 You are here", "📍 நீங்கள் இங்கே இருக்கிறீர்கள்", "📍 현재 위치", "📍 คุณอยู่ที่นี่", "📍 Estás aquí"),
    "qc": ("🎛 Room quick controls", "🎛 அறை விரைவு கட்டுப்பாடுகள்", "🎛 방 빠른 제어", "🎛 การควบคุมห้องด่วน", "🎛 Controles rápidos de habitación"),
    "room_empty": ("No devices in this space yet. Assign some when creating a space, or move them in Device Fleet.", "இந்த இடத்தில் இன்னும் சாதனங்கள் இல்லை. இடத்தை உருவாக்கும்போது சிலவற்றை ஒதுக்குங்கள் அல்லது சாதனக் குழுவில் நகர்த்துங்கள்.", "이 공간에 아직 기기가 없습니다. 공간 생성 시 할당하거나 기기 목록에서 이동하세요.", "ยังไม่มีอุปกรณ์ในพื้นที่นี้ กำหนดเมื่อสร้างพื้นที่ หรือย้ายในรายการอุปกรณ์", "Aún no hay dispositivos en este espacio. Asigna algunos al crear un espacio o muévelos en Dispositivos."),
    "conn_title": ("Remote Access & Smart Geofence", "தொலைதூர அணுகல் & ஸ்மார்ட் ஜியோஃபென்ஸ்", "원격 액세스 & 스마트 지오펜스", "การเข้าถึงระยะไกล & สมาร์ทจีโอเฟนซ์", "Acceso Remoto y Geocerca Inteligente"),
    "conn_mode": ("Where are you right now?", "நீங்கள் இப்போது எங்கே இருக்கிறீர்கள்?", "지금 어디에 있나요?", "ตอนนี้คุณอยู่ที่ไหน?", "¿Dónde estás ahora?"),
    "conn_home": ("🏠 At Home (Local Matter / Wi-Fi Mesh)", "🏠 வீட்டில் (லோக்கல் மேட்டர் / வைஃபை மெஷ்)", "🏠 집 (로컬 매터 / 와이파이 메시)", "🏠 ที่บ้าน (โลคัลแมทเทอร์ / ไวไฟเมช)", "🏠 En casa (Matter local / Wi-Fi Mesh)"),
    "conn_away": ("🚗 Away / En Route (Remote 4G/5G Cloud Relay)", "🚗 வெளியே / வழியில் (ரிமோட் 4G/5G கிளவுட் ரிலே)", "🚗 외출 / 이동 중 (원격 4G/5G 클라우드 릴레이)", "🚗 อยู่นอกบ้าน / ระหว่างทาง (รีโมท 4G/5G คลาวด์รีเลย์)", "🚗 Fuera / En camino (Relé en la nube 4G/5G)"),
    "conn_local_cap": ("🏠 Local control: commands stay inside your home network (Matter / Wi-Fi mesh).", "🏠 லோக்கல் கட்டுப்பாடு: கட்டளைகள் உங்கள் வீட்டு நெட்வொர்க்கிற்குள் இருக்கும் (மேட்டர் / வைஃபை மெஷ்).", "🏠 로컬 제어: 명령은 홈 네트워크 내에 머뭅니다 (매터 / 와이파이 메시).", "🏠 ควบคุมในบ้าน: คำสั่งอยู่ในเครือข่ายบ้าน (แมทเทอร์ / ไวไฟเมช)", "🏠 Control local: los comandos permanecen en tu red doméstica (Matter / Wi-Fi mesh)."),
    "conn_cloud_cap": ("☁️ Remote control: commands travel through the secure 4G/5G cloud relay.", "☁️ ரிமோட் கட்டுப்பாடு: கட்டளைகள் பாதுகாப்பான 4G/5G கிளவுட் ரிலே வழியாகச் செல்லும்.", "☁️ 원격 제어: 명령은 보안 4G/5G 클라우드 릴레이를 통해 전달됩니다.", "☁️ ควบคุมระยะไกล: คำสั่งผ่านคลาวด์รีเลย์ 4G/5G ที่ปลอดภัย", "☁️ Control remoto: los comandos viajan por el relé seguro en la nube 4G/5G."),
    "geo_dist": ("Distance from home (km) - simulated GPS", "வீட்டிலிருந்து தூரம் (கிமீ) - உருவகப்படுத்தப்பட்ட ஜிபிஎஸ்", "집으로부터 거리 (km) - 시뮬레이션 GPS", "ระยะทางจากบ้าน (กม.) - จำลอง GPS", "Distancia desde casa (km) - GPS simulado"),
    "geo_dist_m": ("Distance from home", "வீட்டிலிருந்து தூரம்", "집으로부터 거리", "ระยะทางจากบ้าน", "Distancia desde casa"),
    "geo_eta": ("Estimated arrival", "மதிப்பிடப்பட்ட வருகை", "예상 도착", "เวลาถึงโดยประมาณ", "Llegada estimada"),
    "geo_zone": ("Geofence", "ஜியோஃபென்ஸ்", "지오펜스", "จีโอเฟนซ์", "Geocerca"),
    "geo_idle": ("Watching your route", "உங்கள் பாதையைக் கவனிக்கிறது", "경로를 주시 중", "กำลังติดตามเส้นทาง", "Vigilando tu ruta"),
    "geo_pending": ("Waiting for your confirmation", "உங்கள் உறுதிப்படுத்தலுக்காகக் காத்திருக்கிறது", "확인을 기다리는 중", "รอการยืนยันของคุณ", "Esperando tu confirmación"),
    "geo_confirmed": ("Pre-conditioning confirmed", "முன்-சீரமைப்பு உறுதிப்படுத்தப்பட்டது", "사전 조절 확인됨", "ยืนยันการปรับสภาพล่วงหน้าแล้ว", "Pre-acondicionamiento confirmado"),
    "geo_dismissed": ("Dismissed - appliances on standby", "நிராகரிக்கப்பட்டது - சாதனங்கள் தெரியாமல்", "무시됨 - 대기 중", "ปัดทิ้ง - อุปกรณ์สแตนด์บาย", "Descartado - electrodomésticos en espera"),
    "geo_alert": ("📍 Smart Geofence Alert: Hey {n}, you are {m} mins away from home. Would you like to pre-heat the En-Suite Bath Geyser to 42°C and pre-cool Master Suite AC to 22°C?", "📍 ஸ்மார்ட் ஜியோஃபென்ஸ் எச்சரிக்கை: ஹே {n}, நீங்கள் வீட்டிலிருந்து {m} நிமிடங்கள் தொலைவில் உள்ளீர்கள். என்சூட் பாத் கீசரை 42°C ஆக முன்கூட்டியே சூடாக்கி, மாஸ்டர் சூட் ஏசியை 22°C ஆக முன்கூட்டியே குளிர்விக்கவா?", "📍 스마트 지오펜스 알림: {n}님, 집에서 {m}분 거리에 있습니다. 욕실 온수기를 42°C로 예열하고 마스터 스위트 에어컨을 22°C로 냉방할까요?", "📍 แจ้งเตือนสมาร์ทจีโอเฟนซ์: สวัสดี {n} คุณอยู่ห่างจากบ้าน {m} นาที ต้องการอุ่นเครื่องทำน้ำอุ่นเป็น 42°C และเปิดแอร์ห้องนอนหลักเป็น 22°C ล่วงหน้าหรือไม่?", "📍 Alerta de Geocerca Inteligente: Hola {n}, estás a {m} minutos de casa. ¿Quieres precalentar el calentador del baño a 42°C y precooler el A/C de la suite a 22°C?"),
    "geo_yes": ("✅ Confirm & Pre-Condition Devices", "✅ உறுதிசெய்து சாதனங்களை முன்-சீரமை", "✅ 확인 및 사전 조절", "✅ ยืนยันและปรับสภาพอุปกรณ์", "✅ Confirmar y preacondicionar dispositivos"),
    "geo_no": ("❌ Dismiss / Keep Standby", "❌ நிராகரி / தெரியாமல் வைத்திரு", "❌ 무시 / 대기 유지", "❌ ปัดทิ้ง / คงสถานะสแตนด์บาย", "❌ Descartar / Mantener en espera"),
    "away_pause": ("You are away, so Aura Companion is paused for in-home sensors. Remote commands use the cloud relay.", "நீங்கள் வெளியே இருப்பதால், வீட்டு சென்சார்களுக்கான ஆரா துணை இடைநிறுத்தப்பட்டுள்ளது. ரிமோட் கட்டளைகள் கிளவுட் ரிலேவைப் பயன்படுத்துகின்றன.", "외출 중이므로 실내 센서용 Aura Companion이 일시중지됩니다. 원격 명령은 클라우드 릴레이를 사용합니다.", "คุณอยู่นอกบ้าน Aura Companion จึงหยุดชั่วคราวสำหรับเซ็นเซอร์ในบ้าน คำสั่งระยะไกลใช้คลาวด์รีเลย์", "Estás fuera, Aura Companion está en pausa para sensores. Los comandos remotos usan el relé en la nube."),
    "remote_status": ("Remote pre-conditioning status", "ரிமோட் முன்-சீரமைப்பு நிலை", "원격 사전 조절 상태", "สถานะการปรับสภาพล่วงหน้าระยะไกล", "Estado de preacondicionamiento remoto"),
    "ml_title": ("Room-Level Location & Follow-Me", "அறை அளவு இருப்பிடம் & என்னைப் பின்தொடர்", "방 수준 위치 & 팔로우미", "ตำแหน่งระดับห้อง & ติดตามฉัน", "Ubicación por Habitación y Seguimiento"),
    "ml_dev": ("Tracked wearable / device", "கண்காணிக்கப்பட்ட அணிகலன் / சாதனம்", "추적 장치", "อุปกรณ์สวมใส่ที่ติดตาม", "Dispositivo rastreado"),
    "ml_engine": ("Tracking engine", "கண்காணிப்பு இயந்திரம்", "추적 엔진", "เอนจิ้นติดตาม", "Motor de seguimiento"),
    "ml_uwb": ("UWB - Ultra-Wideband: centimetre accuracy + direction of arrival", "UWB - அல்ட்ரா-வைட்பேண்ட்: சென்டிமீட்டர் துல்லியம் + வருகை திசை", "UWB - 초광대역: 센티미터 정확도 + 도래 방향", "UWB - อัลตร้าไวด์แบนด์: ความแม่นยำระดับเซนติเมตร + ทิศทาง", "UWB - Banda Ultra Ancha: precisión centimétrica + dirección de llegada"),
    "ml_ble": ("BLE - Bluetooth Low Energy: room-level signal-strength (RSSI)", "BLE - புளூடூத் லோ எனர்ஜி: அறை அளவு சமிக்ஞை வலிமை (RSSI)", "BLE - 블루투스 로우 에너지: 방 수준 신호 강도 (RSSI)", "BLE - บลูทูธพลังงานต่ำ: ความแรงสัญญาณระดับห้อง (RSSI)", "BLE - Bluetooth de Baja Energía: intensidad de señal por habitación (RSSI)"),
    "ml_sim": ("Where are you? (live room simulator)", "நீங்கள் எங்கே? (நேரடி அறை சிமுலேட்டர்)", "어디에 있나요? (실시간 방 시뮬레이터)", "คุณอยู่ที่ไหน? (จำลองห้องสด)", "¿Dónde estás? (simulador de habitación en vivo)"),
    "ml_follow": ("Follow-Me: switch off the room I leave and wake the room I enter", "என்னைப் பின்தொடர்: விட்டு வெளியேறும் அறையை அணைத்து, நுழையும் அறையை எழுப்பு", "팔로우미: 떠나는 방은 끄고 들어가는 방은 켜기", "ติดตามฉัน: ปิดห้องที่จากไป เปิดห้องที่เข้ามา", "Seguimiento: apaga la habitación que dejo y enciende la que entro"),
    "ml_cut": ("When I leave a room, its AC goes", "நான் அறையை விட்டு வெளியேறும்போது அதன் ஏசி", "방을 떠나면 에어컨", "เมื่อฉันออกจากห้อง แอร์", "Cuando salgo de una habitación, su A/C"),
    "ml_calm": ("Room-isolated calm (heart rate above 85 BPM in Work Studio)", "அறை-தனிமைப்படுத்தப்பட்ட அமைதி (வேலை ஸ்டுடியோவில் இதயத் துடிப்பு 85 BPM க்கு மேல்)", "방 격리 진정 (작업실 심박수 85 BPM 초과)", "ความสงบเฉพาะห้อง (ชีพจรเกิน 85 BPM ในสตูดิโอทำงาน)", "Calma aislada por habitación (pulso superior a 85 BPM en el estudio)"),
    "ml_away": ("Indoor tracking is paused while you are away from home.", "வீட்டை விட்டு வெளியே இருக்கும்போது உள்ளரங்க கண்காணிப்பு இடைநிறுத்தப்பட்டுள்ளது.", "외출 중에는 실내 추적이 일시중지됩니다.", "การติดตามในบ้านหยุดชั่วคราวเมื่อคุณออกจากบ้าน", "El seguimiento interior se pausa cuando estás fuera de casa."),
    "ml_zone": ("Your zone", "உங்கள் மண்டலம்", "내 구역", "โซนของคุณ", "Tu zona"),
    "ml_dist": ("Distance to room anchor", "அறை அன்கருக்கான தூரம்", "방 앵커까지 거리", "ระยะทางถึงจุดยึดห้อง", "Distancia al ancla de habitación"),
    "ml_aoa": ("Angle of arrival", "வருகை கோணம்", "도래 각도", "มุมการมาถึง", "Ángulo de llegada"),
    "ml_acc": ("Accuracy", "துல்லியம்", "정확도", "ความแม่นยำ", "Precisión"),
    "ml_rssi": ("Signal strength per room anchor (dBm)", "ஒரு அறை அன்கருக்கான சமிக்ஞை வலிமை (dBm)", "방 앵커별 신호 강도 (dBm)", "ความแรงสัญญาณต่อจุดยึดห้อง (dBm)", "Intensidad de señal por ancla (dBm)"),
    "ml_est": ("Estimated room", "மதிப்பிடப்பட்ட அறை", "추정 방", "ห้องที่ประมาณ", "Habitación estimada"),
    "feel": ("You seem {s} → home atmosphere: {m}", "நீங்கள் {s} ஆகத் தெரிகிறது → வீட்டு சூழல்: {m}", "당신은 {s} 상태 → 집 분위기: {m}", "คุณดู {s} → บรรยากาศบ้าน: {m}", "Pareces {s} → ambiente del hogar: {m}"),
    "calm_note": ("🌊 {r} is in calm mode ({m}). Only this room changed; the rest of the house is untouched.", "🌊 {r} அமைதி பயன்முறையில் உள்ளது ({m}). இந்த அறை மட்டும் மாறியது; மற்ற வீடு தொடப்படவில்லை.", "🌊 {r}은(는) 진정 모드({m})입니다. 이 방만 변경되었습니다.", "🌊 {r} อยู่ในโหมดสงบ ({m}) เปลี่ยนเฉพาะห้องนี้", "🌊 {r} está en modo calma ({m}). Solo cambió esta habitación."),
    "rt_title": ("Daily Routine Scheduler", "தினசரி வழக்க அட்டவணையாளர்", "일일 루틴 스케줄러", "ตัวจัดตารางกิจวัตรประจำวัน", "Programador de Rutinas Diarias"),
    "rt_hint": ("Routines pre-activate devices on a timer. They protect their own devices from Auto/Manual changes for a while, so nothing fights each other.", "வழக்கங்கள் டைமரில் சாதனங்களை முன்கூட்டியே இயக்குகின்றன. அவை சிறிது நேரம் ஆட்டோ/கைமுறை மாற்றங்களிலிருந்து தங்கள் சாதனங்களைப் பாதுகாக்கின்றன.", "루틴은 타이머로 기기를 미리 켭니다. 잠시 동안 자동/수동 변경으로부터 보호합니다.", "กิจวัตรจะเปิดอุปกรณ์ล่วงหน้าตามเวลา ป้องกันการเปลี่ยนแปลงชั่วคราว", "Las rutinas preactivan dispositivos con temporizador. Protegen sus dispositivos de cambios automáticos/manuales."),
    "rt_on": ("Enabled", "இயக்கப்பட்டது", "활성화됨", "เปิดใช้งาน", "Habilitado"),
    "rt_wake": ("Wake-up time", "எழும் நேரம்", "기상 시간", "เวลาตื่น", "Hora de despertar"),
    "rt_bath": ("Bath time", "குளியல் நேரம்", "목욕 시간", "เวลาอาบน้ำ", "Hora de baño"),
    "rt_sleep": ("Sleep target", "உறக்க இலக்கு", "수면 목표", "เป้าหมายการนอน", "Objetivo de sueño"),
    "rt_off": ("Start this many minutes before", "இத்தனை நிமிடங்களுக்கு முன்பு தொடங்கு", "몇 분 전에 시작", "เริ่มก่อนกี่นาที", "Comenzar estos minutos antes"),
    "rt_run": ("▶ Run now (test)", "▶ இப்போது இயக்கு (சோதனை)", "▶ 지금 실행 (테스트)", "▶ เรียกใช้เลย (ทดสอบ)", "▶ Ejecutar ahora (prueba)"),
    "rt_add": ("➕ Add Custom Routine", "➕ தனிப்பயன் வழக்கத்தைச் சேர்", "➕ 사용자 루틴 추가", "➕ เพิ่มกิจวัตรกำหนดเอง", "➕ Añadir rutina personalizada"),
    "rt_name": ("Routine name", "வழக்கத்தின் பெயர்", "루틴 이름", "ชื่อกิจวัตร", "Nombre de la rutina"),
    "rt_time": ("Target time", "இலக்கு நேரம்", "목표 시간", "เวลาเป้าหมาย", "Hora objetivo"),
    "rt_devs": ("Devices to control", "கட்டுப்படுத்த வேண்டிய சாதனங்கள்", "제어할 기기", "อุปกรณ์ที่จะควบคุม", "Dispositivos a controlar"),
    "rt_act": ("Action", "செயல்", "동작", "การกระทำ", "Acción"),
    "rt_ran": ("✅ Ran today", "✅ இன்று இயங்கியது", "✅ 오늘 실행됨", "✅ ทำงานวันนี้", "✅ Ejecutado hoy"),
    "rt_need": ("Please enter a routine name and pick at least one device.", "வழக்கத்தின் பெயரை உள்ளிட்டு குறைந்தது ஒரு சாதனத்தைத் தேர்ந்தெடுக்கவும்.", "루틴 이름과 하나 이상의 기기를 선택하세요.", "กรุณาใส่ชื่อกิจวัตรและเลือกอุปกรณ์อย่างน้อยหนึ่งรายการ", "Introduce un nombre de rutina y elige al menos un dispositivo."),
    "rt_made": ("Routine added", "வழக்கம் சேர்க்கப்பட்டது", "루틴 추가됨", "เพิ่มกิจวัตรแล้ว", "Rutina añadida"),
    "rt_ranmsg": ("Scheduled routine started", "திட்டமிடப்பட்ட வழக்கம் தொடங்கியது", "예약된 루틴 시작됨", "กิจวัตรที่ตั้งเวลาไว้เริ่มแล้ว", "Rutina programada iniciada"),
    "theme": ("Theme", "தோற்றம்", "테마", "ธีม", "Tema"),
    "theme_dark": ("🌙 Dark · Black & Gold", "🌙 இருண்ட · கருப்பு & தங்கம்", "🌙 다크 · 블랙 & 골드", "🌙 มืด · ดำ & ทอง", "🌙 Oscuro · Negro y Dorado"),
    "theme_light": ("☀️ Light · White", "☀️ ஒளி · வெள்ளை", "☀️ 라이트 · 화이트", "☀️ สว่าง · ขาว", "☀️ Claro · Blanco"),
    "rs_room": ("Room to configure", "கட்டமைக்க வேண்டிய அறை", "설정할 방", "ห้องที่จะกำหนดค่า", "Habitación a configurar"),
    "rs_hint": ("The Live Dashboard keeps the one-click active-room selector. Everything that sets up rooms, remote access and the geofence lives on this page.", "நேரடி டாஷ்போர்டு ஒரு கிளிக் செயலில் உள்ள அறை தேர்வியை வைத்திருக்கிறது. அறைகள், தொலைதூர அணுகல் மற்றும் ஜியோஃபென்ஸ் அமைப்பது இந்தப் பக்கத்தில் உள்ளது.", "라이브 대시보드는 원클릭 활성 방 선택기를 유지합니다. 방 설정, 원격 액세스, 지오펜스는 이 페이지에 있습니다.", "แดชบอร์ดสดมีตัวเลือกห้องที่ใช้งานอยู่ การตั้งค่าห้อง การเข้าถึงระยะไกล และจีโอเฟนซ์อยู่ในหน้านี้", "El Panel en Vivo mantiene el selector de habitación activa. La configuración de habitaciones, acceso remoto y geocerca está en esta página."),
    "rs_dash_hint": ("Room settings, Remote Access and Smart Geofence now live in the “Room Settings, Remote Access & Smart Geofence” tab of the Navigate menu.", "அறை அமைப்புகள், தொலைதூர அணுகல் மற்றும் ஸ்மார்ட் ஜியோஃபென்ஸ் இப்போது வழிசெலுத்தல் மெனுவின் “அறை அமைப்புகள், தொலைதூர கட்டுப்பாடு & ஜியோஃபென்ஸ்” தாவலில் உள்ளன.", "방 설정, 원격 액세스 및 스마트 지오펜스는 이제 '방 설정, 원격 액세스 & 스마트 지오펜스' 탭에 있습니다.", "การตั้งค่าห้อง การเข้าถึงระยะไกล และสมาร์ทจีโอเฟนซ์อยู่ในแท็บ 'การตั้งค่าห้อง การเข้าถึงระยะไกล & สมาร์ทจีโอเฟนซ์'", "La configuración de habitaciones, acceso remoto y geocerca están en la pestaña 'Configuración de Habitación, Acceso Remoto y Geocerca Inteligente'."),
    "rs_sec_room": ("Room Settings", "அறை அமைப்புகள்", "방 설정", "การตั้งค่าห้อง", "Configuración de Habitación"),
    "rs_manage": ("Manage this space (move devices / delete)", "இந்த இடத்தை நிர்வகி (சாதனங்களை நகர்த்து / நீக்கு)", "이 공간 관리 (기기 이동 / 삭제)", "จัดการพื้นที่นี้ (ย้ายอุปกรณ์ / ลบ)", "Gestionar este espacio (mover / eliminar)"),
    "rs_move": ("Move devices from other rooms into this room", "மற்ற அறைகளிலிருந்து இந்த அறைக்கு சாதனங்களை நகர்த்து", "다른 방의 기기를 이 방으로 이동", "ย้ายอุปกรณ์จากห้องอื่นมาที่ห้องนี้", "Mover dispositivos de otras habitaciones a esta"),
    "rs_move_btn": ("Move devices here", "சாதனங்களை இங்கே நகர்த்து", "기기를 여기로 이동", "ย้ายอุปกรณ์มาที่นี่", "Mover dispositivos aquí"),
    "rs_moved": ("{c} device(s) moved to {n}", "{c} சாதனம்(கள்) {n} க்கு நகர்த்தப்பட்டன", "{c}개 기기가 {n}(으)로 이동됨", "ย้าย {c} อุปกรณ์ไปที่ {n}", "{c} dispositivo(s) movidos a {n}"),
    "rs_dest": ("When deleting, move its devices to", "நீக்கும்போது, அதன் சாதனங்களை இங்கே நகர்த்து", "삭제 시 기기를 이동할 위치", "เมื่อลบ ให้ย้ายอุปกรณ์ไปที่", "Al eliminar, mover dispositivos a"),
    "rs_del": ("Delete this space", "இந்த இடத்தை நீக்கு", "이 공간 삭제", "ลบพื้นที่นี้", "Eliminar este espacio"),
    "rs_deleted": ("Space deleted: {n}", "இடம் நீக்கப்பட்டது: {n}", "공간 삭제됨: {n}", "ลบพื้นที่แล้ว: {n}", "Espacio eliminado: {n}"),
    "rs_protected": ("This space is used by built-in automations (geofence, routines, calm mode) so it cannot be deleted. You can still move devices in and out of it.", "இந்த இடம் உள்ளமைக்கப்பட்ட தானியங்கிகளால் பயன்படுத்தப்படுகிறது (ஜியோஃபென்ஸ், வழக்கங்கள், அமைதி பயன்முறை) எனவே நீக்க முடியாது. சாதனங்களை நகர்த்தலாம்.", "이 공간은 내장 자동화(지오펜스, 루틴, 진정 모드)에 사용되므로 삭제할 수 없습니다. 기기 이동은 가능합니다.", "พื้นที่นี้ใช้โดยระบบอัตโนมัติในตัว (จีโอเฟนซ์ กิจวัตร โหมดสงบ) จึงลบไม่ได้ แต่ย้ายอุปกรณ์ได้", "Este espacio lo usan automatizaciones (geocerca, rutinas, modo calma) y no se puede eliminar. Puedes mover dispositivos."),
    "rs_last": ("You need at least one space.", "குறைந்தது ஒரு இடம் தேவை.", "최소 하나의 공간이 필요합니다.", "คุณต้องมีพื้นที่อย่างน้อยหนึ่งแห่ง", "Necesitas al menos un espacio."),
    "dev_rename": ("Device name (edit to recognise it)", "சாதனத்தின் பெயர் (அடையாளம் காண திருத்து)", "기기 이름 (편집하여 식별)", "ชื่ออุปกรณ์ (แก้ไขเพื่อจดจำ)", "Nombre del dispositivo (editar para reconocerlo)"),
    "dev_rename_bad": ("Name must be 1-40 characters and not used by another device.", "பெயர் 1-40 எழுத்துகளாக இருக்க வேண்டும், மற்ற சாதனத்தால் பயன்படுத்தப்படக்கூடாது.", "이름은 1-40자이며 다른 기기에서 사용되지 않아야 합니다.", "ชื่อต้องยาว 1-40 ตัวอักษรและไม่ซ้ำกับอุปกรณ์อื่น", "El nombre debe tener 1-40 caracteres y no usarse en otro dispositivo."),
    "dev_renamed": ("Renamed to {n}", "{n} என மறுபெயரிடப்பட்டது", "{n}(으)로 이름 변경됨", "เปลี่ยนชื่อเป็น {n}", "Renombrado a {n}"),
    "rs_devices": ("Devices in this room: name, power, level, colour", "இந்த அறையில் உள்ள சாதனங்கள்: பெயர், மின்சாரம், நிலை, நிறம்", "이 방의 기기: 이름, 전원, 수준, 색상", "อุปกรณ์ในห้องนี้: ชื่อ, เปิด/ปิด, ระดับ, สี", "Dispositivos en esta habitación: nombre, encendido, nivel, color"),
    "rs_dev_remove": ("Remove device", "சாதனத்தை அகற்று", "기기 제거", "ลบอุปกรณ์", "Eliminar dispositivo"),
    "rs_add_dev": ("Add another device to this room (e.g. Bulb 2, Table Fan, Air Cooler)", "இந்த அறைக்கு மற்றொரு சாதனத்தைச் சேர் (எ.கா. பல்பு 2, மேசை விசிறி, ஏர் கூலர்)", "이 방에 다른 기기 추가 (예: 전구 2, 탁상 선풍기)", "เพิ่มอุปกรณ์อื่นให้ห้องนี้ (เช่น หลอดไฟ 2, พัดลมตั้งโต๊ะ)", "Añadir otro dispositivo a esta habitación (ej. Bombilla 2, Ventilador, Enfriador)"),
    "rs_dev_added": ("Added {n} to {r}", "{n} ஐ {r} இல் சேர்க்கப்பட்டது", "{n}을(를) {r}에 추가함", "เพิ่ม {n} ใน {r} แล้ว", "Añadido {n} a {r}"),
    "rs_preset": ("Room default (one click on the Live Dashboard)", "அறை இயல்புநிலை (நேரடி டாஷ்போர்டில் ஒரு கிளிக்)", "방 기본값 (라이브 대시보드에서 원클릭)", "ค่าเริ่มต้นห้อง (หนึ่งคลิกบนแดชบอร์ดสด)", "Predeterminado de habitación (un clic en el Panel)"),
    "rs_preset_hint": ("Set the devices below the way you like this room, then save. The Live Dashboard and Auto Mode (when you walk in) use this default.", "விரும்பியபடி சாதனங்களை அமைத்து சேமிக்கவும். நேரடி டாஷ்போர்டு மற்றும் ஆட்டோ மোড இந்த இயல்புநிலையைப் பயன்படுத்தும்.", "원하는 대로 기기를 설정하고 저장하세요. 라이브 대시보드와 자동 모드가 이 기본값을 사용합니다.", "ตั้งค่าอุปกรณ์ตามต้องการแล้วบันทึก แดชบอร์ดสดและโหมดอัตโนมัติใช้ค่านี้", "Configura los dispositivos a tu gusto y guarda. El Panel y el Modo Automático usan este predeterminado."),
    "rs_preset_save": ("💾 Save current settings as this room's default", "💾 தற்போதைய அமைப்புகளை இந்த அறையின் இயல்புநிலையாகச் சேமி", "💾 현재 설정을 이 방의 기본값으로 저장", "💾 บันทึกการตั้งค่าปัจจุบันเป็นค่าเริ่มต้น", "💾 Guardar ajustes actuales como predeterminado"),
    "rs_preset_apply": ("Apply default to {n}", "{n} க்கு இயல்புநிலையைப் பயன்படுத்து", "{n}에 기본값 적용", "ใช้ค่าเริ่มต้นกับ {n}", "Aplicar predeterminado a {n}"),
    "rs_preset_clear": ("Clear default", "இயல்புநிலையை அழி", "기본값 지우기", "ล้างค่าเริ่มต้น", "Borrar predeterminado"),
    "rs_preset_has": ("Saved default covers {c} device(s).", "சேமிக்கப்பட்ட இயல்புநிலை {c} சாதனங்களை உள்ளடக்கியது.", "저장된 기본값이 {c}개 기기를 포함합니다.", "ค่าเริ่มต้นที่บันทึกครอบคลุม {c} อุปกรณ์", "El predeterminado guardado cubre {c} dispositivo(s)."),
    "rs_preset_saved": ("Default saved for {n} ({c} device(s))", "{n} க்கான இயல்புநிலை சேமிக்கப்பட்டது ({c} சாதனங்கள்)", "{n}의 기본값 저장됨 ({c}개 기기)", "บันทึกค่าเริ่มต้นสำหรับ {n} แล้ว ({c} อุปกรณ์)", "Predeterminado guardado para {n} ({c} dispositivo(s))"),
    "rs_preset_cleared": ("Default cleared for {n}", "{n} க்கான இயல்புநிலை அழிக்கப்பட்டது", "{n}의 기본값 삭제됨", "ล้างค่าเริ่มต้นสำหรับ {n} แล้ว", "Predeterminado borrado para {n}"),
    "rs_preset_applied": ("Default applied: {n} ({c} device(s))", "இயல்புநிலை பயன்படுத்தப்பட்டது: {n} ({c} சாதனங்கள்)", "기본값 적용됨: {n} ({c}개 기기)", "ใช้ค่าเริ่มต้นแล้ว: {n} ({c} อุปกรณ์)", "Predeterminado aplicado: {n} ({c} dispositivo(s))"),
    "preset_apply_all": ("Apply defaults to ALL rooms", "அனைத்து அறைகளுக்கும் இயல்புநிலைகளைப் பயன்படுத்து", "모든 방에 기본값 적용", "ใช้ค่าเริ่มต้นกับทุกห้อง", "Aplicar predeterminados a TODAS las habitaciones"),
    "preset_none": ("No saved default for this room yet. Set it up in Room Settings.", "இந்த அறைக்கு இன்னும் சேமிக்கப்பட்ட இயல்புநிலை இல்லை. அறை அமைப்புகளில் அமைக்கவும்.", "이 방에 저장된 기본값이 없습니다. 방 설정에서 구성하세요.", "ยังไม่มีค่าเริ่มต้นสำหรับห้องนี้ ตั้งค่าในการตั้งค่าห้อง", "Aún no hay predeterminado para esta habitación. Configúralo en Ajustes."),
    "mode_bad_name": ("Enter a valid mode name (1-40 letters, numbers, spaces or - & ' . ( ) ).", "சரியான பயன்முறை பெயரை உள்ளிடவும் (1-40 எழுத்துகள், எண்கள், இடைவெளிகள் அல்லது - & ' . ( ) ).", "유효한 모드 이름을 입력하세요 (1-40자, 숫자, 공백 또는 - & ' . ( ) ).", "ใส่ชื่อโหมดที่ถูกต้อง (1-40 ตัวอักษร ตัวเลข ช่องว่าง หรือ - & ' . ( ) )", "Introduce un nombre de modo válido (1-40 letras, números, espacios o - & ' . ( ) )."),
    "mode_dup": ("A mode with this name already exists. Choose another name.", "இந்தப் பெயரில் ஒரு பயன்முறை ஏற்கனவே உள்ளது. வேறு பெயரைத் தேர்ந்தெடுக்கவும்.", "이 이름의 모드가 이미 있습니다. 다른 이름을 선택하세요.", "มีโหมดชื่อนี้อยู่แล้ว เลือกชื่ออื่น", "Ya existe un modo con este nombre. Elige otro."),
    "mode_bad_color": ("The bulb colour is not a valid hex colour (#RRGGBB).", "விளக்கு நிறம் சரியான ஹெக்ஸ் நிறம் (#RRGGBB) அல்ல.", "전구 색상이 유효한 16진수 색상(#RRGGBB)이 아닙니다.", "สีหลอดไฟไม่ใช่สี hex ที่ถูกต้อง (#RRGGBB)", "El color de la bombilla no es un hex válido (#RRGGBB)."),
    "dev_orphan_fix": ("Devices re-homed safely", "சாதனங்கள் பாதுகாப்பாக மீளமைக்கப்பட்டன", "기기가 안전하게 재배치됨", "ย้ายอุปกรณ์กลับอย่างปลอดภัย", "Dispositivos reubicados con seguridad"),
    "geo_started": ("Arrival pre-conditioning started automatically", "வருகை முன்-சீரமைப்பு தானாகத் தொடங்கியது", "도착 사전 조절 자동 시작됨", "เริ่มการปรับสภาพล่วงหน้าอัตโนมัติ", "Preacondicionamiento de llegada iniciado automáticamente"),
    "geo_card_hdr": ("✨ AuraSync Luxury Arrival · Pre-Conditioning Active ({m} mins to home).", "✨ AuraSync ஆடம்பர வருகை · முன்-சீரமைப்பு செயலில் ({m} நிமிடங்கள் வீட்டிற்கு).", "✨ AuraSync 럭셔리 도착 · 사전 조절 활성 ({m}분 남음).", "✨ AuraSync การมาถึงสุดหรู · ปรับสภาพล่วงหน้าทำงาน ({m} นาทีถึงบ้าน)", "✨ Llegada de Lujo AuraSync · Preacondicionamiento Activo ({m} min a casa)."),
    "geo_card_sub": ("Comfort routine is running. Tap a button below to switch off just one item. Nothing else changes.", "வசதி வழக்கம் இயங்குகிறது. ஒரு பொருளை மட்டும் அணைக்க கீழே ஒரு பொத்தானைத் தட்டவும். வேறு எதுவும் மாறாது.", "편안함 루틴이 실행 중입니다. 아래 버튼으로 하나만 끌 수 있습니다. 다른 것은 바뀌지 않습니다.", "กิจวัตรสบายกำลังทำงาน แตะปุ่มด้านล่างเพื่อปิดเพียงรายการเดียว", "La rutina de confort está activa. Pulsa un botón para apagar solo un elemento."),
    "geo_off_geyser": ("🚿 Turn OFF Geyser Alone", "🚿 கீசரை மட்டும் அணை", "🚿 온수기만 끄기", "🚿 ปิดเครื่องทำน้ำอุ่นเท่านั้น", "🚿 Apagar solo el calentador"),
    "geo_off_ac": ("❄️ Turn OFF AC Alone", "❄️ ஏசியை மட்டும் அணை", "❄️ 에어컨만 끄기", "❄️ ปิดแอร์เท่านั้น", "❄️ Apagar solo el A/C"),
    "geo_off_fan": ("🌀 Turn OFF Fan Alone", "🌀 மின்விசிறியை மட்டும் அணை", "🌀 선풍기만 끄기", "🌀 ปิดพัดลมเท่านั้น", "🌀 Apagar solo el ventilador"),
    "geo_on_geyser": ("🚿 Turn Geyser back ON", "🚿 கீசரை மீண்டும் இயக்கு", "🚿 온수기 다시 켜기", "🚿 เปิดเครื่องทำน้ำอุ่นอีกครั้ง", "🚿 Encender el calentador de nuevo"),
    "geo_on_ac": ("❄️ Turn AC back ON", "❄️ ஏசியை மீண்டும் இயக்கு", "❄️ 에어컨 다시 켜기", "❄️ เปิดแอร์อีกครั้ง", "❄️ Encender el A/C de nuevo"),
    "geo_on_fan": ("🌀 Turn Fan back ON", "🌀 மின்விசிறியை மீண்டும் இயக்கு", "🌀 선풍기 다시 켜기", "🌀 เปิดพัดลมอีกครั้ง", "🌀 Encender el ventilador de nuevo"),
    "geo_cancel_all": ("🛑 Cancel All & Return to Standby", "🛑 அனைத்தையும் ரத்துசெய்து தெரியாமல் திரும்பு", "🛑 모두 취소 및 대기로 복귀", "🛑 ยกเลิกทั้งหมด & กลับสแตนด์บาย", "🛑 Cancelar todo y volver a espera"),
    "geo_off_alone": ("{n} switched off. Everything else keeps running.", "{n} அணைக்கப்பட்டது. மற்றவை தொடர்ந்து இயங்கும்.", "{n} 꺼짐. 나머지는 계속 실행됩니다.", "{n} ปิดแล้ว ส่วนอื่นยังทำงาน", "{n} apagado. Lo demás sigue funcionando."),
    "geo_on_again": ("{n} switched back on.", "{n} மீண்டும் இயக்கப்பட்டது.", "{n} 다시 켜짐.", "{n} เปิดอีกครั้งแล้ว", "{n} encendido de nuevo."),
    "geo_cancelled": ("Arrival routine cancelled. Home is on standby.", "வருகை வழக்கம் ரத்து செய்யப்பட்டது. வீடு தெரியாமல் உள்ளது.", "도착 루틴 취소됨. 집이 대기 상태입니다.", "ยกเลิกกิจวัตรการมาถึง บ้านอยู่ในสแตนด์บาย", "Rutina de llegada cancelada. La casa está en espera."),
    "geo_standby": ("Arrival routine cancelled. Everything is on standby.", "வருகை வழக்கம் ரத்து. அனைத்தும் தெரியாமல் உள்ளது.", "도착 루틴 취소. 모두 대기 중.", "ยกเลิกกิจวัตรการมาถึง ทุกอย่างสแตนด์บาย", "Rutina de llegada cancelada. Todo en espera."),
    "geo_restart": ("↺ Start the arrival routine again", "↺ வருகை வழக்கத்தை மீண்டும் தொடங்கு", "↺ 도착 루틴 다시 시작", "↺ เริ่มกิจวัตรการมาถึงอีกครั้ง", "↺ Iniciar la rutina de llegada de nuevo"),
    "geo_auto_toggle": ("Autonomous Pre-Conditioning (Zero-Touch)", "தன்னாட்சி முன்-சீரமைப்பு (பூஜ்ய-தொடுதல்)", "자율 사전 조절 (제로 터치)", "การปรับสภาพล่วงหน้าอัตโนมัติ (ไม่ต้องแตะ)", "Preacondicionamiento Autónomo (Cero Toques)"),
    "geo_auto_hint": ("ON: when you are 5 km / 15 mins away AuraSync warms the bath, cools the bedroom and starts the fan by itself. OFF: it asks you first.", "ON: நீங்கள் 5 கிமீ / 15 நிமிடங்கள் தொலைவில் இருக்கும்போது AuraSync குளியலறையை சூடாக்கி, படுக்கையறையை குளிர்வித்து, விசிறியைத் தானாகத் தொடங்கும். OFF: முதலில் கேட்கும்.", "ON: 5km / 15분 거리일 때 AuraSync가 욕조를 데우고 침실을 식히고 선풍기를 시작합니다. OFF: 먼저 물어봅니다.", "ON: เมื่ออยู่ห่าง 5 กม. / 15 นาที AuraSync จะอุ่นอ่าง ลดอุณหภูมิห้องนอน และเปิดพัดลมเอง OFF: จะถามก่อน", "ON: a 5 km / 15 min AuraSync calienta el baño, enfría el dormitorio y enciende el ventilador. OFF: pregunta primero."),
    "geo_idle_status": ("Home appliances (live status)", "வீட்டு உபகரணங்கள் (நேரடி நிலை)", "가전 기기 (실시간 상태)", "เครื่องใช้ในบ้าน (สถานะสด)", "Electrodomésticos (estado en vivo)"),
    "geo_sim": ("🔧 Trip simulator (try it: slide the distance)", "🔧 பயண சிமுலேட்டர் (முயற்சி: தூரத்தை நகர்த்து)", "🔧 이동 시뮬레이터 (거리 조절)", "🔧 จำลองการเดินทาง (ลองเลื่อนระยะทาง)", "🔧 Simulador de viaje (prueba a deslizar la distancia)"),
    "ui_zen": ("🌿 Zen Mode", "🌿 ஜென் பயன்முறை", "🌿 젠 모드", "🌿 โหมดเซน", "🌿 Modo Zen"),
    "ui_pro": ("🎛️ Pro Studio", "🎛️ ப்ரோ ஸ்டுடியோ", "🎛️ 프로 스튜디오", "🎛️ โปรสตูดิโอ", "🎛️ Pro Studio"),
    "zen_relax": ("Relax & Unwind", "நிதானமாக & தளர்வாக", "휴식 & 이완", "ผ่อนคลาย & คลายเครียด", "Relájate y desconecta"),
    "zen_focus": ("Deep Focus", "ஆழமான கவனம்", "깊은 집중", "สมาธิลึก", "Enfoque profundo"),
    "zen_sleep": ("Sleep Preparation", "உறக்கத் தயாரிப்பு", "수면 준비", "เตรียมตัวนอน", "Preparación para dormir"),
    "zen_away": ("Away Mode", "வெளியே பயன்முறை", "외출 모드", "โหมดออกไปข้างนอก", "Modo Ausente"),
    "zen_home": ("I'm Home Now", "நான் இப்போது வீட்டில்", "지금 집에 있음", "ฉันถึงบ้านแล้ว", "Ya estoy en casa"),
    "zen_quick": ("One touch comfort", "ஒரு தொடுதலில் வசதி", "원터치 편안함", "สะดวกสบายหนึ่งสัมผัส", "Comodidad con un toque"),
    "zen_comfort": ("Comfort {c}°C", "சுகமான நிலை {c}°C", "쾌적 {c}°C", "สบาย {c}°C", "Confort {c}°C"),
    "zen_lights_off": ("Lights off", "விளக்குகள் அணைக்கப்பட்டுள்ளன", "조명 꺼짐", "ไฟปิด", "Luces apagadas"),
    "zen_auto": ("Let AuraSync adjust things for me (wearable)", "AuraSync எனக்காக விஷயங்களைச் சரிசெய்யட்டும் (அணிகலன்)", "AuraSync가 조정하게 하기 (웨어러블)", "ให้ AuraSync ปรับให้ (อุปกรณ์สวมใส่)", "Deja que AuraSync ajuste por mí (wearable)"),
    "zen_well": ("💚 You seem {s}. AuraSync keeps the comfort adjusted for you.", "💚 நீங்கள் {s} ஆகத் தெரிகிறது. AuraSync உங்களுக்கான வசதியைச் சரிசெய்கிறது.", "💚 당신은 {s} 상태입니다. AuraSync가 쾌적함을 조정합니다.", "💚 คุณดู {s} AuraSync ปรับความสบายให้คุณ", "💚 Pareces {s}. AuraSync ajusta el confort por ti."),
    "zen_hidden": ("Technical details are hidden in Zen Mode. Switch to Pro Studio for graphs, mixers and logs.", "ஜென் பயன்முறையில் தொழில்நுட்ப விவரங்கள் மறைக்கப்பட்டுள்ளன. வரைபடங்கள், மிக்சர்கள் மற்றும் பதிவுகளுக்கு ப்ரோ ஸ்டுடியோவுக்கு மாறவும்.", "젠 모드에서는 기술 세부정보가 숨겨집니다. 그래프, 믹서, 로그는 프로 스튜디오에서 확인하세요.", "รายละเอียดทางเทคนิคซ่อนอยู่ในโหมดเซน สลับไปโปรสตูดิโอสำหรับกราฟ มิกเซอร์ และบันทึก", "Los detalles técnicos están ocultos en Modo Zen. Cambia a Pro Studio para gráficos, mezcladores y registros."),
    "watch_title": ("⌚ Lock Screen · Live Activity", "⌚ பூட்டுத் திரை · நேரடி செயல்பாடு", "⌚ 잠금 화면 · 실시간 활동", "⌚ หน้าจอล็อก · กิจกรรมสด", "⌚ Pantalla de bloqueo · Actividad en vivo"),
    "watch_cancel": ("❌ Cancel Arrival Pre-Conditioning", "❌ வருகை முன்-சீரமைப்பை ரத்துசெய்", "❌ 도착 사전 조절 취소", "❌ ยกเลิกการปรับสภาพล่วงหน้าการมาถึง", "❌ Cancelar preacondicionamiento de llegada"),
    "watch_home": ("🏠 At home", "🏠 வீட்டில்", "🏠 집", "🏠 ที่บ้าน", "🏠 En casa"),
    "watch_standby": ("Standing by", "காத்திருக்கிறது", "대기 중", "สแตนด์บาย", "En espera"),
    "watch_preheat": ("♨️ Geyser Pre-heating ({v}°C)", "♨️ கீசர் முன்-சூடாக்கம் ({v}°C)", "♨️ 온수기 예열 ({v}°C)", "♨️ อุ่นเครื่องทำน้ำอุ่น ({v}°C)", "♨️ Precalentando calentador ({v}°C)"),
    "watch_geyser_off": ("♨️ Geyser off", "♨️ கீசர் அணைக்கப்பட்டது", "♨️ 온수기 꺼짐", "♨️ เครื่องทำน้ำอุ่นปิด", "♨️ Calentador apagado"),
    "watch_ac": ("❄️ AC {v}°C", "❄️ ஏசி {v}°C", "❄️ 에어컨 {v}°C", "❄️ แอร์ {v}°C", "❄️ A/C {v}°C"),
    "watch_ac_off": ("❄️ AC off", "❄️ ஏசி அணைக்கப்பட்டது", "❄️ 에어컨 꺼짐", "❄️ แอร์ปิด", "❄️ A/C apagado"),
    "watch_eta": ("🚗 {m} mins to Home", "🚗 வீட்டிற்கு {m} நிமிடங்கள்", "🚗 집까지 {m}분", "🚗 อีก {m} นาทีถึงบ้าน", "🚗 {m} min a casa"),
    "dial_title": ("🔘 Smart Rotary Dial", "🔘 ஸ்மார்ட் ரோட்டரி டயல்", "🔘 스마트 로터리 다이얼", "🔘 สมาร์ทโรตารีไดอัล", "🔘 Dial Giratorio Inteligente"),
    "dial_tap": ("🔘 Dial Tap", "🔘 டயல் தட்டு", "🔘 다이얼 탭", "🔘 แตะไดอัล", "🔘 Tocar dial"),
    "dial_cw": ("🔄 Turn ↻ (brighter · +1°C)", "🔄 திருப்பு ↻ (பிரகாசமான · +1°C)", "🔄 회전 ↻ (밝게 · +1°C)", "🔄 หมุน ↻ (สว่างขึ้น · +1°C)", "🔄 Girar ↻ (más brillo · +1°C)"),
    "dial_ccw": ("🔄 Turn ↺ (dimmer · −1°C)", "🔄 திருப்பு ↺ (மங்கலான · −1°C)", "🔄 회전 ↺ (어둡게 · −1°C)", "🔄 หมุน ↺ (หรี่ลง · −1°C)", "🔄 Girar ↺ (más tenue · −1°C)"),
    "dial_hint": ("Tap = next atmosphere for this room · Turn = brightness and AC target.", "தட்டு = இந்த அறைக்கான அடுத்த சூழல் · திருப்பு = பிரகாசம் மற்றும் ஏசி இலக்கு.", "탭 = 이 방의 다음 분위기 · 회전 = 밝기 및 에어컨 목표.", "แตะ = บรรยากาศถัดไปของห้องนี้ · หมุน = ความสว่างและเป้าหมายแอร์", "Tocar = siguiente ambiente · Girar = brillo y objetivo de A/C."),
    "dial_scope": ("Dial controls", "டயல் கட்டுப்பாடுகள்", "다이얼 제어", "การควบคุมไดอัล", "Controles del dial"),
    "dial_lights": ("Lights", "விளக்குகள்", "조명", "ไฟ", "Luces"),
    "dial_climate": ("Climate", "காலநிலை", "기후", "สภาพอากาศ", "Clima"),
    "dial_both": ("Both", "இரண்டும்", "둘 다", "ทั้งสอง", "Ambos"),
    "voice_title": ("🎙️ Just tell AuraSync", "🎙️ AuraSync-ஐ சொல்லுங்கள்", "🎙️ AuraSync에게 말하세요", "🎙️ บอก AuraSync", "🎙️ Dile a AuraSync"),
    "voice_ph": ("Try: I'm tired · Starting work · Family movie time", "முயற்சி: நான் சோர்வாக இருக்கிறேன் · வேலை தொடங்குகிறது · குடும்ப திரைப்பட நேரம்", "시도: 피곤해 · 작업 시작 · 가족 영화 시간", "ลอง: ฉันเหนื่อย · เริ่มงาน · เวลาหนังครอบครัว", "Prueba: Estoy cansado · Empiezo a trabajar · Cine familiar"),
    "voice_send": ("Send", "அனுப்பு", "보내기", "ส่ง", "Enviar"),
    "voice_tired": ("I'm tired", "நான் சோர்வாக இருக்கிறேன்", "피곤해", "ฉันเหนื่อย", "Estoy cansado"),
    "voice_work": ("Starting work", "வேலை தொடங்குகிறது", "작업 시작", "เริ่มงาน", "Empiezo a trabajar"),
    "voice_movie": ("Family movie time", "குடும்ப திரைப்பட நேரம்", "가족 영화 시간", "เวลาหนังครอบครัว", "Cine familiar"),
    "voice_unknown": ("I didn't catch that. Try \"I'm tired\", \"Starting work\" or \"Family movie time\".", "புரியவில்லை. \"நான் சோர்வாக இருக்கிறேன்\", \"வேலை தொடங்குகிறது\" அல்லது \"குடும்ப திரைப்பட நேரம்\" என்று முயற்சிக்கவும்.", "이해하지 못했습니다. \"피곤해\", \"작업 시작\" 또는 \"가족 영화 시간\"을 시도하세요.", "ไม่เข้าใจ ลอง \"ฉันเหนื่อย\", \"เริ่มงาน\" หรือ \"เวลาหนังครอบครัว\"", "No lo entendí. Prueba \"Estoy cansado\", \"Empiezo a trabajar\" o \"Cine familiar\"."),
    "guest_toggle": ("Guest Mode", "விருந்தினர் பயன்முறை", "게스트 모드", "โหมดแขก", "Modo Invitado"),
    "guest_hint": ("ON: automatic shutdowns and wearable changes pause; the home stays welcoming for visitors.", "ON: தானியங்கி அணைப்புகள் மற்றும் அணிகலன் மாற்றங்கள் இடைநிறுத்தப்படும்; வீடு வருகையாளர்களுக்கு வரவேற்பாக இருக்கும்.", "ON: 자동 종료 및 웨어러블 변경이 일시중지됩니다. 집은 방문객을 환영합니다.", "ON: การปิดอัตโนมัติและการเปลี่ยนแปลงจากอุปกรณ์สวมใส่หยุดชั่วคราว", "ON: las desconexiones automáticas y cambios del wearable se pausan; la casa sigue acogedora."),
    "guest_on": ("Guest Mode is ON: the home keeps a welcoming, steady atmosphere.", "விருந்தினர் பயன்முறை ON: வீடு வரவேற்பான நிலையான சூழலை வைத்திருக்கிறது.", "게스트 모드 ON: 집이 환영하는 안정된 분위기를 유지합니다.", "โหมดแขก ON: บ้านรักษาบรรยากาศที่ต้อนรับ", "Modo Invitado ON: la casa mantiene un ambiente acogedor y estable."),
    "occ_label": ("Who is in this shared room?", "இந்த பகிரப்பட்ட அறையில் யார் இருக்கிறார்கள்?", "이 공유 방에 누가 있나요?", "ใครอยู่ในห้องร่วมนี้?", "¿Quién está en esta habitación compartida?"),
    "occ_1": ("1 person", "1 நபர்", "1명", "1 คน", "1 persona"),
    "occ_2": ("2+ family members", "2+ குடும்ப உறுப்பினர்கள்", "가족 2명 이상", "สมาชิกครอบครัว 2 คนขึ้นไป", "2+ miembros de la familia"),
    "occ_lock": ("Family lock: one person's body signals cannot change the shared room. Atmosphere is held at Neutral Family Ambience (warm 24°C).", "குடும்பப் பூட்டு: ஒரு நபரின் உடல் சமிக்ஞைகள் பகிரப்பட்ட அறையை மாற்ற முடியாது. சூழல் நடுநிலை குடும்ப சூழலில் (சூடான 24°C) வைக்கப்படுகிறது.", "가족 잠금: 한 사람의 신체 신호가 공유 방을 바꿀 수 없습니다. 중립 가족 분위기(따뜻한 24°C)로 유지됩니다.", "ล็อกครอบครัว: สัญญาณร่างกายของคนหนึ่งไม่สามารถเปลี่ยนห้องร่วมได้ บรรยากาศคงอยู่ที่ความเป็นกลางครอบครัว (24°C)", "Bloqueo familiar: las señales corporales de una persona no cambian la habitación compartida. Ambiente neutral (24°C)."),
    "persona_personal": ("Personal sanctuary", "தனிப்பட்ட புகலிடம்", "개인 성소", "สถานที่ส่วนตัว", "Santuario personal"),
    "persona_shared": ("Shared family zone", "பகிரப்பட்ட குடும்ப மண்டலம்", "공유 가족 구역", "โซนครอบครัวร่วม", "Zona familiar compartida"),
    "persona_pick": ("Room type", "அறை வகை", "방 유형", "ประเภทห้อง", "Tipo de habitación"),
    "matter_btn": ("📷 Scan Matter QR / Enter Pairing Code", "📷 Matter QR ஐ ஸ்கேன் செய் / இணைப்புக் குறியீட்டை உள்ளிடு", "📷 Matter QR 스캔 / 페어링 코드 입력", "📷 สแกน Matter QR / ใส่รหัสจับคู่", "📷 Escanear QR Matter / Introducir código"),
    "matter_title": ("Plug & Play setup (Matter 1.3)", "பிளக் & பிளே அமைப்பு (Matter 1.3)", "플러그 앤 플레이 설정 (Matter 1.3)", "ตั้งค่า Plug & Play (Matter 1.3)", "Configuración Plug & Play (Matter 1.3)"),
    "matter_help": ("Scan the QR on the device, or type the code printed under it (for example MT:Y.K10000000000).", "சாதனத்தின் QR ஐ ஸ்கேன் செய்யவும் அல்லது அதன் கீழே அச்சிடப்பட்ட குறியீட்டை உள்ளிடவும் (எடுத்துக்காட்டாக MT:Y.K10000000000).", "기기의 QR을 스캔하거나 아래에 인쇄된 코드를 입력하세요 (예: MT:Y.K10000000000).", "สแกน QR บนอุปกรณ์ หรือพิมพ์รหัสที่พิมพ์ด้านล่าง (เช่น MT:Y.K10000000000)", "Escanea el QR del dispositivo o escribe el código impreso debajo (ejemplo MT:Y.K10000000000)."),
    "matter_code": ("Pairing code", "இணைப்புக் குறியீடு", "페어링 코드", "รหัสจับคู่", "Código de emparejamiento"),
    "matter_room": ("Place it in", "இங்கே வைக்கவும்", "위치할 방", "วางไว้ใน", "Colocarlo en"),
    "matter_pair": ("🔗 Pair now", "🔗 இப்போது இணை", "🔗 지금 페어링", "🔗 จับคู่เลย", "🔗 Emparejar ahora"),
    "matter_demo": ("⚡ Auto-Pair Demo Device in 5s", "⚡ டெமோ சாதனத்தை 5 வினாடிகளில் தானாக இணை", "⚡ 5초 만에 데모 기기 자동 페어링", "⚡ จับคู่อุปกรณ์สาธิตอัตโนมัติใน 5 วินาที", "⚡ Emparejar dispositivo demo en 5 s"),
    "matter_bad": ("That code does not look right. Use a Matter code like MT:Y.K10000000000 or an 11-digit code.", "அந்தக் குறியீடு சரியாகத் தெரியவில்லை. MT:Y.K10000000000 போன்ற Matter குறியீட்டைப் பயன்படுத்தவும் அல்லது 11 இலக்கக் குறியீட்டைப் பயன்படுத்தவும்.", "코드가 올바르지 않습니다. MT:Y.K10000000000 같은 Matter 코드나 11자리 코드를 사용하세요.", "รหัสไม่ถูกต้อง ใช้รหัส Matter เช่น MT:Y.K10000000000 หรือรหัส 11 หลัก", "Ese código no parece correcto. Usa un código Matter como MT:Y.K10000000000 o un código de 11 dígitos."),
    "matter_ok": ("Connected: {n} in {r}", "இணைக்கப்பட்டது: {n} இல் {r}", "연결됨: {n} ({r})", "เชื่อมต่อแล้ว: {n} ใน {r}", "Conectado: {n} en {r}"),
    "matter_s1": ("Looking for the device nearby…", "அருகிலுள்ள சாதனத்தைத் தேடுகிறது…", "근처 기기를 찾는 중…", "กำลังค้นหาอุปกรณ์ใกล้เคียง…", "Buscando el dispositivo cercano…"),
    "matter_s2": ("Securing the connection…", "இணைப்பைப் பாதுகாக்கிறது…", "연결 보안 중…", "กำลังรักษาความปลอดภัยการเชื่อมต่อ…", "Asegurando la conexión…"),
    "matter_s3": ("Joining your home network (Thread / Wi-Fi)…", "உங்கள் வீட்டு நெட்வொர்க்கில் சேருகிறது (Thread / Wi-Fi)…", "홈 네트워크 참여 중 (Thread / Wi-Fi)…", "กำลังเข้าร่วมเครือข่ายบ้าน (Thread / Wi-Fi)…", "Uniéndose a tu red doméstica (Thread / Wi-Fi)…"),
    "matter_s4": ("Identifying the hardware…", "வன்பொருளைக் கண்டறிகிறது…", "하드웨어 식별 중…", "กำลังระบุฮาร์ดแวร์…", "Identificando el hardware…"),
    "matter_s5": ("Binding it to the room…", "அதை அறையுடன் இணைக்கிறது…", "방에 바인딩 중…", "กำลังผูกกับห้อง…", "Vinculándolo a la habitación…"),
    "adv_conn": ("⚙ Advanced manual connection (IP / token, legacy)", "⚙ மேம்பட்ட கைமுறை இணைப்பு (IP / டோக்கன், லெகசி)", "⚙ 고급 수동 연결 (IP / 토큰, 레거시)", "⚙ การเชื่อมต่อด้วยตนเองขั้นสูง (IP / โทเค็น, ดั้งเดิม)", "⚙ Conexión manual avanzada (IP / token, heredado)"),
    "simple_dev": ("Devices", "சாதனங்கள்", "기기", "อุปกรณ์", "Dispositivos"),
    "pro_only": ("Pro Studio", "ப்ரோ ஸ்டுடியோ", "프로 스튜디오", "โปรสตูดิโอ", "Pro Studio"),
    "i18n_wait": ("🌐 Translating AuraSync into your language (first time only)…", "🌐 AuraSync ஐ உங்கள் மொழிக்கு மொழிபெயர்க்கிறது (முதல் முறை மட்டும்)…", "🌐 AuraSync를 귀하의 언어로 번역 중 (첫 번째만)…", "🌐 กำลังแปล AuraSync เป็นภาษาของคุณ (ครั้งแรกเท่านั้น)…", "🌐 Traduciendo AuraSync a tu idioma (solo la primera vez)…"),
    "i18n_missing": ("To show every word in your language please run: pip install deep-translator", "உங்கள் மொழியில் ஒவ்வொரு வார்த்தையையும் காட்ட தயவுசெய்து இயக்கவும்: pip install deep-translator", "모든 단어를 귀하의 언어로 표시하려면 실행하세요: pip install deep-translator", "เพื่อแสดงทุกคำในภาษาของคุณโปรดรัน: pip install deep-translator", "Para mostrar cada palabra en tu idioma ejecuta: pip install deep-translator"),
    "chat_you": ("You", "நீங்கள்", "당신", "คุณ", "Tú"),
    "geo_active": ("Pre-conditioning active", "முன்-சீரமைப்பு செயலில்", "사전 조절 활성", "การปรับสภาพล่วงหน้าทำงาน", "Preacondicionamiento activo"),
    "geo_standby_zone": ("Standby", "தெரியாமல்", "대기", "สแตนด์บาย", "En espera"),
    "chat_offer_sleep": ("Would you like me to dim the lights and switch the home to Wind-Down Sleep?", "விளக்குகளை மங்கலாக்கி வீட்டை விண்ட்-டவுன் தூக்கத்திற்கு மாற்றவா?", "조명을 어둡게 하고 집을 휴식 수면으로 전환할까요?", "ต้องการให้ฉันหรี่ไฟและเปลี่ยนบ้านเป็นโหมดพักผ่อนนอนหลับหรือไม่?", "¿Quieres que atenúe las luces y ponga la casa en modo Sueño?"),
    "chat_offer_calm": ("Want me to soften the lights and play calm sounds while we talk?", "நாம் பேசும்போது விளக்குகளை மென்மையாக்கி அமைதியான ஒலிகளை இயக்கவா?", "대화하는 동안 조명을 부드럽게 하고 차분한 소리를 재생할까요?", "ต้องการให้ฉันลดแสงและเล่นเสียงสงบขณะเราคุยกันหรือไม่?", "¿Quieres que suavice las luces y ponga sonidos relajantes mientras hablamos?"),
    "chat_done_sleep": ("Done. The lights are low and the home is in Wind-Down Sleep. Let your shoulders drop.", "முடிந்தது. விளக்குகள் குறைவாக உள்ளன, வீடு விண்ட்-டவுன் தூக்கத்தில் உள்ளது. தோள்களைத் தளர்த்துங்கள்.", "완료. 조명이 낮고 집이 휴식 수면에 있습니다. 어깨를 내려놓으세요.", "เรียบร้อย ไฟสลัวและบ้านอยู่ในโหมดพักผ่อนนอนหลับ ผ่อนคลายไหล่", "Hecho. Las luces están bajas y la casa en modo Sueño. Relaja los hombros."),
    "chat_done_calm": ("Done. Soft light and calm sound are on. Breathe out slowly with me.", "முடிந்தது. மென்மையான ஒளி மற்றும் அமைதியான ஒலி இயக்கப்பட்டுள்ளன. என்னுடன் மெதுவாக மூச்சை வெளியேற்றுங்கள்.", "완료. 부드러운 조명과 차분한 소리가 켜졌습니다. 천천히 숨을 내쉬세요.", "เรียบร้อย ไฟนุ่มและเสียงสงบเปิดแล้ว หายใจออกช้า ๆ กับฉัน", "Hecho. Luz suave y sonido relajante activos. Respira lento conmigo."),
    "chat_declined": ("Okay, no pressure. I'm still here.", "சரி, அழுத்தம் இல்லை. நான் இன்னும் இங்கே இருக்கிறேன்.", "알겠습니다. 부담 갖지 마세요. 저는 여기 있습니다.", "โอเค ไม่กดดัน ฉันยังอยู่ตรงนี้", "Vale, sin presión. Sigo aquí."),
}
for _k, _v in T.items():
    if not isinstance(_v, tuple):
        T[_k] = (_v,)


CORE_KEYS = ("lang", "nav", "p1", "p2", "p3", "p4", "p5", "mode_manual", "mode_auto", "play", "stop", "welcome",
             "edit", "nudge", "plan", "do", "dont", "caution", "deep", "chat", "chat_ph", "save")
CI = {k: i for i, k in enumerate(CORE_KEYS)}

TX = {
    "Hindi (हिन्दी)": ("भाषा", "मेनू", "लाइव डैशबोर्ड", "मूड और सेटिंग्स", "अंतर्मन की आवाज़ और मार्गदर्शक", "डिवाइस फ्लीट", "सिस्टम सेटिंग्स", "मैनुअल मोड", "ऑटो मोड (वियरेबल बायोमेट्रिक सिंक)", "चलाएँ", "रोकें", "✨ फिर से स्वागत है, {n}!", "✏️ जन्म विवरण संपादित करें", "💛 हे {n}! एक प्यारा सा संकेत: एक धीमी गहरी साँस लीजिए। आज के लिए आपके करने योग्य, न करने योग्य और सावधानी वाले सुझाव तैयार हैं।", "आज की रणनीतिक कार्य योजना", "✅ क्या करें", "❌ क्या न करें", "⚠️ सावधानी", "📖 गहन व्याख्या", "अपने दिव्य कम्पास से बात करें", "अपने आंतरिक कम्पास से पूछें", "सहेजें"),
    "Arabic (العربية)": ("اللغة", "القائمة", "لوحة التحكم المباشرة", "الأجواء والإعدادات", "الصوت الداخلي والدليل", "أسطول الأجهزة", "إعدادات النظام", "الوضع اليدوي", "الوضع التلقائي (مزامنة المؤشرات الحيوية)", "تشغيل", "إيقاف", "✨ مرحبًا بعودتك، {n}!", "✏️ تعديل بيانات الميلاد", "💛 مرحبًا {n}! تذكير لطيف: خذ نفسًا عميقًا وبطيئًا. نصائح اليوم (افعل، لا تفعل، احذر) جاهزة لتبقى متزنًا.", "خطة العمل الاستراتيجية لليوم", "✅ افعل", "❌ لا تفعل", "⚠️ تنبيه", "📖 شرح معمّق", "تحدّث إلى بوصلتك الإلهية", "اسأل بوصلتك الداخلية", "حفظ"),
    "Japanese (日本語)": ("言語", "メニュー", "ライブダッシュボード", "ムードと設定", "内なる声とガイド", "デバイス一覧", "システム設定", "手動モード", "自動モード(ウェアラブル生体同期)", "再生", "停止", "✨ おかえりなさい、{n}さん!", "✏️ 出生情報を編集", "💛 {n}さん、やさしいお知らせです。ゆっくり深呼吸をひとつ。今日の「やるべきこと・避けること・注意点」を用意しました。", "今日の戦略アクションプラン", "✅ やるべきこと", "❌ 避けること", "⚠️ 注意", "📖 詳しい解説", "神聖なコンパスに話しかける", "内なるコンパスに聞いてみましょう", "保存"),
    "Chinese (中文)": ("语言", "导航", "实时仪表盘", "情境与设置", "内心声音与指引", "设备列表", "系统设置", "手动模式", "自动模式(可穿戴生物数据同步)", "播放", "停止", "✨ 欢迎回来，{n}！", "✏️ 编辑出生信息", "💛 嗨，{n}！温馨提醒：请缓慢深呼吸一次。今日的宜做、不宜做与注意事项已备好，助你保持平衡。", "今日策略行动计划", "✅ 宜做", "❌ 不宜做", "⚠️ 注意", "📖 深度解读", "与你的神圣罗盘对话", "向你的内在罗盘提问", "保存"),
    "French (Français)": ("Langue", "Navigation", "Tableau de bord en direct", "Ambiances et réglages", "Voix intérieure et guide", "Parc d'appareils", "Paramètres système", "Mode manuel", "Mode auto (synchro biométrique)", "Lecture", "Arrêt", "✨ Bon retour, {n} !", "✏️ Modifier les données de naissance", "💛 Coucou {n} ! Petit rappel amical : prenez une grande respiration lente. Vos À faire, À éviter et Précautions du jour sont prêts.", "Plan d'action stratégique du jour", "✅ À faire", "❌ À éviter", "⚠️ Prudence", "📖 Explication approfondie", "Parlez à votre Boussole Divine", "Demandez à votre Boussole Intérieure", "Enregistrer"),
    "German (Deutsch)": ("Sprache", "Navigation", "Live-Dashboard", "Stimmungen & Einstellungen", "Innere Stimme & Leitfaden", "Geräteflotte", "Systemeinstellungen", "Manueller Modus", "Automatikmodus (Wearable-Biosync)", "Abspielen", "Stopp", "✨ Willkommen zurück, {n}!", "✏️ Geburtsdaten bearbeiten", "💛 Hallo {n}! Ein freundlicher Hinweis: Atme einmal langsam und tief durch. Deine Tipps für heute (Tun, Lassen, Vorsicht) sind bereit.", "Strategischer Aktionsplan für heute", "✅ Tun", "❌ Lassen", "⚠️ Vorsicht", "📖 Ausführliche Erklärung", "Sprich mit deinem Göttlichen Kompass", "Frage deinen Inneren Kompass", "Speichern"),
    "Italian (Italiano)": ("Lingua", "Navigazione", "Dashboard in tempo reale", "Atmosfere e impostazioni", "Voce interiore e guida", "Flotta dispositivi", "Impostazioni di sistema", "Modalità manuale", "Modalità automatica (sincronizzazione biometrica)", "Riproduci", "Ferma", "✨ Bentornato, {n}!", "✏️ Modifica dati di nascita", "💛 Ciao {n}! Un promemoria gentile: fai un respiro lento e profondo. I tuoi Da fare, Da evitare e Cautela di oggi sono pronti.", "Piano d'azione strategico di oggi", "✅ Da fare", "❌ Da evitare", "⚠️ Cautela", "📖 Spiegazione approfondita", "Parla con la tua Bussola Divina", "Chiedi alla tua Bussola Interiore", "Salva"),
    "Portuguese (Português)": ("Idioma", "Navegação", "Painel ao Vivo", "Ambientes e Ajustes", "Voz Interior e Guia", "Frota de Dispositivos", "Configurações do Sistema", "Modo Manual", "Modo Automático (sincronização biométrica)", "Reproduzir", "Parar", "✨ Bem-vindo de volta, {n}!", "✏️ Editar dados de nascimento", "💛 Olá {n}! Um lembrete gentil: respire fundo e devagar. Seus Fazer, Evitar e Cuidado de hoje estão prontos.", "Plano de Ação Estratégico de Hoje", "✅ Fazer", "❌ Evitar", "⚠️ Cuidado", "📖 Explicação Detalhada", "Fale com sua Bússola Divina", "Pergunte à sua Bússola Interior", "Salvar"),
    "Russian (Русский)": ("Язык", "Навигация", "Панель в реальном времени", "Настроения и настройки", "Внутренний голос и гид", "Парк устройств", "Системные настройки", "Ручной режим", "Авто-режим (синхронизация с носимым устройством)", "Играть", "Стоп", "✨ С возвращением, {n}!", "✏️ Изменить данные рождения", "💛 Привет, {n}! Дружеское напоминание: сделайте один медленный глубокий вдох. Ваши «Делать», «Не делать» и «Осторожно» на сегодня готовы.", "Стратегический план действий на сегодня", "✅ Делать", "❌ Не делать", "⚠️ Осторожно", "📖 Подробное объяснение", "Поговорите со своим Божественным Компасом", "Спросите свой Внутренний Компас", "Сохранить"),
    "Turkish (Türkçe)": ("Dil", "Gezinme", "Canlı Panel", "Ruh Halleri ve Ayarlar", "İç Ses ve Rehber", "Cihaz Filosu", "Sistem Ayarları", "Manuel Mod", "Otomatik Mod (Giyilebilir Biyometrik Senkron)", "Oynat", "Durdur", "✨ Tekrar hoş geldin, {n}!", "✏️ Doğum bilgilerini düzenle", "💛 Merhaba {n}! Nazik bir hatırlatma: yavaşça derin bir nefes al. Bugünün Yapılacaklar, Yapılmayacaklar ve Dikkat önerileri hazır.", "Bugünün Stratejik Eylem Planı", "✅ Yapılacaklar", "❌ Yapılmayacaklar", "⚠️ Dikkat", "📖 Ayrıntılı Açıklama", "İlahi Pusulanla Konuş", "İç Pusulana Sor", "Kaydet"),
    "Dutch (Nederlands)": ("Taal", "Navigatie", "Live Dashboard", "Sferen & Instellingen", "Innerlijke Stem & Gids", "Apparatenpark", "Systeeminstellingen", "Handmatige modus", "Automodus (wearable-biosync)", "Afspelen", "Stop", "✨ Welkom terug, {n}!", "✏️ Geboortegegevens bewerken", "💛 Hoi {n}! Een vriendelijke herinnering: adem eens rustig en diep in. Je Do's, Don'ts en Let op voor vandaag staan klaar.", "Strategisch actieplan van vandaag", "✅ Doen", "❌ Niet doen", "⚠️ Let op", "📖 Uitgebreide uitleg", "Spreek met je Goddelijke Kompas", "Vraag het je Innerlijke Kompas", "Opslaan"),
    "Polish (Polski)": ("Język", "Nawigacja", "Panel na żywo", "Nastroje i ustawienia", "Głos wewnętrzny i przewodnik", "Flota urządzeń", "Ustawienia systemu", "Tryb ręczny", "Tryb automatyczny (synchronizacja biometryczna)", "Odtwórz", "Zatrzymaj", "✨ Witaj ponownie, {n}!", "✏️ Edytuj dane urodzenia", "💛 Cześć {n}! Przyjazne przypomnienie: weź jeden powolny, głęboki oddech. Twoje Rób, Nie rób i Uwaga na dziś są gotowe.", "Strategiczny plan działania na dziś", "✅ Rób", "❌ Nie rób", "⚠️ Uwaga", "📖 Szczegółowe wyjaśnienie", "Porozmawiaj ze swoim Boskim Kompasem", "Zapytaj swój Wewnętrzny Kompas", "Zapisz"),
    "Swedish (Svenska)": ("Språk", "Navigering", "Liveöversikt", "Stämningar & inställningar", "Inre röst & guide", "Enhetsflotta", "Systeminställningar", "Manuellt läge", "Autoläge (biometrisk synk)", "Spela", "Stopp", "✨ Välkommen tillbaka, {n}!", "✏️ Redigera födelseuppgifter", "💛 Hej {n}! En vänlig påminnelse: ta ett långsamt, djupt andetag. Dina Gör, Låt bli och Se upp för idag är redo.", "Dagens strategiska handlingsplan", "✅ Gör", "❌ Låt bli", "⚠️ Se upp", "📖 Fördjupad förklaring", "Tala med din Gudomliga Kompass", "Fråga din Inre Kompass", "Spara"),
    "Greek (Ελληνικά)": ("Γλώσσα", "Πλοήγηση", "Ζωντανός πίνακας", "Διαθέσεις & ρυθμίσεις", "Εσωτερική φωνή & οδηγός", "Στόλος συσκευών", "Ρυθμίσεις συστήματος", "Χειροκίνητη λειτουργία", "Αυτόματη λειτουργία (βιομετρικός συγχρονισμός)", "Αναπαραγωγή", "Διακοπή", "✨ Καλώς ήρθες ξανά, {n}!", "✏️ Επεξεργασία στοιχείων γέννησης", "💛 Γεια σου {n}! Μια φιλική υπενθύμιση: πάρε μια αργή, βαθιά ανάσα. Τα «Να κάνεις», «Να μην κάνεις» και «Προσοχή» της ημέρας είναι έτοιμα.", "Στρατηγικό πλάνο δράσης σήμερα", "✅ Να κάνεις", "❌ Να μην κάνεις", "⚠️ Προσοχή", "📖 Αναλυτική εξήγηση", "Μίλησε στη Θεϊκή σου Πυξίδα", "Ρώτησε την Εσωτερική σου Πυξίδα", "Αποθήκευση"),
    "Indonesian (Bahasa Indonesia)": ("Bahasa", "Navigasi", "Dasbor Langsung", "Suasana & Pengaturan", "Suara Batin & Panduan", "Armada Perangkat", "Pengaturan Sistem", "Mode Manual", "Mode Otomatis (Sinkron Biometrik Wearable)", "Putar", "Berhenti", "✨ Selamat datang kembali, {n}!", "✏️ Ubah data kelahiran", "💛 Hai {n}! Pengingat ramah: tarik napas dalam dan perlahan. Anjuran Lakukan, Hindari, dan Waspada hari ini sudah siap.", "Rencana Aksi Strategis Hari Ini", "✅ Lakukan", "❌ Hindari", "⚠️ Waspada", "📖 Penjelasan Mendalam", "Berbicaralah dengan Kompas Ilahi Anda", "Tanyakan pada Kompas Batin Anda", "Simpan"),
    "Vietnamese (Tiếng Việt)": ("Ngôn ngữ", "Điều hướng", "Bảng điều khiển trực tiếp", "Tâm trạng & Cài đặt", "Tiếng nói nội tâm & Hướng dẫn", "Danh sách thiết bị", "Cài đặt hệ thống", "Chế độ thủ công", "Chế độ tự động (đồng bộ sinh trắc từ thiết bị đeo)", "Phát", "Dừng", "✨ Chào mừng trở lại, {n}!", "✏️ Chỉnh sửa thông tin ngày sinh", "💛 Chào {n}! Một lời nhắc nhẹ nhàng: hãy hít một hơi thật sâu và chậm. Việc nên làm, không nên làm và lưu ý hôm nay đã sẵn sàng.", "Kế hoạch hành động chiến lược hôm nay", "✅ Nên làm", "❌ Không nên làm", "⚠️ Lưu ý", "📖 Giải thích chuyên sâu", "Trò chuyện với La bàn Thiêng liêng của bạn", "Hỏi La bàn Nội tâm của bạn", "Lưu"),
    "Malay (Bahasa Melayu)": ("Bahasa", "Navigasi", "Papan Pemuka Langsung", "Suasana & Tetapan", "Suara Dalaman & Panduan", "Armada Peranti", "Tetapan Sistem", "Mod Manual", "Mod Auto (Segerak Biometrik Wearable)", "Main", "Henti", "✨ Selamat kembali, {n}!", "✏️ Sunting butiran kelahiran", "💛 Hai {n}! Peringatan mesra: tarik nafas dalam-dalam dengan perlahan. Cadangan Buat, Elak dan Berhati-hati hari ini sudah sedia.", "Pelan Tindakan Strategik Hari Ini", "✅ Buat", "❌ Elak", "⚠️ Berhati-hati", "📖 Penjelasan Mendalam", "Bercakap dengan Kompas Ilahi Anda", "Tanya Kompas Dalaman Anda", "Simpan"),
    "Filipino (Tagalog)": ("Wika", "Nabigasyon", "Live Dashboard", "Mga Mood at Setting", "Panloob na Tinig at Gabay", "Mga Device", "Mga Setting ng Sistema", "Manual na Mode", "Auto na Mode (Biometric Sync ng Wearable)", "I-play", "Ihinto", "✨ Welcome back, {n}!", "✏️ I-edit ang Detalye ng Kapanganakan", "💛 Hi {n}! Magiliw na paalala: huminga nang malalim at mabagal. Handa na ang iyong Gawin, Iwasan, at Mag-ingat para ngayong araw.", "Estratehikong Plano ng Aksyon Ngayon", "✅ Gawin", "❌ Iwasan", "⚠️ Mag-ingat", "📖 Malalim na Paliwanag", "Makipag-usap sa Iyong Banal na Kompas", "Magtanong sa Iyong Panloob na Kompas", "I-save"),
}

# Room and mode translation dictionaries
ROOM_NAMES = {
    "Living Lounge": {
        "English": "Living Lounge", "Tamil (தமிழ்)": "லிவிங் லவுன்ஜ்", "Korean (한국어)": "거실 라운지",
        "Thai (Thai)": "เลานจ์นั่งเล่น", "Spanish (Español)": "Salón Lounge", "Hindi (हिन्दी)": "लिविंग लाउंज",
        "Arabic (العربية)": "صالة المعيشة", "Japanese (日本語)": "リビングラウンジ", "Chinese (中文)": "客厅休息区",
        "French (Français)": "Salon", "German (Deutsch)": "Wohnlounge", "Italian (Italiano)": "Salotto",
        "Portuguese (Português)": "Salão de Estar", "Russian (Русский)": "Гостиная", "Turkish (Türkçe)": "Oturma Odası",
        "Dutch (Nederlands)": "Woonkamer", "Polish (Polski)": "Salon", "Swedish (Svenska)": "Vardagsrum",
        "Greek (Ελληνικά)": "Σαλόνι", "Indonesian (Bahasa Indonesia)": "Ruang Santai",
        "Vietnamese (Tiếng Việt)": "Phòng Khách", "Malay (Bahasa Melayu)": "Ruang Tamu", "Filipino (Tagalog)": "Living Lounge"
    },
    "Master Suite": {
        "English": "Master Suite", "Tamil (தமிழ்)": "மாஸ்டர் சூட்", "Korean (한국어)": "마스터 스위트",
        "Thai (Thai)": "ห้องสวีทหลัก", "Spanish (Español)": "Suite Principal", "Hindi (हिन्दी)": "मास्टर सुइट",
        "Arabic (العربية)": "الجناح الرئيسي", "Japanese (日本語)": "マスタースイート", "Chinese (中文)": "主套房",
        "French (Français)": "Suite Parentale", "German (Deutsch)": "Master-Suite", "Italian (Italiano)": "Suite Padronale",
        "Portuguese (Português)": "Suíte Master", "Russian (Русский)": "Главная спальня", "Turkish (Türkçe)": "Ebeveyn Yatak Odası",
        "Dutch (Nederlands)": "Hoofdsuite", "Polish (Polski)": "Główna Sypialnia", "Swedish (Svenska)": "Huvudsvit",
        "Greek (Ελληνικά)": "Κύρια Σουίτα", "Indonesian (Bahasa Indonesia)": "Suite Utama",
        "Vietnamese (Tiếng Việt)": "Phòng Suite Chính", "Malay (Bahasa Melayu)": "Suite Utama", "Filipino (Tagalog)": "Master Suite"
    },
    "En-Suite Bath": {
        "English": "En-Suite Bath", "Tamil (தமிழ்)": "என்சூட் பாத்", "Korean (한국어)": "욕실",
        "Thai (Thai)": "ห้องน้ำในห้องนอน", "Spanish (Español)": "Baño En Suite", "Hindi (हिन्दी)": "अटैच्ड बाथरूम",
        "Arabic (العربية)": "حمام ملحق", "Japanese (日本語)": "バスルーム", "Chinese (中文)": "套房浴室",
        "French (Français)": "Salle de Bain", "German (Deutsch)": "En-Suite-Bad", "Italian (Italiano)": "Bagno Privato",
        "Portuguese (Português)": "Banheiro Suíte", "Russian (Русский)": "Ванная комната", "Turkish (Türkçe)": "Banyo",
        "Dutch (Nederlands)": "En-Suite Bad", "Polish (Polski)": "Łazienka", "Swedish (Svenska)": "Badrum",
        "Greek (Ελληνικά)": "Μπάνιο", "Indonesian (Bahasa Indonesia)": "Kamar Mandi Suite",
        "Vietnamese (Tiếng Việt)": "Phòng Tắm", "Malay (Bahasa Melayu)": "Bilik Mandi", "Filipino (Tagalog)": "En-Suite Bath"
    },
    "Work Studio": {
        "English": "Work Studio", "Tamil (தமிழ்)": "வேலை ஸ்டுடியோ", "Korean (한국어)": "작업실",
        "Thai (Thai)": "สตูดิโอทำงาน", "Spanish (Español)": "Estudio de Trabajo", "Hindi (हिन्दी)": "वर्क स्टूडियो",
        "Arabic (العربية)": "مكتب العمل", "Japanese (日本語)": "ワークスタジオ", "Chinese (中文)": "工作书房",
        "French (Français)": "Studio de Travail", "German (Deutsch)": "Arbeitsstudio", "Italian (Italiano)": "Studio di Lavoro",
        "Portuguese (Português)": "Estúdio de Trabalho", "Russian (Русский)": "Рабочий кабинет", "Turkish (Türkçe)": "Çalışma Stüdyosu",
        "Dutch (Nederlands)": "Werkstudio", "Polish (Polski)": "Studio Pracy", "Swedish (Svenska)": "Arbetsrum",
        "Greek (Ελληνικά)": "Στούντιο Εργασίας", "Indonesian (Bahasa Indonesia)": "Studio Kerja",
        "Vietnamese (Tiếng Việt)": "Phòng Làm Việc", "Malay (Bahasa Melayu)": "Studio Kerja", "Filipino (Tagalog)": "Work Studio"
    },
    "Kitchen": {
        "English": "Kitchen", "Tamil (தமிழ்)": "சமையலறை", "Korean (한국어)": "주방",
        "Thai (Thai)": "ห้องครัว", "Spanish (Español)": "Cocina", "Hindi (हिन्दी)": "रसोई",
        "Arabic (العربية)": "المطبخ", "Japanese (日本語)": "キッチン", "Chinese (中文)": "厨房",
        "French (Français)": "Cuisine", "German (Deutsch)": "Küche", "Italian (Italiano)": "Cucina",
        "Portuguese (Português)": "Cozinha", "Russian (Русский)": "Кухня", "Turkish (Türkçe)": "Mutfak",
        "Dutch (Nederlands)": "Keuken", "Polish (Polski)": "Kuchnia", "Swedish (Svenska)": "Kök",
        "Greek (Ελληνικά)": "Κουζίνα", "Indonesian (Bahasa Indonesia)": "Dapur",
        "Vietnamese (Tiếng Việt)": "Phòng Bếp", "Malay (Bahasa Melayu)": "Dapur", "Filipino (Tagalog)": "Kusina"
    },
    "Reading Room": {
        "English": "Reading Room", "Tamil (தமிழ்)": "படிப்பு அறை", "Korean (한국어)": "독서실",
        "Thai (Thai)": "ห้องอ่านหนังสือ", "Spanish (Español)": "Sala de Lectura", "Hindi (हिन्दी)": "वाचन कक्ष",
        "Arabic (العربية)": "غرفة القراءة", "Japanese (日本語)": "読書室", "Chinese (中文)": "阅读室",
        "French (Français)": "Salle de Lecture", "German (Deutsch)": "Leseraum", "Italian (Italiano)": "Sala Lettura",
        "Portuguese (Português)": "Sala de Leitura", "Russian (Русский)": "Читальня", "Turkish (Türkçe)": "Okuma Odası",
        "Dutch (Nederlands)": "Leeszaal", "Polish (Polski)": "Czytelnia", "Swedish (Svenska)": "Läsrum",
        "Greek (Ελληνικά)": "Αναγνωστήριο", "Indonesian (Bahasa Indonesia)": "Ruang Baca",
        "Vietnamese (Tiếng Việt)": "Phòng Đọc Sách", "Malay (Bahasa Melayu)": "Bilik Bacaan", "Filipino (Tagalog)": "Reading Room"
    },
    "Dining Area": {
        "English": "Dining Area", "Tamil (தமிழ்)": "உணவு அறை", "Korean (한국어)": "식사 공간",
        "Thai (Thai)": "พื้นที่รับประทานอาหาร", "Spanish (Español)": "Comedor", "Hindi (हिन्दी)": "भोजन क्षेत्र",
        "Arabic (العربية)": "منطقة تناول الطعام", "Japanese (日本語)": "ダイニング", "Chinese (中文)": "用餐区",
        "French (Français)": "Salle à Manger", "German (Deutsch)": "Essbereich", "Italian (Italiano)": "Zona Pranzo",
        "Portuguese (Português)": "Área de Jantar", "Russian (Русский)": "Столовая", "Turkish (Türkçe)": "Yemek Alanı",
        "Dutch (Nederlands)": "Eetruimte", "Polish (Polski)": "Jadalnia", "Swedish (Svenska)": "Matsal",
        "Greek (Ελληνικά)": "Τραπεζαρία", "Indonesian (Bahasa Indonesia)": "Area Makan",
        "Vietnamese (Tiếng Việt)": "Khu Vực Ăn", "Malay (Bahasa Melayu)": "Ruang Makan", "Filipino (Tagalog)": "Dining Area"
    },
}

MODE_NAMES = {
    "Relax Evening": {
        "English": "Relax Evening", "Tamil (தமிழ்)": "நிதானமான மாலை", "Korean (한국어)": "편안한 저녁",
        "Thai (Thai)": "เย็นผ่อนคลาย", "Spanish (Español)": "Noche de Relax", "Hindi (हिन्दी)": "आरामदायक शाम",
        "Arabic (العربية)": "أمسية استرخاء", "Japanese (日本語)": "リラックスイブニング", "Chinese (中文)": "放松夜晚",
        "French (Français)": "Soirée Détente", "German (Deutsch)": "Entspannter Abend", "Italian (Italiano)": "Serata Relax",
        "Portuguese (Português)": "Noite Relaxante", "Russian (Русский)": "Спокойный вечер", "Turkish (Türkçe)": "Rahat Akşam",
        "Dutch (Nederlands)": "Ontspannen Avond", "Polish (Polski)": "Relaksujący Wieczór", "Swedish (Svenska)": "Lugn Kväll",
        "Greek (Ελληνικά)": "Χαλαρωτική Βραδιά", "Indonesian (Bahasa Indonesia)": "Malam Santai",
        "Vietnamese (Tiếng Việt)": "Buổi Tối Thư Giãn", "Malay (Bahasa Melayu)": "Malam Santai", "Filipino (Tagalog)": "Relax Evening"
    },
    "Focus": {
        "English": "Focus", "Tamil (தமிழ்)": "கவனம்", "Korean (한국어)": "집중", "Thai (Thai)": "สมาธิ",
        "Spanish (Español)": "Enfoque", "Hindi (हिन्दी)": "एकाग्रता", "Arabic (العربية)": "تركيز",
        "Japanese (日本語)": "フォーカス", "Chinese (中文)": "专注", "French (Français)": "Concentration",
        "German (Deutsch)": "Fokus", "Italian (Italiano)": "Concentrazione", "Portuguese (Português)": "Foco",
        "Russian (Русский)": "Фокус", "Turkish (Türkçe)": "Odaklanma", "Dutch (Nederlands)": "Focus",
        "Polish (Polski)": "Skupienie", "Swedish (Svenska)": "Fokus", "Greek (Ελληνικά)": "Εστίαση",
        "Indonesian (Bahasa Indonesia)": "Fokus", "Vietnamese (Tiếng Việt)": "Tập Trung", "Malay (Bahasa Melayu)": "Fokus",
        "Filipino (Tagalog)": "Focus"
    },
    "Sleep": {
        "English": "Sleep", "Tamil (தமிழ்)": "உறக்கம்", "Korean (한국어)": "수면", "Thai (Thai)": "นอนหลับ",
        "Spanish (Español)": "Sueño", "Hindi (हिन्दी)": "नींद", "Arabic (العربية)": "نوم", "Japanese (日本語)": "睡眠",
        "Chinese (中文)": "睡眠", "French (Français)": "Sommeil", "German (Deutsch)": "Schlaf", "Italian (Italiano)": "Sonno",
        "Portuguese (Português)": "Sono", "Russian (Русский)": "Сон", "Turkish (Türkçe)": "Uyku",
        "Dutch (Nederlands)": "Slaap", "Polish (Polski)": "Sen", "Swedish (Svenska)": "Sömn",
        "Greek (Ελληνικά)": "Ύπνος", "Indonesian (Bahasa Indonesia)": "Tidur", "Vietnamese (Tiếng Việt)": "Ngủ",
        "Malay (Bahasa Melayu)": "Tidur", "Filipino (Tagalog)": "Sleep"
    },
    "Deep Meditation": {
        "English": "Deep Meditation", "Tamil (தமிழ்)": "ஆழ்ந்த தியானம்", "Korean (한국어)": "깊은 명상",
        "Thai (Thai)": "การทำสมาธิแบบลึก", "Spanish (Español)": "Meditación Profunda", "Hindi (हिन्दी)": "गहरा ध्यान",
        "Arabic (العربية)": "تأمل عميق", "Japanese (日本語)": "深い瞑想", "Chinese (中文)": "深度冥想",
        "French (Français)": "Méditation Profonde", "German (Deutsch)": "Tiefe Meditation",
        "Italian (Italiano)": "Meditazione Profonda", "Portuguese (Português)": "Meditação Profunda",
        "Russian (Русский)": "Глубокая медитация", "Turkish (Türkçe)": "Derin Meditasyon",
        "Dutch (Nederlands)": "Diepe Meditatie", "Polish (Polski)": "Głęboka Medytacja", "Swedish (Svenska)": "Djup Meditation",
        "Greek (Ελληνικά)": "Βαθύς Διαλογισμός", "Indonesian (Bahasa Indonesia)": "Meditasi Mendalam",
        "Vietnamese (Tiếng Việt)": "Thiền Sâu", "Malay (Bahasa Melayu)": "Meditasi Mendalam", "Filipino (Tagalog)": "Deep Meditation"
    },
    "Energize": {
        "English": "Energize", "Tamil (தமிழ்)": "உற்சாகமூட்டு", "Korean (한국어)": "활력", "Thai (Thai)": "กระตุ้นพลังงาน",
        "Spanish (Español)": "Energizar", "Hindi (हिन्दी)": "ऊर्जावान", "Arabic (العربية)": "تنشيط",
        "Japanese (日本語)": "元気にする", "Chinese (中文)": "活力", "French (Français)": "Énergiser",
        "German (Deutsch)": "Energie", "Italian (Italiano)": "Energizza", "Portuguese (Português)": "Energizar",
        "Russian (Русский)": "Энергия", "Turkish (Türkçe)": "Enerjik", "Dutch (Nederlands)": "Energiek",
        "Polish (Polski)": "Energia", "Swedish (Svenska)": "Energi", "Greek (Ελληνικά)": "Ενέργεια",
        "Indonesian (Bahasa Indonesia)": "Energi", "Vietnamese (Tiếng Việt)": "Tiếp Năng Lượng", "Malay (Bahasa Melayu)": "Bertenaga",
        "Filipino (Tagalog)": "Energize"
    },
    "Zen Garden": {
        "English": "Zen Garden", "Tamil (தமிழ்)": "ஜென் தோட்டம்", "Korean (한국어)": "젠 가든", "Thai (Thai)": "สวนเซน",
        "Spanish (Español)": "Jardín Zen", "Hindi (हिन्दी)": "ज़ेन गार्डन", "Arabic (العربية)": "حديقة زن",
        "Japanese (日本語)": "禅ガーデン", "Chinese (中文)": "禅意花园", "French (Français)": "Jardin Zen",
        "German (Deutsch)": "Zen-Garten", "Italian (Italiano)": "Giardino Zen", "Portuguese (Português)": "Jardim Zen",
        "Russian (Русский)": "Дзен-сад", "Turkish (Türkçe)": "Zen Bahçesi", "Dutch (Nederlands)": "Zen Tuin",
        "Polish (Polski)": "Ogród Zen", "Swedish (Svenska)": "Zen Trädgård", "Greek (Ελληνικά)": "Κήπος Ζεν",
        "Indonesian (Bahasa Indonesia)": "Taman Zen", "Vietnamese (Tiếng Việt)": "Vườn Thiền", "Malay (Bahasa Melayu)": "Taman Zen",
        "Filipino (Tagalog)": "Zen Garden"
    },
    "Deep Calm Studio": {
        "English": "Deep Calm Studio", "Tamil (தமிழ்)": "ஆழ்ந்த அமைதி ஸ்டுடியோ", "Korean (한국어)": "깊은 고요 스튜디오",
        "Thai (Thai)": "สตูดิโอความสงบลึก", "Spanish (Español)": "Estudio de Calma Profunda", "Hindi (हिन्दी)": "गहरा शांत स्टूडियो",
        "Arabic (العربية)": "استوديو الهدوء العميق", "Japanese (日本語)": "ディープカームスタジオ", "Chinese (中文)": "深度平静工作室",
        "French (Français)": "Studio de Calme Profond", "German (Deutsch)": "Tiefenentspannungsstudio",
        "Italian (Italiano)": "Studio di Calma Profonda", "Portuguese (Português)": "Estúdio de Calma Profunda",
        "Russian (Русский)": "Студия глубокого спокойствия", "Turkish (Türkçe)": "Derin Sakinlik Stüdyosu",
        "Dutch (Nederlands)": "Diepe Rust Studio", "Polish (Polski)": "Studio Głębokiego Spokoju",
        "Swedish (Svenska)": "Djupt Lugn Studio", "Greek (Ελληνικά)": "Στούντιο Βαθιάς Ηρεμίας",
        "Indonesian (Bahasa Indonesia)": "Studio Ketenangan Mendalam", "Vietnamese (Tiếng Việt)": "Studio Tĩnh Lặng Sâu",
        "Malay (Bahasa Melayu)": "Studio Ketenangan Mendalam", "Filipino (Tagalog)": "Deep Calm Studio"
    },
    "Wind-Down Sleep": {
        "English": "Wind-Down Sleep", "Tamil (தமிழ்)": "தளர்வான உறக்கம்", "Korean (한국어)": "휴식 수면",
        "Thai (Thai)": "การนอนหลับผ่อนคลาย", "Spanish (Español)": "Sueño Relajante", "Hindi (हिन्दी)": "आरामदायक नींद",
        "Arabic (العربية)": "نوم استرخائي", "Japanese (日本語)": "リラックス睡眠", "Chinese (中文)": "放松睡眠",
        "French (Français)": "Sommeil Détente", "German (Deutsch)": "Entspannungsschlaf", "Italian (Italiano)": "Sonno Rilassante",
        "Portuguese (Português)": "Sono Relaxante", "Russian (Русский)": "Расслабляющий сон", "Turkish (Türkçe)": "Rahatlatıcı Uyku",
        "Dutch (Nederlands)": "Ontspannen Slaap", "Polish (Polski)": "Sen Relaksacyjny", "Swedish (Svenska)": "Avkopplande Sömn",
        "Greek (Ελληνικά)": "Χαλαρωτικός Ύπνος", "Indonesian (Bahasa Indonesia)": "Tidur Santai",
        "Vietnamese (Tiếng Việt)": "Giấc Ngủ Thư Giãn", "Malay (Bahasa Melayu)": "Tidur Santai", "Filipino (Tagalog)": "Wind-Down Sleep"
    },
    "Cinema Night": {
        "English": "Cinema Night", "Tamil (தமிழ்)": "சினிமா இரவு", "Korean (한국어)": "영화의 밤", "Thai (Thai)": "คืนภาพยนตร์",
        "Spanish (Español)": "Noche de Cine", "Hindi (हिन्दी)": "सिनेमा रात", "Arabic (العربية)": "ليلة سينما",
        "Japanese (日本語)": "シネマナイト", "Chinese (中文)": "电影之夜", "French (Français)": "Soirée Cinéma",
        "German (Deutsch)": "Kinonacht", "Italian (Italiano)": "Notte Cinema", "Portuguese (Português)": "Noite de Cinema",
        "Russian (Русский)": "Киноночь", "Turkish (Türkçe)": "Sinema Gecesi", "Dutch (Nederlands)": "Bioscoopavond",
        "Polish (Polski)": "Noc Filmowa", "Swedish (Svenska)": "Filmkväll", "Greek (Ελληνικά)": "Βραδιά Σινεμά",
        "Indonesian (Bahasa Indonesia)": "Malam Bioskop", "Vietnamese (Tiếng Việt)": "Đêm Điện Ảnh",
        "Malay (Bahasa Melayu)": "Malam Wayang", "Filipino (Tagalog)": "Cinema Night"
    },
    "Neutral Family Ambience": {
        "English": "Neutral Family Ambience", "Tamil (தமிழ்)": "நடுநிலை குடும்ப சூழல்", "Korean (한국어)": "중립 가족 분위기",
        "Thai (Thai)": "บรรยากาศครอบครัวเป็นกลาง", "Spanish (Español)": "Ambiente Familiar Neutral", "Hindi (हिन्दी)": "तटस्थ पारिवारिक माहौल",
        "Arabic (العربية)": "أجواء عائلية محايدة", "Japanese (日本語)": "ニュートラルファミリーアンビエンス", "Chinese (中文)": "中性家庭氛围",
        "French (Français)": "Ambiance Familiale Neutre", "German (Deutsch)": "Neutrale Familienatmosphäre",
        "Italian (Italiano)": "Ambiente Familiare Neutro", "Portuguese (Português)": "Ambiente Familiar Neutro",
        "Russian (Русский)": "Нейтральная семейная атмосфера", "Turkish (Türkçe)": "Nötr Aile Ortamı",
        "Dutch (Nederlands)": "Neutrale Gezinsfeer", "Polish (Polski)": "Neutralna Atmosfera Rodzinna",
        "Swedish (Svenska)": "Neutral Familjestämning", "Greek (Ελληνικά)": "Ουδέτερη Οικογενειακή Ατμόσφαιρα",
        "Indonesian (Bahasa Indonesia)": "Suasana Keluarga Netral", "Vietnamese (Tiếng Việt)": "Không Gian Gia Đình Trung Tính",
        "Malay (Bahasa Melayu)": "Suasana Keluarga Neutral", "Filipino (Tagalog)": "Neutral Family Ambience"
    },
}

LIGHT_WORDS = {
    "Daylight White": {
        "English": "Daylight White", "Tamil (தமிழ்)": "பகல் வெள்ளை", "Korean (한국어)": "주광색 백색",
        "Thai (Thai)": "ขาวแสงกลางวัน", "Spanish (Español)": "Blanco Luz de Día", "Hindi (हिन्दी)": "दिन का सफेद",
        "Arabic (العربية)": "أبيض ضوء النهار", "Japanese (日本語)": "デイライトホワイト", "Chinese (中文)": "日光白",
        "French (Français)": "Blanc Lumière du Jour", "German (Deutsch)": "Tageslichtweiß", "Italian (Italiano)": "Bianco Luce Diurna",
        "Portuguese (Português)": "Branco Luz do Dia", "Russian (Русский)": "Белый дневной", "Turkish (Türkçe)": "Gün Işığı Beyaz",
        "Dutch (Nederlands)": "Daglicht Wit", "Polish (Polski)": "Biel Dzienna", "Swedish (Svenska)": "Dagsljus Vit",
        "Greek (Ελληνικά)": "Λευκό Φωτός Ημέρας", "Indonesian (Bahasa Indonesia)": "Putih Cahaya Siang",
        "Vietnamese (Tiếng Việt)": "Trắng Ánh Sáng Ngày", "Malay (Bahasa Melayu)": "Putih Cahaya Siang", "Filipino (Tagalog)": "Daylight White"
    },
    "Soft White": {
        "English": "Soft White", "Tamil (தமிழ்)": "மென்மையான வெள்ளை", "Korean (한국어)": "소프트 화이트",
        "Thai (Thai)": "ขาวนุ่ม", "Spanish (Español)": "Blanco Suave", "Hindi (हिन्दी)": "कोमल सफेद",
        "Arabic (العربية)": "أبيض ناعم", "Japanese (日本語)": "ソフトホワイト", "Chinese (中文)": "柔和白",
        "French (Français)": "Blanc Doux", "German (Deutsch)": "Sanftes Weiß", "Italian (Italiano)": "Bianco Morbido",
        "Portuguese (Português)": "Branco Suave", "Russian (Русский)": "Мягкий белый", "Turkish (Türkçe)": "Yumuşak Beyaz",
        "Dutch (Nederlands)": "Zacht Wit", "Polish (Polski)": "Miękka Biel", "Swedish (Svenska)": "Mjuk Vit",
        "Greek (Ελληνικά)": "Απαλό Λευκό", "Indonesian (Bahasa Indonesia)": "Putih Lembut",
        "Vietnamese (Tiếng Việt)": "Trắng Dịu", "Malay (Bahasa Melayu)": "Putih Lembut", "Filipino (Tagalog)": "Soft White"
    },
    "Warm Candlelight": {
        "English": "Warm Candlelight", "Tamil (தமிழ்)": "சூடான மெழுகுவர்த்தி வெளிச்சம்", "Korean (한국어)": "따뜻한 촛불",
        "Thai (Thai)": "แสงเทียนอบอุ่น", "Spanish (Español)": "Luz de Vela Cálida", "Hindi (हिन्दी)": "गर्म मोमबत्ती",
        "Arabic (العربية)": "ضوء شمعة دافئ", "Japanese (日本語)": "暖かいキャンドルライト", "Chinese (中文)": "温暖烛光",
        "French (Français)": "Lumière de Bougie Chaud", "German (Deutsch)": "Warmes Kerzenlicht", "Italian (Italiano)": "Luce di Candela Calda",
        "Portuguese (Português)": "Luz de Vela Quente", "Russian (Русский)": "Теплый свет свечей", "Turkish (Türkçe)": "Sıcak Mum Işığı",
        "Dutch (Nederlands)": "Warm Kaarslicht", "Polish (Polski)": "Ciepłe Światło Świec", "Swedish (Svenska)": "Varmt Ljus",
        "Greek (Ελληνικά)": "Ζεστό Φως Κεριού", "Indonesian (Bahasa Indonesia)": "Cahaya Lilin Hangat",
        "Vietnamese (Tiếng Việt)": "Ánh Nến Ấm", "Malay (Bahasa Melayu)": "Cahaya Lilin Hangat", "Filipino (Tagalog)": "Warm Candlelight"
    },
    "Calm Blue": {
        "English": "Calm Blue", "Tamil (தமிழ்)": "அமைதியான நீலம்", "Korean (한국어)": "차분한 블루",
        "Thai (Thai)": "สีน้ำเงินสงบ", "Spanish (Español)": "Azul Calma", "Hindi (हिन्दी)": "शांत नीला",
        "Arabic (العربية)": "أزرق هادئ", "Japanese (日本語)": "穏やかなブルー", "Chinese (中文)": "平静蓝",
        "French (Français)": "Bleu Calme", "German (Deutsch)": "Ruhiges Blau", "Italian (Italiano)": "Blu Calmo",
        "Portuguese (Português)": "Azul Calmo", "Russian (Русский)": "Спокойный синий", "Turkish (Türkçe)": "Sakin Mavi",
        "Dutch (Nederlands)": "Kalm Blauw", "Polish (Polski)": "Spokojny Błękit", "Swedish (Svenska)": "Lugn Blå",
        "Greek (Ελληνικά)": "Ήρεμο Μπλε", "Indonesian (Bahasa Indonesia)": "Biru Tenang",
        "Vietnamese (Tiếng Việt)": "Xanh Lam Tĩnh", "Malay (Bahasa Melayu)": "Biru Tenang", "Filipino (Tagalog)": "Calm Blue"
    },
    "Fresh Green": {
        "English": "Fresh Green", "Tamil (தமிழ்)": "புதிய பச்சை", "Korean (한국어)": "싱그러운 그린",
        "Thai (Thai)": "สีเขียวสด", "Spanish (Español)": "Verde Fresco", "Hindi (हिन्दी)": "ताज़ा हरा",
        "Arabic (العربية)": "أخضر منعش", "Japanese (日本語)": "フレッシュグリーン", "Chinese (中文)": "清新绿",
        "French (Français)": "Vert Frais", "German (Deutsch)": "Frisches Grün", "Italian (Italiano)": "Verde Fresco",
        "Portuguese (Português)": "Verde Fresco", "Russian (Русский)": "Свежий зелёный", "Turkish (Türkçe)": "Taze Yeşil",
        "Dutch (Nederlands)": "Fris Groen", "Polish (Polski)": "Świeża Zieleń", "Swedish (Svenska)": "Fräsch Grön",
        "Greek (Ελληνικά)": "Φρέσκο Πράσινο", "Indonesian (Bahasa Indonesia)": "Hijau Segar",
        "Vietnamese (Tiếng Việt)": "Xanh Tươi", "Malay (Bahasa Melayu)": "Hijau Segar", "Filipino (Tagalog)": "Fresh Green"
    },
    "Violet Glow": {
        "English": "Violet Glow", "Tamil (தமிழ்)": "ஊதா பளபளப்பு", "Korean (한국어)": "바이올렛 글로우",
        "Thai (Thai)": "แสงสีม่วง", "Spanish (Español)": "Brillo Violeta", "Hindi (हिन्दी)": "बैंगनी चमक",
        "Arabic (العربية)": "توهج بنفسجي", "Japanese (日本語)": "バイオレットグロー", "Chinese (中文)": "紫罗兰辉光",
        "French (Français)": "Lueur Violette", "German (Deutsch)": "Violettes Leuchten", "Italian (Italiano)": "Bagliore Viola",
        "Portuguese (Português)": "Brilho Violeta", "Russian (Русский)": "Фиолетовое свечение", "Turkish (Türkçe)": "Mor Işıltı",
        "Dutch (Nederlands)": "Violette Gloed", "Polish (Polski)": "Fioletowy Blask", "Swedish (Svenska)": "Violett Glöd",
        "Greek (Ελληνικά)": "Βιολετί Λάμψη", "Indonesian (Bahasa Indonesia)": "Cahaya Violet",
        "Vietnamese (Tiếng Việt)": "Ánh Tím", "Malay (Bahasa Melayu)": "Cahaya Violet", "Filipino (Tagalog)": "Violet Glow"
    },
    "Warm Amber": {
        "English": "Warm Amber", "Tamil (தமிழ்)": "சூடான அம்பர்", "Korean (한국어)": "따뜻한 앰버",
        "Thai (Thai)": "อำพันอบอุ่น", "Spanish (Español)": "Ámbar Cálido", "Hindi (हिन्दी)": "गर्म एम्बर",
        "Arabic (العربية)": "كهرماني دافئ", "Japanese (日本語)": "ウォームアンバー", "Chinese (中文)": "暖琥珀色",
        "French (Français)": "Ambre Chaud", "German (Deutsch)": "Warmes Bernstein", "Italian (Italiano)": "Ambra Calda",
        "Portuguese (Português)": "Âmbar Quente", "Russian (Русский)": "Теплый янтарь", "Turkish (Türkçe)": "Sıcak Kehribar",
        "Dutch (Nederlands)": "Warm Amber", "Polish (Polski)": "Ciepły Bursztyn", "Swedish (Svenska)": "Varm Bärnsten",
        "Greek (Ελληνικά)": "Ζεστό Κεχριμπάρι", "Indonesian (Bahasa Indonesia)": "Amber Hangat",
        "Vietnamese (Tiếng Việt)": "Hổ Phách Ấm", "Malay (Bahasa Melayu)": "Amber Hangat", "Filipino (Tagalog)": "Warm Amber"
    }
}
LIGHT_ADJ = {
    "Bright": {"English": "Bright", "Tamil (தமிழ்)": "பிரகாசமான", "Korean (한국어)": "밝은", "Thai (Thai)": "สว่าง", "Spanish (Español)": "Brillante", "Hindi (हिन्दी)": "उज्ज्वल", "Arabic (العربية)": "ساطع", "Japanese (日本語)": "明るい", "Chinese (中文)": "明亮", "French (Français)": "Lumineux", "German (Deutsch)": "Hell", "Italian (Italiano)": "Luminoso", "Portuguese (Português)": "Brilhante", "Russian (Русский)": "Яркий", "Turkish (Türkçe)": "Parlak", "Dutch (Nederlands)": "Helder", "Polish (Polski)": "Jasny", "Swedish (Svenska)": "Ljus", "Greek (Ελληνικά)": "Φωτεινό", "Indonesian (Bahasa Indonesia)": "Terang", "Vietnamese (Tiếng Việt)": "Sáng", "Malay (Bahasa Melayu)": "Terang", "Filipino (Tagalog)": "Bright"},
    "Soft": {"English": "Soft", "Tamil (தமிழ்)": "மென்மையான", "Korean (한국어)": "부드러운", "Thai (Thai)": "นุ่ม", "Spanish (Español)": "Suave", "Hindi (हिन्दी)": "कोमल", "Arabic (العربية)": "ناعم", "Japanese (日本語)": "ソフト", "Chinese (中文)": "柔和", "French (Français)": "Doux", "German (Deutsch)": "Sanft", "Italian (Italiano)": "Morbido", "Portuguese (Português)": "Suave", "Russian (Русский)": "Мягкий", "Turkish (Türkçe)": "Yumuşak", "Dutch (Nederlands)": "Zacht", "Polish (Polski)": "Miękki", "Swedish (Svenska)": "Mjuk", "Greek (Ελληνικά)": "Απαλό", "Indonesian (Bahasa Indonesia)": "Lembut", "Vietnamese (Tiếng Việt)": "Dịu", "Malay (Bahasa Melayu)": "Lembut", "Filipino (Tagalog)": "Soft"},
    "Dim": {"English": "Dim", "Tamil (தமிழ்)": "மங்கலான", "Korean (한국어)": "어두운", "Thai (Thai)": "หรี่", "Spanish (Español)": "Tenue", "Hindi (हिन्दी)": "मंद", "Arabic (العربية)": "خافت", "Japanese (日本語)": "薄暗い", "Chinese (中文)": "暗淡", "French (Français)": "Sombre", "German (Deutsch)": "Gedimmt", "Italian (Italiano)": "Fioco", "Portuguese (Português)": "Escuro", "Russian (Русский)": "Тусклый", "Turkish (Türkçe)": "Loş", "Dutch (Nederlands)": "Gedoofd", "Polish (Polski)": "Przyćmiony", "Swedish (Svenska)": "Dämpad", "Greek (Ελληνικά)": "Χαμηλό", "Indonesian (Bahasa Indonesia)": "Redup", "Vietnamese (Tiếng Việt)": "Mờ", "Malay (Bahasa Melayu)": "Malap", "Filipino (Tagalog)": "Dim"},
}


def t(key, **kw):
    lang = st.session_state.get("lang", "English")
    i = LANGS.index(lang)
    row = T[key]
    if i < 5:
        text = row[i] if i < len(row) else row[0]
    elif key in CI and lang in TX:
        text = TX[lang][CI[key]]
    else:
        text = row[0]
    for k, v in kw.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def tr_room(name):
    lang = st.session_state.get("lang", "English")
    return ROOM_NAMES.get(name, {}).get(lang, name)


def tr_mode(name):
    lang = st.session_state.get("lang", "English")
    return MODE_NAMES.get(name, {}).get(lang, name)


# ----------------------------------------------------------------------------
# Full-app translation layer.
# ----------------------------------------------------------------------------
LANG_CODES = {"Tamil (தமிழ்)": "ta", "Korean (한국어)": "ko", "Thai (Thai)": "th", "Spanish (Español)": "es",
              "Hindi (हिन्दी)": "hi", "Arabic (العربية)": "ar", "Japanese (日本語)": "ja", "Chinese (中文)": "zh-CN",
              "French (Français)": "fr", "German (Deutsch)": "de", "Italian (Italiano)": "it",
              "Portuguese (Português)": "pt", "Russian (Русский)": "ru", "Turkish (Türkçe)": "tr",
              "Dutch (Nederlands)": "nl", "Polish (Polski)": "pl", "Swedish (Svenska)": "sv", "Greek (Ελληνικά)": "el",
              "Indonesian (Bahasa Indonesia)": "id", "Vietnamese (Tiếng Việt)": "vi", "Malay (Bahasa Melayu)": "ms",
              "Filipino (Tagalog)": "tl"}
SCRIPT_RANGES = {"ta": [(0x0B80, 0x0BFF)], "ko": [(0xAC00, 0xD7AF), (0x1100, 0x11FF)], "th": [(0x0E00, 0x0E7F)],
                 "hi": [(0x0900, 0x097F)], "ar": [(0x0600, 0x06FF)], "ja": [(0x3040, 0x30FF), (0x4E00, 0x9FFF)],
                 "zh-CN": [(0x4E00, 0x9FFF)], "ru": [(0x0400, 0x04FF)], "el": [(0x0370, 0x03FF)]}
PH_RE = re.compile(r"\{[A-Za-z_][A-Za-z_0-9]*\}|\d+(?:[.,:]\d+)*")
EDGE_RE = re.compile(r"^(\W*)(.*?)(\W*)$", re.S)
LETTERS_RE = re.compile(r"[^\W\d_]{2}")

_REG = sys.modules.setdefault("_aurasync_reg", types.ModuleType("_aurasync_reg"))
if not hasattr(_REG, "lock"):
    _REG.lock = threading.Lock()
    _REG.cache = None
    _REG.fail = 0
    _REG.down_until = 0.0
    _REG.saved_at = 0.0
    _REG.pending = False
    _REG.static = {}
    _REG.cands = None
    _REG.mt_ok = None
    _REG.wrapped = False
    _REG.impl = {}


def lang_code():
    return LANG_CODES.get(st.session_state.get("lang", "English"))


def _cache_file():
    try:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "aurasync_i18n_cache.json")
    except NameError:
        return "aurasync_i18n_cache.json"


def _cache():
    if _REG.cache is None:
        data = {}
        try:
            with open(_cache_file(), encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        _REG.cache = data if isinstance(data, dict) else {}
    return _REG.cache


def _cache_save(force=False):
    if not _REG.pending:
        return
    if not force and time.time() - _REG.saved_at < 4:
        return
    try:
        with _REG.lock:
            blob = json.dumps(_REG.cache, ensure_ascii=False)
        with open(_cache_file(), "w", encoding="utf-8") as f:
            f.write(blob)
        _REG.saved_at = time.time()
        _REG.pending = False
    except Exception:
        pass


def mt_available():
    if _REG.mt_ok is None:
        try:
            import deep_translator  # noqa: F401
            _REG.mt_ok = True
        except Exception:
            _REG.mt_ok = False
    return _REG.mt_ok


def _mt_one(code, text):
    if time.time() < _REG.down_until:
        return None
    try:
        from deep_translator import GoogleTranslator
        out = GoogleTranslator(source="auto", target=code).translate(text)
        if not isinstance(out, str) or not out.strip():
            return None
        _REG.fail = 0
        return out
    except Exception:
        _REG.fail += 1
        if _REG.fail >= 4:
            _REG.down_until = time.time() + 90
            _REG.fail = 0
        return None


def _templ(core):
    """Numbers and {placeholders} become {0}, {1}... so one translation serves every value."""
    toks = []

    def sub(m):
        toks.append(m.group(0))
        return "{" + str(len(toks) - 1) + "}"
    return PH_RE.sub(sub, core), toks


def _norm_ph(text):
    return re.sub(r"\{\s*(\d+)\s*\}", r"{\1}", text)


def _untempl(text, toks):
    text = _norm_ph(text)
    for i, tok in enumerate(toks):
        text = text.replace("{" + str(i) + "}", tok)
    return text


def _ph_same(a, b):
    return set(re.findall(r"\{\s*(\d+)\s*\}", a)) == set(re.findall(r"\{\s*(\d+)\s*\}", b))


def _mt_batch(code, templs):
    """Translate many short strings with few requests."""
    chunks, chunk, size = [], [], 0
    for s in templs:
        if "\n" in s:
            continue
        if chunk and (size + len(s) > 2800 or len(chunk) >= 40):
            chunks.append(chunk)
            chunk, size = [], 0
        chunk.append(s)
        size += len(s) + 1
    if chunk:
        chunks.append(chunk)

    def work(ch):
        if len(ch) > 1:
            r = _mt_one(code, "\n".join(ch))
            if r is not None:
                parts = r.split("\n")
                if len(parts) == len(ch):
                    return dict(zip(ch, parts))
        res = {}
        for s in ch:
            x = _mt_one(code, s)
            if x:
                res[s] = x
        return res
    out = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(work, chunks):
            out.update(res)
    return out


def _static_set(lang):
    s = _REG.static.get(lang)
    if s is None:
        s, i = set(), LANGS.index(lang)
        for key, row in T.items():
            v = None
            if i < 5:
                v = row[i] if i < len(row) else None
            elif lang in TX and key in CI:
                v = TX[lang][CI[key]]
            if v:
                s.add(v)
                s.add(re.sub(r"^\W+|\W+$", "", v))
        _REG.static[lang] = s
    return s


def _skip(core, code):
    """Already in the chosen language (hand translation or same script)?"""
    lang = st.session_state.get("lang", "English")
    if core in _static_set(lang):
        return True
    rng = SCRIPT_RANGES.get(code)
    if rng:
        letters = [c for c in core if c.isalpha()]
        if letters:
            hit = sum(1 for c in letters if any(a <= ord(c) <= b for a, b in rng))
            if hit / len(letters) >= 0.3:
                return True
    return False


def tr(text):
    """Translate one display string into the chosen language (no-op in English)."""
    code = lang_code()
    if not code or not isinstance(text, str) or not text.strip():
        return text
    m = EDGE_RE.match(text)
    lead, core, tail = m.group(1), m.group(2), m.group(3)
    if not LETTERS_RE.search(core) or _skip(core, code):
        return text
    templ, toks = _templ(core)
    if not LETTERS_RE.search(templ):
        return text
    key = code + "|" + templ
    cache = _cache()
    hit = cache.get(key)
    if hit is None:
        if not mt_available() or time.time() < _REG.down_until:
            return text
        out = _mt_one(code, templ)
        if not out or not _ph_same(templ, out):
            return text
        hit = _norm_ph(out)
        cache[key] = hit
        _REG.pending = True
        _cache_save()
    return lead + _untempl(hit, toks) + tail


def tr_html(text):
    if re.search(r"<(style|script|svg)\b", text, re.I):
        return text
    out, skip = [], False
    for p in re.split(r"(<[^>]+>)", text):
        if len(p) > 2 and p.startswith("<") and p.endswith(">") and not p.startswith("< "):
            low = p.lower()
            if 'translate="no"' in low:
                skip = True
            elif low.startswith("</span") and skip:
                skip = False
            out.append(p)
        elif skip or not p.strip():
            out.append(p)
        else:
            raw = html.unescape(p)
            new = tr(raw)
            out.append(p if new == raw else html.escape(new, quote=False))
    return "".join(out)


def tr_md(text, html_ok=False):
    if not lang_code() or not isinstance(text, str) or not text.strip():
        return text
    if html_ok or re.search(r"<[A-Za-z/!]", text):
        return tr_html(text)
    if "```" in text or "](" in text:
        return text
    return "\n".join(ln if "`" in ln else tr(ln) for ln in text.split("\n"))


def _ui_like(s):
    if not (3 <= len(s) <= 160) or re.fullmatch(r"[a-z_0-9]+", s) or "\n" in s:
        return False
    if re.search(r"[<>;=\\]|::|->|https?:|\.py\b|#[0-9a-fA-F]{3,8}\b|\w\(\)|\bst\.|\bss\.", s):
        return False
    return not re.search(r"[{}]", PH_RE.sub("", s))


def _candidates():
    if _REG.cands is None:
        pool = set()
        for row in T.values():
            if row and row[0]:
                pool.add(row[0])
        try:
            with open(os.path.abspath(__file__), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for n in ast.walk(tree):
                if isinstance(n, ast.Constant) and isinstance(n.value, str):
                    pool.add(n.value)
        except Exception:
            pass
        out = set()
        for s in pool:
            if _ui_like(s):
                core = EDGE_RE.match(s).group(2)
                tpl, _ = _templ(core)
                if LETTERS_RE.search(tpl) and len(tpl) <= 200:
                    out.add(tpl)
        _REG.cands = sorted(out)
    return _REG.cands


def i18n_prefetch():
    """Translate every static UI string for the chosen language in a few parallel batches."""
    code = lang_code()
    if not code or not mt_available():
        return False
    cache = _cache()
    todo = [s for s in _candidates() if (code + "|" + s) not in cache and not _skip(s, code)]
    if not todo:
        return True
    res = _mt_batch(code, todo)
    for s, o in res.items():
        if _ph_same(s, o):
            cache[code + "|" + s] = _norm_ph(o)
    _REG.pending = True
    _cache_save(force=True)
    return bool(res)


_I18N_TEXT = ("markdown", "caption", "subheader", "header", "title", "info", "success", "warning", "error", "toast")
_I18N_LABEL = ("button", "form_submit_button", "toggle", "checkbox", "selectbox", "multiselect", "radio", "slider",
               "select_slider", "text_input", "text_area", "number_input", "color_picker", "time_input", "date_input",
               "segmented_control", "pills", "expander", "popover", "chat_input", "file_uploader", "camera_input",
               "download_button", "link_button", "progress")
_I18N_OPTS = ("selectbox", "multiselect", "radio", "segmented_control", "select_slider", "pills")


def _xl_args(impl, kind, is_method, a, k):
    a, i0 = list(a), (1 if is_method else 0)
    trf, md = impl["tr"], impl["tr_md"]
    if kind == "text":
        if len(a) > i0 and isinstance(a[i0], str):
            a[i0] = md(a[i0], bool(k.get("unsafe_allow_html")))
        elif isinstance(k.get("body"), str):
            k["body"] = md(k["body"], bool(k.get("unsafe_allow_html")))
        return tuple(a), k
    if len(a) > i0 and isinstance(a[i0], str):
        a[i0] = trf(a[i0])
    elif isinstance(k.get("label"), str):
        k["label"] = trf(k["label"])
    for nm in ("help", "placeholder", "text"):
        if isinstance(k.get(nm), str):
            k[nm] = trf(k[nm])
    if kind == "opts" and k.get("key") != "lang":
        ff = k.get("format_func")
        k["format_func"] = (lambda x, _f=ff: trf(str(_f(x) if _f else x)))
    return tuple(a), k


def _i18n_wrap(fn, name, is_method):
    kind = "text" if name in _I18N_TEXT else ("opts" if name in _I18N_OPTS else "label")

    def w(*a, **k):
        impl = _REG.impl
        try:
            if impl["lang_code"]():
                a, k = _xl_args(impl, kind, is_method, a, k)
        except Exception:
            pass
        return fn(*a, **k)
    w._aura = True
    w.__name__ = getattr(fn, "__name__", name)
    w.__doc__ = getattr(fn, "__doc__", None)
    return w


def install_i18n():
    """Every Streamlit text / label call goes through the translator, so no page can stay in English."""
    _REG.impl = {"tr": tr, "tr_md": tr_md, "lang_code": lang_code}
    if _REG.wrapped:
        return
    try:
        from streamlit.delta_generator import DeltaGenerator
    except Exception:
        DeltaGenerator = None
    for name in _I18N_TEXT + _I18N_LABEL:
        fn = getattr(st, name, None)
        if callable(fn) and not getattr(fn, "_aura", False):
            setattr(st, name, _i18n_wrap(fn, name, False))
        if DeltaGenerator is not None:
            fn = getattr(DeltaGenerator, name, None)
            if callable(fn) and not getattr(fn, "_aura", False):
                setattr(DeltaGenerator, name, _i18n_wrap(fn, name, True))
    _REG.wrapped = True


# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
PALETTES = {
    # Dark: black and gold
    "dark": {"SCHEME": "dark", "BG": "#0B0B0B", "SIDE": "#121212", "BTN": "#0B0B0B", "ACC": "#D4AF37", "ACC2": "#B8962E",
             "ONACC": "#141414", "CARD1": "#161616", "CARD2": "#0F0F0F", "STAT": "#121212", "SUB": "#BBA85A",
             "LOG": "#CFC7AE", "MUTE": "#9A9172", "CHATBG": "#0F0F0F", "BUBDV": "#1D1D1D", "TXT": "#EDE6D3",
             "TXT2": "#E8E2D0", "INPUT": "#171717", "BORDER": "#3A3320", "POP": "#1A1A1A", "HUE": "48deg"},
    # Light: pure white page, electric blue accent, near-black text
    "light": {"SCHEME": "light", "BG": "#FFFFFF", "SIDE": "#FFFFFF", "BTN": "#FFFFFF", "ACC": "#0057FF", "ACC2": "#0043CC",
              "ONACC": "#FFFFFF", "CARD1": "#FFFFFF", "CARD2": "#F5F8FF", "STAT": "#F3F7FF", "SUB": "#3F4F73",
              "LOG": "#1E293B", "MUTE": "#566176", "CHATBG": "#FFFFFF", "BUBDV": "#EEF3FF", "TXT": "#0F172A",
              "TXT2": "#1E293B", "INPUT": "#FFFFFF", "BORDER": "#CFDBF5", "POP": "#FFFFFF", "HUE": "212deg"},
}

CSS_T = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
:root { color-scheme: @SCHEME@; }
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; color: @TXT@; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background-color: @BG@ !important; }
[data-testid="stHeader"], [data-testid="stBottom"] > div { background-color: @BG@ !important; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background-color: @SIDE@ !important; }
[data-testid="stSidebar"] { border-right: 1px solid @ACC@40; }
.stApp p, .stApp li, .stApp label, [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p { color: @TXT@; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: @MUTE@ !important; }
[data-baseweb="radio"] *, [data-baseweb="checkbox"] *, [data-testid="stToggle"] * { color: @TXT@; }
hr { border-color: @BORDER@ !important; }
h1, h2, h3, h4 { color: @ACC@ !important; font-weight: 600; letter-spacing: 0.3px; }
[data-baseweb="input"] > div, [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
  background-color: @INPUT@ !important; border-color: @BORDER@ !important; color: @TXT@ !important; }
input, textarea { color: @TXT@ !important; -webkit-text-fill-color: @TXT@ !important; background-color: transparent !important; }
[data-baseweb="select"] div, [data-baseweb="select"] span, [data-baseweb="select"] svg { color: @TXT@ !important; fill: @TXT@ !important; }
[data-baseweb="tag"] { background-color: @ACC@ !important; }
[data-baseweb="tag"] span, [data-baseweb="tag"] svg { color: @ONACC@ !important; fill: @ONACC@ !important; }
[data-baseweb="popover"], [data-baseweb="popover"] > div, [data-baseweb="menu"], ul[role="listbox"], [data-baseweb="calendar"] {
  background-color: @POP@ !important; color: @TXT@ !important; }
[data-baseweb="popover"] li, [role="option"] { background-color: @POP@ !important; color: @TXT@ !important; }
[data-baseweb="popover"] li:hover, [role="option"]:hover, [role="option"][aria-selected="true"] { background-color: @ACC@33 !important; }
[data-testid="stNumberInput"] button { background-color: @INPUT@ !important; color: @TXT@ !important; border-color: @BORDER@ !important; }
[data-testid="stChatInput"] > div { background-color: @INPUT@ !important; border-color: @BORDER@ !important; }
[data-testid="stExpander"] details { border: 1px solid @BORDER@ !important; border-radius: 12px; background-color: @CARD1@ !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: @TXT@ !important; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color: @BORDER@ !important; }
[data-testid="stAlert"] { background-color: @ACC@14 !important; border: 1px solid @ACC@55; border-radius: 12px; }
[data-testid="stAlert"] *, [data-testid="stToast"] * { color: @TXT@ !important; }
[data-testid="stToast"] { background-color: @POP@ !important; border: 1px solid @ACC@55; }
[data-testid="stSlider"] [role="slider"] { background-color: @ACC@ !important; }
[data-testid="stSlider"] [data-testid="stThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] { color: @ACC@ !important; }
[data-testid="stProgress"] [role="progressbar"] > div { background-color: @ACC@ !important; }
[data-testid="stButtonGroup"] button { background-color: @INPUT@ !important; color: @TXT@ !important; border: 1px solid @BORDER@ !important; }
[data-testid="stButtonGroup"] button p { color: inherit !important; }
[data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_controlActive"],
[data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[aria-pressed="true"] { background-color: @ACC@ !important; color: @ONACC@ !important; border-color: @ACC@ !important; }
.stButton > button, .stFormSubmitButton > button { background: @BTN@; color: @ACC@; border: 1px solid @ACC@; border-radius: 10px; }
.stButton > button:hover, .stFormSubmitButton > button:hover { background: @ACC@; color: @BTN@; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] { background: @ACC@; color: @ONACC@; border: 1px solid @ACC@; }
.stButton > button p, .stFormSubmitButton > button p { color: inherit !important; }
[data-baseweb="select"] > div { background-color: @INPUT@ !important; border: 1px solid @BORDER@ !important; }
[data-baseweb="select"] > div *:not(svg):not(path) { background-color: transparent !important; color: @TXT@ !important;
  -webkit-text-fill-color: @TXT@ !important; }
[data-baseweb="select"] svg { fill: @TXT@ !important; }
[data-baseweb="select"] [data-baseweb="tag"] { background-color: @ACC@ !important; }
[data-baseweb="select"] [data-baseweb="tag"] * { color: @ONACC@ !important; -webkit-text-fill-color: @ONACC@ !important; }
[data-testid="stExpander"] summary { background-color: @CARD1@ !important; color: @TXT@ !important; border-radius: 12px; }
[data-testid="stExpander"] summary:hover, [data-testid="stExpander"] details[open] > summary { background-color: @STAT@ !important; }
[data-testid="stExpander"] details > div { background-color: @CARD1@ !important; }
[data-testid="stForm"] { background-color: @CARD1@ !important; border: 1px solid @BORDER@ !important; }
[data-baseweb="radio"] > div:first-child, label[data-baseweb="checkbox"] > div:first-child { filter: hue-rotate(@HUE@); }
[data-baseweb="popover"] *, [data-baseweb="menu"] *, ul[role="listbox"] *, [data-baseweb="calendar"] *,
[data-baseweb="datepicker"] *, [data-baseweb="timepicker"] * { color: @TXT@ !important; }
[data-baseweb="select"] input, [data-baseweb="input"] input, .stTextInput input, .stNumberInput input,
.stTimeInput input, .stDateInput input, textarea { color: @TXT@ !important; -webkit-text-fill-color: @TXT@ !important;
  background-color: @INPUT@ !important; caret-color: @ACC@; }
input::placeholder, textarea::placeholder { color: @MUTE@ !important; -webkit-text-fill-color: @MUTE@ !important; opacity: 1; }
[data-baseweb="select"] > div, .stTextInput > div > div, .stNumberInput > div > div, .stTimeInput > div > div { background-color: @INPUT@ !important; border: 1px solid @BORDER@ !important; }
[data-baseweb="tooltip"], [data-testid="stTooltipContent"] { background-color: @POP@ !important; color: @TXT@ !important; }
[data-baseweb="tooltip"] *, [data-testid="stTooltipContent"] * { color: @TXT@ !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] [data-baseweb="radio"] div { color: @TXT@ !important; }
[data-testid="stColorPicker"] label p, [data-testid="stCheckbox"] label p, [data-testid="stToggle"] label p { color: @TXT@ !important; }
.stAlert p, [data-testid="stAlert"] p { color: @TXT@ !important; }
.zen { background: linear-gradient(135deg, @CARD1@, @STAT@); border: 2px solid @ACC@; border-radius: 26px; padding: 26px 30px;
  box-shadow: 0 6px 24px @ACC@22; margin: 8px 0 14px 0; }
.zen .zr { font-size: 2.05rem; font-weight: 700; color: @ACC@; line-height: 1.25; }
.zen .zl { font-size: 1.4rem; color: @TXT@; margin-top: 8px; font-weight: 500; }
.zen .zs { font-size: 1.02rem; color: @MUTE@; margin-top: 8px; }
[class*="st-key-zenbtn_"] button { min-height: 88px; font-size: 1.15rem !important; font-weight: 700; border-radius: 22px;
  border: 2px solid @ACC@ !important; width: 100%; }
.island { background: #0B0B10; color: #FFFFFF; border-radius: 34px; padding: 14px 24px; display: flex; flex-wrap: wrap;
  gap: 8px 22px; align-items: center; box-shadow: 0 8px 22px rgba(0,0,0,.35); margin: 6px 0 8px 0; }
.island .it { font-size: 1.02rem; color: #F5F5F7; font-weight: 600; }
.island .cap { font-size: .78rem; color: #A1A1AA; width: 100%; letter-spacing: .4px; }
.pre { background: linear-gradient(135deg, @CARD1@, @STAT@); border: 2px solid @ACC@; border-radius: 22px; padding: 18px 22px;
  margin: 8px 0 10px 0; box-shadow: 0 6px 22px @ACC@22; }
.pre .ph { font-size: 1.15rem; font-weight: 700; color: @ACC@; }
.pre .ps { font-size: .98rem; color: @TXT@; margin-top: 4px; }
.ptiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; margin: 10px 0 6px 0; }
.ptile { border-radius: 16px; padding: 12px 14px; border: 1px solid @BORDER@; background: @CARD1@; }
.ptile.on { border: 2px solid @ACC@; background: @ACC@14; }
.ptile .pi { font-size: 1.5rem; }
.ptile .pn { font-size: .85rem; color: @MUTE@; }
.ptile .pv { font-size: 1.15rem; font-weight: 700; color: @TXT@; }
.atbl { width: 100%; border-collapse: collapse; font-size: 0.9rem; background: @CARD1@; border: 1px solid @BORDER@; }
.atbl th { text-align: left; padding: 8px 10px; background: @STAT@; color: @ACC@; border-bottom: 1px solid @ACC@55; white-space: nowrap; }
.atbl td { padding: 7px 10px; color: @TXT@; border-bottom: 1px solid @BORDER@; }
.atbl tr:last-child td { border-bottom: none; }
.card { background: linear-gradient(145deg, @CARD1@, @CARD2@); border: 1px solid @ACC@55; border-radius: 16px; padding: 18px 20px; min-height: 130px; box-shadow: 0 4px 24px @ACC@14; }
.card h4 { margin: 0 0 8px 0; }
.card p { margin: 0; line-height: 1.55; color: @TXT2@; }
.banner { background: @ACC@14; border: 1px solid @ACC@; border-radius: 14px; padding: 14px 18px; margin: 10px 0 10px 0; }
.geo { background: linear-gradient(135deg, @ACC@33, @ACC@14); border: 2px solid @ACC@; border-radius: 16px; padding: 16px 20px; margin: 8px 0 8px 0; font-size: 1.05rem; line-height: 1.5; animation: geopulse 2s ease-in-out infinite; }
@keyframes geopulse { 0%, 100% { box-shadow: 0 0 0 0 @ACC@55; } 50% { box-shadow: 0 0 0 10px @ACC@00; } }
.pill { display: inline-block; border: 1px solid @ACC@; border-radius: 20px; padding: 1px 10px; font-size: 0.78rem; color: @ACC@; margin-left: 6px; }
.brand { font-size: 1.4rem; font-weight: 700; color: @ACC@; }
.stat { background: @STAT@; border: 1px solid @ACC@33; border-radius: 12px; padding: 10px 12px; min-height: 66px; margin-bottom: 8px; }
.stat .sl { font-size: 0.78rem; color: @SUB@; }
.stat .sv { font-size: 1.1rem; font-weight: 600; color: @TXT@; word-break: break-word; }
.sw { display: inline-block; width: 12px; height: 12px; border-radius: 50%; border: 1px solid @ACC@; margin-right: 6px; vertical-align: middle; }
.aibox { background: linear-gradient(145deg, @CARD1@, @CARD2@); border: 1px solid @ACC@66; border-radius: 14px; padding: 12px 16px; margin: 6px 0 10px 0; }
.logl { font-family: monospace; font-size: 0.8rem; color: @LOG@; margin: 2px 0; }
.chathead { display: flex; align-items: center; gap: 8px; background: @STAT@; border: 1px solid @ACC@44; border-radius: 14px 14px 0 0; padding: 10px 16px; color: @ACC@; font-weight: 600; }
.chathead .dot { width: 9px; height: 9px; border-radius: 50%; background: #4CD964; display: inline-block; }
.chathead small { color: @MUTE@; font-weight: 400; }
.chatbox { background: @CHATBG@; border: 1px solid @ACC@33; border-top: none; border-radius: 0 0 14px 14px; padding: 12px 12px 4px 12px; margin-bottom: 8px; }
.crow { display: flex; margin: 5px 0; }
.crow.me { justify-content: flex-end; }
.bub { max-width: 78%; padding: 9px 13px 19px 13px; border-radius: 18px; position: relative; line-height: 1.45; font-size: 0.97rem; word-wrap: break-word; }
.bub.me { background: linear-gradient(135deg, @ACC@, @ACC2@); color: @ONACC@; border-bottom-right-radius: 4px; }
.bub.dv { background: @BUBDV@; border: 1px solid @ACC@33; color: @TXT@; border-bottom-left-radius: 4px; }
.bub .ts { position: absolute; right: 11px; bottom: 3px; font-size: 0.64rem; opacity: 0.65; }
.bub.typing { padding: 12px 16px; }
.bub.typing span { display: inline-block; width: 7px; height: 7px; margin: 0 2px; border-radius: 50%; background: @ACC@; animation: blink 1.2s infinite; }
.bub.typing span:nth-child(2) { animation-delay: 0.2s; }
.bub.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%, 80%, 100% { opacity: 0.25; } 40% { opacity: 1; } }
</style>
"""


def native_light():
    """Streamlit's own theme."""
    try:
        return st.context.theme.type == "light"
    except Exception:
        return False


def is_light():
    """The sidebar Theme switch decides (Dark = black & gold, Light = white)."""
    choice = st.session_state.get("theme_choice")
    if choice in ("dark", "light"):
        return choice == "light"
    return native_light()


def pal():
    return PALETTES["light" if is_light() else "dark"]


def build_css():
    css = CSS_T
    for k, v in pal().items():
        css = css.replace("@" + k + "@", v)
    return css


def themed(page):
    """Colour tokens used by the small HTML components (audio player, chime button)."""
    p = pal()
    return (page.replace("__BG__", p["SIDE"]).replace("__BTN__", p["BTN"])
            .replace("__ACC__", p["ACC"]).replace("__SUB__", p["SUB"]))


def html_table(rows):
    """Theme-aware table."""
    if not rows:
        return
    cols = list(rows[0].keys())
    head = "".join("<th>" + html.escape(str(c)) + "</th>" for c in cols)
    body = "".join("<tr>" + "".join("<td>" + html.escape(str(r[c])) + "</td>" for c in cols) + "</tr>" for r in rows)
    st.markdown('<div style="overflow-x:auto"><table class="atbl"><thead><tr>' + head + "</tr></thead><tbody>" +
                body + "</tbody></table></div>", unsafe_allow_html=True)


def themed_line_chart(values, height=220):
    """Line chart painted with the active theme colours."""
    p = pal()
    values = list(values)
    ch = None
    try:
        import altair as alt
        df = pd.DataFrame({"i": list(range(len(values))), "v": values})
        axis = alt.Axis(title=None, labelColor=p["SUB"], gridColor=p["BORDER"], domainColor=p["BORDER"], tickColor=p["BORDER"])
        ch = (alt.Chart(df).mark_line(color=p["ACC"], strokeWidth=2.2)
              .encode(x=alt.X("i:Q", axis=None), y=alt.Y("v:Q", scale=alt.Scale(zero=False), axis=axis))
              .properties(height=height).configure(background="transparent").configure_view(strokeWidth=0))
    except Exception:
        ch = None
    if ch is not None:
        for kw in ({"theme": None, "use_container_width": True}, {"theme": None, "width": "stretch"}, {"theme": None}):
            try:
                st.altair_chart(ch, **kw)
                return
            except TypeError:
                continue
            except Exception:
                break
    st.line_chart(pd.DataFrame({"bpm": values}), height=height, color=p["ACC"])


def stat(label, value, extra=""):
    return ('<div class="stat"><div class="sl">' + html.escape(label) + '</div><div class="sv">' + extra +
            html.escape(str(value)) + "</div></div>")


# ----------------------------------------------------------------------------
# Static data
# ----------------------------------------------------------------------------
GENRES = ["Pop", "Rock", "Blues", "Hip-Hop", "Jazz", "Classical", "Metal", "Folk", "EDM", "Country",
          "Disco", "OM Mantra", "Chinese Zen", "Lo-Fi Chill", "Ambient Space", "Calm 432Hz"]
INSTRUMENTS = ["Piano", "Flute", "Rain", "Tabla", "Veena", "Singing Bowls", "Strings", "Ocean Waves", "Sitar", "Harp"]
SCENES = {"Warm Glow": "#FFB347", "Candlelight": "#FF8C42", "Aurora": "#5FFBB1", "Sunset": "#FF6B6B",
          "Ocean": "#3FA7D6", "Cool Focus": "#EAF4FF"}
AC_MODES = ["Cool", "Dry", "Fan Only", "Sleep Eco"]
FAN_MODES = {"Off": 0, "Breeze": 1, "Medium": 3, "Turbo": 5}
SPACE_TYPES = ["Living", "Bedroom", "Bath", "Workspace", "Kitchen", "Dining", "Reading", "Outdoor", "Entertainment", "Other"]
SPACE_ICONS = ["🛋️", "🛏️", "🛁", "💼", "🍳", "📚", "🌿", "🎮", "🧘", "🎬", "🚗", "🏠"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
PROTOS_BULB = ["Simulation", "Philips WiZ (UDP)", "Home Assistant / REST"]
PROTOS = ["Simulation", "Home Assistant / REST"]

# (id, icon, name, group, level label, min, max, default, ambience device used by modes)
CATALOG = [
    ("bulb", "💡", "Philips WiZ Smart Bulb", "Lighting", "Brightness", 5, 100, 60, False),
    ("ac", "❄", "Air Conditioner", "Air & Climate", "Temperature (°C)", 16, 30, 24, False),
    ("fan", "🌀", "Ceiling Fan", "Air & Climate", "Speed", 0, 5, 2, False),
    ("curtain", "🪟", "Smart Curtains / Blinds Motor", "Ambience", "Open position (%)", 0, 100, 50, False),
    ("scent", "🌸", "Smart Room Scent Sprayer", "Ambience", "Intensity", 0, 100, 40, True),
    ("diffuser", "💨", "Aroma Oil Diffuser", "Ambience", "Mist level", 0, 100, 50, True),
    ("speaker", "🔊", "Smart Speaker", "Ambience", "Volume", 0, 100, 30, True),
    ("ledstrip", "🌈", "LED Strip Lights", "Lighting", "Brightness", 0, 100, 60, True),
    ("lamp", "🛋", "Smart Table Lamp", "Lighting", "Brightness", 0, 100, 50, True),
    ("dimmer", "🎚", "Smart Dimmer Switch", "Lighting", "Level", 0, 100, 70, False),
    ("switch", "🔘", "Smart Switch", "Power", None, 0, 0, 0, False),
    ("board", "🔲", "Smart Switch Board (4-gang)", "Power", None, 0, 0, 0, False),
    ("plug", "🔌", "Smart Plug", "Power", None, 0, 0, 0, False),
    ("purifier", "🌿", "Air Purifier", "Air & Climate", "Fan speed", 0, 100, 40, True),
    ("humid", "💧", "Humidifier", "Air & Climate", "Mist level", 0, 100, 50, True),
    ("dehum", "🏜", "Dehumidifier", "Air & Climate", "Target humidity (%)", 30, 80, 55, False),
    ("heater", "🔥", "Room Heater", "Air & Climate", "Temperature (°C)", 16, 30, 22, False),
    ("cooler", "🧊", "Air Cooler", "Air & Climate", "Fan speed", 0, 100, 50, False),
    ("thermo", "🌡", "Smart Thermostat", "Air & Climate", "Target (°C)", 16, 30, 24, False),
    ("aqm", "🧪", "Air Quality Monitor", "Air & Climate", None, 0, 0, 0, False),
    ("geyser", "🚿", "Smart Water Heater (Geyser)", "Water", "Temperature (°C)", 30, 75, 45, False),
    ("pump", "🚰", "Smart Water Pump / Tank Controller", "Water", None, 0, 0, 0, False),
    ("wpur", "🫗", "Smart Water Purifier", "Water", None, 0, 0, 0, False),
    ("leak", "💦", "Water Leak Sensor", "Water", None, 0, 0, 0, False),
    ("irrig", "🌱", "Garden Irrigation Controller", "Outdoor", "Duration (min)", 1, 60, 10, False),
    ("tv", "📺", "Smart TV", "Entertainment", "Volume", 0, 100, 25, False),
    ("projector", "🎞", "Smart Projector", "Entertainment", "Brightness", 0, 100, 70, False),
    ("mattress", "🛏", "Smart Mattress Warmer", "Sleep", "Warmth", 0, 100, 30, True),
    ("sleepsens", "😴", "Sleep Tracker Pad", "Sleep", None, 0, 0, 0, False),
    ("lock", "🔐", "Smart Door Lock", "Security", None, 0, 0, 0, False),
    ("camera", "📹", "CCTV / Security Camera", "Security", None, 0, 0, 0, False),
    ("doorbell", "🔔", "Video Doorbell", "Security", None, 0, 0, 0, False),
    ("smoke", "🚨", "Smoke / Gas Detector", "Security", None, 0, 0, 0, False),
    ("garage", "🚗", "Garage Door Opener", "Security", None, 0, 0, 0, False),
    ("vacuum", "🤖", "Robot Vacuum", "Appliances", "Suction", 0, 100, 60, False),
    ("washer", "🧺", "Smart Washing Machine", "Appliances", None, 0, 0, 0, False),
    ("fridge", "🥶", "Smart Refrigerator", "Appliances", "Temperature (°C)", 1, 8, 4, False),
    ("coffee", "☕", "Smart Coffee Maker", "Appliances", "Strength", 1, 10, 5, False),
    ("kettle", "🫖", "Smart Kettle", "Appliances", "Temperature (°C)", 40, 100, 90, False),
    ("ev", "⚡", "EV Charger", "Energy", "Charge limit (%)", 50, 100, 80, False),
    ("solar", "☀", "Solar Inverter Monitor", "Energy", None, 0, 0, 0, False),
    ("pet", "🐾", "Smart Pet Feeder", "Pets", None, 0, 0, 0, False),
    ("aquarium", "🐠", "Aquarium Controller", "Pets", "Light (%)", 0, 100, 60, False),
    ("towel", "♨", "Towel Warmer", "Water", "Warmth", 0, 100, 50, False),
    ("spatial", "🎶", "Spatial Speaker", "Ambience", "Volume", 0, 100, 30, True),
    ("focusaudio", "🎧", "Focus Audio", "Ambience", "Volume", 0, 100, 25, True),
    ("soundpad", "🎼", "Acoustic Sound Pad", "Ambience", "Volume", 0, 100, 25, True),
    ("tasklight", "🔦", "Task Lights", "Lighting", "Brightness", 0, 100, 80, False),
    ("ambilight", "🪔", "Ambient Lighting", "Lighting", "Brightness", 0, 100, 40, False),
    ("wallsw", "🔘", "Smart Wall Switches", "Power", None, 0, 0, 0, False),
]
CAT = {c[0]: c for c in CATALOG}
AMB = [c[0] for c in CATALOG if c[8]]
UNIT = {"bulb": "%", "ac": " °C", "curtain": "% open", "fan": "", "geyser": " °C", "heater": " °C", "thermo": " °C",
        "fridge": " °C", "kettle": " °C", "coffee": "", "irrig": " min"}
# Pre-configured zones: name -> (icon, type, [(device type, label)])
DEFAULT_SPACES = {
    "Living Lounge": ("🛋️", "Living", [("bulb", "Bulbs"), ("fan", "Fan"), ("ac", "AC"), ("spatial", "Spatial Speaker"),
                                       ("diffuser", "Scent Diffuser")]),
    "Master Suite": ("🛏️", "Bedroom", [("bulb", "Bulbs"), ("fan", "Fan"), ("ac", "AC"), ("diffuser", "Scent Diffuser"),
                                       ("curtain", "Smart Curtains"), ("mattress", "Smart Mattress")]),
    "En-Suite Bath": ("🛁", "Bath", [("geyser", "Smart Water Heater / Geyser"), ("towel", "Towel Warmer"),
                                     ("ambilight", "Ambient Lighting")]),
    "Work Studio": ("💼", "Workspace", [("bulb", "Task Bulbs"), ("fan", "Fan"), ("ac", "AC"), ("purifier", "Air Purifier"),
                                        ("focusaudio", "Focus Audio")]),
    "Kitchen": ("🍳", "Kitchen", [("coffee", "Smart Coffee Brewer"), ("wallsw", "Smart Wall Switches"),
                                  ("tasklight", "Task Lights")]),
    "Reading Room": ("📚", "Reading", [("bulb", "Warm Bulbs"), ("ac", "AC"), ("soundpad", "Acoustic Sound Pad"),
                                       ("curtain", "Curtains")]),
    "Dining Area": ("🍽️", "Dining", [("bulb", "Dining Bulbs"), ("fan", "Fan"), ("ac", "AC")]),
}

DEFAULT_MODES = {
    "Deep Meditation": {"bulb": "#2B1B5E", "bright": 25, "fan": 1, "ac": 24, "curtain": 20, "genre": "OM Mantra",
                        "extras": ["scent", "purifier", "speaker", "diffuser"]},
    "Sleep": {"bulb": "#3A1F00", "bright": 10, "fan": 1, "ac": 25, "curtain": 0, "genre": "Ambient Space",
              "extras": ["purifier", "mattress"]},
    "Focus": {"bulb": "#FFF4E0", "bright": 90, "fan": 2, "ac": 23, "curtain": 70, "genre": "Lo-Fi Chill",
              "extras": ["purifier", "speaker", "lamp"]},
    "Relax Evening": {"bulb": "#FFB347", "bright": 55, "fan": 2, "ac": 24, "curtain": 30, "genre": "Jazz",
                      "extras": ["scent", "speaker"]},
    "Energize": {"bulb": "#FFFFFF", "bright": 100, "fan": 4, "ac": 22, "curtain": 100, "genre": "EDM",
                 "extras": ["speaker", "ledstrip"]},
    "Zen Garden": {"bulb": "#9FD8B0", "bright": 60, "fan": 2, "ac": 24, "curtain": 60, "genre": "Chinese Zen",
                   "extras": ["scent", "speaker", "purifier", "diffuser"]},
    "Deep Calm Studio": {"bulb": "#0B3C7A", "bright": 30, "fan": 1, "ac": 22, "curtain": 30, "genre": "Calm 432Hz",
                         "extras": ["purifier", "focusaudio"]},
    "Wind-Down Sleep": {"bulb": "#3A1F00", "bright": 8, "fan": 1, "ac": 21, "curtain": 0, "genre": "Calm 432Hz",
                        "extras": ["purifier", "mattress"]},
    "Cinema Night": {"bulb": "#3B1F6B", "bright": 15, "fan": 2, "ac": 23, "curtain": 0, "genre": "Classical",
                     "extras": ["speaker"]},
    "Neutral Family Ambience": {"bulb": "#FFE6C7", "bright": 55, "fan": 2, "ac": 24, "curtain": 50, "genre": "Ambient Space",
                                "extras": ["speaker"]},
}
NEUTRAL_MODE = "Neutral Family Ambience"
CINEMA_MODE = "Cinema Night"
# Room personas: personal sanctuaries follow one person, shared family zones protect the whole family
PERSONAL_ZONES = ("Work Studio", "Master Suite", "En-Suite Bath", "Reading Room")
SHARED_ZONES = ("Living Lounge", "Kitchen", "Dining Area")
BASE_MIX = {k: 0 for k in INSTRUMENTS}

# Device behaviour the AI applies when the detected body state changes: (device, on, level, reason)
STATE_RULES = {
    "sleep": [("bulb", False, None, "lights off for deep sleep"), ("ledstrip", False, None, "LED strip off"),
              ("lamp", False, None, "table lamp off"),
              ("curtain", True, 0, "closing the curtains for darkness and deep sleep"),
              ("lock", True, None, "locking the door for the night"),
              ("tv", False, None, "switching the TV off"), ("projector", False, None, "projector off"),
              ("coffee", False, None, "coffee maker off"), ("kettle", False, None, "kettle off"),
              ("geyser", False, None, "water heater off while you sleep"),
              ("speaker", True, 8, "very low volume for sleep sounds"),
              ("mattress", True, 30, "warming the bed gently")],
    "wake": [("bulb", True, 60, "warm, gentle light to wake you softly"),
             ("curtain", True, 100, "opening the curtains to welcome daylight"),
             ("geyser", True, 45, "heating water for your morning"), ("coffee", True, 5, "brewing your coffee"),
             ("speaker", True, 25, "soft morning music"), ("mattress", False, None, "bed warmer off"),
             ("lock", False, None, "unlocking the door")],
    "stress": [("curtain", True, 25, "softening the daylight to calm you"),
               ("tv", False, None, "TV off to reduce stimulation"), ("speaker", True, 30, "calming sounds on"),
               ("scent", True, 60, "calming scent on")],
    "active": [("curtain", True, 90, "letting daylight in for energy"), ("speaker", True, 40, "energising volume")],
    "relaxed": [("speaker", True, 30, "relaxed background volume")],
}
STATE_EN = {"sleep": "asleep", "wake": "waking up", "stress": "stressed", "active": "active", "relaxed": "relaxed"}


# ----------------------------------------------------------------------------
# Device registry, connection layer and logging
# ----------------------------------------------------------------------------
def log(text):
    ss = st.session_state
    ss.log = ([{"t": datetime.now().strftime("%H:%M:%S"), "x": text}] + ss.log)[:60]


def new_device(cid, name, room):
    ss = st.session_state
    c = CAT[cid]
    ss.uid += 1
    return {"uid": ss.uid, "cid": cid, "name": name, "room": room, "on": False,
            "lvl": c[7] if c[4] else 0, "color": "#FFB347", "proto": "Simulation", "addr": "", "token": "",
            "status": "connected", "last": "", "rev": 0}


HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def valid_hex(c):
    return isinstance(c, str) and bool(HEX_RE.match(c.strip()))


def safe_hex(c, fallback="#FFB347"):
    return c.strip() if valid_hex(c) else fallback


def hex_rgb(h):
    h = safe_hex(h).lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def valid_mode_name(n):
    return isinstance(n, str) and bool(re.fullmatch(r"\w[\w \-&'.()]{0,39}", n.strip()))


def full_mix(m=None):
    """Always returns all 10 instruments as clamped ints (0-100)."""
    m = m if isinstance(m, dict) else {}
    out = {}
    for k in INSTRUMENTS:
        try:
            v = int(float(m.get(k, 0)))
        except (TypeError, ValueError):
            v = 0
        out[k] = max(0, min(100, v))
    return out


def any_mix(m):
    return isinstance(m, dict) and any(full_mix(m).values())


def wiz_send(addr, payload):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1.0)
    try:
        s.sendto(json.dumps(payload).encode("utf-8"), (addr, 38899))
        data, _ = s.recvfrom(2048)
        return json.loads(data.decode("utf-8"))
    finally:
        s.close()


def push(dev):
    """Send the device's current state to the real device (no-op for Simulation)."""
    if dev["proto"] == "Simulation" or dev["status"] != "connected" or not dev["addr"]:
        return
    try:
        if dev["proto"].startswith("Philips"):
            r, g, b = hex_rgb(dev["color"])
            params = {"state": bool(dev["on"]), "dimming": max(10, int(dev["lvl"])), "r": r, "g": g, "b": b}
            wiz_send(dev["addr"], {"id": 1, "method": "setPilot", "params": params})
        else:
            body = {"source": "AuraSync", "device": dev["name"], "type": dev["cid"], "room": dev["room"],
                    "state": "on" if dev["on"] else "off", "level": dev["lvl"], "color": dev["color"]}
            hdr = {"Authorization": "Bearer " + dev["token"]} if dev["token"] else {}
            requests.post(dev["addr"], json=body, headers=hdr, timeout=2)
        dev["last"] = "sent " + datetime.now().strftime("%H:%M:%S") + (" via cloud relay" if st.session_state.conn["mode"] == "away" else " via local mesh")
    except Exception as e:
        dev["status"] = "offline"
        dev["last"] = type(e).__name__


def connect_device(dev):
    """Handshake with the device. Simulation always succeeds; real transports are really probed."""
    try:
        if dev["proto"] == "Simulation":
            dev["status"], dev["last"] = "connected", "simulated device ready"
        elif dev["proto"].startswith("Philips"):
            res = wiz_send(dev["addr"], {"id": 1, "method": "getPilot", "params": {}})
            ok = bool(res)
            dev["status"], dev["last"] = ("connected" if ok else "offline"), ("WiZ answered" if ok else "no answer")
        else:
            hdr = {"Authorization": "Bearer " + dev["token"]} if dev["token"] else {}
            r = requests.get(dev["addr"], headers=hdr, timeout=2)
            dev["status"] = "connected" if r.status_code < 500 else "offline"
            dev["last"] = "HTTP " + str(r.status_code)
    except Exception as e:
        dev["status"], dev["last"] = "offline", type(e).__name__
    return dev["status"] == "connected"


def set_dev(dev, on=None, lvl=None, color=None, why=""):
    """Single entry point for every device change."""
    before = (dev["on"], dev["lvl"], dev["color"])
    if on is not None:
        dev["on"] = bool(on)
    if lvl is not None:
        c = CAT[dev["cid"]]
        try:
            dev["lvl"] = max(c[5], min(c[6], int(lvl))) if c[4] else 0
        except (TypeError, ValueError):
            pass
    if color is not None and valid_hex(color):
        dev["color"] = color.strip()
    changed = before != (dev["on"], dev["lvl"], dev["color"])
    if changed:
        dev["rev"] = dev.get("rev", 0) + 1
        push(dev)
        if why:
            c = CAT[dev["cid"]]
            state = "ON" if dev["on"] else "OFF"
            lv = (" " + str(dev["lvl"]) + UNIT.get(dev["cid"], "%")) if (dev["on"] and c[4]) else ""
            log(c[1] + " " + dev["name"] + ": " + state + lv + " - " + why)
    return changed


# ----------------------------------------------------------------------------
# Spaces, presence (Follow-Me), holds, geofence and routines
# ----------------------------------------------------------------------------
CUT_CIDS = {"bulb", "tasklight", "ambilight", "lamp", "ledstrip", "dimmer", "fan", "ac", "scent", "diffuser",
            "speaker", "spatial", "focusaudio", "soundpad"}
GLOBAL_CIDS = {"geyser", "coffee", "lock", "kettle", "tv", "projector"}
BULBLIKE = ("bulb", "tasklight", "ambilight")
EQUIV = {"spatial": "speaker", "focusaudio": "speaker", "soundpad": "speaker", "diffuser": "scent",
         "tasklight": "bulb", "ambilight": "bulb"}
CALM_ROOMS = ("Work Studio",)
# Spaces that built-in automations look up by name (geofence, routines, calm mode)
PROTECTED_SPACES = ("En-Suite Bath", "Master Suite", "Work Studio")
CALM_MODE = "Deep Calm Studio"
WIND_MODE = "Wind-Down Sleep"
HOLD_FOREVER = 10 ** 12
UWB_DEVICES = ["Apple Watch Series 6", "Apple Watch Series 7", "Apple Watch Series 8", "Apple Watch Series 9",
               "Apple Watch Series 10", "Apple Watch Ultra", "iPhone (UWB)", "Samsung Galaxy S-Ultra", "UWB Tag"]
BLE_DEVICES = ["Oura Ring", "Ultrahuman Ring", "Fitness Band (no UWB)"]


def engine_of(name):
    return "UWB" if name in UWB_DEVICES else "BLE"


def space_devs(name):
    ss = st.session_state
    sp = ss.spaces.get(name)
    if not sp:
        return []
    ids = set(sp["devices"])
    return [d for d in ss.fleet if d["uid"] in ids]


def assign_device(dev, room):
    ss = st.session_state
    for sp in ss.spaces.values():
        if dev["uid"] in sp["devices"]:
            sp["devices"].remove(dev["uid"])
    ss.spaces[room]["devices"].append(dev["uid"])
    dev["room"] = room


def find_dev(room, cid):
    return next((d for d in space_devs(room) if d["cid"] == cid), None)


def held(d):
    return st.session_state.holds.get(d["uid"], 0) > time.time()


def hold(d, secs):
    st.session_state.holds[d["uid"]] = time.time() + secs


def scope_devs():
    """Devices that the current atmosphere / automation is allowed to touch."""
    ss = st.session_state
    if ss.cfg["follow_me"] and ss.presence["room"] in ss.spaces:
        return space_devs(ss.presence["room"])
    return list(ss.fleet)


def eff_mode():
    """The atmosphere that is really playing around you."""
    ss = st.session_state
    if ss.conn["mode"] == "home":
        return ss.room_mode.get(ss.presence["room"], ss.active_mode)
    return ss.active_mode


def first_name():
    p = st.session_state.get("profile")
    return p["name"].split()[0] if p and p.get("name") else "Mani"


def eta_min(km):
    return int(round(km * 3))


def apply_mode(name, why=True, devs=None, set_active=True):
    """Sync bulbs, AC, fan, curtains and ambient devices to a mode."""
    ss = st.session_state
    env = ss.modes[name]
    if set_active:
        ss.active_mode = name
        ss.cfg["mix"] = full_mix(env["mix"]) if any_mix(env.get("mix")) else full_mix(ss.cfg.get("mix"))
    pool = scope_devs() if devs is None else devs
    extras = env.get("extras", [])
    for d in pool:
        if held(d):
            continue
        c = d["cid"]
        if c in BULBLIKE:
            set_dev(d, env.get("bulb_on", True), env.get("bright", 60), safe_hex(env.get("bulb")))
        elif c == "ac":
            set_dev(d, env.get("ac_on", True), env["ac"])
        elif c == "fan":
            set_dev(d, env.get("fan_on", True), env["fan"])
        elif c == "curtain":
            set_dev(d, True, env.get("curtain", 50))
        elif CAT[c][8]:
            set_dev(d, c in extras or EQUIV.get(c) in extras)
    if why:
        where = (" in " + ss.presence["room"]) if (devs is None and ss.cfg["follow_me"]) else ""
        log("🎼 Atmosphere '" + name + "' applied (" + env["genre"] + ")" + where)


def apply_rules(state):
    ss = st.session_state
    h = datetime.now().hour
    scope = [d for d in scope_devs() if d["room"] not in ss.room_mode]
    for cid, on, lvl, why in STATE_RULES.get(state, []):
        pool = ss.fleet if cid in GLOBAL_CIDS else scope
        for d in pool:
            if held(d) or EQUIV.get(d["cid"], d["cid"]) != cid:
                continue
            set_dev(d, on, lvl, why=why)
    if state == "relaxed":
        for d in scope:
            if d["cid"] == "curtain" and not held(d):
                day = 7 <= h < 17
                set_dev(d, True, max(d["lvl"], 70) if day else 30,
                        why="keeping daylight in" if day else "evening privacy and calm")


def fine_tune(r, state):
    """Continuously nudge AC / fan from skin temperature and trim the water heater schedule."""
    ss = st.session_state
    ss.skin_hist = (ss.skin_hist + [r["skin"]])[-5:]
    skin = sum(ss.skin_hist) / len(ss.skin_hist)
    env = ss.modes[ss.active_mode]
    dac, dfan, why = int(env["ac"]), int(env["fan"]), "back to the atmosphere baseline"
    if skin >= 34.4:
        dac, dfan = dac - 1, min(5, dfan + 1)
        why = "body warmth {:.1f} °C is high: a little more cooling".format(skin)
    elif skin <= 32.9:
        dac, dfan = dac + 1, max(0, dfan - 1)
        why = "body warmth {:.1f} °C is low: easing the chill".format(skin)
    for d in scope_devs():
        if held(d) or d["room"] in ss.room_mode:
            continue
        if d["cid"] == "ac" and d["on"]:
            set_dev(d, lvl=dac, why=why)
        elif d["cid"] == "fan" and d["on"]:
            set_dev(d, lvl=dfan, why=why)
    for d in ss.fleet:
        if d["cid"] == "geyser" and state == "sleep" and 5 <= datetime.now().hour < 7 and not d["on"] and not held(d):
            set_dev(d, True, 45, why="pre-heating water before your usual wake-up")


def room_persona(name):
    sp = st.session_state.spaces.get(name, {})
    if sp.get("persona") in ("personal", "shared"):
        return sp["persona"]
    if name in SHARED_ZONES:
        return "shared"
    if name in PERSONAL_ZONES:
        return "personal"
    return "shared" if sp.get("type") in ("Living", "Kitchen", "Dining", "Entertainment") else "personal"


def family_blocked():
    """Guest Mode, or a shared room with 2+ people."""
    ss = st.session_state
    return bool(ss.get("guest_mode")) or ss.presence["room"] in ss.get("family_lock", ())


def clear_room_override(room):
    ss = st.session_state
    if room not in ss.get("family_lock", ()):
        ss.room_mode.pop(room, None)


def automation_step(res, r):
    """Aura Companion: acts on devices when the detected state changes."""
    ss = st.session_state
    if family_blocked():
        return False
    state, changed = res["state"], False
    calm = bool(ss.room_mode.get(ss.presence["room"]))
    if state != ss.last_state:
        ss.last_state = state
        log("🌿 Aura noticed you are " + STATE_EN[state] + " - " + res["reason"])
        target = state_mode(state)
        if target != ss.active_mode:
            if calm:
                ss.active_mode = target
            else:
                apply_mode(target)
                changed = True
        if not calm:
            apply_rules(state)
    fine_tune(r, state)
    return changed


# ---- Follow-Me and room-isolated calm
def move_user(room):
    ss = st.session_state
    old = ss.presence["room"]
    if room == old or room not in ss.spaces:
        return
    ss.presence["room"] = room
    eng = engine_of(ss.cfg["tracker"])
    if not ss.cfg["follow_me"]:
        log("📍 " + eng + " tracking: you moved " + old + " → " + room + " (Follow-Me is off)")
        return
    if ss.get("guest_mode"):
        log("📍 Guest Mode: you moved " + old + " → " + room + ". No shutdowns, the home stays welcoming for everyone")
        return
    eco = ss.cfg["cut_mode"] == "Eco standby"
    cut = woke = 0
    for d in ([] if old in ss.get("family_lock", ()) else space_devs(old)):
        if d["cid"] in CUT_CIDS and not held(d):
            if d["cid"] == "ac" and eco:
                cut += 1 if set_dev(d, True, 27) else 0
            else:
                cut += 1 if set_dev(d, False) else 0
    clear_room_override(old)
    if room in ss.get("family_lock", ()):
        log("📍 " + old + " → " + room + ": the family is here, so the room keeps its Neutral Family Ambience")
        return
    target = space_devs(room)
    before = {d["uid"]: (d["on"], d["lvl"], d["color"]) for d in target}
    if ss.cfg["auto_mode"] and ss.spaces[room].get("preset"):
        apply_preset(room, why=False)
        label = "its saved room default"
    else:
        apply_mode(ss.active_mode, why=False, devs=target, set_active=False)
        label = "'" + ss.active_mode + "'"
    woke = sum(1 for d in target if before[d["uid"]] != (d["on"], d["lvl"], d["color"]))
    log("📍 " + eng + " tracking: " + old + " → " + room + ". Follow-Me: " + str(cut) + " device(s) in " + old +
        (" dropped to eco standby/off" if eco else " switched off") + ", " + str(woke) + " device(s) in " + room +
        " woke up with " + label)


def on_sim_move(key):
    ss = st.session_state
    r = ss.get(key)
    if r not in ss.spaces:
        ss.room_rev = ss.get("room_rev", 0) + 1
        return
    move_user(r)
    set_active_room(ss.presence["room"])
    ss.flash = "📍 " + tr_room(ss.presence["room"])


def room_calm_step(hr):
    """Heart rate above 85 BPM in the Work Studio calms ONLY that room."""
    ss, cfg = st.session_state, st.session_state.cfg
    room = ss.presence["room"]
    if family_blocked():
        return None
    active = cfg["auto_mode"] and cfg["calm_on"] and ss.conn["mode"] == "home"
    cur = ss.room_mode.get(room)
    if room in CALM_ROOMS and active and hr > 85 and cur != CALM_MODE:
        ss.room_mode[room] = CALM_MODE
        apply_mode(CALM_MODE, why=False, devs=space_devs(room), set_active=False)
        log("🌊 " + room + " calm mode ON (heartbeat " + str(hr) + " bpm): deep ocean blue light, 432Hz ambient sound, "
            "22 °C. Only " + room + " changed; the rest of the house is untouched.")
        return "on"
    if cur == CALM_MODE and (hr <= 80 or not active or room not in CALM_ROOMS):
        ss.room_mode.pop(room, None)
        apply_mode(ss.active_mode, why=False, devs=space_devs(room), set_active=False)
        log("🌤 " + room + " back to your normal atmosphere (" + ss.active_mode + ")")
        return "off"
    return None


# ---- Remote control and smart geofence
def switch_conn(mode):
    ss = st.session_state
    if mode not in ("home", "away") or mode == ss.conn["mode"]:
        return
    ss.conn["mode"] = mode
    ss.geo = {"state": "idle", "chimed": False, "km": 20, "rev": ss.geo.get("rev", 0) + 1}
    if mode == "home":
        for uid, ts in list(ss.holds.items()):
            if ts >= HOLD_FOREVER:
                del ss.holds[uid]
        log("🏠 Welcome home: back on local control (Matter / Wi-Fi mesh)")
    else:
        log("🚗 You are away: commands now use the 4G/5G cloud relay")


def set_conn():
    ss = st.session_state
    switch_conn(ss.get("conn_sel", ss.conn["mode"]))


# Luxury arrival pre-conditioning: (room, device type, target)
GEO_PARTS = {"geyser": ("En-Suite Bath", "geyser", 42), "ac": ("Master Suite", "ac", 22), "fan": ("Master Suite", "fan", 2)}
GEO_ICON = {"geyser": "🚿", "ac": "❄️", "fan": "🌀"}
GEO_NAME = {"geyser": "Geyser · En-Suite Bath", "ac": "AC · Master Suite", "fan": "Ceiling Fan · Master Suite"}


def geo_dev(part):
    room, cid, _ = GEO_PARTS[part]
    return find_dev(room, cid)


def geo_autorun(auto=True):
    """Zero-touch: pre-condition the home through the cloud relay and lock it against competing ambient loops."""
    ss = st.session_state
    for part, (room, cid, lvl) in GEO_PARTS.items():
        d = geo_dev(part)
        if d:
            set_dev(d, True, lvl, why="☁️ cloud relay: luxury arrival pre-conditioning")
            hold(d, HOLD_FOREVER)
    ss.geo.update(state="active", chimed=False, auto=bool(auto))
    log(("✨ Zero-touch: " if auto else "✅ You confirmed: ") + "Geyser 42 °C, Master Suite AC 22 °C and Ceiling Fan speed 2 "
        "were switched on through the cloud relay")
    ss.flash = "✨ " + t("geo_started")


def geo_check():
    ss = st.session_state
    km = int(ss.geo.get("km", 20))
    if ss.conn["mode"] != "away":
        return
    if km <= 5 and ss.geo["state"] == "idle":
        if ss.cfg.get("geo_auto", True):
            geo_autorun(True)
        else:
            ss.geo.update(state="pending", chimed=False)
            log("📍 Geofence: you entered the 5 km / 15 min zone. Waiting for your confirmation; nothing was switched on")
    elif km > 5 and ss.geo["state"] in ("pending", "dismissed", "standby"):
        ss.geo.update(state="idle", chimed=False)


def cb_geo_slider(key):
    ss = st.session_state
    try:
        ss.geo["km"] = max(0, min(20, int(ss.get(key, ss.geo["km"]))))
    except (TypeError, ValueError):
        return
    geo_check()


def geo_jump(km):
    ss = st.session_state
    ss.geo["km"] = int(km)
    ss.geo["rev"] = ss.geo.get("rev", 0) + 1   # rebuilds the slider with the new value
    geo_check()


def cb_geo_auto(key):
    ss = st.session_state
    ss.cfg["geo_auto"] = bool(ss.get(key))
    if ss.cfg["geo_auto"] and ss.conn["mode"] == "away" and ss.geo["state"] == "pending":
        geo_autorun(True)


def geo_part_set(part, on):
    """One-touch override: switch ONE appliance off (or back on)."""
    ss = st.session_state
    d = geo_dev(part)
    if d is None:
        return
    target = GEO_PARTS[part][2]
    set_dev(d, bool(on), target if on else None, why="☁️ cloud relay: " + ("switched back on" if on else "switched off by you"))
    hold(d, HOLD_FOREVER)
    log(GEO_ICON[part] + " " + GEO_NAME[part] + (" back ON" if on else " turned OFF alone; the other appliances keep running"))
    ss.flash = GEO_ICON[part] + " " + t("geo_on_again" if on else "geo_off_alone", n=GEO_NAME[part].split(" · ")[0])


def geo_cancel_all():
    ss = st.session_state
    for part in GEO_PARTS:
        d = geo_dev(part)
        if d:
            set_dev(d, False, why="☁️ cloud relay: arrival routine cancelled")
            ss.holds.pop(d["uid"], None)
    ss.geo.update(state="standby", chimed=True)
    log("🛑 Arrival routine cancelled: all pre-conditioned appliances are OFF and the home is back on standby")
    ss.flash = "🛑 " + t("geo_cancelled")


def geo_restart():
    st.session_state.geo["state"] = "idle"
    geo_check()


def geo_confirm():
    geo_autorun(False)


def geo_dismiss():
    ss = st.session_state
    ss.geo["state"] = "dismissed"
    log("❌ Geofence alert dismissed: all home appliances stay on standby")
    ss.flash = "❌ " + t("geo_dismissed")


# ---- Daily routines
def fmt12(tm):
    return tm.strftime("%I:%M %p")


def shift_t(tm, minutes):
    return (datetime.combine(date.today(), tm) + timedelta(minutes=minutes)).time()


def default_routines():
    return [
        {"id": "wake", "kind": "wake_bath", "name": "Morning Wake-Up & Hot Bath", "enabled": True,
         "wake": dtime(6, 30), "bath": dtime(6, 45), "offset": 20},
        {"id": "night", "kind": "wind_down", "name": "Night Wind-Down Routine", "enabled": True,
         "sleep": dtime(22, 30), "offset": 30},
    ]


def routine_events(r):
    off = int(r.get("offset", 0))
    if r["kind"] == "wake_bath":
        return [("geyser", shift_t(r["bath"], -off)), ("wake", r["wake"])]
    if r["kind"] == "wind_down":
        return [("wind", shift_t(r["sleep"], -off))]
    return [("custom", shift_t(r["time"], -off))]


def routine_logic(r):
    off = int(r.get("offset", 0))
    if r["kind"] == "wake_bath":
        return ("Geyser will automatically switch ON at " + fmt12(shift_t(r["bath"], -off)) + " so hot water is ready exactly at " +
                fmt12(r["bath"]) + " without manual switching. At " + fmt12(r["wake"]) +
                ", Master Suite curtains open and the bulbs rise gently.")
    if r["kind"] == "wind_down":
        return ("At " + fmt12(shift_t(r["sleep"], -off)) + ", Master Suite AC will set to 21°C, smart curtains will close (0%), "
                "and 432Hz ambient sleep audio will begin fading in.")
    names = ", ".join(d["name"] for d in st.session_state.fleet if d["uid"] in r.get("uids", [])) or "-"
    return "At " + fmt12(shift_t(r["time"], -off)) + ", " + names + " will switch " + ("ON" if r.get("on", True) else "OFF") + "."


def exec_event(r, tag):
    ss = st.session_state
    off = int(r.get("offset", 0))
    nm = "⏰ " + r["name"]
    if tag == "geyser":
        d = find_dev("En-Suite Bath", "geyser") or next((x for x in ss.fleet if x["cid"] == "geyser"), None)
        if d:
            set_dev(d, True, why=nm + ": heating now so hot water is ready at " + fmt12(r["bath"]))
            hold(d, (off + 45) * 60)
    elif tag == "wake":
        ss.room_mode.pop("Master Suite", None)
        cur, bulb = find_dev("Master Suite", "curtain"), find_dev("Master Suite", "bulb")
        if cur:
            set_dev(cur, True, 100, why=nm + ": opening the curtains to welcome you")
            hold(cur, 20 * 60)
        if bulb:
            set_dev(bulb, True, 40, "#FFB347", why=nm + ": soft warm light")
            hold(bulb, 20 * 60)
    elif tag == "wind":
        ac, cur = find_dev("Master Suite", "ac"), find_dev("Master Suite", "curtain")
        if ac:
            set_dev(ac, True, 21, why=nm + ": cooling the Master Suite to 21 °C")
            hold(ac, 90 * 60)
        if cur:
            set_dev(cur, True, 0, why=nm + ": closing the curtains")
            hold(cur, 90 * 60)
        ss.room_mode["Master Suite"] = WIND_MODE
        ss.fade_tok += 1
        log(nm + ": 432Hz ambient sleep audio is fading in (press Play once to start sound)")
    else:
        for uid in r.get("uids", []):
            d = next((x for x in ss.fleet if x["uid"] == uid), None)
            if d:
                set_dev(d, r.get("on", True), why=nm)
                hold(d, 30 * 60)


def run_routines():
    """Fire any routine whose start time was reached in the last 30 minutes."""
    ss = st.session_state
    now = datetime.now()
    today = now.date().isoformat()
    ran = False
    for r in ss.daily_routines:
        if not r["enabled"]:
            continue
        for tag, tm in routine_events(r):
            trig = datetime.combine(now.date(), tm)
            key = r["id"] + ":" + tag
            if trig <= now < trig + timedelta(minutes=30) and ss.routine_runs.get(key) != today:
                ss.routine_runs[key] = today
                exec_event(r, tag)
                ran = True
    return ran


def run_routine_now(rid):
    ss = st.session_state
    r = next((x for x in ss.daily_routines if x["id"] == rid), None)
    if r:
        for tag, _ in routine_events(r):
            exec_event(r, tag)
        ss.flash = "▶ " + r["name"]


def del_routine(rid):
    ss = st.session_state
    ss.daily_routines = [r for r in ss.daily_routines if r["id"] != rid]


def add_routine():
    ss = st.session_state
    name = (ss.get("nr_name") or "").strip()
    uids = ss.get("nr_devs") or []
    if not name or not uids:
        ss.flash = t("rt_need")
        return
    ss.rt_seq = ss.get("rt_seq", 0) + 1
    ss.daily_routines.append({"id": "c" + str(ss.rt_seq), "kind": "custom", "name": name, "enabled": True,
                              "time": ss.get("nr_time", dtime(18, 0)), "offset": int(ss.get("nr_off", 0)),
                              "uids": list(uids), "on": ss.get("nr_act", "Switch ON") == "Switch ON"})
    ss.flash = "✅ " + t("rt_made")


def create_space():
    ss = st.session_state
    name = (ss.get("sp_name") or "").strip()[:40]
    if not name:
        ss.flash = t("sp_need")
        return
    if name in ss.spaces:
        ss.flash = t("sp_dup")
        return
    ss.spaces[name] = {"icon": ss.get("sp_icon", "🏠"), "type": ss.get("sp_type", "Other"), "devices": [], "preset": None,
                       "persona": ss.get("sp_persona") if ss.get("sp_persona") in ("personal", "shared") else None}
    for uid in ss.get("sp_devs") or []:
        d = next((x for x in ss.fleet if x["uid"] == uid), None)
        if d:
            assign_device(d, name)
    set_active_room(name)
    log("➕ New space created: " + name)
    ss.flash = t("sp_made", n=name)


def set_active_room(name):
    """ONE source of truth for the active room."""
    ss = st.session_state
    if name in ss.spaces:
        ss["sel_room"] = name
    ss["room_rev"] = ss.get("room_rev", 0) + 1


def pick_room(key):
    ss = st.session_state
    v = ss.get(key)
    set_active_room(v if v in ss.spaces else current_room())


def dev_by_uid(uid):
    return next((x for x in st.session_state.fleet if x["uid"] == uid), None)


def name_taken(name, skip_uid=None):
    low = name.strip().lower()
    return any(d["name"].strip().lower() == low and d["uid"] != skip_uid for d in st.session_state.fleet)


def unique_name(base, skip_uid=None):
    name, k = base, 2
    while name_taken(name, skip_uid):
        name = base + " #" + str(k)
        k += 1
    return name


def snapshot_room(room):
    ss = st.session_state
    devs = space_devs(room)
    ss.spaces[room]["preset"] = ({str(d["uid"]): {"on": bool(d["on"]), "lvl": int(d["lvl"]), "color": safe_hex(d["color"])}
                                  for d in devs} if devs else None)
    return len(devs)


def apply_preset(room, why=True, force=False):
    """Apply the saved room default. Manual one-click use forces it; automation respects holds."""
    ss = st.session_state
    sp = ss.spaces.get(room)
    pre = sp.get("preset") if sp else None
    if not pre:
        return 0
    n = 0
    for d in space_devs(room):
        p = pre.get(str(d["uid"]))
        if p is None or (held(d) and not force):
            continue
        set_dev(d, p.get("on"), p.get("lvl"), p.get("color"))
        n += 1
    if why:
        log("⚡ Room default applied: " + room + " (" + str(n) + " device(s))")
    return n


def cb_save_preset():
    ss = st.session_state
    room = current_room()
    n = snapshot_room(room)
    log("💾 Default saved for " + room + " (" + str(n) + " device(s))")
    ss.flash = t("rs_preset_saved", n=tr_room(room), c=n)


def cb_clear_preset():
    ss = st.session_state
    room = current_room()
    ss.spaces[room]["preset"] = None
    ss.flash = t("rs_preset_cleared", n=tr_room(room))


def cb_apply_preset(room):
    ss = st.session_state
    n = apply_preset(room, force=True)
    ss.flash = t("rs_preset_applied", n=tr_room(room), c=n) if n else t("preset_none")


def cb_apply_all_presets():
    ss = st.session_state
    total = 0
    for room in list(ss.spaces):
        total += apply_preset(room, force=True)
    ss.flash = t("rs_preset_applied", n="ALL", c=total)


def repair_orphans():
    """Every device belongs to exactly one existing space."""
    ss = st.session_state
    if "fleet" not in ss or not ss.get("spaces"):
        return 0
    names = list(ss.spaces)
    fallback = names[0]
    uids = {d["uid"] for d in ss.fleet}
    owner, fixed = {}, 0
    for n, sp in ss.spaces.items():
        keep = []
        for u in dict.fromkeys(sp["devices"]):
            if u in uids and u not in owner:
                owner[u] = n
                keep.append(u)
            else:
                fixed += 1
        sp["devices"] = keep
    for d in ss.fleet:
        if d["uid"] not in owner:
            home = d["room"] if d["room"] in ss.spaces else fallback
            ss.spaces[home]["devices"].append(d["uid"])
            owner[d["uid"]] = home
            fixed += 1
        if d["room"] != owner[d["uid"]]:
            d["room"] = owner[d["uid"]]
    for sp in ss.spaces.values():
        sp.setdefault("preset", None)
    if ss.presence.get("room") not in ss.spaces:
        ss.presence["room"] = fallback
    if ss.get("sel_room") not in ss.spaces:
        ss["sel_room"] = ss.presence["room"]
    if fixed:
        log("🛟 " + t("dev_orphan_fix") + " (" + str(fixed) + ")")
    return fixed


def ensure_modes():
    """Every mode carries a valid colour, genre and a complete 10-instrument mix."""
    ss = st.session_state
    for k, v in DEFAULT_MODES.items():
        if k not in ss.modes:
            ss.modes[k] = dict(v)
    for name, m in ss.modes.items():
        m["bulb"] = safe_hex(m.get("bulb"))
        m["mix"] = full_mix(m.get("mix"))
        if m.get("genre") not in GENRES:
            m["genre"] = GENRES[0]
        m.setdefault("fan", 1)
        m.setdefault("ac", 24)
        m.setdefault("extras", [])
    ss.cfg["mix"] = full_mix(ss.cfg.get("mix"))


def connect_all():
    ss = st.session_state
    bar = st.progress(0.0)
    ok = 0
    for i, d in enumerate(ss.fleet):
        ok += 1 if connect_device(d) else 0
        bar.progress((i + 1) / float(len(ss.fleet)))
    log("🔗 Connected " + str(ok) + " of " + str(len(ss.fleet)) + " devices")


def init_state():
    ss = st.session_state
    if ss.get("theme_choice") not in ("dark", "light"):
        ss["theme_choice"] = "light" if native_light() else "dark"
    if "modes" not in ss:
        ss.modes = {k: dict(v) for k, v in DEFAULT_MODES.items()}
    if "cfg" not in ss:
        ss.cfg = {"auto_mode": False, "source": "sim", "scn": "relaxed",
                  "api_url": "http://localhost:8000/latest-biometrics", "thr": 100, "rel": 78, "rest": 62, "poll": 3,
                  "notif": True, "chime": True, "timer": 0, "tok": 0, "bed": 100, "mix": dict(BASE_MIX),
                  "follow_me": True, "cut_mode": "Off", "calm_on": True, "tracker": "Apple Watch Series 9",
                  "geo_auto": True}
    for k, v in (("holds", {}), ("room_mode", {}), ("conn", {"mode": "home"}),
                 ("geo", {"state": "idle", "chimed": False, "km": 20, "rev": 0}), ("presence", {"room": "Living Lounge"}),
                 ("fade_tok", 0), ("routine_runs", {}), ("daily_routines", default_routines())):
        if k not in ss:
            ss[k] = v
    if "fleet" not in ss:
        ss.uid = 0
        ss.log = []
        ss.fleet = []
        ss.spaces = {}
        for room, (icon, typ, devs) in DEFAULT_SPACES.items():
            ids = []
            for cid, label in devs:
                d = new_device(cid, label + " · " + room, room)
                ss.fleet.append(d)
                ids.append(d["uid"])
            ss.spaces[room] = {"icon": icon, "type": typ, "devices": ids, "preset": None}
        ss.active_mode = "Relax Evening"
        apply_mode(ss.active_mode)
        # Pre-fill every predefined room's one-click default
        keep = {d["uid"]: (d["on"], d["lvl"], d["color"]) for d in ss.fleet}
        apply_mode(ss.active_mode, why=False, devs=list(ss.fleet), set_active=False)
        for room in ss.spaces:
            snapshot_room(room)
        for d in ss.fleet:
            d["on"], d["lvl"], d["color"] = keep[d["uid"]]
        ss.log = []
    for k, v in (("hr_hist", [72 + random.randint(-3, 3) for _ in range(30)]), ("skin_hist", []),
                 ("bstate", "relaxed"), ("last_state", None), ("wake_ticks", 0), ("sleep_ts", 0.0), ("prev_auto", False),
                 ("flash", ""), ("profile", None), ("editing", False), ("chat", []), ("chimed", False),
                 ("sel_room", ss.presence["room"]), ("room_rev", 0), ("rerun_pending", False), ("last_rerun", 0.0),
                 ("ui_mode", "zen"), ("guest_mode", False), ("guest_rev", 0), ("family_lock", set()), ("occupancy", {}),
                 ("dial_idx", {}), ("dial_scope", "both"), ("voice_last", ""), ("pending_offer", None),
                 ("last_offer_at", -99), ("last_topic", None), ("deeper", 0), ("ui_rev", 0)):
        if k not in ss:
            ss[k] = v
    repair_orphans()
    ensure_modes()


# ----------------------------------------------------------------------------
# Biometrics + AI analysis
# ----------------------------------------------------------------------------
SCN = {"relaxed": (68, (50, 70), 33.6, False), "active": (90, (38, 55), 34.8, False),
       "stress": (115, (20, 32), 34.5, False), "sleep": (54, (75, 95), 32.7, True),
       "wake": (73, (48, 60), 33.8, False)}


def read_biometrics():
    cfg = st.session_state.cfg
    last = st.session_state.hr_hist[-1]
    if cfg["source"] == "wear":
        try:
            r = requests.get(cfg["api_url"], timeout=1.5)
            r.raise_for_status()
            d = r.json()
            stage = str(d.get("sleep_stage", "")).lower()
            asleep = bool(d.get("asleep", d.get("sleeping", stage in ("light", "deep", "rem", "asleep"))))
            return {"hr": int(d.get("heart_rate", d.get("hr", last))), "hrv": int(d.get("hrv", 55)),
                    "spo2": float(d.get("spo2", 97)), "skin": float(d.get("temperature", 33.5)),
                    "asleep": asleep, "flag": any(k in d for k in ("asleep", "sleeping", "sleep_stage")), "live": True}
        except Exception:
            pass
    tgt, hrv, skin, asleep = SCN[cfg["scn"]]
    hr = int(max(45, min(140, last + (tgt - last) * 0.35 + random.gauss(0, 1.5))))
    return {"hr": hr, "hrv": random.randint(hrv[0], hrv[1]), "spo2": round(random.uniform(96, 99), 1),
            "skin": round(skin + random.gauss(0, 0.15), 1), "asleep": asleep, "live": False}


def analyze(r):
    """Turn raw wearable numbers into a body state with a confidence and a plain-language reason."""
    ss, cfg = st.session_state, st.session_state.cfg
    hist = ss.hr_hist
    h = datetime.now().hour
    recent = hist[-5:]
    avg = sum(recent) / float(len(recent))
    slope = (recent[-1] - recent[0]) / float(max(1, len(recent) - 1))
    rest, hrv, prev = cfg["rest"], r["hrv"], ss.bstate
    sim = not r["live"]
    night = h >= 21 or h < 7
    if r.get("asleep") or (night and avg <= rest * 0.92 and hrv >= 60):
        state, conf = "sleep", 75 + min(20, max(0, int(rest - avg) * 2))
    elif prev != "wake" and time.time() - ss.sleep_ts < 600 and not r.get("asleep") \
            and (slope >= 1.0 or avg - min(hist[-10:]) >= 5 or r.get("flag") or sim) and (4 <= h <= 11 or sim):
        state, conf = "wake", 82
        ss.sleep_ts = 0.0
    elif prev == "wake" and ss.wake_ticks < 6:
        state, conf = "wake", 80
    elif avg >= cfg["thr"] or (prev == "stress" and avg >= cfg["thr"] - 5) or (hrv < 28 and avg >= rest * 1.3):
        state, conf = "stress", min(98, 60 + int((avg - cfg["thr"]) * 1.5) + max(0, (40 - hrv) // 2))
    elif avg < cfg["rel"] or (prev == "relaxed" and avg < cfg["rel"] + 3):
        state, conf = "relaxed", min(96, 70 + max(0, int(cfg["rel"] - avg)))
    else:
        state, conf = "active", 72
    if state == "sleep":
        ss.sleep_ts = time.time()
    ss.wake_ticks = ss.wake_ticks + 1 if state == "wake" else 0
    ss.bstate = state
    reason = "Heartbeat {:.0f} bpm, calm level {}, body warmth {} °C".format(avg, hrv, r["skin"])
    return {"state": state, "conf": max(50, min(99, conf)), "reason": reason}


def state_mode(state):
    h = datetime.now().hour
    if state == "sleep":
        return "Sleep"
    if state == "wake":
        return "Energize"
    if state == "stress":
        return "Deep Meditation"
    if state == "active":
        return "Focus" if h < 21 else "Relax Evening"
    if 6 <= h < 11:
        return "Zen Garden"
    if 11 <= h < 18:
        return "Focus"
    if 18 <= h < 22:
        return "Relax Evening"
    return "Sleep"


# ----------------------------------------------------------------------------
# Procedural music engine (Web Audio API).
# ----------------------------------------------------------------------------
ENGINE_JS = r"""
(function () {
  var A = { v: __VER__, ctx: null, playing: false, p: null, nodes: null, tick: null, timerH: null, tTok: null,
            genre: null, st: null, step: 0, nextT: 0, bus: null, deg: 4, arpI: 0, w: {}, nbuf: null };
  var INS = ['Piano', 'Flute', 'Rain', 'Tabla', 'Veena', 'Singing Bowls', 'Strings', 'Ocean Waves', 'Sitar', 'Harp'];
  var TEN = 'BNNBBNNBBTTNNNNB';
  function NOTE(m) { return (A.tune || 440) * Math.pow(2, (m - 69) / 12); }
  var SC = { maj: [0, 2, 4, 5, 7, 9, 11], min: [0, 2, 3, 5, 7, 8, 10], pent: [0, 2, 4, 7, 9], mpent: [0, 3, 5, 7, 10],
             blues: [0, 3, 5, 6, 7, 10], lyd: [0, 2, 4, 6, 7, 9, 11], phr: [0, 1, 3, 5, 7, 8, 10], dor: [0, 2, 3, 5, 7, 9, 10] };
  function semi(sc, d) {
    var s = SC[sc], L = s.length, o = Math.floor(d / L), i = ((d % L) + L) % L;
    return s[i] + 12 * o;
  }
  function D(o) {
    var d = { ls: null, sw: 0, n: 3, pa: 0.1, rev: 0.25, kick: '', snare: '', hat: '', oh: '', bass: '', bw: 'sine',
              bl: 0.3, bd: 2, lead: '', lm: 'sparse', lt: 'pluck', lw: 'triangle', ll: 0.12, lo: 12, noise: 'none', nl: 0 };
    for (var k in o) { d[k] = o[k]; }
    return d;
  }
  var S = {
    'Pop': D({ sc: 'maj', root: 48, bpm: 108, prog: [0, 4, 5, 3], pw: 'triangle', pl: 0.8, cut: 5000,
      kick: 'x...x...x...x...', snare: '....x.......x...', hat: 'x.x.x.x.x.x.x.x.', bass: 'x..x..x...x.x...', bw: 'sawtooth', bl: 0.25,
      lead: 'x..x..x.x..x.x..', lm: 'walk', lw: 'square', ll: 0.1 }),
    'Rock': D({ sc: 'min', root: 40, bpm: 122, prog: [0, 5, 2, 6], pw: 'sawtooth', pl: 0.9, pa: 0.02, cut: 3200,
      kick: 'x.....x.x.....x.', snare: '....x.......x...', hat: 'x.x.x.x.x.x.x.x.', bass: 'x.x.x.x.x.x.x.x.', bw: 'sawtooth', bl: 0.3, bd: 1.5,
      lead: 'x...x.x.....x...', lm: 'walk', ls: 'mpent', lw: 'sawtooth', ll: 0.1 }),
    'Blues': D({ sc: 'dor', root: 45, bpm: 84, sw: 0.33, prog: [0, 0, 3, 0], n: 4, pw: 'triangle', pl: 0.7, cut: 2200,
      kick: 'x.......x.......', snare: '....x.......x...', hat: 'x.x.x.x.x.x.x.x.', bass: 'x...x...x...x...', bw: 'triangle', bl: 0.45, bd: 3,
      lead: 'x.....x...x.x...', lm: 'walk', ls: 'blues', lw: 'triangle', ll: 0.16 }),
    'Hip-Hop': D({ sc: 'min', root: 36, bpm: 90, sw: 0.2, prog: [0, 0, 5, 3], n: 4, pw: 'triangle', pl: 0.5, cut: 1500,
      kick: 'x..x......x.x...', snare: '....x.......x...', hat: 'x.x.x.x.x.x.x.xx', bass: 'x..x......x.x...', bw: 'sine', bl: 0.7, bd: 5,
      lead: '..x.....x...x...', lm: 'sparse', lt: 'bell', lw: 'sine', ll: 0.12, lo: 24 }),
    'Jazz': D({ sc: 'maj', root: 48, bpm: 100, sw: 0.33, prog: [1, 4, 0, 5], n: 4, pw: 'sine', pl: 0.7, pa: 0.15, cut: 3000, rev: 0.35,
      kick: 'x.......x.......', hat: 'x.x.x.x.x.x.x.x.', bass: 'x...x...x...x...', bw: 'triangle', bl: 0.45, bd: 3.5,
      lead: 'x.x...x.x.x...x.', lm: 'walk', ls: 'dor', lw: 'triangle', ll: 0.16 }),
    'Classical': D({ sc: 'maj', root: 48, bpm: 72, prog: [0, 3, 4, 0], pw: 'sine', pl: 0.7, pa: 0.2, cut: 4500, rev: 0.4,
      bass: 'x...............', bw: 'sine', bl: 0.35, bd: 12, lead: 'x.x.x.x.x.x.x.x.', lm: 'arp', lw: 'triangle', ll: 0.14 }),
    'Metal': D({ sc: 'phr', root: 36, bpm: 150, prog: [0, 0, 1, 0], pw: 'sawtooth', pl: 0.9, pa: 0.02, cut: 2800, rev: 0.1,
      kick: 'x.xxx.xxx.xxx.xx', snare: '....x.......x...', hat: 'x.x.x.x.x.x.x.x.', bass: 'xxxxxxxxxxxxxxxx', bw: 'sawtooth', bl: 0.22, bd: 0.8,
      lead: 'x..x..x.x..x.x..', lm: 'walk', ls: 'phr', lw: 'sawtooth', ll: 0.1 }),
    'Folk': D({ sc: 'maj', root: 50, bpm: 96, prog: [0, 3, 0, 4], pw: 'triangle', pl: 0.5, cut: 3500,
      kick: 'x.......x.......', hat: 'x.x.x.x.x.x.x.x.', bass: 'x.......x.......', bw: 'triangle', bl: 0.3, bd: 3,
      lead: 'x.xx.x.xx.xx.x.x', lm: 'arp', lw: 'triangle', ll: 0.15, noise: 'wind', nl: 0.03 }),
    'EDM': D({ sc: 'min', root: 45, bpm: 128, prog: [0, 5, 2, 6], pw: 'sawtooth', pl: 0.75, pa: 0.05, cut: 6000, rev: 0.2,
      kick: 'x...x...x...x...', snare: '....x.......x...', oh: '..x...x...x...x.', bass: '.x.x.x.x.x.x.x.x', bw: 'sawtooth', bl: 0.28, bd: 1.5,
      lead: 'xxxxxxxxxxxxxxxx', lm: 'arp', lw: 'sawtooth', ll: 0.07, lo: 24 }),
    'Country': D({ sc: 'maj', root: 43, bpm: 104, sw: 0.1, prog: [0, 0, 3, 4], pw: 'triangle', pl: 0.5, cut: 4000,
      kick: 'x...x...x...x...', snare: '....x.......x...', hat: 'x.x.x.x.x.x.x.x.', bass: 'x.......x.......', bw: 'triangle', bl: 0.4, bd: 3,
      lead: 'x.xx.x.x.xx.x.xx', lm: 'arp', lw: 'triangle', ll: 0.15, noise: 'wind', nl: 0.03 }),
    'Disco': D({ sc: 'min', root: 45, bpm: 118, prog: [0, 5, 3, 4], n: 4, pw: 'sawtooth', pl: 0.5, cut: 4500,
      kick: 'x...x...x...x...', snare: '....x.......x...', oh: '..x...x...x...x.', bass: 'x.xx.xx.x.xx.xx.', bw: 'sawtooth', bl: 0.25, bd: 1,
      lead: 'x.x.x.x.x.x.x.x.', lm: 'arp', lw: 'square', ll: 0.08 }),
    'OM Mantra': D({ sc: 'pent', root: 38, bpm: 40, prog: [0], pw: 'sine', pl: 1.0, pa: 0.35, cut: 900, rev: 0.7,
      bass: 'x...............', bw: 'sine', bl: 0.55, bd: 16, lead: 'x.......x.......', lm: 'sparse', lt: 'bell', lw: 'sine', ll: 0.25 }),
    'Chinese Zen': D({ sc: 'pent', root: 50, bpm: 56, prog: [0, 2, 1, 0], pw: 'sine', pl: 0.5, pa: 0.3, cut: 3500, rev: 0.5,
      bass: 'x...............', bw: 'sine', bl: 0.3, bd: 12, lead: 'x..x....x.....x.', lm: 'walk', ls: 'pent', lw: 'triangle', ll: 0.2,
      noise: 'wind', nl: 0.05 }),
    'Lo-Fi Chill': D({ sc: 'min', root: 45, bpm: 76, sw: 0.25, prog: [0, 5, 2, 6], n: 4, pw: 'triangle', pl: 0.6, cut: 1700, rev: 0.4,
      kick: 'x.....x..x......', snare: '....x.......x...', hat: '..x...x...x...x.', bass: 'x.....x..x......', bw: 'sine', bl: 0.5, bd: 4,
      lead: '..x.....x..x....', lm: 'walk', ls: 'mpent', lw: 'triangle', ll: 0.18, lo: 24, noise: 'rain', nl: 0.12 }),
    'Calm 432Hz': D({ sc: 'pent', root: 45, tune: 432, bpm: 42, prog: [0, 2, 1, 0], n: 3, pw: 'sine', pl: 0.9, pa: 0.4, cut: 1200, rev: 0.8,
      bass: 'x...............', bw: 'sine', bl: 0.5, bd: 16, lead: 'x.......x.......', lm: 'sparse', lt: 'bell', lw: 'sine', ll: 0.18,
      lo: 24, noise: 'ocean', nl: 0.08 }),
    'Ambient Space': D({ sc: 'lyd', root: 43, bpm: 44, prog: [0, 4, 1, 5], n: 4, pw: 'sawtooth', pl: 0.5, pa: 0.4, cut: 1100, rev: 0.8,
      bass: 'x...............', bw: 'sine', bl: 0.4, bd: 16, lead: 'x.......x...x...', lm: 'sparse', lt: 'bell', lw: 'sine', ll: 0.2,
      lo: 24, noise: 'wind', nl: 0.07 })
  };
  function ensure() {
    if (!A.ctx) { var C = window.AudioContext || window.webkitAudioContext; A.ctx = new C(); }
    if (A.ctx.state === 'suspended') { A.ctx.resume(); }
    return A.ctx;
  }
  function tone(type, f, t, peak, dur, dest, atk, det, fl) {
    var c = A.ctx, o = c.createOscillator(), g = c.createGain(), a = atk || 0.01, e = t + Math.max(dur, a + 0.05), fx = null;
    o.type = type; o.frequency.setValueAtTime(f, t);
    if (det) { o.detune.value = det; }
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(peak, t + a);
    g.gain.exponentialRampToValueAtTime(0.0005, e);
    if (fl) {
      fx = c.createBiquadFilter(); fx.type = fl[0]; fx.frequency.setValueAtTime(fl[1], t); fx.Q.value = fl[2] || 1;
      o.connect(fx); fx.connect(g);
    } else { o.connect(g); }
    g.connect(dest); o.start(t); o.stop(e + 0.1);
    o.fx = fx;
    return o;
  }
  function pad(type, f, t, peak, att, dur, dest, det, fl) {
    var c = A.ctx, o = c.createOscillator(), g = c.createGain(), fx = null;
    o.type = type; o.frequency.setValueAtTime(f, t);
    if (det) { o.detune.value = det; }
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(peak, t + att);
    g.gain.setValueAtTime(peak, t + dur * 0.6);
    g.gain.exponentialRampToValueAtTime(0.0005, t + dur);
    if (fl) {
      fx = c.createBiquadFilter(); fx.type = fl[0]; fx.frequency.value = fl[1]; fx.Q.value = fl[2] || 1;
      o.connect(fx); fx.connect(g);
    } else { o.connect(g); }
    g.connect(dest); o.start(t); o.stop(t + dur + 0.1);
    o.fx = fx;
    return o;
  }
  function nburst(t, dur, type, freq, peak, dest) {
    var c = A.ctx, s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
    s.buffer = A.nbuf; f.type = type; f.frequency.value = freq;
    g.gain.setValueAtTime(peak, t); g.gain.exponentialRampToValueAtTime(0.0005, t + dur);
    s.connect(f); f.connect(g); g.connect(dest); s.start(t, Math.random()); s.stop(t + dur + 0.05);
  }
  function kick(t, d) { var o = tone('sine', 150, t, 0.9, 0.3, d, 0.003); o.frequency.exponentialRampToValueAtTime(42, t + 0.14); }
  function snare(t, d) { nburst(t, 0.18, 'highpass', 1800, 0.35, d); tone('triangle', 190, t, 0.25, 0.12, d, 0.003); }
  function hat(t, d, open) { nburst(t, open ? 0.22 : 0.05, 'highpass', 7000, open ? 0.12 : 0.09, d); }
  function bell(f, t, peak, d) { tone('sine', f, t, peak, 7, d, 0.01); tone('sine', f * 2.76, t, peak * 0.4, 4, d, 0.01); }

  /* ---- the ten instrument voices ---- */
  function piano(f, t, vel, d) {
    var amp = [1, 0.5, 0.28, 0.14, 0.07];
    for (var i = 0; i < amp.length; i++) { tone('sine', f * (i + 1), t, 0.34 * vel * amp[i], 2.6 / (1 + i * 0.7), d, 0.004); }
    nburst(t, 0.03, 'bandpass', 2200, 0.08 * vel, d);
  }
  function flute(f, t, dur, d) {
    var c = A.ctx, o = pad('sine', f, t, 0.34, 0.1, dur, d, 0), lfo = c.createOscillator(), lg = c.createGain();
    pad('sine', f * 2, t, 0.06, 0.12, dur, d, 0);
    lfo.frequency.value = 5.2; lg.gain.value = 10; lfo.connect(lg); lg.connect(o.detune); lfo.start(t); lfo.stop(t + dur + 0.2);
    nburst(t, dur * 0.8, 'bandpass', 3200, 0.03, d);
  }
  function tabla(code, t, d) {
    if (code === 'B') { var o = tone('sine', 150, t, 0.6, 0.5, d, 0.003); o.frequency.exponentialRampToValueAtTime(65, t + 0.3); }
    var open = (code === 'T'), f = open ? 560 : 430;
    tone('sine', f, t, 0.4, open ? 0.5 : 0.16, d, 0.002);
    tone('sine', f * 2.3, t, 0.15, open ? 0.3 : 0.08, d, 0.002);
    nburst(t, 0.025, 'bandpass', 3000, 0.14, d);
  }
  function veena(f, t, d) {
    var o = tone('sawtooth', f, t, 0.26, 1.6, d, 0.004, 0, ['lowpass', 3600, 2]);
    o.frequency.setValueAtTime(f * 1.05, t); o.frequency.exponentialRampToValueAtTime(f, t + 0.1);
    if (o.fx) { o.fx.frequency.exponentialRampToValueAtTime(700, t + 1.0); }
    tone('triangle', f * 2, t, 0.06, 0.9, d, 0.004);
  }
  function sitar(f, t, d) {
    var o = tone('sawtooth', f, t, 0.24, 1.4, d, 0.003, 0, ['bandpass', 2400, 5]);
    o.frequency.setValueAtTime(f * 0.97, t); o.frequency.exponentialRampToValueAtTime(f, t + 0.05);
    if (o.fx) { o.fx.frequency.exponentialRampToValueAtTime(900, t + 0.9); }
    tone('square', f * 1.5, t, 0.05, 0.6, d, 0.003, 0, ['lowpass', 2500, 1]);
  }
  function bowl(f, t, d) {
    [1, 2.71, 5.13].forEach(function (r, i) {
      tone('sine', f * r, t, 0.34 / (1 + i * 1.3), 10 / (1 + i * 0.8), d, 0.01);
      tone('sine', f * r + 1.2 + i, t, 0.34 / (1 + i * 1.3), 10 / (1 + i * 0.8), d, 0.01);
    });
  }
  function strings(ch, t, bd, d) {
    ch.forEach(function (mid) {
      [-9, 0, 9].forEach(function (c) { pad('sawtooth', NOTE(mid + 12), t, 0.06, bd * 0.35, bd * 1.25, d, c, ['lowpass', 2300, 0.7]); });
    });
  }
  function harp(ch, t, d) {
    var notes = [], i;
    for (i = 0; i < ch.length; i++) { notes.push(ch[i] + 12); }
    for (i = 0; i < ch.length; i++) { notes.push(ch[i] + 24); }
    notes.forEach(function (m, k) {
      tone('triangle', NOTE(m), t + k * 0.09, 0.32, 2.4, d, 0.003);
      tone('sine', NOTE(m) * 2, t + k * 0.09, 0.08, 1.2, d, 0.003);
    });
  }
  function walk(k, sc) {
    var w = A.w, st = [-2, -1, -1, 0, 1, 1, 2];
    w[k] = (w[k] === undefined ? 3 : w[k]) + st[Math.floor(Math.random() * st.length)];
    if (w[k] < -2) { w[k] = -2; }
    if (w[k] > 9) { w[k] = 9; }
    return semi(sc, w[k]);
  }
  function chord(st, deg) {
    var r = [];
    for (var i = 0; i < st.n; i++) { r.push(st.root + semi(st.sc, deg + 2 * i)); }
    return r;
  }
  function leadFreq(st, ch) {
    var m;
    if (st.lm === 'arp') {
      var n = ch.length * 2, i = A.arpI % n; A.arpI += 1;
      m = ch[i % ch.length] + (i >= ch.length ? 12 : 0) + st.lo;
    } else if (st.lm === 'walk') {
      var steps = [-2, -1, -1, 0, 1, 1, 2];
      A.deg += steps[Math.floor(Math.random() * steps.length)];
      if (A.deg < -2) { A.deg = -2; }
      if (A.deg > 9) { A.deg = 9; }
      m = st.root + semi(st.ls || st.sc, A.deg) + st.lo;
    } else {
      m = ch[Math.floor(Math.random() * ch.length)] + st.lo + (Math.random() < 0.4 ? 12 : 0);
    }
    return NOTE(m);
  }
  function mkBus(st) {
    var c = A.ctx, n = A.nodes, g = c.createGain(), lp = c.createBiquadFilter(), sd = c.createGain();
    lp.type = 'lowpass'; lp.frequency.value = st.cut; sd.gain.value = st.rev;
    g.connect(lp); lp.connect(n.master); lp.connect(sd); sd.connect(n.dly);
    return { g: g, lp: lp, sd: sd };
  }
  A.bedLevel = function () { return ((A.p && A.p.bed !== undefined) ? A.p.bed : 100) / 100; };
  A.setStyle = function (g) {
    var c = A.ctx, now = c.currentTime, old = A.bus;
    A.genre = g; A.st = S[g] || S['Ambient Space']; A.tune = A.st.tune || 440;
    var nb = mkBus(A.st);
    if (old) {
      old.g.gain.cancelScheduledValues(now);
      old.g.gain.setTargetAtTime(0, now, 0.15);
      setTimeout(function () { try { old.g.disconnect(); old.lp.disconnect(); old.sd.disconnect(); } catch (e) {} }, 1500);
    }
    nb.g.gain.setValueAtTime(0.0001, now); nb.g.gain.setTargetAtTime(A.bedLevel(), now + 0.05, 0.2);
    A.bus = nb; A.step = 0; A.nextT = now + 0.12; A.deg = 4; A.arpI = 0; A.w = {};
    A.applyNoise();
  };
  A.applyBed = function () { if (A.bus && !(A.fadeEnd && A.ctx.currentTime < A.fadeEnd)) { A.bus.g.gain.setTargetAtTime(A.bedLevel(), A.ctx.currentTime, 0.15); } };
  A.applyNoise = function () {
    var n = A.nodes, st = A.st;
    if (!n || !st) { return; }
    var now = A.ctx.currentTime;
    n.rain.gain.setTargetAtTime(st.noise === 'rain' ? st.nl * 0.8 : 0, now, 0.6);
    n.wind.gain.setTargetAtTime(st.noise === 'wind' ? st.nl * 1.2 : 0, now, 0.6);
    n.ocean.gain.setTargetAtTime(st.noise === 'ocean' ? st.nl : 0, now, 0.6);
  };
  A.applyMix = function () {
    var n = A.nodes, m = (A.p && A.p.mix) || {};
    if (!n) { return; }
    var now = A.ctx.currentTime;
    INS.forEach(function (k) { if (n.inst && n.inst[k]) { n.inst[k].gain.setTargetAtTime((Number(m[k]) || 0) / 100, now, 0.08); } });
  };
  A.play = function (s, bar, t, dur) {
    var st = A.st, m = A.p.mix || {}, d = A.bus.g;
    function L(k) { return (m[k] || 0) / 100; }
    function G(k) { return A.nodes.inst[k]; }
    var deg = st.prog[bar % st.prog.length], ch = chord(st, deg), rootM = st.root + semi(st.sc, deg);
    if (s === 0) {
      var bd = dur * 16;
      ch.forEach(function (mid) {
        var f = NOTE(mid);
        pad(st.pw, f, t, 0.05 * st.pl, bd * st.pa + 0.05, bd * 1.1, d, 6);
        pad(st.pw, f, t, 0.05 * st.pl, bd * st.pa + 0.05, bd * 1.1, d, -6);
      });
    }
    if (st.kick.charAt(s) === 'x') { kick(t, d); }
    if (st.snare.charAt(s) === 'x') { snare(t, d); }
    if (st.hat.charAt(s) === 'x') { hat(t, d, false); }
    if (st.oh.charAt(s) === 'x') { hat(t, d, true); }
    if (st.bass.charAt(s) === 'x') { tone(st.bw, NOTE(rootM - 12), t, 0.3 * st.bl, dur * st.bd, d, 0.01); }
    if (st.lead.charAt(s) === 'x') {
      var f2 = leadFreq(st, ch);
      if (st.lt === 'bell') { bell(f2, t, st.ll * 0.5, d); } else { tone(st.lw, f2, t, st.ll * 0.6, 0.55, d, 0.005); }
    }
    /* instruments: each one plays only while its own slider is above zero */
    if (L('Piano') > 0.02) {
      if (s % 8 === 0) { ch.forEach(function (mid, i) { piano(NOTE(mid), t + i * 0.035, 0.9, G('Piano')); }); }
      else if (s % 4 === 2 && Math.random() < 0.8) { piano(NOTE(st.root + 12 + walk('pi', st.ls || st.sc)), t, 0.8, G('Piano')); }
    }
    if (L('Flute') > 0.02 && s % 8 === 2 && Math.random() < 0.85) {
      flute(NOTE(st.root + 24 + walk('fl', 'pent')), t, dur * 7, G('Flute'));
    }
    if (L('Tabla') > 0.02 && s % 2 === 0) {
      var code = TEN.charAt(Math.floor(((bar % 2) * 16 + s) / 2));
      if (code !== '.') { tabla(code, t, G('Tabla')); }
    }
    if (L('Veena') > 0.02 && s % 2 === 0 && Math.random() < 0.6) { veena(NOTE(st.root + 12 + walk('ve', 'pent')), t, G('Veena')); }
    if (L('Sitar') > 0.02 && (s % 4 === 3 || s === 0) && Math.random() < 0.8) { sitar(NOTE(st.root + 12 + walk('si', 'pent')), t, G('Sitar')); }
    if (L('Harp') > 0.02 && s % 8 === 0) { harp(ch, t, G('Harp')); }
    if (L('Strings') > 0.02 && s === 0) { strings(ch, t, dur * 16, G('Strings')); }
    if (L('Singing Bowls') > 0.02 && s === 0 && bar % 2 === 0) { bowl(NOTE(st.root + 24 + (bar % 4 === 0 ? 0 : 7)), t, G('Singing Bowls')); }
    if (L('Rain') > 0.02 && Math.random() < 0.6) { nburst(t + Math.random() * dur, 0.025, 'highpass', 4000, 0.16, G('Rain')); }
  };
  A.sched = function () {
    if (!A.playing || !A.p || !A.nodes || !A.st || !A.bus) { return; }
    var c = A.ctx, now = c.currentTime, dur = 60 / A.st.bpm / 4;
    if (A.nextT < now - 0.3) { A.nextT = now + 0.05; }
    while (A.nextT < now + 0.35) {
      var s = A.step % 16, bar = Math.floor(A.step / 16);
      var t = A.nextT + ((s % 2 === 1) ? A.st.sw * dur : 0);
      A.play(s, bar, t, dur);
      A.step += 1; A.nextT += dur;
    }
  };
  A.arm = function () {
    if (A.timerH) { clearTimeout(A.timerH); A.timerH = null; }
    if (A.playing && A.p && A.p.tMin > 0) { A.timerH = setTimeout(function () { A.stop(); }, A.p.tMin * 60000); }
  };
  A.update = function (p) {
    p = p || {};
    var mm = {}, srcMix = (p.mix && typeof p.mix === 'object') ? p.mix : {};
    INS.forEach(function (k) { var v = Number(srcMix[k]); mm[k] = isFinite(v) ? Math.max(0, Math.min(100, v)) : 0; });
    p.mix = mm;
    if (!p.genre) { p.genre = 'Ambient Space'; }
    A.p = p;
    if (p.tTok !== A.tTok) { A.tTok = p.tTok; A.arm(); }
    if (A.playing) {
      if (p.genre !== A.genre) { A.setStyle(p.genre); } else { A.applyNoise(); A.applyBed(); }
      A.applyMix();
      A.fadeIn();
    }
  };
  A.fadeIn = function () {
    var p = A.p;
    if (!A.playing || !A.bus || !p || !p.fade || p.fadeTok === A.fadeTok) { return; }
    var now = A.ctx.currentTime;
    A.fadeTok = p.fadeTok; A.fadeEnd = now + p.fade;
    A.bus.g.gain.cancelScheduledValues(now);
    A.bus.g.gain.setValueAtTime(0.0001, now);
    A.bus.g.gain.linearRampToValueAtTime(A.bedLevel(), now + p.fade);
  };
  A.start = function () {
    if (A.playing) { return; }
    var c = ensure(), n = { srcs: [] };
    n.master = c.createGain(); n.master.gain.setValueAtTime(0.0001, c.currentTime);
    n.master.gain.linearRampToValueAtTime(0.7, c.currentTime + 1.5);
    n.comp = c.createDynamicsCompressor(); n.master.connect(n.comp); n.comp.connect(c.destination);
    n.dly = c.createDelay(1.0); n.dly.delayTime.value = 0.375;
    n.fb = c.createGain(); n.fb.gain.value = 0.35; n.wet = c.createGain(); n.wet.gain.value = 0.8;
    n.dly.connect(n.fb); n.fb.connect(n.dly); n.dly.connect(n.wet); n.wet.connect(n.master);
    n.ibus = c.createGain(); n.ibus.gain.value = 1.5; n.ibus.connect(n.master);
    n.isend = c.createGain(); n.isend.gain.value = 0.3; n.ibus.connect(n.isend); n.isend.connect(n.dly);
    n.inst = {};
    INS.forEach(function (k) { var g = c.createGain(); g.gain.value = 0; g.connect(n.ibus); n.inst[k] = g; });
    var len = c.sampleRate * 2, buf = c.createBuffer(1, len, c.sampleRate), d = buf.getChannelData(0);
    for (var k = 0; k < len; k++) { d[k] = Math.random() * 2 - 1; }
    A.nbuf = buf;
    function bed(t1, f1, t2, f2, rate) {
      var s = c.createBufferSource(); s.buffer = buf; s.loop = true;
      var a = c.createBiquadFilter(); a.type = t1; a.frequency.value = f1; s.connect(a);
      var last = a;
      if (t2) { var b = c.createBiquadFilter(); b.type = t2; b.frequency.value = f2; a.connect(b); last = b; }
      var sw = c.createGain(); sw.gain.value = rate > 0 ? 0.6 : 1; last.connect(sw);
      if (rate > 0) {
        var o = c.createOscillator(); o.frequency.value = rate;
        var og = c.createGain(); og.gain.value = 0.4; o.connect(og); og.connect(sw.gain); o.start(); n.srcs.push(o);
      }
      var g = c.createGain(); g.gain.value = 0; sw.connect(g); g.connect(n.master); s.start(); n.srcs.push(s);
      return g;
    }
    n.rain = bed('highpass', 700, 'lowpass', 7000, 0);
    n.wind = bed('bandpass', 500, null, 0, 0.07);
    n.ocean = bed('lowpass', 450, null, 0, 0.1);
    /* instrument beds: continuous rain and ocean waves, each on its own slider gain */
    var rs = c.createBufferSource(); rs.buffer = buf; rs.loop = true;
    var rh = c.createBiquadFilter(); rh.type = 'highpass'; rh.frequency.value = 900;
    var rl = c.createBiquadFilter(); rl.type = 'lowpass'; rl.frequency.value = 7000;
    var rg = c.createGain(); rg.gain.value = 0.75;
    rs.connect(rh); rh.connect(rl); rl.connect(rg); rg.connect(n.inst['Rain']); rs.start(); n.srcs.push(rs);
    var os = c.createBufferSource(); os.buffer = buf; os.loop = true;
    var ol = c.createBiquadFilter(); ol.type = 'lowpass'; ol.frequency.value = 550;
    var sw2 = c.createGain(); sw2.gain.value = 0.5;
    var l1 = c.createOscillator(); l1.frequency.value = 0.09;
    var l1g = c.createGain(); l1g.gain.value = 0.4; l1.connect(l1g); l1g.connect(sw2.gain);
    var l2 = c.createOscillator(); l2.frequency.value = 0.13;
    var l2g = c.createGain(); l2g.gain.value = 250; l2.connect(l2g); l2g.connect(ol.frequency);
    os.connect(ol); ol.connect(sw2); sw2.connect(n.inst['Ocean Waves']); os.start(); l1.start(); l2.start();
    n.srcs.push(os, l1, l2);
    A.nodes = n; A.playing = true; A.bus = null;
    A.setStyle((A.p && A.p.genre) || 'Ambient Space');
    A.applyMix(); A.arm(); A.fadeIn();
    A.tick = setInterval(A.sched, 40);
  };
  A.stop = function () {
    var n = A.nodes;
    if (A.tick) { clearInterval(A.tick); A.tick = null; }
    if (A.timerH) { clearTimeout(A.timerH); A.timerH = null; }
    A.playing = false; A.nodes = null; A.bus = null; A.genre = null; A.fadeEnd = 0;
    if (!n) { return; }
    n.master.gain.cancelScheduledValues(A.ctx.currentTime);
    n.master.gain.setTargetAtTime(0, A.ctx.currentTime, 0.25);
    setTimeout(function () {
      try { n.srcs.forEach(function (x) { x.stop(); }); n.master.disconnect(); } catch (e) {}
    }, 1500);
  };
  A.chime = function () {
    var c = ensure(), t0 = c.currentTime + 0.05;
    [880, 1318.5, 1760].forEach(function (f, i) { tone('sine', f, t0 + i * 0.18, 0.12, 1.6, c.destination, 0.02); });
  };
  A.styles = S;
  window.__aura = A;
})();
"""

ENGINE_VER = 8

HOST_BOOT = """
<script id="eng" type="text/plain">__ENGINE__</script>
<script>
var P;
try { P = window.parent; void P.document.body; } catch (e) { P = window; }
if (!P.__aura || P.__aura.v !== __VER__) {
  if (P.__aura && P.__aura.playing) { try { P.__aura.stop(); } catch (e) {} }
  var sc = P.document.createElement('script');
  sc.textContent = document.getElementById('eng').textContent;
  P.document.head.appendChild(sc);
}
var A = P.__aura;
</script>
"""

AUDIO_HTML = """
<style>
  body { margin: 0; }
  #box { display: flex; align-items: center; gap: 12px; background: __BG__; border: 1px solid __ACC__; border-radius: 14px;
         padding: 8px 12px; font-family: Inter, Arial, sans-serif; color: __ACC__; box-sizing: border-box; }
  #tg { width: 44px; height: 44px; flex: none; border-radius: 50%; background: __BTN__; color: __ACC__;
        border: 1px solid __ACC__; font-size: 18px; cursor: pointer; }
  #tg:hover { background: __ACC__; color: __BTN__; }
  #txt { flex: 1; min-width: 0; }
  #ttl { font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  #sub { font-size: 11px; color: __SUB__; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  #eq { display: flex; gap: 2px; align-items: flex-end; height: 22px; }
  .b { width: 3px; height: 5px; background: __ACC__; border-radius: 2px; }
  .on .b { animation: eq 0.9s ease-in-out infinite; }
  .on .b:nth-child(2) { animation-delay: 0.2s; }
  .on .b:nth-child(3) { animation-delay: 0.4s; }
  .on .b:nth-child(4) { animation-delay: 0.1s; }
  @keyframes eq { 0%, 100% { height: 5px; } 50% { height: 20px; } }
</style>
<div id="box">
  <button id="tg"></button>
  <div id="txt"><div id="ttl"></div><div id="sub"></div></div>
  <div id="eq"><span class="b"></span><span class="b"></span><span class="b"></span><span class="b"></span></div>
</div>
__BOOT__
<script>
var PARAMS = __PARAMS__, PLAY = __PLAY__, STOP = __STOP__, SEND = __SEND__;
var btn = document.getElementById('tg'), ttl = document.getElementById('ttl');
var sub = document.getElementById('sub'), box = document.getElementById('box');
if (SEND || !A.p) { A.update(PARAMS); }
function paint() {
  var p = A.p || PARAMS;
  ttl.textContent = p.title; sub.textContent = p.sub;
  btn.textContent = A.playing ? '■' : '▶';
  btn.title = A.playing ? STOP : PLAY;
  box.className = A.playing ? 'on' : '';
}
btn.onclick = function () { if (A.playing) { A.stop(); } else { A.start(); } paint(); };
paint();
setInterval(paint, 700);
</script>
"""

CHIME_HTML = """
<style>body { margin: 0; }</style>
<div style="font-family:Inter,Arial,sans-serif;text-align:left;">
  <button id="rg" title="Ring" style="background:__BTN__;color:__ACC__;border:1px solid __ACC__;border-radius:20px;padding:4px 16px;font-size:16px;cursor:pointer;">🔔</button>
</div>
__BOOT__
<script>
var AUTO = __AUTO__;
document.getElementById('rg').onclick = function () { A.chime(); };
if (AUTO) { setTimeout(function () { try { A.chime(); } catch (e) {} }, 400); }
</script>
"""


def boot():
    return HOST_BOOT.replace("__ENGINE__", ENGINE_JS).replace("__VER__", str(ENGINE_VER))


def audio_component(params, send):
    page = (AUDIO_HTML.replace("__BOOT__", boot()).replace("__PARAMS__", json.dumps(params))
            .replace("__PLAY__", json.dumps(t("play"))).replace("__STOP__", json.dumps(t("stop")))
            .replace("__SEND__", "true" if send else "false"))
    components.html(themed(page), height=74)


def synth_params(name):
    cfg = st.session_state.cfg
    env = st.session_state.modes[name]
    p = {"genre": env.get("genre", GENRES[0]), "mix": full_mix(cfg["mix"]), "modeMix": full_mix(env.get("mix")),
         "bed": max(0, min(100, int(cfg["bed"]))), "tMin": cfg["timer"],
         "tTok": cfg["tok"], "title": tr_mode(name), "sub": tr(env.get("genre", GENRES[0]))}
    if name == WIND_MODE:
        p["fade"] = 300
        p["fadeTok"] = st.session_state.fade_tok
    return p


# ----------------------------------------------------------------------------
# Page 1 - Live Dashboard
# ----------------------------------------------------------------------------
def seg(label, options, key, fmt=None, on_change=None, args=None, selected=None, disabled=False, hide_label=False):
    """Segmented control (falls back to a horizontal radio on older Streamlit)."""
    fmt = fmt or str
    args = args or ()
    base = dict(key=key, format_func=fmt, on_change=on_change, args=args, disabled=disabled)
    extra = {"label_visibility": "collapsed"} if hide_label else {}
    if hasattr(st, "segmented_control"):
        default = selected if selected in options else None
        try:
            return st.segmented_control(label, options, default=default, **base, **extra)
        except TypeError:
            return st.segmented_control(label, options, default=default, **base)
    idx = options.index(selected) if selected in options else 0
    try:
        return st.radio(label, options, index=idx, horizontal=True, **base, **extra)
    except TypeError:
        return st.radio(label, options, index=idx, horizontal=True, **base)


def room_selector(prefix, label):
    ss = st.session_state
    key = prefix + "_room_" + str(ss.get("room_rev", 0))
    seg(label, list(ss.spaces), key, lambda n: ss.spaces[n]["icon"] + " " + tr_room(n), on_change=pick_room, args=(key,),
        selected=current_room())


def chime_component(auto):
    components.html(themed(CHIME_HTML.replace("__BOOT__", boot()).replace("__AUTO__", "true" if auto else "false")),
                    height=48)


def run_live(fn):
    if hasattr(st, "fragment"):
        st.fragment(run_every=st.session_state.cfg["poll"])(fn)()
    else:
        fn()


def dev_text(d):
    c = CAT[d["cid"]]
    if not d["on"]:
        return t("off")
    return "ON" + ((" · " + str(d["lvl"]) + UNIT.get(d["cid"], "%")) if c[4] else "")


def current_room():
    ss = st.session_state
    room = ss.get("sel_room")
    return room if room in ss.spaces else next(iter(ss.spaces))


def live_devices():
    ss = st.session_state
    room = current_room()
    sp = ss.spaces[room]
    here = ss.conn["mode"] == "home" and ss.presence["room"] == room
    st.markdown("**" + sp["icon"] + " " + html.escape(tr_room(room)) + "**" +
                (' <span class="pill">' + t("here") + "</span>" if here else ""), unsafe_allow_html=True)
    devs = space_devs(room)
    if not devs:
        st.caption(t("room_empty"))
        return
    cards = []
    for d in devs:
        sw = ""
        if d["cid"] in BULBLIKE and d["on"]:
            sw = '<span class="sw" style="background:' + html.escape(d["color"]) + '"></span>'
        cards.append(stat(CAT[d["cid"]][1] + " " + d["name"].split(" · ")[0], dev_text(d), sw))
    cols = st.columns(4)
    for i, c in enumerate(cards):
        cols[i % 4].markdown(c, unsafe_allow_html=True)


def render_rooms():
    """Live Dashboard: one-click Active Room selector + one-click saved room default."""
    ss = st.session_state
    room_selector("dash", "🏠 " + t("room_sel"))
    room = current_room()
    has = bool(ss.spaces[room].get("preset"))
    any_has = any(sp.get("preset") for sp in ss.spaces.values())
    c1, c2 = st.columns(2)
    c1.button("⚡ " + t("rs_preset_apply", n=tr_room(room)), key="dash_preset_go", disabled=not has,
              on_click=cb_apply_preset, args=(room,))
    c2.button("⚡ " + t("preset_apply_all"), key="dash_preset_all", disabled=not any_has, on_click=cb_apply_all_presets)
    if not has:
        st.caption(t("preset_none"))


def geo_val(part, d):
    if not d["on"]:
        return "OFF"
    if part == "fan":
        return "ON · Speed " + str(d["lvl"])
    return "ON · " + str(d["lvl"]) + " °C"


def precond_tiles():
    tiles = []
    for part in GEO_PARTS:
        d = geo_dev(part)
        if d is None:
            continue
        tiles.append('<div class="ptile ' + ("on" if d["on"] else "off") + '"><div class="pi">' + GEO_ICON[part] +
                     '</div><div class="pn">' + html.escape(tr_room(GEO_NAME[part].split(' · ')[1])) +
                     '</div><div class="pv">' + geo_val(part, d) + "</div></div>")
    return '<div class="ptiles">' + "".join(tiles) + "</div>"


def render_precond_card(prefix):
    """Luxury Pre-Conditioning Status Card: live ON/OFF per appliance + one-touch overrides."""
    ss = st.session_state
    state = ss.geo["state"]
    if state == "active":
        st.markdown('<div class="pre"><div class="ph">' + html.escape(t("geo_card_hdr", m=eta_min(ss.geo["km"]))) +
                    '</div><div class="ps">' + html.escape(t("geo_card_sub")) + "</div>" + precond_tiles() + "</div>",
                    unsafe_allow_html=True)
        cols = st.columns(3)
        for col, part in zip(cols, GEO_PARTS):
            d = geo_dev(part)
            if d is None:
                continue
            on = bool(d["on"])
            col.button(t("geo_off_" + part) if on else t("geo_on_" + part), key=prefix + "_geo_" + part,
                       on_click=geo_part_set, args=(part, not on))
        st.button(t("geo_cancel_all"), key=prefix + "_geo_cancel", type="primary", on_click=geo_cancel_all)
    else:
        st.markdown(precond_tiles(), unsafe_allow_html=True)
        if state == "standby":
            st.info(t("geo_standby"))
            st.button(t("geo_restart"), key=prefix + "_geo_restart", on_click=geo_restart)


def render_geo_banner(show_card=True):
    """Shown on every page while you are away: the consent prompt (Autonomous OFF) or the live arrival card."""
    ss = st.session_state
    if ss.conn["mode"] != "away":
        return
    state = ss.geo["state"]
    if state == "pending":
        msg = t("geo_alert", n=html.escape(first_name()), m=eta_min(ss.geo["km"]))
        st.markdown('<div class="geo">' + msg + "</div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        b1.button(t("geo_yes"), on_click=geo_confirm, type="primary", key="geo_yes_btn")
        b2.button(t("geo_no"), on_click=geo_dismiss, key="geo_no_btn")
    elif state == "active" and show_card:
        render_precond_card("gb")
    if state in ("pending", "active"):
        ring = not ss.geo["chimed"]
        ss.geo["chimed"] = True
        if ring:
            chime_component(True)


def geo_sim_controls():
    ss = st.session_state
    gkey = "geo_km_" + str(ss.geo.get("rev", 0))
    st.slider(t("geo_dist"), 0, 20, value=int(ss.geo["km"]), key=gkey, on_change=cb_geo_slider, args=(gkey,))
    q = st.columns(5)
    for col, km in zip(q, (20, 15, 10, 5, 0)):
        col.button(str(km) + " km", key="gj_" + str(km), on_click=geo_jump, args=(km,))


def render_connection():
    ss = st.session_state
    zen = ss.ui_mode == "zen"
    st.subheader("📡 " + t("conn_title"))
    modes = ["home", "away"]
    st.radio(t("conn_mode"), modes, index=modes.index(ss.conn["mode"]), key="conn_sel", horizontal=True,
             format_func=lambda m: t("conn_home") if m == "home" else t("conn_away"), on_change=set_conn)
    st.toggle(t("geo_auto_toggle"), value=bool(ss.cfg.get("geo_auto", True)), key="geo_auto_rc",
              on_change=cb_geo_auto, args=("geo_auto_rc",))
    st.caption(t("geo_auto_hint"))
    if ss.conn["mode"] == "home":
        st.caption(t("conn_local_cap"))
        return
    st.caption(t("conn_cloud_cap"))
    km = ss.geo["km"]
    if zen:
        st.markdown("**" + t("watch_eta", m=eta_min(km)) + "**")
        with st.expander(t("geo_sim")):
            geo_sim_controls()
    else:
        geo_sim_controls()
        zone = {"idle": "geo_idle", "pending": "geo_pending", "confirmed": "geo_confirmed", "dismissed": "geo_dismissed",
                "active": "geo_active", "standby": "geo_standby_zone"}[ss.geo["state"]]
        m = st.columns(3)
        m[0].markdown(stat(t("geo_dist_m"), str(km) + " km"), unsafe_allow_html=True)
        m[1].markdown(stat(t("geo_eta"), str(eta_min(km)) + " mins"), unsafe_allow_html=True)
        m[2].markdown(stat(t("geo_zone"), t(zone)), unsafe_allow_html=True)
        st.progress(max(0.0, min(1.0, 1 - km / 20.0)))
    st.markdown("**" + t("remote_status") + "**")
    render_precond_card("rc")


def loc_readout():
    ss, cfg = st.session_state, st.session_state.cfg
    eng = engine_of(cfg["tracker"])
    room = ss.presence["room"]
    names = list(ss.spaces)
    if ss.conn["mode"] != "home":
        return
    if eng == "UWB":
        c = st.columns(4)
        c[0].markdown(stat(t("ml_zone"), ss.spaces[room]["icon"] + " " + tr_room(room)), unsafe_allow_html=True)
        c[1].markdown(stat(t("ml_dist"), str(random.randint(25, 160)) + " cm"), unsafe_allow_html=True)
        c[2].markdown(stat(t("ml_aoa"), str(random.randint(-60, 60)) + "°"), unsafe_allow_html=True)
        c[3].markdown(stat(t("ml_acc"), "± 10 cm"), unsafe_allow_html=True)
    else:
        idx = {n: i for i, n in enumerate(names)}
        rows = []
        for n in names:
            dist = 1.5 if n == room else 2 + 4 * abs(idx[n] - idx[room])
            rows.append({"Room anchor": tr_room(n), "RSSI (dBm)": int(-45 - 20 * math.log10(max(dist, 1)) + random.gauss(0, 1.5))})
        best = max(rows, key=lambda x: x["RSSI (dBm)"])["Room anchor"]
        c = st.columns(2)
        c[0].markdown(stat(t("ml_est"), ss.spaces[best]["icon"] + " " + tr_room(best)), unsafe_allow_html=True)
        c[1].markdown(stat(t("ml_acc"), "Room level"), unsafe_allow_html=True)
        st.caption(t("ml_rssi"))
        html_table(rows)
    calm = ss.room_mode.get(room)
    if calm == CALM_MODE:
        st.info(t("calm_note", r=tr_room(room), m=tr_mode(calm)))


def render_microloc():
    ss, cfg = st.session_state, st.session_state.cfg
    zen = ss.ui_mode == "zen"
    st.subheader("📍 " + t("ml_title"))
    if not zen:
        opts = UWB_DEVICES + BLE_DEVICES
        c1, c2 = st.columns([2, 3])
        cfg["tracker"] = c1.selectbox(t("ml_dev"), opts, index=opts.index(cfg["tracker"]),
                                      format_func=lambda x: ("📡 UWB · " if x in UWB_DEVICES else "📶 BLE · ") + x)
        eng = engine_of(cfg["tracker"])
        c2.markdown(stat(t("ml_engine"), t("ml_uwb") if eng == "UWB" else t("ml_ble")), unsafe_allow_html=True)
    if ss.conn["mode"] == "home":
        skey = "sim_room_" + ss.presence["room"]
        seg(t("ml_sim"), list(ss.spaces), skey, lambda n: ss.spaces[n]["icon"] + " " + tr_room(n), on_change=on_sim_move,
            args=(skey,), selected=ss.presence["room"])
    else:
        st.info(t("ml_away"))
    if zen:
        f1, f3 = st.columns(2)
    else:
        f1, f2, f3 = st.columns(3)
    cfg["follow_me"] = f1.toggle(t("ml_follow"), value=cfg["follow_me"])
    if not zen:
        cuts = ["Off", "Eco standby"]
        cfg["cut_mode"] = f2.selectbox(t("ml_cut"), cuts, index=cuts.index(cfg["cut_mode"]),
                                       format_func=lambda x: "OFF" if x == "Off" else "Eco standby (27 °C)")
    cfg["calm_on"] = f3.toggle(t("ml_calm"), value=cfg["calm_on"])
    if not zen:
        run_live(loc_readout)


def flush_rerun():
    """Run at the END of the fragment: a single debounced full-app rerun when automation changed the atmosphere."""
    ss = st.session_state
    if not ss.get("rerun_pending"):
        return
    if time.time() - ss.get("last_rerun", 0.0) < 1.5:
        return
    ss["rerun_pending"] = False
    ss["last_rerun"] = time.time()
    try:
        st.rerun(scope="app")
    except TypeError:
        st.rerun()


def bio_panel(zen=False):
    ss, cfg = st.session_state, st.session_state.cfg
    r = read_biometrics()
    ss.hr_hist = (ss.hr_hist + [r["hr"]])[-60:]
    res = analyze(r)
    home = ss.conn["mode"] == "home"
    try:
        if run_routines():
            ss.flash = "⏰ " + t("rt_ranmsg")
            ss.rerun_pending = True
        ev = room_calm_step(r["hr"])
        if ev:
            ss.flash = ("🌊 " + tr_room(ss.presence["room"]) + " calm mode") if ev == "on" else ("🌤 " + tr_room(ss.presence["room"]) + " normal")
            ss.rerun_pending = True
        if cfg["auto_mode"] and home and automation_step(res, r):
            ss.flash = "🫀 " + t("st_" + res["state"]) + " → " + tr_mode(ss.active_mode)
            ss.rerun_pending = True
    except Exception as e:
        log("⚠ automation step skipped: " + type(e).__name__)
    if cfg["auto_mode"] and not home:
        st.caption("🚗 " + t("away_pause"))
    if cfg["source"] == "wear" and not r["live"]:
        st.caption("⚠️ " + t("offline"))
    if zen:
        st.caption(t("zen_well", s=t("st_" + res["state"])))
        flush_rerun()
        return
    b = st.columns(5)
    b[0].markdown(stat(t("state_lbl"), t("st_" + res["state"])), unsafe_allow_html=True)
    b[1].markdown(stat(t("bpm"), r["hr"]), unsafe_allow_html=True)
    b[2].markdown(stat("HRV (ms)", r["hrv"]), unsafe_allow_html=True)
    b[3].markdown(stat(t("spo2"), r["spo2"]), unsafe_allow_html=True)
    b[4].markdown(stat(t("skin"), r["skin"]), unsafe_allow_html=True)
    themed_line_chart(ss.hr_hist, 220)
    st.markdown("**" + t("live_dev") + "**")
    live_devices()
    mode_line = t("mode_auto").split(" (")[0] if cfg["auto_mode"] else t("mode_manual")
    st.markdown('<div class="aibox"><b>🌿 ' + t("ai_auto") + "</b> · " + html.escape(mode_line) + "<br>" +
                html.escape(t("feel", s=t("st_" + res["state"]), m=tr_mode(eff_mode()))) +
                "<br><span class='logl'>" + html.escape(res["reason"]) + "</span></div>",
                unsafe_allow_html=True)
    with st.expander("📜 " + t("ai_log")):
        for e in ss.log[:8]:
            st.markdown('<div class="logl">' + e["t"] + "  " + html.escape(e["x"]) + "</div>", unsafe_allow_html=True)
    flush_rerun()


def bio_panel_zen():
    bio_panel(True)


def page_dashboard_pro():
    ss, cfg = st.session_state, st.session_state.cfg
    st.header(t("p1"))
    render_rooms()
    render_zero_ui()
    render_family_panel()
    cfg["auto_mode"] = st.radio(t("mode_sel"), [False, True], index=1 if cfg["auto_mode"] else 0,
                                format_func=lambda a: t("mode_auto") if a else t("mode_manual"), horizontal=True)
    if cfg["auto_mode"] and not ss.prev_auto:
        ss.last_state = None
    ss.prev_auto = cfg["auto_mode"]
    c1, c2 = st.columns(2)
    with c1:
        if not cfg["auto_mode"]:
            names = list(ss.modes.keys())
            choice = st.selectbox(t("atmos"), names, index=names.index(ss.active_mode), format_func=tr_mode)
            if choice != ss.active_mode:
                clear_room_override(ss.presence["room"])
                apply_mode(choice)
        else:
            st.info(t("auto_on"))
    with c2:
        opts = [0, 15, 30, 45, 60, 90, 120]
        new_t = st.selectbox(t("timer"), opts, index=opts.index(cfg["timer"]),
                             format_func=lambda x: t("off") if x == 0 else str(x) + " " + t("min"))
        if new_t != cfg["timer"]:
            cfg["timer"] = new_t
            cfg["tok"] += 1

    shown = eff_mode()
    m = st.columns(2)
    m[0].markdown(stat(t("active"), tr_mode(shown)), unsafe_allow_html=True)
    m[1].markdown(stat(t("genre"), ss.modes[shown]["genre"]), unsafe_allow_html=True)

    st.caption("⚙ " + t("rs_dash_hint"))

    st.subheader("🎧 " + t("studio"))
    studio = st.container()
    with st.expander("🎚 " + t("mixer"), expanded=True):
        cfg["bed"] = st.slider(t("bed"), 0, 100, int(cfg["bed"]))
        cols = st.columns(2)
        for i, ins in enumerate(INSTRUMENTS):
            with cols[i % 2]:
                cfg["mix"][ins] = st.slider(ins + " (%)", 0, 100, int(cfg["mix"][ins]))
    with studio:
        audio_component(synth_params(shown), True)

    st.subheader("🫀 " + t("bio"))
    if not cfg["auto_mode"]:
        st.caption(t("auto_hint"))
    b1, b2 = st.columns(2)
    srcs = ["sim", "wear"]
    cfg["source"] = b1.radio(t("source"), srcs, index=srcs.index(cfg["source"]), horizontal=True,
                             format_func=lambda s: t(s))
    if cfg["source"] == "sim":
        scns = list(SCN.keys())
        cfg["scn"] = b2.selectbox(t("scn"), scns, index=scns.index(cfg["scn"]), format_func=lambda s: t("st_" + s))
    if hasattr(st, "fragment"):
        st.fragment(run_every=cfg["poll"])(bio_panel)()
    else:
        bio_panel()
        st.button("↻ Refresh")


# ----------------------------------------------------------------------------
# Zen Mode dashboard, Zero-UI layer, family logic
# ----------------------------------------------------------------------------
def light_words(color, lvl):
    r, g, b = hex_rgb(color)
    if r > 200 and g > 200 and b > 200:
        tone_key = "Daylight White" if lvl > 70 else "Soft White"
    elif r >= 200 and 130 <= g <= 215 and b < 160:
        tone_key = "Warm Candlelight"
    elif b > r and b > g:
        tone_key = "Calm Blue"
    elif g > r and g >= b:
        tone_key = "Fresh Green"
    elif r < 140 and b > 80:
        tone_key = "Violet Glow"
    else:
        tone_key = "Warm Amber"
    adj_key = "Dim" if lvl < 25 else ("Soft" if lvl < 60 else "Bright")
    lang = st.session_state.get("lang", "English")
    adj = LIGHT_ADJ[adj_key].get(lang, adj_key)
    tone = LIGHT_WORDS[tone_key].get(lang, tone_key)
    return adj + " " + tone


def plain_ambience(room):
    ss = st.session_state
    devs = space_devs(room)
    ac = next((d for d in devs if d["cid"] in ("ac", "thermo", "heater") and d["on"]), None)
    temp = int(ac["lvl"]) if ac else int(ss.modes[eff_mode()]["ac"])
    bulb = next((d for d in devs if d["cid"] in BULBLIKE + ("lamp", "ledstrip") and d["on"]), None)
    light = light_words(bulb["color"], int(bulb["lvl"])) if bulb else t("zen_lights_off")
    return temp, light


def render_zen_card(room, mode):
    ss = st.session_state
    sp = ss.spaces[room]
    temp, light = plain_ambience(room)
    extra = ""
    if ss.get("guest_mode"):
        extra = "👥 " + t("guest_on")
    elif room in ss.get("family_lock", ()):
        extra = "👨‍👩‍👧 " + t("occ_lock")
    st.markdown('<div class="zen"><div class="zr">' + sp["icon"] + " " + html.escape(tr_room(room)) + " · " + html.escape(tr_mode(mode)) +
                '</div><div class="zl">' + html.escape(t("zen_comfort", c=temp)) + " · " + html.escape(light) +
                '</div><div class="zs">' + html.escape(extra) + "</div></div>", unsafe_allow_html=True)


def set_away_mode():
    """One touch: everything non-essential off (AC to eco), then the geofence takes over for the way back."""
    ss = st.session_state
    for d in ss.fleet:
        if held(d):
            continue
        if d["cid"] == "ac":
            set_dev(d, True, 27, why="Away Mode: eco standby")
        elif d["cid"] in CUT_CIDS or d["cid"] in ("fan", "tv", "projector", "speaker", "spatial", "diffuser", "scent"):
            set_dev(d, False, why="Away Mode: switched off")
    switch_conn("away")
    log("🚗 Away Mode: the home is on standby. AuraSync will prepare your arrival automatically")
    ss.flash = "🚗 " + t("zen_away")


def go_home_mode():
    switch_conn("home")
    st.session_state.flash = "🏠 " + t("zen_home")


def zen_go(kind):
    ss = st.session_state
    room = ss.presence["room"]
    if kind == "away":
        return set_away_mode() if ss.conn["mode"] == "home" else go_home_mode()
    mode = {"relax": "Relax Evening", "focus": "Focus", "sleep": WIND_MODE}[kind]
    if mode not in ss.modes:
        return
    clear_room_override(room)
    apply_mode(mode)
    if kind == "sleep":
        ss.fade_tok += 1
    ss.flash = "✨ " + tr_mode(mode)


def page_dashboard_zen():
    ss, cfg = st.session_state, st.session_state.cfg
    st.header(t("p1"))
    render_rooms()
    shown = eff_mode()
    render_zen_card(current_room(), shown)
    st.markdown("**" + t("zen_quick") + "**")
    away = ss.conn["mode"] == "away"
    items = (("relax", "🌿 " + t("zen_relax"), "Relax Evening"), ("focus", "💼 " + t("zen_focus"), "Focus"),
             ("sleep", "🌙 " + t("zen_sleep"), WIND_MODE),
             ("away", ("🏠 " + t("zen_home")) if away else ("🚗 " + t("zen_away")), None))
    for col, (k, label, mode) in zip(st.columns(4), items):
        col.button(label, key="zenbtn_" + k, type=("primary" if (mode and ss.active_mode == mode) else "secondary"),
                   on_click=zen_go, args=(k,))
    studio = st.container()
    with studio:
        audio_component(synth_params(shown), True)
    cfg["auto_mode"] = st.toggle(t("zen_auto"), value=bool(cfg["auto_mode"]))
    if cfg["auto_mode"] and not ss.prev_auto:
        ss.last_state = None
    ss.prev_auto = cfg["auto_mode"]
    render_zero_ui()
    render_family_panel()
    st.caption(t("zen_hidden"))
    if hasattr(st, "fragment"):
        st.fragment(run_every=cfg["poll"])(bio_panel_zen)()
    else:
        bio_panel(True)


def page_dashboard():
    if st.session_state.ui_mode == "pro":
        page_dashboard_pro()
    else:
        page_dashboard_zen()


# ---- Zero-UI: lock-screen card, rotary dial, voice quick-bar
def render_watch_card():
    ss = st.session_state
    away = ss.conn["mode"] == "away"
    bath, ac = geo_dev("geyser"), geo_dev("ac")
    st.markdown("**" + t("watch_title") + "**")
    if away and ss.geo["state"] == "active":
        km = ss.geo["km"]
        bits = [t("watch_eta", m=eta_min(km)),
                t("watch_preheat", v=bath["lvl"]) if (bath and bath["on"]) else t("watch_geyser_off"),
                t("watch_ac", v=ac["lvl"]) if (ac and ac["on"]) else t("watch_ac_off")]
    elif away:
        bits = [t("watch_eta", m=eta_min(ss.geo["km"])), t("watch_standby")]
    else:
        room = ss.presence["room"]
        bits = [t("watch_home"), ss.spaces[room]["icon"] + " " + tr_room(room), "🎼 " + tr_mode(eff_mode())]
    st.markdown('<div class="island">' + "".join('<span class="it">' + html.escape(b) + "</span>" for b in bits) + "</div>",
                unsafe_allow_html=True)
    st.button(t("watch_cancel"), key="watch_cancel_btn", on_click=geo_cancel_all,
              disabled=not (away and ss.geo["state"] == "active"))


LIGHT_CIDS = ("bulb", "tasklight", "ambilight", "lamp", "ledstrip", "dimmer")
DIAL_ORDER = ["Relax Evening", "Focus", "Deep Meditation", "Zen Garden", "Energize", "Sleep"]


def dial_values(room):
    devs = space_devs(room)
    lights = [d["lvl"] for d in devs if d["cid"] in LIGHT_CIDS and d["on"]]
    acs = [d["lvl"] for d in devs if d["cid"] in ("ac", "thermo", "heater") and d["on"]]
    bright = int(sum(lights) / len(lights)) if lights else 0
    temp = int(sum(acs) / len(acs)) if acs else None
    return bright, temp


def cb_dial_tap():
    ss = st.session_state
    room = current_room()
    order = [m for m in DIAL_ORDER if m in ss.modes]
    if not order:
        return
    i = (ss.dial_idx.get(room, -1) + 1) % len(order)
    ss.dial_idx[room] = i
    mode = order[i]
    if room not in ss.get("family_lock", ()):
        ss.room_mode[room] = mode
    apply_mode(mode, why=False, devs=space_devs(room), set_active=False)
    log("🔘 Dial tap: " + room + " → " + mode)
    ss.flash = "🔘 " + tr_room(room) + " · " + tr_mode(mode)


def cb_dial_turn(delta):
    ss = st.session_state
    room = current_room()
    scope = ss.get("dial_scope", "both")
    for d in space_devs(room):
        c = d["cid"]
        if scope in ("lights", "both") and c in LIGHT_CIDS:
            if delta > 0 and not d["on"]:
                set_dev(d, True, 30)
            elif d["on"]:
                set_dev(d, lvl=d["lvl"] + 10 * delta)
        if scope in ("climate", "both") and c in ("ac", "thermo", "heater") and d["on"]:
            set_dev(d, lvl=d["lvl"] + delta)
    bright, temp = dial_values(room)
    log("🔄 Dial turned " + ("clockwise" if delta > 0 else "counter-clockwise") + " in " + room)
    ss.flash = "🔄 " + str(bright) + "%" + ((" · " + str(temp) + " °C") if temp else "")


def render_dial():
    ss = st.session_state
    room = current_room()
    bright, temp = dial_values(room)
    p = pal()
    st.markdown("**" + t("dial_title") + "**")
    left, right = st.columns([1, 2])
    ring = ('<div style="width:150px;height:150px;border-radius:50%;margin:auto;'
            'background:conic-gradient(' + p["ACC"] + " " + str(bright * 3.6) + "deg," + p["BORDER"] + " 0);"
            'display:flex;align-items:center;justify-content:center;">'
            '<div style="width:112px;height:112px;border-radius:50%;background:' + p["CARD1"] + ';display:flex;'
            'flex-direction:column;align-items:center;justify-content:center;color:' + p["TXT"] + ';">'
            '<div style="font-size:1.5rem;font-weight:700;">' + (str(temp) + "°C" if temp else "--") + '</div>'
            '<div style="font-size:.8rem;color:' + p["MUTE"] + ';">' + str(bright) + "% 💡</div></div></div>")
    left.markdown(ring, unsafe_allow_html=True)
    with right:
        b = st.columns(3)
        b[0].button(t("dial_ccw"), key="dial_ccw_btn", on_click=cb_dial_turn, args=(-1,))
        b[1].button(t("dial_tap"), key="dial_tap_btn", type="primary", on_click=cb_dial_tap)
        b[2].button(t("dial_cw"), key="dial_cw_btn", on_click=cb_dial_turn, args=(1,))
        scopes = ["lights", "climate", "both"]
        st.radio(t("dial_scope"), scopes, index=scopes.index(ss.dial_scope), horizontal=True, key="dial_scope_w",
                 format_func=lambda s: t("dial_" + s) if s != "both" else t("dial_both"), on_change=cb_dial_scope)
        st.caption(t("dial_hint"))


def cb_dial_scope():
    ss = st.session_state
    if ss.get("dial_scope_w") in ("lights", "climate", "both"):
        ss.dial_scope = ss.dial_scope_w


VOICE_INTENTS = (
    ("home", ("i'm home", "im home", "back home", "i am home", "arrived home")),
    ("away", ("leaving", "going out", "heading out", "away mode", "bye")),
    ("movie", ("movie", "film", "cinema", "netflix", "watch tv")),
    ("work", ("work", "focus", "study", "office", "meeting", "concentrate")),
    ("sleep", ("tired", "sleepy", "sleep", "bed", "exhausted", "good night", "goodnight")),
    ("relax", ("relax", "unwind", "chill", "calm")),
    ("off", ("lights off", "turn off", "switch off")),
    ("dim", ("dim", "darker", "too bright")),
    ("bright", ("brighter", "too dark", "more light")),
    ("cool", ("too hot", "hot", "stuffy", "cooler")),
    ("warm", ("too cold", "cold", "chilly", "warmer")),
)


def voice_do(kind):
    ss = st.session_state
    room = current_room()
    near = space_devs(room)
    if kind == "sleep":
        clear_room_override(ss.presence["room"])
        apply_mode(WIND_MODE)
        ss.fade_tok += 1
        for d in ss.fleet:
            if d["cid"] in BULBLIKE and d["on"] and d["lvl"] > 10 and d["room"] == ss.presence["room"]:
                set_dev(d, lvl=8)
        return "🌙 Wind-Down Sleep is on and the bulbs are dimmed. Rest well."
    if kind == "work":
        clear_room_override(ss.presence["room"])
        apply_mode("Focus")
        for d in ss.fleet:
            if d["cid"] == "tasklight" and d["room"] in (room, ss.presence["room"], "Work Studio"):
                set_dev(d, True, 80)
        return "💼 Focus mode is on with bright task lighting."
    if kind == "movie":
        clear_room_override(ss.presence["room"])
        apply_mode(CINEMA_MODE)
        for d in near:
            if d["cid"] in ("tv", "projector"):
                set_dev(d, True)
            if d["cid"] == "curtain":
                set_dev(d, True, 0)
        return "🎬 Curtains closed and Cinematic lighting is on. Enjoy the movie."
    if kind == "relax":
        clear_room_override(ss.presence["room"])
        apply_mode("Relax Evening")
        return "🌿 Relax Evening is on."
    if kind == "away":
        set_away_mode()
        return "🚗 Away Mode is on. I will prepare your arrival."
    if kind == "home":
        go_home_mode()
        return "🏠 Welcome home."
    if kind in ("dim", "bright", "off"):
        for d in near:
            if d["cid"] in LIGHT_CIDS:
                if kind == "off":
                    set_dev(d, False)
                elif d["on"]:
                    set_dev(d, lvl=d["lvl"] + (20 if kind == "bright" else -20))
        return "💡 Done."
    if kind in ("cool", "warm"):
        for d in near:
            if d["cid"] in ("ac", "thermo", "heater") and d["on"]:
                set_dev(d, lvl=d["lvl"] + (-1 if kind == "cool" else 1))
        return "❄️ Climate adjusted by 1 °C."
    return ""


def run_voice(text):
    low = (text or "").lower().strip()
    for kind, keys in VOICE_INTENTS:
        if any(k in low for k in keys):
            msg = voice_do(kind)
            if msg:
                log("🎙️ Voice: “" + text.strip() + "” → " + kind)
                return msg
    return t("voice_unknown")


def cb_voice_send():
    ss = st.session_state
    txt = (ss.get("voice_txt") or "").strip()
    if txt:
        ss.voice_last = run_voice(txt)


def cb_voice_preset(text):
    st.session_state.voice_last = run_voice(text)


def render_voice_bar():
    ss = st.session_state
    st.markdown("**" + t("voice_title") + "**")
    cols = st.columns(3)
    for col, (k, text) in zip(cols, (("tired", "I'm tired"), ("work", "Starting work"), ("movie", "Family movie time"))):
        col.button(t("voice_" + k), key="voice_p_" + k, on_click=cb_voice_preset, args=(text,))
    with st.form("voice_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        c1.text_input(t("voice_title"), key="voice_txt", placeholder=t("voice_ph"), label_visibility="collapsed")
        c2.form_submit_button(t("voice_send"), on_click=cb_voice_send)
    if ss.voice_last:
        st.caption(ss.voice_last)


def render_zero_ui():
    render_watch_card()
    render_voice_bar()
    render_dial()


# ---- Family logic: shared-room occupancy guard + Guest Mode
def apply_neutral(room):
    ss = st.session_state
    ss.room_mode[room] = NEUTRAL_MODE
    apply_mode(NEUTRAL_MODE, why=False, devs=space_devs(room), set_active=False)


def cb_occ(room, key):
    ss = st.session_state
    n = ss.get(key, 1)
    ss.occupancy[room] = 2 if n == 2 else 1
    if ss.occupancy[room] == 2 and room_persona(room) == "shared":
        ss.family_lock.add(room)
        apply_neutral(room)
        log("👨‍👩‍👧 " + room + ": 2+ family members. Body signals are locked out; the room holds Neutral Family Ambience")
    else:
        if room in ss.family_lock:
            ss.family_lock.discard(room)
            ss.room_mode.pop(room, None)
            apply_mode(ss.active_mode, why=False, devs=space_devs(room), set_active=False)
            log("👤 " + room + ": back to one person. Personal comfort resumes")


def apply_guest_presets():
    ss = st.session_state
    mode = "Relax Evening" if "Relax Evening" in ss.modes else list(ss.modes)[0]
    for r in list(ss.room_mode):
        if r not in ss.family_lock:
            ss.room_mode.pop(r, None)
    apply_mode(mode, why=False, devs=list(ss.fleet))
    for d in ss.fleet:
        if d["cid"] == "ac":
            set_dev(d, True, 24)


def cb_guest(key):
    ss = st.session_state
    on = bool(ss.get(key))
    ss.guest_mode = on
    ss.guest_rev = ss.get("guest_rev", 0) + 1
    if on:
        apply_guest_presets()
        log("👥 Guest Mode ON: the whole home holds a welcoming, steady atmosphere")
    else:
        log("👥 Guest Mode OFF: automatic comfort resumes")


def guest_toggle(prefix):
    ss = st.session_state
    key = prefix + "_" + str(ss.get("guest_rev", 0))
    st.toggle("👥 " + t("guest_toggle") + " (ON / OFF)", value=bool(ss.guest_mode), key=key, on_change=cb_guest, args=(key,))


def render_family_panel():
    ss = st.session_state
    room = current_room()
    persona = room_persona(room)
    c1, c2 = st.columns(2)
    with c1:
        guest_toggle("guest_db")
        st.caption(t("guest_hint"))
    with c2:
        st.markdown("**" + ("🛋️ " if persona == "shared" else "🔒 ") + t("persona_" + persona) + "** · " + html.escape(tr_room(room)))
        if persona == "shared":
            key = "occ_" + room
            ss.occupancy.setdefault(room, 1)
            st.radio(t("occ_label"), [1, 2], index=ss.occupancy[room] - 1, horizontal=True, key=key,
                     format_func=lambda n: t("occ_1") if n == 1 else t("occ_2"), on_change=cb_occ, args=(room, key))
            if room in ss.family_lock:
                st.info(t("occ_lock"))


# ---- Matter 1.3 plug & play onboarding (simulated pairing)
MATTER_RE = re.compile(r"^MT:[A-Z0-9.\-]{8,40}$")
MATTER_MANUAL = re.compile(r"^\d{4}-?\d{3}-?\d{4}$")
MATTER_KINDS = [("bulb", "Philips WiZ Bulb"), ("diffuser", "Smart Scent Diffuser"), ("curtain", "Curtain Motor")]


def matter_valid(code):
    c = (code or "").strip().upper()
    return bool(MATTER_RE.match(c) or MATTER_MANUAL.match(c))


def matter_kind(code):
    h = int(hashlib.sha1(code.strip().upper().encode()).hexdigest(), 16)
    return MATTER_KINDS[h % len(MATTER_KINDS)]


def matter_add(code, room):
    ss = st.session_state
    cid, label = matter_kind(code)
    nd = new_device(cid, unique_name(label), room)
    nd["proto"], nd["status"], nd["addr"] = "Matter over Thread/Wi-Fi", "connected", ""
    nd["last"] = "paired with Matter 1.3 in 5 s"
    ss.fleet.append(nd)
    ss.spaces[room]["devices"].append(nd["uid"])
    ss.room_rev = ss.get("room_rev", 0) + 1
    log("📷 Matter: " + nd["name"] + " paired and bound to " + room)
    return nd


def matter_body():
    ss = st.session_state
    st.caption(t("matter_help"))
    code = st.text_input(t("matter_code"), key="mt_code", placeholder="MT:Y.K10000000000")
    rooms = list(ss.spaces)
    room = st.selectbox(t("matter_room"), rooms, index=rooms.index(current_room()), key="mt_room",
                        format_func=tr_room)
    c1, c2 = st.columns(2)
    pair = c1.button(t("matter_pair"), key="mt_pair", type="primary")
    demo = c2.button(t("matter_demo"), key="mt_demo")
    if not (pair or demo):
        return
    use = code.strip().upper() if pair else "MT:DEMO" + str(random.randint(10000, 99999))
    if pair and not matter_valid(use):
        st.error(t("matter_bad"))
        return
    bar, box = st.progress(0.0), st.empty()
    steps = ("matter_s1", "matter_s2", "matter_s3", "matter_s4", "matter_s5")
    for i, s in enumerate(steps):
        box.markdown("**" + t(s) + "**")
        bar.progress((i + 1) / len(steps))
        time.sleep(1.0)
    nd = matter_add(use, room)
    ss.flash = "✅ " + t("matter_ok", n=nd["name"], r=tr_room(room))
    st.rerun()


def open_matter():
    title = tr(t("matter_title"))
    if hasattr(st, "dialog"):
        st.dialog(title)(matter_body)()
    else:
        with st.expander(title, expanded=True):
            matter_body()


# ----------------------------------------------------------------------------
# Page 6 - Room Settings, Remote Access & Smart Geofence
# ----------------------------------------------------------------------------
def cb_power(uid, key):
    ss = st.session_state
    d = dev_by_uid(uid)
    if d is not None and key in ss:
        set_dev(d, bool(ss[key]), why="switched by you" + (" (☁️ cloud relay)" if ss.conn["mode"] == "away" else ""))


def cb_level(uid, key):
    ss = st.session_state
    d = dev_by_uid(uid)
    if d is not None and key in ss:
        set_dev(d, lvl=ss[key], why="level set by you")


def cb_color(uid, key):
    ss = st.session_state
    d = dev_by_uid(uid)
    if d is None or key not in ss:
        return
    if valid_hex(ss[key]):
        set_dev(d, color=ss[key], why="colour set by you")
    else:
        d["rev"] = d.get("rev", 0) + 1


def cb_rename(uid, key):
    ss = st.session_state
    d = dev_by_uid(uid)
    if d is None or key not in ss:
        return
    new = (ss[key] or "").strip()
    if new == d["name"]:
        return
    d["rev"] = d.get("rev", 0) + 1     # rebuilds the input (restores the old name if the new one is rejected)
    if not new or len(new) > 40 or name_taken(new, uid):
        ss.flash = t("dev_rename_bad")
        return
    log("✏️ " + d["name"] + " renamed to " + new)
    d["name"] = new
    ss.flash = t("dev_renamed", n=new)


def cb_dev_room(uid, key):
    ss = st.session_state
    d = dev_by_uid(uid)
    r = ss.get(key)
    if d is not None and r in ss.spaces and r != d["room"]:
        assign_device(d, r)
    ss.room_rev = ss.get("room_rev", 0) + 1


def cb_dev_field(uid, key, field):
    d = dev_by_uid(uid)
    if d is not None and key in st.session_state:
        d[field] = (st.session_state[key] or "").strip()


def cb_proto(uid, key):
    d = dev_by_uid(uid)
    v = st.session_state.get(key)
    if d is not None and v and v != d["proto"]:
        d["proto"] = v
        d["status"] = "connected" if v == "Simulation" else "not connected"


COLOR_CIDS = ("bulb", "tasklight", "ambilight", "ledstrip", "lamp")


def device_editor(d, p):
    """Rename + power + level + colour for one device."""
    uid = d["uid"]
    c = CAT[d["cid"]]
    tag = p + "_" + str(uid) + "_" + str(d.get("rev", 0))
    a, b, lv, co = st.columns([3, 1.2, 3, 1])
    k = "nm_" + tag
    a.text_input(t("dev_rename"), value=d["name"], key=k, max_chars=40, on_change=cb_rename, args=(uid, k))
    k = "pwr_" + tag
    b.toggle(t("power_lbl"), value=bool(d["on"]), key=k, on_change=cb_power, args=(uid, k))
    if c[4]:
        k = "lvl_" + tag
        lo, hi = int(c[5]), int(c[6])
        lv.slider(c[4], lo, hi, value=max(lo, min(hi, int(d["lvl"]))), key=k, on_change=cb_level, args=(uid, k))
    if d["cid"] in COLOR_CIDS:
        k = "col_" + tag
        co.color_picker(t("bulb"), value=safe_hex(d["color"]), key=k, on_change=cb_color, args=(uid, k))


def add_device_here():
    ss = st.session_state
    room = current_room()
    cid = ss.get("ad_cid")
    if cid not in CAT:
        return
    base = (ss.get("ad_name") or "").strip()[:40] or CAT[cid][2]
    nd = new_device(cid, unique_name(base), room)
    ss.fleet.append(nd)
    ss.spaces[room]["devices"].append(nd["uid"])
    ss.room_rev = ss.get("room_rev", 0) + 1
    log("➕ " + nd["name"] + " added to " + room)
    ss.flash = t("rs_dev_added", n=nd["name"], r=tr_room(room))


def move_devices_here(key):
    ss = st.session_state
    room = current_room()
    moved = 0
    for uid in list(ss.get(key) or []):
        d = dev_by_uid(uid)
        if d and d["room"] != room:
            assign_device(d, room)
            moved += 1
    ss.room_rev = ss.get("room_rev", 0) + 1
    if moved:
        log("🔀 " + str(moved) + " device(s) moved into " + room)
        ss.flash = t("rs_moved", c=moved, n=tr_room(room))


def delete_space(key):
    """Delete the selected custom space."""
    ss = st.session_state
    name = current_room()
    if name in PROTECTED_SPACES:
        ss.flash = t("rs_protected")
        return
    dests = [n for n in ss.spaces if n != name]
    if not dests:
        ss.flash = t("rs_last")
        return
    dest = ss.get(key) if ss.get(key) in dests else dests[0]
    moving = [d for d in ss.fleet if d["room"] == name or d["uid"] in ss.spaces[name]["devices"]]
    for d in moving:
        assign_device(d, dest)
    ss.spaces[name]["devices"] = []
    ss.spaces.pop(name, None)
    ss.room_mode.pop(name, None)
    if ss.presence["room"] == name:
        ss.presence["room"] = dest
    repair_orphans()
    set_active_room(dest)
    log("🗑 Space deleted: " + name + " (" + str(len(moving)) + " device(s) moved to " + dest + ")")
    ss.flash = t("rs_deleted", n=tr_room(name))


def render_room_settings():
    ss = st.session_state
    st.subheader("🏠 " + t("rs_sec_room"))
    room_selector("rs", t("rs_room"))
    room = current_room()
    sp = ss.spaces[room]
    devs = space_devs(room)
    st.markdown("**" + sp["icon"] + " " + html.escape(tr_room(room)) + "** · " + str(len(devs)) + " 🔌 · " +
                ("🛋️ " if room_persona(room) == "shared" else "🔒 ") + t("persona_" + room_persona(room)))

    st.markdown("**⚡ " + t("rs_preset") + "**")
    st.caption(t("rs_preset_hint"))
    pre = sp.get("preset")
    b1, b2, b3 = st.columns([3, 2, 1])
    b1.button(t("rs_preset_save"), key="rs_pre_save", on_click=cb_save_preset)
    b2.button("⚡ " + t("rs_preset_apply", n=tr_room(room)), key="rs_pre_apply", disabled=not pre,
              on_click=cb_apply_preset, args=(room,))
    b3.button(t("rs_preset_clear"), key="rs_pre_clear", disabled=not pre, on_click=cb_clear_preset)
    if pre:
        st.caption(t("rs_preset_has", c=len(pre)))

    with st.expander(t("rs_devices"), expanded=True):
        if not devs:
            st.caption(t("room_empty"))
        for d in devs:
            with st.container(border=True):
                st.markdown("**" + CAT[d["cid"]][1] + " " + html.escape(d["name"]) + "** · " + CAT[d["cid"]][2])
                device_editor(d, "rs")
                st.button("🗑 " + t("rs_dev_remove"), key="rs_rm_" + str(d["uid"]), on_click=remove_device,
                          args=(d["uid"],))

    with st.expander(t("rs_add_dev")):
        with st.form("add_dev_form", clear_on_submit=True):
            f1, f2 = st.columns([3, 2])
            f1.selectbox(t("dev_pick"), list(CAT.keys()), key="ad_cid",
                         format_func=lambda k: CAT[k][1] + " " + CAT[k][2] + "  ·  " + CAT[k][3])
            f2.text_input(t("dev_name"), key="ad_name", max_chars=40)
            st.form_submit_button(t("dev_btn"), on_click=add_device_here)

    with st.expander(t("qc")):
        cols = st.columns(3)
        for i, d in enumerate(devs):
            with cols[i % 3]:
                k = "qc_pwr_" + str(d["uid"]) + "_" + str(d.get("rev", 0))
                st.toggle(CAT[d["cid"]][1] + " " + d["name"], value=bool(d["on"]), key=k, on_change=cb_power,
                          args=(d["uid"], k))

    with st.expander(t("add_space")):
        with st.form("add_space_form", clear_on_submit=True):
            st.text_input(t("sp_name"), key="sp_name", max_chars=40)
            f1, f2 = st.columns(2)
            f1.selectbox(t("sp_icon"), SPACE_ICONS, key="sp_icon")
            f2.selectbox(t("sp_type"), SPACE_TYPES, key="sp_type")
            st.selectbox(t("persona_pick"), ["personal", "shared"], key="sp_persona",
                         format_func=lambda x: t("persona_" + x))
            labels = {d["uid"]: CAT[d["cid"]][1] + " " + d["name"] + "  (" + d["room"] + ")" for d in ss.fleet}
            st.multiselect(t("sp_devs"), list(labels.keys()), format_func=lambda u: labels[u], key="sp_devs")
            st.form_submit_button(t("sp_btn"), on_click=create_space)

    with st.expander(t("rs_manage")):
        others = {d["uid"]: CAT[d["cid"]][1] + " " + d["name"] + "  (" + d["room"] + ")"
                  for d in ss.fleet if d["room"] != room}
        mk = "rs_move_" + str(ss.get("room_rev", 0)) + "_" + room
        st.multiselect(t("rs_move"), list(others.keys()), default=[], format_func=lambda u: others[u], key=mk)
        st.button(t("rs_move_btn"), key="rs_move_btn", on_click=move_devices_here, args=(mk,))
        st.divider()
        dests = [n for n in ss.spaces if n != room]
        if room in PROTECTED_SPACES:
            st.caption(t("rs_protected"))
        elif dests:
            dk = "rs_dest_" + str(ss.get("room_rev", 0)) + "_" + room
            st.selectbox(t("rs_dest"), dests, key=dk, format_func=tr_room)
            st.button("🗑 " + t("rs_del"), key="rs_del_btn", on_click=delete_space, args=(dk,))


def page_rooms():
    st.header(t("p6"))
    st.caption(t("rs_hint"))
    render_room_settings()
    st.divider()
    render_connection()
    st.divider()
    render_microloc()


def render_routines():
    ss = st.session_state
    st.divider()
    st.subheader("⏰ " + t("rt_title"))
    st.caption(t("rt_hint"))
    today = date.today().isoformat()
    labels = {d["uid"]: CAT[d["cid"]][1] + " " + d["name"] for d in ss.fleet}
    for r in list(ss.daily_routines):
        rid = r["id"]
        with st.container(border=True):
            h1, h2 = st.columns([4, 1])
            h1.markdown("**" + html.escape(r["name"]) + "**")
            r["enabled"] = h2.toggle(t("rt_on"), value=r["enabled"], key="rt_en_" + rid)
            if r["kind"] == "wake_bath":
                a, b, c = st.columns(3)
                r["wake"] = a.time_input(t("rt_wake"), value=r["wake"], step=300, key="rt_wk_" + rid)
                r["bath"] = b.time_input(t("rt_bath"), value=r["bath"], step=300, key="rt_bt_" + rid)
                r["offset"] = c.number_input(t("rt_off"), 0, 120, int(r["offset"]), step=5, key="rt_of_" + rid)
            elif r["kind"] == "wind_down":
                a, c = st.columns(2)
                r["sleep"] = a.time_input(t("rt_sleep"), value=r["sleep"], step=300, key="rt_sl_" + rid)
                r["offset"] = c.number_input(t("rt_off"), 0, 120, int(r["offset"]), step=5, key="rt_of_" + rid)
            else:
                a, c = st.columns(2)
                r["time"] = a.time_input(t("rt_time"), value=r["time"], step=300, key="rt_tm_" + rid)
                r["offset"] = c.number_input(t("rt_off"), 0, 120, int(r["offset"]), step=5, key="rt_of_" + rid)
                keep = [u for u in r.get("uids", []) if u in labels]
                r["uids"] = st.multiselect(t("rt_devs"), list(labels.keys()), default=keep,
                                           format_func=lambda u: labels[u], key="rt_dv_" + rid)
                r["on"] = st.radio(t("rt_act"), ["Switch ON", "Switch OFF"], index=0 if r.get("on", True) else 1,
                                   horizontal=True, key="rt_ac_" + rid) == "Switch ON"
            st.info(routine_logic(r))
            f1, f2, f3 = st.columns([1, 1, 3])
            f1.button(t("rt_run"), key="rt_go_" + rid, on_click=run_routine_now, args=(rid,))
            if r["kind"] == "custom":
                f2.button("🗑", key="rt_dl_" + rid, on_click=del_routine, args=(rid,))
            if any(ss.routine_runs.get(rid + ":" + tag) == today for tag, _ in routine_events(r)):
                f3.caption(t("rt_ran"))
    with st.expander(t("rt_add")):
        with st.form("add_routine_form", clear_on_submit=True):
            st.text_input(t("rt_name"), key="nr_name")
            a, b = st.columns(2)
            a.time_input(t("rt_time"), value=dtime(18, 0), step=300, key="nr_time")
            b.number_input(t("rt_off"), 0, 120, 0, step=5, key="nr_off")
            st.multiselect(t("rt_devs"), list(labels.keys()), format_func=lambda u: labels[u], key="nr_devs")
            st.radio(t("rt_act"), ["Switch ON", "Switch OFF"], horizontal=True, key="nr_act")
            st.form_submit_button(t("save"), on_click=add_routine)


# ----------------------------------------------------------------------------
# Page 2 - Moods & Settings
# ----------------------------------------------------------------------------
def extra_name(k):
    return CAT[k][1] + " " + CAT[k][2]


def page_moods():
    if st.session_state.ui_mode == "pro":
        page_moods_pro()
        return
    st.header(t("p2"))
    st.caption(t("zen_hidden"))
    render_routines()


def page_moods_pro():
    ss = st.session_state
    st.header(t("p2"))
    st.subheader(t("std_cfg"))
    names = list(ss.modes.keys())
    sel = st.selectbox(t("mode"), names, index=names.index(ss.active_mode), key="edit_mode_sel", format_func=tr_mode)
    m = ss.modes[sel]
    c1, c2, c3, c4, c5 = st.columns(5)
    bulb = c1.color_picker(t("bulb"), m["bulb"], key="cp_" + sel)
    bright = c2.slider(t("bright"), 5, 100, int(m.get("bright", 60)), key="br_" + sel)
    fan = c3.slider(t("fan"), 0, 5, int(m["fan"]), key="fan_" + sel)
    ac = c4.slider(t("ac"), 16, 30, int(m["ac"]), key="ac_" + sel)
    genre = c5.selectbox(t("genre"), GENRES, index=GENRES.index(m["genre"]) if m["genre"] in GENRES else 0, key="gn_" + sel)
    t1, t2, t3, t4 = st.columns(4)
    bulb_on = t1.toggle(t("bulb_pw"), value=bool(m.get("bulb_on", True)), key="bo_" + sel)
    fan_on = t2.toggle(t("fan_pw"), value=bool(m.get("fan_on", True)), key="fo_" + sel)
    ac_on = t3.toggle(t("ac_pw"), value=bool(m.get("ac_on", True)), key="ao_" + sel)
    curtain = t4.slider(t("curtain"), 0, 100, int(m.get("curtain", 50)), key="cu_" + sel)
    ex = st.multiselect(t("extras"), AMB, default=[x for x in m.get("extras", []) if x in AMB],
                        format_func=extra_name, key="ex_" + sel)
    if st.button(t("save"), key="save_std"):
        if not valid_hex(bulb):
            st.warning(t("mode_bad_color"))
        else:
            ss.modes[sel] = dict(m, bulb=bulb.strip(), bright=bright, fan=fan, ac=ac, genre=genre, curtain=curtain,
                                 bulb_on=bulb_on, fan_on=fan_on, ac_on=ac_on, extras=ex, mix=full_mix(m.get("mix")))
            if sel == ss.active_mode:
                apply_mode(sel)
            ss.flash = t("saved")
            st.rerun()

    st.divider()
    st.subheader(t("custom"))
    cname = st.text_input(t("cname"), key="cm_name")
    d1, d2, d3, d4 = st.columns(4)
    scene = d1.selectbox(t("dev_bulb"), list(SCENES.keys()), key="cm_scene")
    acm = d2.selectbox(t("dev_ac"), AC_MODES, key="cm_acm")
    fanm = d3.selectbox(t("dev_fan"), list(FAN_MODES.keys()), index=1, key="cm_fan")
    actemp = d4.slider(t("ac"), 16, 30, 24, key="cm_actemp")
    q1, q2, q3, q4 = st.columns(4)
    cbo = q1.toggle(t("bulb_pw"), value=True, key="cm_bo")
    cfo = q2.toggle(t("fan_pw"), value=True, key="cm_fo")
    cao = q3.toggle(t("ac_pw"), value=True, key="cm_ao")
    ccu = q4.slider(t("curtain"), 0, 100, 50, key="cm_cu")
    cgenre = st.selectbox(t("genre"), GENRES, key="cm_genre")
    cex = st.multiselect(t("extras"), AMB, format_func=extra_name, key="cm_ex")
    st.caption(t("intens"))
    cols = st.columns(5)
    mix = {}
    for i, ins in enumerate(INSTRUMENTS):
        with cols[i % 5]:
            mix[ins] = st.slider(ins, 0, 100, 0, key="cm_mix_" + ins)
    if st.button(t("save"), key="save_custom"):
        nm = (cname or "").strip()
        col = SCENES.get(scene, "")
        if not valid_mode_name(nm):
            st.warning(t("mode_bad_name"))
        elif nm in ss.modes:
            st.warning(t("mode_dup"))
        elif not valid_hex(col):
            st.warning(t("mode_bad_color"))
        else:
            ss.modes[nm] = {"bulb": col, "bright": 60, "fan": FAN_MODES.get(fanm, 1), "ac": actemp,
                            "curtain": ccu, "genre": cgenre if cgenre in GENRES else GENRES[0], "acmode": acm,
                            "mix": full_mix(mix), "bulb_on": cbo, "fan_on": cfo, "ac_on": cao, "extras": cex}
            ss.flash = t("saved")
            st.rerun()

    render_routines()


# ----------------------------------------------------------------------------
# Background chart engine.
# ----------------------------------------------------------------------------
PL_EL = {
    "Mercury": (0.38709927, 0.00000037, 0.20563593, 0.00001906, 7.00497902, -0.00594749, 252.25032350, 149472.67411175, 77.45779628, 0.16047689, 48.33076593, -0.12534081),
    "Venus": (0.72333566, 0.00000390, 0.00677672, -0.00004107, 3.39467605, -0.00078890, 181.97909950, 58517.81538729, 131.60246718, 0.00268329, 76.67984255, -0.27769418),
    "Earth": (1.00000261, 0.00000562, 0.01671123, -0.00004392, -0.00001531, -0.01294668, 100.46457166, 35999.37244981, 102.93768193, 0.32327364, 0.0, 0.0),
    "Mars": (1.52371034, 0.00001847, 0.09339410, 0.00007882, 1.84969142, -0.00813131, -4.55343205, 19140.30268499, -23.94362959, 0.44441088, 49.55953891, -0.29257343),
    "Jupiter": (5.20288700, -0.00011607, 0.04838624, -0.00013253, 1.30439695, -0.00183714, 34.39644051, 3034.74612775, 14.72847983, 0.21252668, 100.47390909, 0.20469106),
    "Saturn": (9.53667594, -0.00125060, 0.05386179, -0.00050991, 2.48599187, 0.00193609, 49.95424423, 1222.49362201, 92.59887831, -0.41897216, 113.66242448, -0.28867794),
}
AY0 = 23.85306
CITIES = {
    "chennai": (13.08, 80.27, 5.5), "madras": (13.08, 80.27, 5.5), "madurai": (9.92, 78.12, 5.5),
    "coimbatore": (11.02, 76.96, 5.5), "trichy": (10.80, 78.69, 5.5), "tiruchirappalli": (10.80, 78.69, 5.5),
    "salem": (11.66, 78.15, 5.5), "tirunelveli": (8.73, 77.70, 5.5), "vellore": (12.92, 79.13, 5.5),
    "erode": (11.34, 77.72, 5.5), "thanjavur": (10.79, 79.14, 5.5), "tiruppur": (11.11, 77.34, 5.5),
    "bengaluru": (12.97, 77.59, 5.5), "bangalore": (12.97, 77.59, 5.5), "hyderabad": (17.39, 78.49, 5.5),
    "mumbai": (19.08, 72.88, 5.5), "delhi": (28.61, 77.21, 5.5), "kolkata": (22.57, 88.36, 5.5),
    "pune": (18.52, 73.86, 5.5), "ahmedabad": (23.02, 72.57, 5.5), "kochi": (9.93, 76.27, 5.5),
    "thiruvananthapuram": (8.52, 76.94, 5.5), "jaipur": (26.91, 75.79, 5.5), "lucknow": (26.85, 80.95, 5.5),
    "colombo": (6.93, 79.86, 5.5), "kathmandu": (27.72, 85.32, 5.75), "dhaka": (23.81, 90.41, 6.0),
    "singapore": (1.35, 103.82, 8.0), "kuala lumpur": (3.14, 101.69, 8.0), "jakarta": (-6.2, 106.85, 7.0),
    "bangkok": (13.76, 100.50, 7.0), "manila": (14.60, 120.98, 8.0), "hong kong": (22.32, 114.17, 8.0),
    "seoul": (37.57, 126.98, 9.0), "tokyo": (35.68, 139.69, 9.0), "dubai": (25.20, 55.27, 4.0),
    "doha": (25.29, 51.53, 3.0), "riyadh": (24.71, 46.68, 3.0), "istanbul": (41.01, 28.98, 3.0),
    "moscow": (55.76, 37.62, 3.0), "cairo": (30.04, 31.24, 2.0), "london": (51.51, -0.13, 0.0),
    "paris": (48.86, 2.35, 1.0), "berlin": (52.52, 13.40, 1.0), "madrid": (40.42, -3.70, 1.0),
    "new york": (40.71, -74.01, -5.0), "toronto": (43.65, -79.38, -5.0), "san francisco": (37.77, -122.42, -8.0),
    "sydney": (-33.87, 151.21, 10.0),
}


def locate(place):
    s = place.lower()
    for k, v in CITIES.items():
        if k in s:
            return v
    return CITIES["chennai"]


def _s(x):
    return math.sin(math.radians(x))


def jd_of(dt):
    y, m = dt.year, dt.month
    d = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def sun_lon(c):
    l0 = 280.46646 + 36000.76983 * c
    m = 357.52911 + 35999.05029 * c
    return (l0 + (1.914602 - 0.004817 * c) * _s(m) + 0.019993 * _s(2 * m) + 0.000289 * _s(3 * m)) % 360


def moon_lon(c):
    lp = 218.3164477 + 481267.88123421 * c
    d = 297.8501921 + 445267.1114034 * c
    m = 357.5291092 + 35999.0502909 * c
    mp = 134.9633964 + 477198.8675055 * c
    f = 93.2720950 + 483202.0175233 * c
    lon = (lp + 6.288774 * _s(mp) + 1.274027 * _s(2 * d - mp) + 0.658314 * _s(2 * d) + 0.213618 * _s(2 * mp)
           - 0.185116 * _s(m) - 0.114332 * _s(2 * f) + 0.058793 * _s(2 * d - 2 * mp) + 0.057066 * _s(2 * d - m - mp)
           + 0.053322 * _s(2 * d + mp) + 0.045758 * _s(2 * d - m) - 0.040923 * _s(m - mp) - 0.034720 * _s(d)
           - 0.030383 * _s(m + mp))
    return lon % 360


def helio(name, c):
    el = PL_EL[name]
    a, e, inc = el[0] + el[1] * c, el[2] + el[3] * c, el[4] + el[5] * c
    big_l, w, node = el[6] + el[7] * c, el[8] + el[9] * c, el[10] + el[11] * c
    mm = math.radians((big_l - w) % 360)
    ea = mm + e * math.sin(mm)
    for _ in range(6):
        ea = ea - (ea - e * math.sin(ea) - mm) / (1 - e * math.cos(ea))
    xp, yp = a * (math.cos(ea) - e), a * math.sqrt(1 - e * e) * math.sin(ea)
    om, nd, ic = math.radians(w - node), math.radians(node), math.radians(inc)
    x = (math.cos(om) * math.cos(nd) - math.sin(om) * math.sin(nd) * math.cos(ic)) * xp + \
        (-math.sin(om) * math.cos(nd) - math.cos(om) * math.sin(nd) * math.cos(ic)) * yp
    y = (math.cos(om) * math.sin(nd) + math.sin(om) * math.cos(nd) * math.cos(ic)) * xp + \
        (-math.sin(om) * math.sin(nd) + math.cos(om) * math.cos(nd) * math.cos(ic)) * yp
    return x, y


def positions(utc):
    """Approximate sidereal longitudes (0-360) of the nine bodies for a UTC datetime."""
    c = (jd_of(utc) - 2451545.0) / 36525.0
    ay = AY0 + 1.39697 * c
    ex, ey = helio("Earth", c)
    out = {"Sun": (sun_lon(c) - ay) % 360, "Moon": (moon_lon(c) - ay) % 360}
    for nm in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        x, y = helio(nm, c)
        out[nm] = (math.degrees(math.atan2(y - ey, x - ex)) - AY0) % 360
    out["Rahu"] = (125.0445479 - 1934.1362891 * c - ay) % 360
    out["Ketu"] = (out["Rahu"] + 180.0) % 360
    return out


def asc_lon(utc, lat, lon_e):
    jd = jd_of(utc)
    c = (jd - 2451545.0) / 36525.0
    gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * c * c) % 360
    ramc = math.radians((gmst + lon_e) % 360)
    eps = math.radians(23.439291 - 0.0130042 * c)
    y = math.cos(ramc)
    x = -(math.sin(ramc) * math.cos(eps) + math.tan(math.radians(lat)) * math.sin(eps))
    return (math.degrees(math.atan2(y, x)) - (AY0 + 1.39697 * c)) % 360


def build_chart(p):
    lat, lon, tz = locate(p["pob"])
    hh = p["h"] % 12 + (12 if p["ap"] == "PM" else 0)
    local = datetime(p["dob"].year, p["dob"].month, p["dob"].day, hh, p["m"])
    utc = local - timedelta(hours=tz)
    pos = positions(utc)
    return {"asc": int(asc_lon(utc, lat, lon) // 30), "pos": pos, "sign": {k: int(v // 30) for k, v in pos.items()},
            "birth": local, "tz": tz}


DASHA = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7), ("Rahu", 18), ("Jupiter", 16),
         ("Saturn", 19), ("Mercury", 17)]
SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]


def dasha_now(ch, now_local):
    moon = ch["pos"]["Moon"]
    span = 360.0 / 27
    i = int(moon // span) % 9
    frac = (moon % span) / span
    t0 = ch["birth"] - timedelta(days=frac * DASHA[i][1] * 365.25)
    while True:
        lord, yrs = DASHA[i % 9]
        end = t0 + timedelta(days=yrs * 365.25)
        if now_local < end:
            break
        t0, i = end, i + 1
    sub_start, sub, sub_end = t0, lord, end
    for k in range(9):
        sub, sy = DASHA[(i + k) % 9]
        sub_end = sub_start + timedelta(days=yrs * sy / 120.0 * 365.25)
        if now_local < sub_end:
            break
        sub_start = sub_end
    return lord, end, sub, sub_end


def chart_facts(p):
    ch = build_chart(p)
    sg, asc = ch["sign"], ch["asc"]
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    tr = positions(now_utc)
    tsg = {k: int(v // 30) for k, v in tr.items()}

    def house(pl):
        return (sg[pl] - asc) % 12 + 1

    def lord_of(offset):
        return SIGN_LORD[(asc + offset) % 12]

    def from_moon(pl):
        return (tsg[pl] - sg["Moon"]) % 12 + 1

    lord, end, sub, sub_end = dasha_now(ch, now_utc + timedelta(hours=ch["tz"]))
    day_h = from_moon("Moon")
    day = "good" if day_h in (3, 6, 10, 11) else ("tough" if day_h in (4, 8, 12) else "mid")
    f = {"lord": lord, "end": end.year, "sub": sub, "ela": asc % 4, "elm": sg["Moon"] % 4, "mod": sg["Moon"] % 3,
         "el7": (asc + 6) % 4, "l10": lord_of(9), "l7": lord_of(6), "l2": lord_of(1), "l11": lord_of(10),
         "l4": lord_of(3), "day": day, "sati": from_moon("Saturn") in (12, 1, 2),
         "jup_good": from_moon("Jupiter") in (2, 5, 7, 9, 11)}
    f["h10"] = house(f["l10"])
    for key, pl in (("hv", "Venus"), ("hm", "Mars"), ("hme", "Mercury"), ("hj", "Jupiter"), ("hk", "Ketu"),
                    ("hmoon", "Moon")):
        f[key] = house(pl)
    return f


# ----------------------------------------------------------------------------
# Divine Compass voice
# ----------------------------------------------------------------------------
ENERGY = {"Sun": "your core confidence", "Moon": "your emotional tides", "Mars": "your fire and drive",
          "Mercury": "your thinking mind", "Jupiter": "your wisdom and grace", "Venus": "your heart and love-energy",
          "Saturn": "your discipline and life-lessons", "Rahu": "your restless hunger to grow",
          "Ketu": "your detached, deeper-seeking side"}
HOUSE = ["", "your identity and personal path", "money, family and speech", "courage, skills and communication",
         "home, inner peace and roots", "creativity, learning and romance", "daily work, health and service",
         "partnership and close relationships", "transformation and hidden depths",
         "luck, higher learning and purpose", "career and public standing", "gains, friendships and big goals",
         "rest, solitude and letting go"]
ELEM = {0: "fiery, action-loving", 1: "grounded, steady", 2: "airy, curious", 3: "deep, feeling"}
NEED = {0: "action and inspiration", 1: "stability and visible progress", 2: "ideas and conversation",
        3: "emotional safety and meaning"}
PARTNER = {0: "bold, passionate", 1: "steady, dependable", 2: "witty, communicative", 3: "caring, emotionally deep"}
MODN = {0: "start-things-up", 1: "deep-focus", 2: "variety-loving"}
MODTIP = {0: "start a small project and learn by doing", 1: "go deep on one subject in long calm blocks",
          2: "mix subjects and use short, varied sessions"}
SEASON = {"Sun": "stepping into your own authority and visibility", "Moon": "emotional healing, home and nurturing",
          "Mars": "courage, action and building momentum", "Mercury": "learning, communication and smart moves",
          "Jupiter": "growth, guidance and expansion", "Venus": "love, comfort, creativity and refinement",
          "Saturn": "patient building, responsibility and deep life-lessons",
          "Rahu": "big ambition, change and unexpected turns", "Ketu": "letting go, spiritual deepening and clarity"}
DAYQ = {"good": "Today's energy around you is supportive, a good day to move on things you've been postponing.",
        "mid": "Today feels mixed and steady, so go step by step and don't rush big decisions.",
        "tough": "Today's energy is a little sensitive and heavy, so protect your peace, go slow and avoid forcing decisions."}
TA_SEASON = {"Sun": "உங்கள் சுய அதிகாரம் மற்றும் அடையாளம் வளரும்", "Moon": "மன நலம், வீடு மற்றும் அரவணைப்பு",
             "Mars": "தைரியம், செயல் மற்றும் முன்னேற்றம்", "Mercury": "கற்றல், பேச்சு மற்றும் புத்திசாலித்தனமான முடிவுகள்",
             "Jupiter": "வளர்ச்சி, வழிகாட்டுதல் மற்றும் விரிவாக்கம்", "Venus": "அன்பு, சுகம் மற்றும் படைப்பாற்றல்",
             "Saturn": "பொறுமை, பொறுப்பு மற்றும் வாழ்க்கைப் பாடங்கள்",
             "Rahu": "பெரிய ஆசை, மாற்றம் மற்றும் எதிர்பாராத திருப்பங்கள்", "Ketu": "விடுதலை, ஆன்மீக ஆழம் மற்றும் தெளிவு"}
TA_ELEM = {0: "நெருப்பு போன்ற, செயலை விரும்பும்", 1: "நிலையான, அடித்தளமான", 2: "காற்று போன்ற, ஆர்வமுள்ள",
           3: "ஆழமான, உணர்வுப்பூர்வமான"}
TA_DAY = {"good": "இன்றைய சூழல் உங்களுக்கு ஆதரவாக உள்ளது; தள்ளிப்போட்ட வேலைகளைத் தொடங்கலாம்.",
          "mid": "இன்று கலவையான நாள்; அவசர முடிவுகள் வேண்டாம், படிப்படியாகச் செல்லுங்கள்.",
          "tough": "இன்று மனம் கொஞ்சம் உணர்ச்சிவசப்படும்; அமைதியைக் காத்து, முக்கிய முடிவுகளைத் தள்ளிவையுங்கள்."}


def insight_en(topic, f):
    s = SEASON[f["lord"]]
    if topic == "work":
        return ("I see your career path being steered by " + ENERGY[f["l10"]] + ", and it lives in the zone of " +
                HOUSE[f["h10"]] + ". You're also in a long season of " + s + " until " + str(f["end"]) +
                ", so growth will come through that door.")
    if topic == "love":
        return ("Your heart-energy lives in the zone of " + HOUSE[f["hv"]] + ", and you tend to attract " +
                PARTNER[f["el7"]] + " partners. You're in a season of " + s + ", which is shaping how you love and what you tolerate.")
    if topic == "money":
        return ("Money flows to you through " + ENERGY[f["l2"]] + ", and your gains arrive via " + ENERGY[f["l11"]] + ". " +
                ("Growth energy is supporting you right now, so careful expansion works."
                 if f["jup_good"] else "This is a steady-and-save phase rather than a big-risk phase."))
    if topic == "stress":
        return ("Your nature is " + ELEM[f["elm"]] + " and it needs " + NEED[f["elm"]] + " to feel safe. " +
                ("A heavy, testing phase is passing over your emotional tides right now, which is why everything feels louder than it really is. It is temporary."
                 if f["sati"] else "Your emotional tides are asking for rest and routine more than answers."))
    if topic == "anger":
        return ("Your fire sits in the zone of " + HOUSE[f["hm"]] + ", so whenever that part of life is touched you flare fast. " +
                DAYQ[f["day"]])
    if topic == "study":
        return ("Your thinking mind works through the zone of " + HOUSE[f["hme"]] + ", and wisdom flows from " +
                HOUSE[f["hj"]] + ". As a " + MODN[f["mod"]] + " learner you absorb best when you " + MODTIP[f["mod"]] + ".")
    if topic == "purpose":
        return ("Your wisdom and grace point toward " + HOUSE[f["hj"]] + ", while your deeper-seeking side in " +
                HOUSE[f["hk"]] + " asks you to loosen your grip there. This is a season of " + s + ", which is when purpose becomes clearer.")
    if topic == "family":
        return ("Home and roots are shaped by " + ENERGY[f["l4"]] + ", with your emotional tides in the zone of " +
                HOUSE[f["hmoon"]] + ". In this season of " + s + ", family patterns are being rewritten gently.")
    if topic == "health":
        return "Your vitality follows " + ELEM[f["elm"]] + " rhythms, so protect sleep and routine first. " + DAYQ[f["day"]]
    if topic == "decide":
        return ("Timing matters: you're in a season of " + s + ". " +
                ("Growth energy is on your side, so if your gut agrees, you can move."
                 if f["jup_good"] else "The energy favours patience: gather facts and wait for one clear sign."))
    if topic == "today":
        return DAYQ[f["day"]] + " You're in a season of " + s + " until " + str(f["end"]) + "."
    return "I feel you as a " + ELEM[f["ela"]] + " soul, currently in a season of " + s + " until " + str(f["end"]) + "."


def insight_ta(topic, f):
    return ("இப்போது நீங்கள் " + TA_SEASON[f["lord"]] + " என்ற காலகட்டத்தில் இருக்கிறீர்கள் (" + str(f["end"]) +
            " வரை). உங்கள் இயல்பு " + TA_ELEM[f["elm"]] + " தன்மை கொண்டது. " + TA_DAY[f["day"]])


def insight_tg(topic, f):
    return "Naan paakkaradhu: " + insight_en(topic, f)


GUIDE_EN = {
    "work": "Stop trying to prove yourself everywhere. Choose the one outcome that matters this week, tell your team clearly, and let the rest be 'good enough'.",
    "love": "Speak the feeling underneath the complaint. Say 'I feel...' before 'You always...'. Closeness grows from honesty, not perfect timing.",
    "money": "Put income, fixed costs and one goal on a single page. Any big spend that fails that page can wait 48 hours.",
    "stress": "Breathe out slower than you breathe in for two minutes, then do just one small task. Clarity follows calm, never the other way round.",
    "anger": "Don't act for 90 seconds. Breathe in for 4, hold for 4, out for 6. Then walk or splash cold water on your face before you speak and the message will come out cleaner.",
    "study": "Study in 25-minute blocks with 5-minute breaks and the phone in another room. Teach what you learned out loud to an imaginary student, that's how it sticks.",
    "purpose": "Purpose rarely arrives as a thunderbolt. Notice what you'd do for free and what drains you, then do a little more of the first and less of the second this month.",
    "family": "Listen for one full minute without defending yourself. Most family tension softens when people feel heard before they're corrected.",
    "health": "Fix your wake-up time, dim the lights an hour before bed and keep the next seven days simple. Sleep is the base of everything.",
    "decide": "Write what you'd choose if fear were not in the room. Then ask which option you'll respect yourself for a year from now.",
    "today": "Pick one priority for today, finish it before noon, and let everything else be a bonus.",
    "general": "Take one slow breath and tell me which part feels heaviest: the situation, the people, or the uncertainty?",
}
GUIDE_TG = {
    "work": "Ellathulayum nirupikka try pannathinga. Indha week-ku mukkiyamana oru result-a mattum choose pannunga, team-kitta clear-a sollunga, mathadhu 'good enough' nu vitrunga.",
    "love": "Complaint-ku pinnadi irukkura feeling-a pesunga. 'Nee eppavum...' nu solradhukku munnadi 'Enakku... nu thonuthu' nu sollunga. Nerukkam honesty-la varum.",
    "money": "Varumanam, selavu, oru goal - moonum oru page-la ezhudhunga. Sandhegam iruntha periya selavai 48 maniyaakku wait pannunga.",
    "stress": "Rendu nimisham mella moochu vidunga (ullukku vida veliyila neram jaasthi), appuram oru sinna velaiya mattum pannunga. Amaidhikku apuram thelivu varum.",
    "anger": "90 second edhuvum seiyaadheenga. 4 count moochu ulla, 4 pidichikonga, 6 count veliya. Appuram konjam nadanga illa mugathula thanni adinga, appuram pesunga.",
    "study": "25 nimisham padinga, 5 nimisham break. Phone vera room-la vainga. Padichadha oru imaginary student-ku sollikkudunga, appo dhaan manasula nikkum.",
    "purpose": "Purpose oru nodila vaarathu. Edhu free-a pannalaam nu thonudhu, edhu energy-a edukkudhu nu gavanichu, indha month muthal-adhai konjam adhigam pannunga.",
    "family": "Oru nimisham full-a defend pannaama kelunga. Pala family tension, 'naan kekkapaduren' nu thonumbodhu thaane kuraiyum.",
    "health": "Ezhundhirikkara neratha fix pannunga, thoonga oru mani munnaadiye light kuraiyunga, adutha 7 naal simple-a vechukkonga.",
    "decide": "Bayam illanaa neenga enna choose pannuveenga nu ezhudhunga. Oru varusham kazhichum mariyaadhai kudukkara option edhu nu paarunga.",
    "today": "Indha naalukku oru mukkiya velaiya mattum choose pannunga, madhiyam munnadi mudichidunga, mathadhu bonus.",
    "general": "Oru deep breath edunga - edhu romba baaramaa irukku: soozhnilai, aalungal, illa theriyaadha vishayam?",
}
GUIDE_TA = {
    "work": "எல்லா இடத்திலும் உங்களை நிரூபிக்க முயல வேண்டாம். இந்த வாரம் முக்கியமான ஒரு இலக்கை மட்டும் தேர்ந்தெடுத்து குழுவிடம் தெளிவாகச் சொல்லுங்கள்.",
    "love": "புகாருக்குப் பின்னால் இருக்கும் உணர்வைப் பேசுங்கள். 'நீ எப்போதும்...' என்பதற்கு முன் 'எனக்கு... என்று தோன்றுகிறது' என்று சொல்லுங்கள்.",
    "money": "வருமானம், செலவு, ஒரு இலக்கு - மூன்றையும் ஒரு பக்கத்தில் எழுதுங்கள்; சந்தேகம் இருந்தால் 48 மணி நேரம் காத்திருங்கள்.",
    "stress": "இரண்டு நிமிடம் மெதுவாக மூச்சை வெளியேற்றுங்கள்; பிறகு ஒரு சிறிய வேலையை மட்டும் செய்யுங்கள். அமைதிக்குப் பிறகுதான் தெளிவு வரும்.",
    "anger": "90 வினாடி எதுவும் செய்யாதீர்கள். 4 எண்ணிக்கை உள்ளிழுத்து, 4 பிடித்து, 6 வெளியேற்றுங்கள். பிறகு கொஞ்சம் நடந்துவிட்டு பேசுங்கள்.",
    "study": "25 நிமிடம் படியுங்கள், 5 நிமிடம் ஓய்வு. போனை வேறு அறையில் வையுங்கள். படித்ததை வாய்விட்டுச் சொல்லிப் பாருங்கள்.",
    "purpose": "நோக்கம் ஒரே நொடியில் வராது. எதைச் சும்மா செய்வீர்கள், எது சோர்வடையச் செய்கிறது என்று கவனித்து, முதலாவதை இந்த மாதம் அதிகம் செய்யுங்கள்.",
    "family": "ஒரு நிமிடம் உங்களை நியாயப்படுத்தாமல் கேளுங்கள். புரிந்துகொள்ளப்படுகிறோம் என்று உணரும்போது குடும்ப பதற்றம் தானாகக் குறையும்.",
    "health": "எழும் நேரத்தை நிலைப்படுத்துங்கள்; தூங்க ஒரு மணி நேரம் முன்பே விளக்குகளை மங்கலாக்குங்கள்; அடுத்த ஏழு நாட்கள் எளிமையாக வையுங்கள்.",
    "decide": "பயம் இல்லாவிட்டால் எதைத் தேர்ந்தெடுப்பீர்கள் என்று எழுதுங்கள். ஒரு வருடம் கழித்தும் உங்களை மதிக்க வைக்கும் தேர்வு எது என்று பாருங்கள்.",
    "today": "இன்றைக்கு ஒரே ஒரு முக்கிய வேலையைத் தேர்ந்தெடுத்து மதியத்துக்குள் முடியுங்கள்; மற்றவை போனஸ்.",
    "general": "ஒரு ஆழ்ந்த மூச்சு எடுங்கள் - சூழ்நிலை, மனிதர்கள், தெரியாத எதிர்காலம் - இதில் எது அதிகம் அழுத்துகிறது?",
}
DEEPER = {
    "en": ["Try this tonight: write three lines - what I feel, what I need, one small step. Then close the page.",
           "Drink a glass of water, stand barefoot for two minutes, and breathe out longer than you breathe in.",
           "Send one honest, kind message to someone you trust. You don't have to carry this alone.",
           "Hum 'Om' slowly for one minute. The vibration settles the nervous system faster than thinking.",
           "Take a 20-minute screen-free walk and let the answers come to you instead of chasing them."],
    "tg": ["Indha raathiri idhai try pannunga: moonu line ezhudhunga - enna feel pannuren, enna venum, oru sinna step. Appuram page-a moodidunga.",
           "Oru glass thanni kudinga, rendu nimisham paadham nilathula nillunga, ulla vida veliya moochu neramaa vidunga.",
           "Nambikkai irukkura oru aal-kitta honest-aana, anbaana message anuppunga. Ellathaiyum neenga mattum sumakka venaam.",
           "Oru nimisham mella 'Om' nu hum pannunga. Yosikkiradhai vida vibration nenjai vegama amaidhiyaakkum.",
           "20 nimisham phone illaama nadanga. Pathil-a thedaama, athuvaa varattum."],
    "ta": ["இன்று இரவு முயற்சி செய்யுங்கள்: மூன்று வரி எழுதுங்கள் - நான் என்ன உணர்கிறேன், என்ன தேவை, ஒரு சிறிய படி. பிறகு பக்கத்தை மூடுங்கள்.",
           "ஒரு குவளை தண்ணீர் குடியுங்கள், இரண்டு நிமிடம் வெறுங்காலில் நில்லுங்கள், உள்ளிழுப்பதைவிட நீளமாக வெளியேற்றுங்கள்.",
           "நம்பிக்கையான ஒருவருக்கு உண்மையான, அன்பான செய்தி அனுப்புங்கள். எல்லாவற்றையும் நீங்கள் மட்டும் சுமக்க வேண்டாம்.",
           "ஒரு நிமிடம் மெதுவாக 'ஓம்' என்று ஒலியுங்கள். சிந்திப்பதை விட அந்த அதிர்வு மனதை வேகமாக அமைதியாக்கும்.",
           "20 நிமிடம் போன் இல்லாமல் நடந்து வாருங்கள்; பதில்களைத் துரத்தாமல் அவை வரட்டும்."],
}
OPEN_EN = {
    "sad": ["I'm right here with you. 🙏 Let it out, there's no hurry.", "I can feel the weight in your words. Breathe, you're not alone in this."],
    "angry": ["I hear that fire. 🔥 It's okay to feel it, let's cool it together.", "Something touched a nerve. Take one breath with me first."],
    "stress": ["Okay, pause with me for a second. 🌿 You don't have to carry it all at once.", "I feel the pressure around you. Let's slow it down together."],
    "greet": ["Hey {n} 🙏 I'm here. How's your heart today?", "Welcome back {n} ✨ I was just sensing your energy. How are you feeling?"],
    "neutral": ["I hear you, {n}. 🙏", "Thank you for trusting me with this, {n}."],
    "thanks": ["Always, {n} 💛 I'm right here whenever you need me."],
}
OPEN_TG = {
    "sad": ["Naan unga kooda irukken. 🙏 Mella sollunga, avasaram illa."],
    "angry": ["Kovam puriyuthu. 🔥 Konjam moochu edunga, naama saanthama pannalaam."],
    "stress": ["Konjam pause pannunga. 🌿 Ellaam oru nimishathula sumakka venaam."],
    "greet": ["Hey {n} 🙏 Naan inga dhaan irukken. Indha naal eppadi irukku?"],
    "neutral": ["Puriyuthu {n}. 🙏"],
    "thanks": ["Eppavum {n} 💛 Thevai-na naan inga dhaan."],
}
OPEN_TA = {
    "sad": ["நான் உங்களுடன்தான் இருக்கிறேன். 🙏 மெதுவாகச் சொல்லுங்கள்."],
    "angry": ["அந்தக் கோபம் புரிகிறது. 🔥 ஒரு மூச்சு எடுங்கள், சேர்ந்து அமைதியாக்குவோம்."],
    "stress": ["ஒரு நொடி நிறுத்துங்கள். 🌿 எல்லாவற்றையும் ஒரே நேரத்தில் சுமக்க வேண்டாம்."],
    "greet": ["வணக்கம் {n} 🙏 நான் இங்கேதான் இருக்கிறேன். இன்று எப்படி இருக்கிறீர்கள்?"],
    "neutral": ["புரிகிறது {n}. 🙏"],
    "thanks": ["எப்போதும் {n} 💛 தேவைப்படும்போது நான் இங்கே இருக்கிறேன்."],
}
CLOSE_EN = ["Tell me more: what part of this keeps replaying in your mind?",
            "Want me to look at what the next few months are showing for this?",
            "What's one small thing you could do today? I'll hold the rest with you."]
CLOSE_TG = ["Innum sollunga: edhu ungal manasula thirumba thirumba odudhu?", "Adutha konja maadhangal idhukku enna kaattudhu nu paakkava?"]
CLOSE_TA = ["இன்னும் சொல்லுங்கள்: எது உங்கள் மனதில் திரும்பத் திரும்ப ஓடுகிறது?", "அடுத்த சில மாதங்கள் இதற்கு என்ன காட்டுகின்றன என்று பார்க்கவா?"]

TANG = {"enna", "epdi", "eppadi", "romba", "seri", "naan", "nan", "ennaku", "enakku", "pannu", "panna", "iruku", "irukku",
        "illa", "vela", "velai", "kadhal", "kaadhal", "paisa", "panam", "kadan", "kashtam", "mudiyala", "venum", "thambi",
        "anna", "sollu", "kavalai", "bayam", "thookam", "kuzhappam", "kalyanam", "pannalama", "irukken", "nalla", "ippo",
        "kovam", "kobam", "kopam", "padippu", "inniku", "indru", "amma", "appa", "vanakkam", "nandri"}
LATIN = [
    ("es", {"hola", "estoy", "quiero", "necesito", "gracias", "trabajo", "dinero", "amor", "ayuda", "cómo", "pero"}),
    ("fr", {"bonjour", "salut", "merci", "travail", "argent", "amour", "pourquoi", "comment", "suis", "mais", "besoin"}),
    ("de", {"hallo", "danke", "arbeit", "geld", "liebe", "warum", "ich", "bin", "aber", "nicht", "bitte"}),
    ("it", {"ciao", "grazie", "lavoro", "soldi", "amore", "perché", "sono", "voglio", "aiuto", "bisogno"}),
    ("pt", {"olá", "obrigado", "trabalho", "dinheiro", "estou", "quero", "você", "não", "preciso"}),
    ("id", {"saya", "aku", "terima", "kasih", "kerja", "uang", "cinta", "bagaimana", "tidak", "tolong"}),
]
TOPICS = {
    "anger": {"angry", "anger", "furious", "rage", "irritated", "irritating", "temper", "kovam", "kobam", "kopam"},
    "stress": {"stress", "stressed", "anxious", "anxiety", "tired", "overwhelmed", "worried", "tension", "kavalai", "bayam", "lonely", "sad", "depressed"},
    "love": {"love", "relationship", "partner", "crush", "marriage", "kadhal", "kaadhal", "kalyanam", "breakup", "girlfriend", "boyfriend", "realtionship", "realationship"},
    "work": {"work", "job", "career", "boss", "office", "promotion", "vela", "velai", "business"},
    "money": {"money", "salary", "debt", "invest", "paisa", "panam", "kadan", "loan", "income"},
    "study": {"study", "exam", "education", "college", "school", "marks", "padippu", "padi", "course", "learn", "degree"},
    "purpose": {"purpose", "meaning", "direction", "destiny", "aim", "calling", "mission", "lost"},
    "family": {"family", "mother", "father", "amma", "appa", "parents", "wife", "husband", "kids", "child", "brother", "sister"},
    "health": {"health", "sleep", "thookam", "body", "energy", "diet", "tiredness"},
    "decide": {"decide", "decision", "confused", "choice", "should", "kuzhappam", "pannalama"},
    "today": {"today", "indru", "inniku", "tonight", "tomorrow", "daily"},
}
TA_KEYS = {"கோபம்": "anger", "கவலை": "stress", "அழுத்தம்": "stress", "பயம்": "stress", "காதல்": "love",
           "திருமணம்": "love", "வேலை": "work", "பணம்": "money", "படிப்பு": "study", "கல்வி": "study",
           "நோக்கம்": "purpose", "குடும்பம்": "family", "தூக்கம்": "health", "உடல்": "health",
           "முடிவு": "decide", "இன்று": "today"}
MOOD_WORDS = {"sad": {"sad", "depressed", "cry", "crying", "lonely", "hurt", "empty", "hopeless", "alone", "kashtam", "azhugai"},
              "angry": TOPICS["anger"],
              "stress": {"stress", "stressed", "anxious", "anxiety", "tired", "overwhelmed", "worried", "tension", "bayam", "kavalai"}}
GREET = {"hi", "hii", "hey", "heyy", "hello", "hlo", "yo", "vanakkam", "hola"}
THANKS = {"thanks", "thank", "thx", "nandri", "ty"}
FOLLOW = {"why", "how", "then", "what", "next", "more", "ok", "okay", "and", "so", "tell", "explain", "yes", "sure"}
OTHER = {
    "ko": ("저는 당신의 신성한 나침반입니다. ", "깊게 숨을 쉬어 보세요. 오늘은 작고 진심 어린 한 걸음만 내딛으세요. 명료함은 그 뒤에 따라옵니다.", "이 중 어떤 부분이 가장 무겁게 느껴지나요?"),
    "th": ("ฉันคือเข็มทิศศักดิ์สิทธิ์ของคุณ ", "หายใจเข้าลึก ๆ แล้วก้าวเล็ก ๆ ที่จริงใจเพียงหนึ่งก้าวในวันนี้ ความชัดเจนจะตามมาเอง", "ส่วนไหนที่รู้สึกหนักที่สุดสำหรับคุณ?"),
    "es": ("Soy tu Brújula Divina. ", "Respira profundo y da hoy un único paso pequeño y sincero; la claridad llegará después.", "¿Qué parte te pesa más ahora mismo?"),
    "ja": ("私はあなたの神聖なコンパスです。", "深呼吸をして、今日は小さく誠実な一歩だけ踏み出してください。明確さはそのあとについてきます。", "どの部分がいちばん重く感じますか?"),
    "zh": ("我是你的神圣罗盘。", "深呼吸一下，今天只迈出一小步真诚的脚步，清晰感会随之而来。", "其中哪一部分让你感觉最沉重？"),
    "ar": ("أنا بوصلتك الإلهية. ", "خذ نفسًا عميقًا وخطُ اليوم خطوة صغيرة وصادقة واحدة؛ فالوضوح يأتي بعدها.", "أي جزء يبدو الأثقل عليك الآن؟"),
    "hi": ("मैं आपका दिव्य कम्पास हूँ। ", "एक गहरी साँस लीजिए और आज बस एक छोटा, सच्चा कदम उठाइए; स्पष्टता उसके बाद आती है।", "इनमें से कौन-सा हिस्सा सबसे भारी लग रहा है?"),
    "ru": ("Я ваш Божественный Компас. ", "Сделайте глубокий вдох и сделайте сегодня один маленький искренний шаг — ясность придёт следом.", "Какая часть сейчас кажется самой тяжёлой?"),
    "fr": ("Je suis votre Boussole Divine. ", "Respirez profondément et faites aujourd'hui un seul petit pas sincère ; la clarté viendra ensuite.", "Quelle partie vous semble la plus lourde en ce moment ?"),
    "de": ("Ich bin dein Göttlicher Kompass. ", "Atme tief durch und geh heute nur einen kleinen, ehrlichen Schritt; die Klarheit folgt danach.", "Welcher Teil fühlt sich gerade am schwersten an?"),
    "it": ("Sono la tua Bussola Divina. ", "Fai un respiro profondo e compi oggi un solo piccolo passo sincero; la chiarezza arriverà dopo.", "Quale parte ti pesa di più in questo momento?"),
    "pt": ("Sou sua Bússola Divina. ", "Respire fundo e dê hoje um único passo pequeno e sincero; a clareza vem depois.", "Qual parte parece mais pesada agora?"),
    "id": ("Saya Kompas Ilahi Anda. ", "Tarik napas dalam dan ambil satu langkah kecil yang tulus hari ini; kejelasan akan menyusul.", "Bagian mana yang terasa paling berat sekarang?"),
}


def seed_of(*parts):
    return int(hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest(), 16)


def profile_seed(p):
    return seed_of(p["name"].strip().lower(), p["dob"], p["pob"].strip().lower(), p["tob"])


def daily_seed(p):
    return seed_of(profile_seed(p), date.today().isoformat())


def pick(pool, s, shift):
    return pool[(s >> shift) % len(pool)]


def detect_lang(msg):
    cjk = False
    for ch in msg:
        o = ord(ch)
        if 0x0B80 <= o <= 0x0BFF:
            return "ta"
        if 0xAC00 <= o <= 0xD7AF:
            return "ko"
        if 0x0E00 <= o <= 0x0E7F:
            return "th"
        if 0x3040 <= o <= 0x30FF:
            return "ja"
        if 0x0600 <= o <= 0x06FF:
            return "ar"
        if 0x0900 <= o <= 0x097F:
            return "hi"
        if 0x0400 <= o <= 0x04FF:
            return "ru"
        if 0x4E00 <= o <= 0x9FFF:
            cjk = True
    if cjk:
        return "zh"
    words = set(re.findall(r"[^\W\d_]+", msg.lower()))
    if words & TANG:
        return "tanglish"
    for code, vocab in LATIN:
        if words & vocab:
            return code
    return "en"


def detect_topic(msg):
    for key, k in TA_KEYS.items():
        if key in msg:
            return k
    words = set(re.findall(r"[a-zA-Z]+", msg.lower()))
    for k, kw in TOPICS.items():
        if words & kw:
            return k
    return None


MEM_FILE = "aurasync_user_memory.json"
YES_W = {"yes", "yeah", "yep", "yup", "sure", "ok", "okay", "please", "haan", "aama"}
NO_W = {"no", "nope", "nah", "later"}
TOPIC_LABEL = {"anger": "anger", "stress": "stress", "love": "relationships", "work": "work", "money": "money",
               "study": "your studies", "purpose": "your purpose", "family": "family", "health": "health and rest",
               "decide": "a big decision", "today": "your day", "general": "what is on your mind"}
LEARN = (
    (re.compile(r"\bmy (wife|husband|partner|mother|mom|father|dad|son|daughter|brother|sister|boss|friend|kids|parents)\b"),
     lambda m: "mentioned your " + m.group(1)),
    (re.compile(r"\bi (?:have|got|am having) an? (exam|interview|presentation|deadline|surgery|trip|wedding|meeting)\b"),
     lambda m: "have " + ("an " if m.group(1)[0] in "aeiou" else "a ") + m.group(1) + " coming up"),
    (re.compile(r"\b(?:can'?t|cannot|couldn'?t|unable to) sleep\b|\binsomnia\b|\bsleepless\b"),
     lambda m: "have been struggling to sleep"),
    (re.compile(r"\bi (?:love|like|enjoy) ([a-z ]{3,24})"), lambda m: "enjoy " + m.group(1).strip()),
    (re.compile(r"\bi work (?:as|at|in) ([a-z ]{3,24})"), lambda m: "work " + m.group(1).strip()),
)


def _mem_path():
    try:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), MEM_FILE)
    except NameError:
        return MEM_FILE


def mem_get():
    """What the companion has learned about this user."""
    ss = st.session_state
    key = ((ss.profile or {}).get("name") or "guest").strip().lower()
    cur = ss.get("user_mem")
    if cur is None or cur.get("_key") != key:
        saved = {}
        try:
            with open(_mem_path(), encoding="utf-8") as f:
                saved = json.load(f).get(key, {})
        except Exception:
            saved = {}
        cur = {"_key": key, "msgs": 0, "sessions": 0, "topics": {}, "moods": {}, "hours": {}, "notes": [],
               "last_topic": None}
        cur.update({k: v for k, v in saved.items() if k in cur and k != "_key"})
        cur["sessions"] += 1
        ss.user_mem = cur
    return cur


def mem_save():
    ss = st.session_state
    mem = ss.get("user_mem")
    if not mem:
        return
    try:
        try:
            with open(_mem_path(), encoding="utf-8") as f:
                allm = json.load(f)
        except Exception:
            allm = {}
        allm[mem["_key"]] = {k: v for k, v in mem.items() if k != "_key"}
        with open(_mem_path(), "w", encoding="utf-8") as f:
            json.dump(allm, f, ensure_ascii=False)
    except Exception:
        pass


def learn_from(msg, topic, mood):
    mem = mem_get()
    low = msg.lower()
    mem["msgs"] += 1
    if topic:
        mem["topics"][topic] = mem["topics"].get(topic, 0) + 1
        mem["last_topic"] = topic
    mem["moods"][mood] = mem["moods"].get(mood, 0) + 1
    h = str(datetime.now().hour)
    mem["hours"][h] = mem["hours"].get(h, 0) + 1
    for rx, fn in LEARN:
        m = rx.search(low)
        if m:
            note = fn(m)
            if note not in mem["notes"]:
                mem["notes"] = (mem["notes"] + [note])[-12:]
    mem_save()


def memory_line(mem, topic, prior, first):
    ss = st.session_state
    parts, h = [], datetime.now().hour
    if topic and topic != "general" and prior.get(topic, 0) >= 1:
        parts.append(TOPIC_LABEL.get(topic, topic).capitalize() + " keeps coming up for you, " + first +
                     ". That tells me it really matters.")
    elif mem["notes"] and len(ss.chat) % 3 == 0:
        parts.append("I remember that you " + mem["notes"][-1] + ".")
    if ss.get("last_state") == "stress":
        parts.append("Your wearable also shows some tension in your body right now.")
    if (h >= 23 or h < 5) and topic in ("health", "stress", "general", None):
        parts.append("It's late, so rest may help more than answers tonight.")
    return " ".join(parts)


def run_offer(kind):
    ss = st.session_state
    if kind == "sleep":
        apply_mode(WIND_MODE)
        ss.fade_tok += 1
    else:
        apply_mode("Deep Meditation" if "Deep Meditation" in ss.modes else ss.active_mode)


# ----------------------------------------------------------------------------
# NVIDIA NIM LLM integration
# ----------------------------------------------------------------------------
NVIDIA_SYSTEM_PROMPT = """You are AuraSync Divine Compass, a wise, empathetic, and grounded AI companion. You are philosophically insightful, psychologically supportive, and always concise (2 to 4 sentences max per message). You understand the user's astrological grounding and environmental state, and you adapt your tone to match their conversational language (English, Tamil, Tanglish, Korean, Thai, etc.).
"""


def divine_reply(msg, p):
    """Live LLM integration via NVIDIA NIM, falling back to the rule-based engine."""
    ss = st.session_state
    # Attempt LLM
    if OpenAI is not None:
        try:
            api_key = st.secrets.get("NVIDIA_API_KEY", "")
            if api_key:
                client = OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=api_key,
                )
                f = chart_facts(p)
                room = ss.presence["room"]
                mode = eff_mode()
                bio = ss.get("last_state", "unknown")
                mem = mem_get()
                mem_str = f"Last topic: {mem.get('last_topic')}. Notes: {mem.get('notes')}."
                sys_msg = (
                    NVIDIA_SYSTEM_PROMPT
                    + f"\n\nUser: {p['name']} (born {p['dob']} in {p['pob']})."
                    + f"\nEnvironment: Room: {room}, Mode: {mode}, Biometrics: {bio}."
                    + f"\nAstrology: Dasha lord: {f['lord']}, Season: {f['lord']}, End year: {f['end']}."
                    + f"\nMemory: {mem_str}"
                )
                messages = [{"role": "system", "content": sys_msg}]
                # Add recent chat history
                for m in ss.chat[-5:]:
                    messages.append({"role": m["role"], "content": m["content"]})
                messages.append({"role": "user", "content": msg})
                response = client.chat.completions.create(
                    model="meta/llama-3.1-70b-instruct",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150,
                    timeout=10,
                )
                reply = response.choices[0].message.content.strip()
                if reply:
                    # Update memory based on message
                    topic = detect_topic(msg)
                    mood = "neutral"
                    for k, vocab in MOOD_WORDS.items():
                        if set(re.findall(r"[^\W\d_]+", msg.lower())) & vocab:
                            mood = k
                            break
                    learn_from(msg, topic, mood)
                    return [reply]
        except Exception as e:
            log(f"⚠ NVIDIA NIM fallback: {type(e).__name__}")
    # Fallback to rule-based
    return divine_reply_rule_based(msg, p)


def divine_reply_rule_based(msg, p):
    """A natural, memory-aware reply: one or two short messages, no stock 'I hear you' filler."""
    ss = st.session_state
    lg = detect_lang(msg)
    first = p["name"].split()[0].title() if p["name"].split() else p["name"]
    words = set(re.findall(r"[^\W\d_]+", msg.lower()))
    seed = seed_of(msg, len(ss.chat), daily_seed(p))
    topic = detect_topic(msg)
    mood = "neutral"
    for k, vocab in MOOD_WORDS.items():
        if words & vocab:
            mood = k
            break
    for key, k in (("கோபம்", "angry"), ("வருத்தம்", "sad"), ("அழுகை", "sad"), ("தனிமை", "sad"), ("கவலை", "stress"), ("பயம்", "stress")):
        if key in msg:
            mood = k
            break
    mem = mem_get()
    prior = dict(mem["topics"])
    returning = mem["msgs"] > 0 or mem["sessions"] > 1
    offer = ss.get("pending_offer")
    if offer and len(words) <= 4:
        if words & YES_W:
            ss.pending_offer = None
            run_offer(offer)
            learn_from(msg, None, "neutral")
            return [t("chat_done_" + offer)]
        if words & NO_W:
            ss.pending_offer = None
            learn_from(msg, None, "neutral")
            return [t("chat_declined")]
    learn_from(msg, topic, mood)
    if lg in OTHER:
        o = OTHER[lg]
        return [o[0] + first + ". 🌟 " + o[1], o[2]]
    code = {"ta": "ta", "tanglish": "tg"}.get(lg, "en")
    opens = {"en": OPEN_EN, "tg": OPEN_TG, "ta": OPEN_TA}[code]
    guides = {"en": GUIDE_EN, "tg": GUIDE_TG, "ta": GUIDE_TA}[code]
    closes = {"en": CLOSE_EN, "tg": CLOSE_TG, "ta": CLOSE_TA}[code]
    if words & THANKS and len(words) <= 4:
        return [pick(opens["thanks"], seed, 3).replace("{n}", first)]
    f = chart_facts(p)
    if words & GREET and len(words) <= 3:
        day = {"en": DAYQ, "ta": TA_DAY, "tg": DAYQ}[code][f["day"]]
        if code == "en" and returning:
            label = TOPIC_LABEL.get(mem.get("last_topic") or "general", "what is on your mind")
            line = "Welcome back, " + first + " ✨ " + (("Last time we talked about " + label + ". How has that been sitting with you?")
                                                          if mem.get("last_topic") else "How are you feeling today?")
        else:
            line = pick(opens["greet"], seed, 3).replace("{n}", first)
        return [line + " " + day]
    follow = topic is None and len(words) <= 5 and (words & FOLLOW) and ss.get("last_topic")
    if follow:
        k = ss.get("deeper", 0)
        ss.deeper = k + 1
        tips = DEEPER[code]
        return [tips[k % len(tips)] + " " + closes[(k + 1) % len(closes)]]
    if topic is None:
        topic = "stress" if mood in ("sad", "stress") else ("anger" if mood == "angry" else "general")
    ss.last_topic, ss.deeper = topic, 0
    ins = {"en": insight_en, "tg": insight_tg, "ta": insight_ta}[code](topic, f)
    lead = pick(opens[mood], seed, 3).replace("{n}", first) if mood in opens and mood != "neutral" else ""
    first_bubble = (lead + " " + ins).strip()
    tail = []
    if code == "en":
        ml = memory_line(mem, topic, prior, first)
        if ml:
            tail.append(ml)
    tail.append(guides[topic])
    h = datetime.now().hour
    gap = len(ss.chat) - ss.get("last_offer_at", -99)
    strained = bool(re.search(r"can'?t sleep|insomnia|sleepless|stress|anxious|overwhelm|exhaust|burn(?:ed|t)? out|tired", msg.lower()))
    if code == "en" and gap >= 8 and (strained or mood in ("stress", "sad", "angry") or topic in ("stress", "health")):
        kind = "sleep" if (h >= 21 or h < 5) else "calm"
        ss.pending_offer = kind
        ss.last_offer_at = len(ss.chat)
        tail.append(t("chat_offer_" + kind))
    else:
        tail.append(pick(closes, seed, 9))
    return [first_bubble, " ".join(tail)]


def welcome_parts(p):
    f = chart_facts(p)
    first = p["name"].split()[0].title() if p["name"].split() else p["name"]
    if st.session_state.get("lang", "").startswith("Tamil"):
        return ["வணக்கம் " + first + " 🙏", "உங்கள் அதிர்வை நான் உணர்கிறேன். " + TA_DAY[f["day"]],
                "மனதில் இருப்பதைச் சொல்லுங்கள் - வேலை, காதல், பணம், குடும்பம், மன அழுத்தம், எதுவாக இருந்தாலும். நான் இங்கே இருக்கிறேன்."]
    mem = mem_get()
    if mem["msgs"] > 0 and mem.get("last_topic"):
        second = ("Good to see you again. Last time we talked about " +
                  TOPIC_LABEL.get(mem["last_topic"], "what was on your mind") + ". How has it been since?")
    else:
        second = "I've been sensing your energy since you arrived. " + DAYQ[f["day"]]
    return ["Hey " + first + " 🙏 " + second, "What's on your mind today? I'm right here."]


def md_inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s.replace("\n", "<br>")


def bubble(role, text, ts):
    cls = "me" if role == "user" else "dv"
    tick = " ✓✓" if role == "user" else ""
    body = md_inline(text)
    if role == "user":
        body = '<span translate="no">' + body + "</span>"
    return ('<div class="crow ' + cls + '"><div class="bub ' + cls + '">' + body +
            '<span class="ts">' + ts + tick + "</span></div></div>")


TYPING = '<div class="crow dv"><div class="bub dv typing"><span></span><span></span><span></span></div></div>'


def add_msg(role, text):
    st.session_state.chat.append({"role": role, "content": text, "ts": datetime.now().strftime("%H:%M")})


# ----------------------------------------------------------------------------
# Page 3 - Inner Voice & Guide
# ----------------------------------------------------------------------------
ARCH = [
    ("The Steady Builder", "you create security through patience and consistency",
     "you can cling to routines after they stop serving you", "protect long blocks of calm and build slowly"),
    ("The Intuitive Connector", "you read emotional undercurrents faster than most people",
     "you can absorb other people's moods as your own", "set gentle boundaries before you offer support"),
    ("The Visionary Strategist", "you see patterns and possibilities early",
     "you can drift into overthinking before acting", "turn each big idea into one small visible step"),
    ("The Quiet Achiever", "you work with depth and very little ego",
     "you may hide your needs until you feel depleted", "state your needs early and plainly"),
    ("The Spirited Explorer", "you bring energy, curiosity and fresh starts",
     "you can scatter your effort across too many fronts", "choose one priority and finish it"),
    ("The Grounded Healer", "you bring warmth and steadiness to those around you",
     "you can postpone your own recovery", "schedule your rest like an important meeting"),
]
ARCH_TA = [
    ("நிலைத்த உருவாக்குநர்", "நீங்கள் பொறுமையும் நிலைத்தன்மையும் கொண்டு பாதுகாப்பை உருவாக்குகிறீர்கள்",
     "பழைய வழக்கங்கள் தேவையற்றதாகிவிட்டாலும் அவற்றை விடாமல் பற்றிக்கொள்ளலாம்", "அமைதியான நீண்ட நேரங்களைப் பாதுகாத்து மெதுவாக உருவாக்குங்கள்"),
    ("உணர்வுபூர்வ இணைப்பாளர்", "மற்றவர்களை விட வேகமாக உணர்வு அலைகளைப் படிக்கிறீர்கள்",
     "மற்றவர்களின் மனநிலையை உங்களுடையதாகவே உள்வாங்கிக்கொள்ளலாம்", "ஆதரவு வழங்கும் முன் மென்மையான எல்லைகளை வகுத்துக்கொள்ளுங்கள்"),
    ("தொலைநோக்கு மூலோபாயவாதி", "மாதிரிகள் மற்றும் சாத்தியங்களை முன்கூட்டியே பார்க்கிறீர்கள்",
     "செயல்படும் முன் அதிகமாகச் சிந்திக்கத் தொடங்கலாம்", "ஒவ்வொரு பெரிய கருத்தையும் ஒரு சிறிய புலப்படும் படியாக மாற்றுங்கள்"),
    ("அமைதியான சாதனையாளர்", "ஆழமாகவும் மிகக் குறைந்த அகங்காரத்துடனும் வேலை செய்கிறீர்கள்",
     "சோர்வடையும் வரை உங்கள் தேவைகளை மறைக்கலாம்", "உங்கள் தேவைகளை முன்கூட்டியே தெளிவாகச் சொல்லுங்கள்"),
    ("ஆர்வமுள்ள ஆய்வாளர்", "ஆற்றல், ஆர்வம் மற்றும் புதிய தொடக்கங்களைக் கொண்டு வருகிறீர்கள்",
     "பல முனைகளில் உங்கள் முயற்சியைச் சிதறடிக்கலாம்", "ஒரு முன்னுரிமையைத் தேர்ந்தெடுத்து அதை முடிக்கவும்"),
    ("அடித்தளமான குணப்படுத்துபவர்", "உங்களைச் சுற்றியுள்ளவர்களுக்கு அரவணைப்பையும் நிலைத்தன்மையையும் தருகிறீர்கள்",
     "உங்கள் சொந்த குணமடைவதைத் தள்ளிப்போடலாம்", "ஒரு முக்கியமான கூட்டத்தைப் போல உங்கள் ஓய்வைத் திட்டமிடுங்கள்"),
]
REFLECT = [
    "What would I do today if I trusted myself fully?",
    "Which commitment am I keeping only out of guilt?",
    "What is one thing I am avoiding that would feel lighter once done?",
    "Whose approval am I chasing, and what do I actually want?",
    "What does my body need right now that my mind keeps overriding?",
]
REFLECT_TA = [
    "என்னை முழுமையாக நம்பினால் இன்று நான் என்ன செய்வேன்?",
    "குற்ற உணர்வின் காரணமாக மட்டுமே நான் எந்த உறுதிமொழியைக் கடைப்பிடிக்கிறேன்?",
    "முடிந்ததும் இலகுவாக உணரக்கூடிய, நான் தவிர்க்கும் ஒரு விஷயம் என்ன?",
    "யாருடைய அங்கீகாரத்தை நான் துரத்துகிறேன், நான் உண்மையில் என்ன விரும்புகிறேன்?",
    "என் மனம் தொடர்ந்து புறக்கணிக்கும், என் உடலுக்கு இப்போது என்ன தேவை?",
]
DOS = [
    "{n}, spend the first 20 minutes of your day on your single most important task before opening any messages.",
    "Name what you feel in one honest sentence before you react to a difficult message.",
    "Take a 10-minute walk without your phone to reset your thinking.",
    "Have the one kind but honest conversation you have been postponing.",
    "Write down three things within your control today and act on the first one right away.",
    "Between meetings, drink water, stretch, and breathe slowly for two minutes.",
]
DOS_TA = [
    "{n}, எந்தச் செய்திகளையும் திறப்பதற்கு முன் உங்கள் நாளின் முதல் 20 நிமிடங்களை உங்களுக்கு மிக முக்கியமான ஒரு வேலைக்கு செலவிடுங்கள்.",
    "கடினமான ஒரு செய்திக்கு எதிர்வினையாற்றும் முன், நீங்கள் உணர்வதை ஒரு நேர்மையான வாக்கியத்தில் சொல்லுங்கள்.",
    "உங்கள் சிந்தனையை புதுப்பிக்க 10 நிமிடம் ஃபோன் இல்லாமல் நடந்து வாருங்கள்.",
    "நீங்கள் தள்ளிப்போட்டுக்கொண்டிருக்கும் அந்த ஒரு கனிவான ஆனால் நேர்மையான உரையாடலை நடத்துங்கள்.",
    "இன்று உங்கள் கட்டுப்பாட்டில் உள்ள மூன்று விஷயங்களை எழுதி, முதலாவதை உடனே செயல்படுத்துங்கள்.",
    "கூட்டங்களுக்கு இடையே, தண்ணீர் குடித்து, உடலை நீட்டி, இரண்டு நிமிடம் மெதுவாக மூச்சு விடுங்கள்.",
]
DONTS = [
    "Don't make a big commitment while you are tired or emotionally charged.",
    "Don't compare your behind-the-scenes with someone else's highlight reel.",
    "Don't say yes automatically; pause for one full breath before agreeing.",
    "Don't scroll news or social media in the first hour after waking.",
    "Don't rehearse worst-case scenarios; ask what is actually known right now.",
    "Don't carry other people's mood as your personal responsibility.",
]
DONTS_TA = [
    "சோர்வாக அல்லது உணர்ச்சிவசப்பட்ட நிலையில் பெரிய உறுதிமொழி எதுவும் அளிக்க வேண்டாம்.",
    "உங்கள் மேடைக்குப் பின்னால் நடப்பதை மற்றவர்களின் சிறந்த தருணங்களுடன் ஒப்பிட வேண்டாம்.",
    "தானாகவே 'சரி' என்று சொல்ல வேண்டாம்; ஒப்புக்கொள்ளும் முன் ஒரு முழு மூச்சு எடுத்து நிறுத்துங்கள்.",
    "எழுந்த பிறகு முதல் ஒரு மணி நேரத்தில் செய்திகள் அல்லது சமூக வலைதளங்களை உருட்ட வேண்டாம்.",
    "மோசமான சூழ்நிலைகளை மனதில் பயிற்சி செய்ய வேண்டாம்; இப்போது உண்மையில் என்ன தெரிகிறது என்று கேளுங்கள்.",
    "மற்றவர்களின் மனநிலையை உங்கள் தனிப்பட்ட பொறுப்பாக சுமக்க வேண்டாம்.",
]
CAUTIONS = [
    "Energy may dip in the afternoon, so schedule demanding work early and keep the evening light.",
    "Watch for impatience in conversations about money or deadlines; slow your tone before your words.",
    "Small misunderstandings can grow today, so confirm important details in writing.",
    "You may be tempted to over-give; protect one hour purely for yourself.",
    "Decision fatigue is likely; simplify your choices and postpone non-urgent ones.",
    "Sensitivity to criticism may run higher than usual; separate feedback from your self-worth.",
]
CAUTIONS_TA = [
    "மதியம் ஆற்றல் குறையலாம், எனவே கடினமான வேலைகளை முன்கூட்டியே திட்டமிட்டு மாலையை இலகுவாக வைத்திருங்கள்.",
    "பணம் அல்லது காலக்கெடு பற்றிய உரையாடல்களில் பொறுமையின்மையைக் கவனியுங்கள்; வார்த்தைகளுக்கு முன் உங்கள் தொனியை மெதுவாக்குங்கள்.",
    "சிறிய தவறான புரிதல்கள் இன்று வளரலாம், எனவே முக்கியமான விவரங்களை எழுத்துப்பூர்வமாக உறுதிப்படுத்துங்கள்.",
    "அதிகமாகக் கொடுக்கும் ஆசை வரலாம்; உங்களுக்காக மட்டுமே ஒரு மணி நேரத்தைப் பாதுகாத்துக் கொள்ளுங்கள்.",
    "முடிவெடுக்கும் சோர்வு ஏற்படலாம்; உங்கள் தேர்வுகளை எளிமையாக்கி அவசரமற்றவற்றைத் தள்ளிப்போடுங்கள்.",
    "விமர்சனத்திற்கான உணர்திறன் வழக்கத்தை விட அதிகமாக இருக்கலாம்; கருத்துக்களை உங்கள் சுயமரியாதையிலிருந்து பிரிக்கவும்.",
]

def deep_text(kind, p):
    ps, ds = profile_seed(p), daily_seed(p)
    lang = st.session_state.get("lang", "English")
    is_ta = lang.startswith("Tamil")
    
    if is_ta:
        a = ARCH_TA[ps % len(ARCH_TA)]
        ref = pick(REFLECT_TA, ds, 11)
        season = "இந்த காலகட்டத்தில் " + TA_SEASON.get(chart_facts(p)["lord"], "மாற்றம்")
        day_q = TA_DAY.get(chart_facts(p)["day"], "")
        sati = "உங்கள் உணர்வு அலைகளின் மீது கனமான, சோதனையான காலகட்டம் கடந்து செல்கிறது, எனவே உங்களிடம் கருணையுடன் இருங்கள். " if chart_facts(p)["sati"] else ""
        
        if kind == "do":
            return ("**இது உங்களுக்கு ஏன் வேலை செய்கிறது, " + p["name"] + ".** உங்கள் மனோபாவம் *" + a[0] + "* போன்றது: " + a[1] +
                    ". நீங்கள் இப்போது " + season + ", எனவே இன்றைய செயல் அந்த பலத்தை ஒரு உறுதியான விஷயத்தில் செலுத்துகிறது. "
                    "நீங்கள் " + p["pob"] + " இல் வாழ்க்கையைத் தொடங்கியதால், உங்கள் நாளைத் தொடங்கும் விதத்தை இன்னும் வடிவமைக்கும் ஆரம்ப பழக்கங்களைக் கவனித்து, உதவும் பழக்கங்களை மட்டும் வைத்திருங்கள். "
                    "உங்களுக்கான நம்பகமான வளர்ச்சிப் பாதை: " + a[3] + ".\n\n**சிந்திக்க:** " + ref)
        if kind == "dont":
            return ("**இது எதைப் பாதுகாக்கிறது, " + p["name"] + ".** *" + a[0] + "* இன் இருண்ட பக்கம் என்னவென்றால் " + a[2] +
                    ". இன்றைய 'செய்யாதே' என்பது உங்கள் ஆற்றல் வெளியேறும் முன் அதைப் பாதுகாக்கும் ஒரு எல்லை. " + day_q +
                    " உங்களுக்கு அந்த உந்துதல் ஏற்படும் போதெல்லாம் பத்து வினாடிகள் நிறுத்திப் பயிற்சி செய்யுங்கள், அந்த உந்துதல் உண்மையில் எதைக் கேட்கிறது என்பதைக் கவனியுங்கள்.\n\n**சிந்திக்க:** " + ref)
        return ("**இந்த எச்சரிக்கைக்குப் பின்னால் உள்ள முறை, " + p["name"] + ".** *" + a[0] + "* போன்ற மக்கள் பெரும்பாலும் கணிக்கக்கூடிய மன அழுத்த வளைவை எதிர்கொள்கிறார்கள்: " + a[2] +
                ". " + sati +
                "இன்றைய எச்சரிக்கை ஒரு முன்னெச்சரிக்கை, கணிப்பு அல்ல. ஒரு சிறிய மீட்பு நடவடிக்கையை முன்கூட்டியே திட்டமிடுங்கள் (ஒரு சிறு நடை, ஒரு கிளாஸ் தண்ணீர், அமைதியான ஒருவருடன் பேசுவது) சரிவு ஒரு சுழலாக மாறாமல் இருக்க. காலப்போக்கில், "
                + a[3] + " கற்றுக்கொள்வதன் மூலம் நீங்கள் வளர்கிறீர்கள்.\n\n**சிந்திக்க:** " + ref)
    
    # English fallback
    a = ARCH[ps % len(ARCH)]
    ref = pick(REFLECT, ds, 11)
    f = chart_facts(p)
    name, pob = p["name"], p["pob"]
    season = "a season of " + SEASON[f["lord"]]
    if kind == "do":
        return ("**Why this works for you, " + name + ".** Your temperament pattern resembles *" + a[0] + "*: " + a[1] +
                ". Right now you are in " + season + ", so today's action channels that strength into something concrete. "
                "Because you began life in " + pob + ", notice which early habits still shape how you start your day, and keep "
                "only the ones that help. A reliable growth path for you is to " + a[3] + ".\n\n**Reflect:** " + ref)
    if kind == "dont":
        return ("**What this protects, " + name + ".** The shadow side of *" + a[0] + "* is that " + a[2] +
                ". Today's 'don't' is a boundary that guards your energy before it leaks. " + DAYQ[f["day"]] +
                " Practice a pause of ten seconds whenever you feel the urge, and notice what the urge was really asking for.\n\n**Reflect:** " + ref)
    return ("**The pattern behind this caution, " + name + ".** People shaped like *" + a[0] + "* often face a predictable stress "
            "curve: " + a[2] + ". " + ("A heavy, testing phase is passing over your emotional tides, so be gentle with yourself. "
                                       if f["sati"] else "") +
            "Today's caution is an early warning, not a prediction. Pre-plan one small recovery action "
            "(a short walk, a glass of water, a call with someone calm) so the dip never turns into a spiral. Over time, "
            "you grow by learning to " + a[3] + ".\n\n**Reflect:** " + ref)


def profile_form():
    ss = st.session_state
    p = ss.profile or {}
    st.subheader(t("setup"))
    with st.form("profile_form"):
        name = st.text_input(t("name"), value=p.get("name", ""))
        dob0 = p.get("dob", date(1995, 1, 1))
        st.markdown("**" + t("dob") + "**")
        d1, d2, d3 = st.columns(3)
        dday = d1.selectbox(t("day"), list(range(1, 32)), index=dob0.day - 1)
        dmon = d2.selectbox(t("month"), list(range(1, 13)), index=dob0.month - 1, format_func=lambda m: MONTHS[m - 1])
        dyear = d3.selectbox(t("year"), list(range(1940, 2041)), index=min(max(dob0.year, 1940), 2040) - 1940)
        pob = st.text_input(t("pob"), value=p.get("pob", ""))
        st.markdown("**" + t("tob") + "**")
        c1, c2, c3 = st.columns(3)
        hr = c1.selectbox(t("hour"), list(range(1, 13)), index=p.get("h", 6) - 1)
        mn = c2.selectbox(t("minute"), list(range(0, 60)), index=p.get("m", 0), format_func=lambda x: str(x).zfill(2))
        ap = c3.selectbox("AM / PM", ["AM", "PM"], index=0 if p.get("ap", "AM") == "AM" else 1)
        ok = st.form_submit_button(t("save"))
    dob = date(dyear, dmon, min(dday, calendar.monthrange(dyear, dmon)[1]))
    if ok:
        if not name.strip() or not pob.strip():
            st.warning(t("need_fields"))
        else:
            tob = str(hr).zfill(2) + ":" + str(mn).zfill(2) + " " + ap
            ss.profile = {"name": name.strip(), "dob": dob, "pob": pob.strip(), "tob": tob, "h": hr, "m": mn, "ap": ap}
            ss.editing = False
            ss.chat = []
            ss.chimed = False
            ss.last_topic = None
            st.rerun()


def card(title, text):
    st.markdown('<div class="card"><h4>' + html.escape(title) + "</h4><p>" + html.escape(text) + "</p></div>",
                unsafe_allow_html=True)


def page_inner_voice():
    ss = st.session_state
    st.header(t("p3"))
    if ss.profile is None or ss.editing:
        profile_form()
        if ss.profile is None:
            st.info(t("need_profile"))
        return

    p = ss.profile
    n = html.escape(p["name"])
    wc, bc = st.columns([4, 1])
    wc.markdown('<div class="banner"><b>' + t("welcome", n=n) + "</b></div>", unsafe_allow_html=True)
    if bc.button(t("edit")):
        ss.editing = True
        st.rerun()
    if ss.cfg["notif"]:
        st.markdown('<div class="banner">' + t("nudge", n=n) + "</div>", unsafe_allow_html=True)
        if ss.cfg["chime"]:
            ring = not ss.chimed
            ss.chimed = True
            chime_component(ring)

    st.subheader(t("plan"))
    ds = daily_seed(p)
    is_ta = st.session_state.get("lang", "").startswith("Tamil")
    
    if is_ta:
        items = [("do", pick(DOS_TA, ds, 3)), ("dont", pick(DONTS_TA, ds, 17)), ("caution", pick(CAUTIONS_TA, ds, 29))]
    else:
        items = [("do", pick(DOS, ds, 3)), ("dont", pick(DONTS, ds, 17)), ("caution", pick(CAUTIONS, ds, 29))]
        
    cols = st.columns(3)
    for col, (kind, text) in zip(cols, items):
        with col:
            card(t(kind), text.replace("{n}", p["name"]))
            with st.expander(t("deep")):
                st.markdown(deep_text(kind, p))

    st.divider()
    st.subheader("🧭 " + t("chat"))
    q = st.chat_input(t("chat_ph"))
    if not ss.chat:
        for part in welcome_parts(p):
            add_msg("assistant", part)
    st.markdown('<div class="chathead"><span class="dot"></span>' + t("chat") + " <small>· " + t("online") +
                "</small></div>", unsafe_allow_html=True)
    st.markdown('<div class="chatbox">' + "".join(bubble(m["role"], m["content"], m.get("ts", "")) for m in ss.chat) +
                "</div>", unsafe_allow_html=True)
    if q:
        tail = st.container()
        add_msg("user", q)
        tail.markdown(bubble("user", q, ss.chat[-1]["ts"]), unsafe_allow_html=True)
        parts = divine_reply(q, p)
        for part in parts:
            slot = tail.empty()
            slot.markdown(TYPING, unsafe_allow_html=True)
            time.sleep(min(2.2, 0.6 + len(part) * 0.012))
            add_msg("assistant", part)
            slot.markdown(bubble("assistant", part, ss.chat[-1]["ts"]), unsafe_allow_html=True)
# ----------------------------------------------------------------------------
# Pages 4 & 5
# ----------------------------------------------------------------------------
def remove_device(uid):
    ss = st.session_state
    ss.fleet = [d for d in ss.fleet if d["uid"] != uid]
    for sp in ss.spaces.values():
        if uid in sp["devices"]:
            sp["devices"].remove(uid)
        if sp.get("preset"):
            sp["preset"].pop(str(uid), None)
    ss.holds.pop(uid, None)
    ss.room_rev = ss.get("room_rev", 0) + 1


def add_fleet_device():
    ss = st.session_state
    cid, room = ss.get("fl_add_cid"), ss.get("fl_add_room")
    if cid not in CAT or room not in ss.spaces:
        return
    base = (ss.get("fl_add_name") or "").strip()[:40] or CAT[cid][2]
    nd = new_device(cid, unique_name(base), room)
    ss.fleet.append(nd)
    ss.spaces[room]["devices"].append(nd["uid"])
    ss.room_rev = ss.get("room_rev", 0) + 1
    log("➕ " + nd["name"] + " added to " + room)


def page_fleet():
    ss = st.session_state
    pro = ss.ui_mode == "pro"
    st.header(t("p4"))
    st.subheader("🔗 " + t("conn_hub"))
    total = len(ss.fleet)
    ok = sum(1 for d in ss.fleet if d["status"] == "connected")
    h1, h2, h3 = st.columns(3)
    h1.markdown(stat(t("dev_my"), total), unsafe_allow_html=True)
    h2.markdown(stat(t("s_ok"), str(ok) + " / " + str(total)), unsafe_allow_html=True)
    h3.markdown(stat(t("ai_auto"), t("mode_auto").split(" (")[0] if ss.cfg["auto_mode"] else t("mode_manual")),
                unsafe_allow_html=True)
    st.caption(t("dev_hint"))
    if st.button(t("matter_btn"), key="mt_open", type="primary"):
        open_matter()
    if pro:
        b1, b2 = st.columns(2)
        if b1.button(t("conn_all"), key="fl_conn_all"):
            connect_all()
        if b2.button(t("sync"), key="fl_sync"):
            apply_mode(ss.active_mode, devs=list(ss.fleet))
            ss.flash = t("synced") + " (" + tr_mode(ss.active_mode) + ")"
            st.rerun()
        with st.expander("➕ " + t("dev_add")):
            with st.form("add_device", clear_on_submit=True):
                a1, a2, a3 = st.columns([3, 2, 2])
                a1.selectbox(t("dev_pick"), list(CAT.keys()), key="fl_add_cid",
                             format_func=lambda k: CAT[k][1] + " " + CAT[k][2] + "  ·  " + CAT[k][3])
                a2.selectbox(t("dev_room"), list(ss.spaces), key="fl_add_room", format_func=tr_room)
                a3.text_input(t("dev_name"), key="fl_add_name", max_chars=40)
                st.form_submit_button(t("dev_btn"), on_click=add_fleet_device)

    st.subheader("🔌 " + t("dev_my") + " (" + str(len(ss.fleet)) + ")")
    badge = {"connected": "🟢 " + t("s_ok"), "offline": "🔴 " + t("s_off"), "not connected": "⚪ " + t("s_no")}
    cols = st.columns(2 if pro else 3)
    for i, dv in enumerate(ss.fleet):
        c = CAT[dv["cid"]]
        uid = dv["uid"]
        with cols[i % len(cols)]:
            with st.container(border=True):
                st.markdown("**" + c[1] + " " + html.escape(dv["name"]) + "**  \n" + html.escape(tr_room(dv["room"])) + " · " +
                            badge.get(dv["status"], dv["status"]))
                if not pro:
                    k = "fl_zpw_" + str(uid) + "_" + str(dv.get("rev", 0))
                    st.toggle(t("power_lbl"), value=bool(dv["on"]), key=k, on_change=cb_power, args=(uid, k))
                    continue
                device_editor(dv, "fl")
                with st.expander(t("adv_conn")):
                    rooms = list(ss.spaces)
                    rk = "fl_room_" + str(uid) + "_" + str(ss.get("room_rev", 0))
                    st.selectbox(t("dev_room"), rooms, index=rooms.index(dv["room"]) if dv["room"] in rooms else 0,
                                 key=rk, on_change=cb_dev_room, args=(uid, rk), format_func=tr_room)
                    if "Matter" in dv["proto"]:
                        st.caption("🟢 Matter · " + t("s_ok"))
                    else:
                        protos = PROTOS_BULB if dv["cid"] == "bulb" else PROTOS
                        pk = "fl_proto_" + str(uid)
                        st.selectbox(t("proto"), protos, index=protos.index(dv["proto"]) if dv["proto"] in protos else 0,
                                     key=pk, on_change=cb_proto, args=(uid, pk))
                        if dv["proto"] != "Simulation":
                            ak, tk = "fl_addr_" + str(uid), "fl_tok_" + str(uid)
                            st.text_input(t("addr"), value=dv["addr"], key=ak, on_change=cb_dev_field,
                                          args=(uid, ak, "addr"))
                            st.text_input("Token", value=dv["token"], key=tk, type="password", on_change=cb_dev_field,
                                          args=(uid, tk, "token"))
                        st.button(t("conn_btn"), key="cn_" + str(uid), on_click=connect_device, args=(dv,))
                if dv["last"]:
                    st.caption(dv["last"])
                st.button("🗑", key="rm_" + str(uid), on_click=remove_device, args=(uid,))

    if pro:
        st.subheader("📜 " + t("ai_log"))
        for e in ss.log[:12]:
            st.markdown('<div class="logl">' + e["t"] + "  " + html.escape(e["x"]) + "</div>", unsafe_allow_html=True)
        rows = [{"Device": CAT[d["cid"]][1] + " " + d["name"], "Room": tr_room(d["room"]), "Status": "ON" if d["on"] else "OFF",
                 "Level": (str(d["lvl"]) + UNIT.get(d["cid"], "%")) if CAT[d["cid"]][4] else "-",
                 "Link": d["proto"] + " / " + d["status"]} for d in ss.fleet]
        st.subheader("📋 " + t("summary"))
        html_table(rows)


def page_system():
    ss, cfg = st.session_state, st.session_state.cfg
    st.header(t("p5"))
    cfg["api_url"] = st.text_input(t("api"), value=cfg["api_url"])
    c1, c2, c3, c4 = st.columns(4)
    cfg["thr"] = c1.slider(t("thr"), 85, 150, int(cfg["thr"]))
    cfg["rel"] = c2.slider(t("rel"), 55, 95, int(cfg["rel"]))
    cfg["rest"] = c3.slider(t("rest"), 40, 80, int(cfg["rest"]))
    cfg["poll"] = c4.slider(t("poll"), 2, 15, int(cfg["poll"]))
    cfg["notif"] = st.toggle(t("notif"), value=cfg["notif"])
    cfg["chime"] = st.toggle(t("chime"), value=cfg["chime"])
    st.toggle(t("geo_auto_toggle"), value=bool(cfg.get("geo_auto", True)), key="geo_auto_sys",
              on_change=cb_geo_auto, args=("geo_auto_sys",))
    b1, b2 = st.columns(2)
    if b1.button(t("test")):
        try:
            r = requests.get(cfg["api_url"], timeout=2)
            st.success("HTTP " + str(r.status_code))
        except Exception as e:
            st.error(type(e).__name__)
    if b2.button(t("reset")):
        lang = ss.get("lang", "English")
        for k in list(ss.keys()):
            if k not in ("lang", "nav", "theme_choice"):
                del ss[k]
        ss["lang"] = lang
        st.rerun()


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
NAV_ORDER = [1, 6, 2, 3, 4, 5]


def cb_ui_mode(key):
    ss = st.session_state
    v = ss.get(key)
    if v in ("zen", "pro"):
        ss.ui_mode = v
    ss.ui_rev = ss.get("ui_rev", 0) + 1


def render_topbar():
    ss = st.session_state
    _, c2 = st.columns([2, 3])
    key = "ui_mode_w_" + str(ss.get("ui_rev", 0))
    with c2:
        seg("Mode", ["zen", "pro"], key, lambda m: t("ui_zen") if m == "zen" else t("ui_pro"), on_change=cb_ui_mode,
            args=(key,), selected=ss.ui_mode, hide_label=True)


def main():
    init_state()
    ss = st.session_state
    install_i18n()
    code = lang_code()
    if code and mt_available() and not ss.get("i18n_ok_" + code):
        with st.spinner(t("i18n_wait")):
            ss["i18n_ok_" + code] = bool(i18n_prefetch())
    repair_orphans()
    st.markdown(build_css(), unsafe_allow_html=True)
    with st.sidebar:
        st.markdown('<div class="brand">✨ AuraSync</div>', unsafe_allow_html=True)
        st.caption(t("sub"))
        st.caption("📍 " + (tr_room(ss.presence["room"]) if ss.conn["mode"] == "home" else "Away · cloud relay"))
        st.selectbox("🌐 " + t("lang"), LANGS, key="lang")
        if code and not mt_available():
            st.warning(t("i18n_missing"))
        st.radio("🌗 " + t("theme"), ["dark", "light"], key="theme_choice",
                 format_func=lambda x: t("theme_dark") if x == "dark" else t("theme_light"))
        guest_toggle("guest_sb")
        st.divider()
        st.radio(t("nav"), NAV_ORDER, format_func=lambda i: t("p" + str(i)), key="nav")
        st.divider()
        audio_component(synth_params(eff_mode()), ss.nav != 1)
    render_topbar()
    if ss.flash:
        st.toast(ss.flash)
        ss.flash = ""
    run_routines()
    render_geo_banner(show_card=(ss.nav != 6))
    pages = {1: page_dashboard, 2: page_moods, 3: page_inner_voice, 4: page_fleet, 5: page_system, 6: page_rooms}
    pages[ss.nav]()
    _cache_save()


main()
import streamlit.components.v1 as components

# Background & lock screen audio playback
components.html(
    """
<script>
if ('mediaSession' in navigator) {
    navigator.mediaSession.metadata = new MediaMetadata({
        title: "AuraSync Soundscape",
        artist: "AuraSync Ambient AI",
        album: "Atmospheric Intelligence"
    });
    navigator.mediaSession.setActionHandler('play', () => {});
    navigator.mediaSession.setActionHandler('pause', () => {});
}
const audioTags = window.parent.document.querySelectorAll('audio');
audioTags.forEach(el => {
    el.setAttribute('playsinline', 'true');
    el.setAttribute('webkit-playsinline', 'true');
});
</script>
""",
    height=0,
    width=0,
)