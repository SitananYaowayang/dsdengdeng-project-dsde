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
    
    /* --- SPACING --- */
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
    /* 2. SLIDER */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #002A6E !important;
        border-color: #002A6E !important;
    }
    div[data-testid="stSlider"] div[style*="background-color: rgb(255, 75, 75)"],
    div[data-testid="stSlider"] div[style*="background-color: #ff4b4b"] {
        background-color: #002A6E !important;
    }
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
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-of-type,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-of-type > div {
        background-color: #002A6E !important;
        border: 2px solid #002A6E !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) > div:first-of-type {
        border-color: #FFFFFF !important;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.7) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) > div:first-of-type > div {
        background-color: #002A6E !important;
    }
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
    button[aria-selected="true"] p {
        color: #002A6E !important; /* A shade of blue for the text */
    }
    [data-baseweb="tab-highlight"] {
        background-color: #002A6E !important; /* The same shade of blue for the underline */
    }
    button[data-baseweb="tab"]:hover p {
        color: #002A6E !important; /* Blue on hover */
    }

    /*  6. Selectbox */
    /* กรอบ + ตัวอักษรของ selectbox */
    div[data-baseweb="select"] > div {
        background-color: #002A6E !important; 
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"] > div:hover {
        background-color: #002A6E !important; 
    }
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 2px solid #00B3A4 !important;
    }
    ul[role="listbox"] li {
        color: #003366 !important;
    }
    ul[role="listbox"] li[aria-selected="true"] {
        background-color: #0056A6 !important;
        color: white !important;
    }
    ul[role="listbox"] li:hover {
        background-color: #00B3A4 !important;
        color: white !important;
    }
    div[data-baseweb="select"] svg {
        fill: #FFFFFF !important;
    }
    div[data-baseweb="select"] > div:hover svg {
        fill: #00B3A4 !important;
    }

    /* --- NUMBER INPUT & DATE INPUT --- */
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stDateInput"] div[data-baseweb="input"] {
        border-color: #002A6E !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #002A6E !important;
        box-shadow: none !important;
    }
    div[data-testid="stNumberInput"] input {
        color: #002A6E !important;
        caret-color: #002A6E !important;
    }
    div[data-testid="stNumberInput"] button {
        border-color: #002A6E !important;
        color: #002A6E !important;
    }
    div[data-testid="stNumberInput"] button:hover,
    div[data-testid="stNumberInput"] button:active {
        background-color: #002A6E !important;
        color: white !important;
    }
    

    /* --- BUTTONS --- */
    button[data-testid="stBaseButton-primary"] {
        background-color: #002A6E !important;
        border-color: #002A6E !important;
        color: white !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #0056A6 !important;
        border-color: #0056A6 !important;
        color: white !important;
    }
    button[data-testid="stBaseButton-primary"]:focus, 
    button[data-testid="stBaseButton-primary"]:active {
        background-color: #002A6E !important; 
        border-color: #002A6E !important;
        box-shadow: 0 0 0 0.2rem rgba(0, 42, 110, 0.5) !important; /* เพิ่มเงารอบปุ่มเมื่อ Focus */
}
</style>
"""