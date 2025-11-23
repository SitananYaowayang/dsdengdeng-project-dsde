CUSTOM_CSS = """
<style>
    /* --- FONT & ICON --- */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai+Looped:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');
    html, body, [class*="st-"] {
        font-family: 'IBM Plex Sans Thai Looped', sans-serif !important;
    }
    span[data-testid="stIconMaterial"],
    [data-testid*="stIcon"] *,
    i, 
    button[title*="navigation"] *
    { 
        font-family: "Material Symbols Outlined", sans-serif !important;
    }
    .st-emotion-cache-1mnn934 * {
        font-family: "Material Symbols Outlined", sans-serif !important;
    }

    /* --- MAIN CONTENT ("White BG, Navy Text) --- */
    .main {
        background-color: white !important;
        color: #002A6E !important;
    }
    .st-emotion-cache-18ni2x2 { 
        background-color: white !important;
        color: #002A6E !important;
    }
    .main div, .main p, .main h1, .main h2, .main h3 {
        color: #002A6E !important; 
    }
    /* Global fallback */
    h1, h2, h3, h4, h5 {
        font-family: 'IBM Plex Sans Thai Looped', sans-serif !important;
        color: #002A6E !important;
    }
    h3 {
        font-weight: 600 !important;
        font-size: 1.5rem !important;
    }

    /* --- SIDEBAR (Navy BG, White Text) --- */
    [data-testid="stSidebar"] {
        background-color: #002A6E !important;
    }
    [data-testid="stSidebar"] > div:first-child { 
        background-color: #002A6E !important; 
    }
    [data-testid="stSidebarHeader"] {
        background-color: #002A6E !important;
    }
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: white !important;
        background-color: white !important;
        opacity: 0.7 !important;
    }
    
    /* --- SPACING (Reduce Top Margin) --- */
    .block-container {
        padding-top: 2rem !important; 
        padding-bottom: 1rem !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: -2rem !important;
    }

    /* --- LINK --- */
    .no-underline-link {
        color: #007bff !important;
        text-decoration: none !important; 
        font-size: 0.8rem;
        font-style: italic;
    }
    .no-underline-link:hover {
        text-decoration: underline !important; 
        color: #FF4B4B !important; 
    }

    /* --- WIDGETS COLOR CHANGE (RED to #002A6E) --- */
    /* 1. TAG */
    span[data-baseweb="tag"] {
        background-color: #002A6E !important;
    }
    /* 1. SLIDER: ส่วนที่ลากแล้ว (Filled Track) และ ปุ่ม (Thumb) */
    /* เทคนิค: แทนที่จะเดาชื่อ Class เราสั่งว่า "อะไรก็ตามใน Slider ที่เคยเป็นสีแดง ให้เป็นสีน้ำเงิน" */
    /* วิธีนี้จะทำให้ "ส่วนที่ยังไม่ลาก" (ซึ่งเป็นสีเทา) ไม่ถูกเปลี่ยนสี */
    
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #002A6E !important; /* สีปุ่ม */
        border-color: #002A6E !important;
    }
    
    div[data-testid="stSlider"] div[style*="background-color: rgb(255, 75, 75)"],
    div[data-testid="stSlider"] div[style*="background-color: #ff4b4b"] {
        background-color: #002A6E !important; /* สีเส้นที่ลากแล้ว */
    }

    /* 2. SLIDER */
    div[data-testid="stSliderThumbValue"] {
        color: #002A6E !important;
    }
    div[data-testid="stSliderTickBar"] span {
        color: #002A6E !important;
    }
    div[role="slider"] {
        background-color: #002A6E !important;
        border-color: #002A6E !important;
    }
    div[data-testid="stSlider"] div[style*="background-color: rgb(255, 75, 75)"],
    div[data-testid="stSlider"] div[style*="background-color: #ff4b4b"] {
        background-color: #002A6E !important;
    }
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #002A6E !important;
    }
    
    /* 3. RADIO BUTTONS & CHECKBOXES */
    /* --- Checkbox Fix --- */
    /* 3.1 เปลี่ยนเฉพาะ 'กล่องสี่เหลี่ยม' (span ตัวแรก) ให้เป็นสีน้ำเงิน */
    [data-testid="stCheckbox"] label:has(input:checked) > span:first-child {
        background-color: #002A6E !important;
        border-color: #002A6E !important;
    }
    
    /* 3.2 บังคับให้ส่วนข้อความ (div) พื้นหลังใส ไม่เอาสีน้ำเงิน */
    [data-testid="stCheckbox"] label > div {
        background-color: transparent !important;
        color: #002A6E !important; /* สีตัวอักษรยังคงเป็นสีน้ำเงิน */
    }
    div[data-testid="stRadio"] label:has(input:checked) > div:first-of-type,
    div[data-testid="stRadio"] label:has(input:checked) > div:first-of-type > div {
        background-color: #002A6E !important;
    }
    
    /* 4. SEARCH BOX */
    div[data-baseweb="select"] > div:focus-within {
        border-color: #002A6E !important;
        box-shadow: 0 0 0 1px #002A6E !important; /* ทำให้ขอบชัดขึ้น */
    }
    div[data-baseweb="select"] input {
        caret-color: #002A6E !important;
    }
</style>
"""