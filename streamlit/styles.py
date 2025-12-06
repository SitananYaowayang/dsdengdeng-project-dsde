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

    /* เฉพาะ radio ภายใน Sidebar เท่านั้น */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-of-type,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-of-type > div {
        background-color: #002A6E !important;  /* ปุ่มปกติสีน้ำเงินเข้ม */
        border: 2px solid #002A6E !important;
    }
    /* เมื่อถูกเลือก: ขอบเป็นสีขาว */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) > div:first-of-type {
        border-color: #FFFFFF !important;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.7) !important;
    }
    /* ด้านในยังเป็นสีน้ำเงินเหมือนเดิม */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) > div:first-of-type > div {
        background-color: #002A6E !important;
    }
    
    /* 3. RADIO BUTTONS & CHECKBOXES */
    [data-testid="stCheckbox"] label:has(input:checked) > span:first-child {
        background-color: #002A6E !important;
        border-color: #002A6E !important;
    }
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

    /* 5. Tab */
    /* Change the color of the active tab's text */
    button[aria-selected="true"] p {
        color: #002A6E !important; /* A shade of blue for the text */
    }
    /* Change the color of the highlight/underline beneath the active tab */
    [data-baseweb="tab-highlight"] {
        background-color: #002A6E !important; /* The same shade of blue for the underline */
    }
    /* Change the text color of ANY tab on hover to blue */
    button[data-baseweb="tab"]:hover p {
        color: #002A6E !important; /* Blue on hover */
    }

    /*  6. Selectbox */
    /* กรอบ + ตัวอักษรของ selectbox */
    div[data-baseweb="select"] > div {
        background-color: #002A6E !important; 
        color: #FFFFFF !important;
    }
    /* ตอน hover */
    div[data-baseweb="select"] > div:hover {
        background-color: #002A6E !important; 
    }
    /* Dropdown panel */
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 2px solid #00B3A4 !important;
    }
    /* Option ธรรมดา */
    ul[role="listbox"] li {
        color: #003366 !important;
    }
    /* Option ที่เลือก */
    ul[role="listbox"] li[aria-selected="true"] {
        background-color: #0056A6 !important;
        color: white !important;
    }
    /* Option ตอน hover */
    ul[role="listbox"] li:hover {
        background-color: #00B3A4 !important;
        color: white !important;
    }
    /* ลูกศรของ selectbox */
    div[data-baseweb="select"] svg {
        fill: #FFFFFF !important;
    }
    /* ตอน hover — ลูกศร */
    div[data-baseweb="select"] > div:hover svg {
        fill: #00B3A4 !important;
    }

    /* --- 2. NUMBER INPUT & DATE INPUT (Border & Focus) --- */
    /* เปลี่ยนสีขอบ (Border) ของช่องกรอกข้อมูลเมื่อยังไม่กด */
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stDateInput"] div[data-baseweb="input"] {
        border-color: #002A6E !important;
    }

    /* เปลี่ยนสีขอบและเงา (Focus Ring) เมื่อคลิกที่ช่อง */
    div[data-baseweb="input"]:focus-within {
        border-color: #002A6E !important;
        box-shadow: none !important; /* ลบเงาสีแดงเดิมออกถ้ามี */
        /* หรือถ้าอยากได้เงาสีฟ้าจางๆ ให้ใช้บรรทัดล่างนี้แทน */
        /* box-shadow: 0 0 0 0.2rem rgba(0, 42, 110, 0.25) !important; */
    }

    /* 3. เปลี่ยนสีตัวเลขที่พิมพ์ และสี Cursor กระพริบ */
    div[data-testid="stNumberInput"] input {
        color: #002A6E !important;       /* สีตัวเลข */
        caret-color: #002A6E !important; /* สี Cursor กระพริบ */
    }

    /* 4. ปุ่ม +/- ด้านหลัง */
    div[data-testid="stNumberInput"] button {
        border-color: #002A6E !important;
        color: #002A6E !important;
    }
    
    /* ปุ่ม +/- ตอนกดหรือเอาเมาส์ทาบ */
    div[data-testid="stNumberInput"] button:hover,
    div[data-testid="stNumberInput"] button:active {
        background-color: #002A6E !important;
        color: white !important;
    }

    /* =========================================
       ส่วนที่ 1: แก้ไขขอบช่อง Input (ทั้ง Date และ Number)
       ========================================= */

    /* เปลี่ยนสีขอบตอนปกติ */
    div[data-testid="stDateInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        border-color: #002A6E !important;
    }

    /* เปลี่ยนสีขอบและเงาตอนกด (Focus) - แก้ขอบแดง */
    div[data-testid="stDateInput"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
        border-color: #002A6E !important;
        box-shadow: 0 0 0 0.2rem rgba(0, 42, 110, 0.25) !important;
    }
    
    /* เปลี่ยนสีไอคอนปฏิทินด้านขวา */
    div[data-testid="stDateInput"] svg {
        fill: #002A6E !important;
    }

    

</style>
"""