import streamlit as st
import google.generativeai as genai
import sqlite3
import re
from datetime import datetime

# ការកំណត់ទំព័រ (Page Config)
st.set_page_config(
    page_title="ដើមកសិកម្ម AI - ក្បួនចិញ្ចឹមសត្វ និងដាំដំណាំស្តង់ដាអន្តរជាតិ",
    page_icon="🌱",
    layout="wide"
)

# រចនាបថ CSS សម្រាប់ពុម្ពអក្សរខ្មែរ និងពណ៌បៃតងតំណាង ដើមកសិកម្ម
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Battambang:wght@400;700&family=Koulen&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Battambang', sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #388e3c 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        font-family: 'Koulen', sans-serif;
        color: #ffeb3b;
        margin: 0;
        font-size: 2.1rem;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        width: 100%;
        font-size: 1.05rem;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        color: #ffeb3b;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e8f5e9;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: bold;
        color: #1b5e20;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        color: #ffeb3b !important;
    }
    </style>
""", unsafe_allow_html=True)

# តភ្ជាប់ Database SQLite ដើម្បីរក្សាទុកប្រវត្តិឯកសារទាំងសត្វ និងដំណាំ
def init_db():
    conn = sqlite3.connect('daem_kasikamm_guides.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS animal_guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT DEFAULT 'ចិញ្ចឹមសត្វ',
            animal_name TEXT,
            farming_system TEXT,
            scale TEXT,
            content TEXT,
            created_at TEXT
        )
    ''')
    # បន្ថែមជួរឈរ category ដោយស្វ័យប្រវត្តិ បើជា Database ចាស់
    try:
        c.execute("ALTER TABLE animal_guides ADD COLUMN category TEXT DEFAULT 'ចិញ្ចឹមសត្វ'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def save_guide(category, item_name, farming_system, scale, content):
    conn = sqlite3.connect('daem_kasikamm_guides.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO animal_guides (category, animal_name, farming_system, scale, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (category, item_name, farming_system, scale, content, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def get_all_guides(filter_category="ទាំងអស់"):
    conn = sqlite3.connect('daem_kasikamm_guides.db')
    c = conn.cursor()
    if filter_category == "ទាំងអស់":
        c.execute('SELECT id, category, animal_name, farming_system, scale, content, created_at FROM animal_guides ORDER BY id DESC')
    else:
        c.execute('SELECT id, category, animal_name, farming_system, scale, content, created_at FROM animal_guides WHERE category = ? ORDER BY id DESC', (filter_category,))
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# ការកំណត់ API Key និងបណ្ណាល័យក្នុង Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    st.markdown("### ⚙️ ការកំណត់ប្រព័ន្ធ ដើមកសិកម្ម")
    
    api_key = ""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ បានភ្ជាប់ API Key ដោយស្វ័យប្រវត្តិ")
    except Exception:
        pass

    if not api_key:
        api_key = st.text_input("បញ្ចូល Google Gemini API Key:", type="password")
    
    st.markdown("---")
    st.markdown("### 📚 បណ្ណាល័យឯកសារដែលបានរក្សាទុក")
    lib_filter = st.radio(
        "ត្រងមើលតាមប្រភេទ៖",
        ["ទាំងអស់", "ចិញ្ចឹមសត្វ", "ដាំដំណាំ"],
        horizontal=True
    )
    saved_records = get_all_guides(lib_filter)
    if saved_records:
        selected_record = st.selectbox(
            "ជ្រើសរើសមើលឯកសារចាស់ៗ៖",
            options=saved_records,
            format_func=lambda x: f"{'🥬' if x[1] == 'ដាំដំណាំ' else '🐾'} {x[2]} ({x[3]}) - {x[6]}"
        )
        if st.button("📖 បើកមើលឯកសារនេះ"):
            st.session_state['current_guide'] = selected_record[5]
            st.session_state['current_title'] = f"{selected_record[2]} - {selected_record[3]}"
            st.session_state['current_category'] = selected_record[1] or "ចិញ្ចឹមសត្វ"
    else:
        st.info("មិនទាន់មានឯកសាររក្សាទុកនៅឡើយទេ។")

# ក្បាលទំព័រ (Header)
st.markdown("""
    <div class="main-header">
        <h1>🌱 ប្រព័ន្ធបង្កើតក្បួនចិញ្ចឹមសត្វ និងដាំដំណាំស្តង់ដាអាជីព-អន្តរជាតិ</h1>
        <p>ដោយ ដើមកសិកម្ម • ប្រឹក្សាបច្ចេកទេសកសិកម្ម និងឱសថសត្វស្តង់ដា (096 841 3424 / 085 696 350 / 097 923 3833)</p>
    </div>
""", unsafe_allow_html=True)

# បង្កើតផ្ទាំង Tab ទាំង ២
tab_animal, tab_crop = st.tabs([
    "🐾 ក្បួនចិញ្ចឹមសត្វ (Livestock & Aquaculture)",
    "🥬 ក្បួនដាំដំណាំបន្លែ និងដំណាំផ្សេងៗ (Crops & Vegetables)"
])

# ==============================================================================
# TAB 1: ក្បួនចិញ្ចឹមសត្វ
# ==============================================================================
with tab_animal:
    col1, col2, col3 = st.columns([2, 1.5, 1.5])

    with col1:
        animal_input = st.text_input(
            "✍️ សរសេរឈ្មោះសត្វដែលចង់ចិញ្ចឹម (អាចសរសេរសត្វអ្វីក៏បាន)៖",
            placeholder="ឧទាហរណ៍៖ កង្កែប, ត្រីទីឡាព្យ៉ា, ជ្រូកសាច់, មាន់ស្រែ, ក្តាមថ្ម, បង្កងអូស្ត្រាលី...",
            key="animal_input"
        )

    with col2:
        animal_system = st.selectbox(
            "🏗️ ប្រព័ន្ធចិញ្ចឹម (Farming System)៖",
            [
                "ស្តង់ដាទំនើប / អេកូឡូស៊ី (Semi-Intensive / Bio-System)",
                "បែបឧស្សាហកម្មខ្នាតធំ (Intensive Commercial)",
                "បែបធម្មជាតិ / សរីរាង្គ (Organic / Free-Range)",
                "បែបសន្សំសំចៃទីធ្លា / ទឹករាក់ / បណ្តែតទឹក"
            ],
            key="animal_system"
        )

    with col3:
        animal_scale = st.selectbox(
            "📊 ទំហំអាជីវកម្ម (Scale)៖",
            [
                "កម្រិតអាជីព និងពាណិជ្ជកម្ម (Commercial Standard)",
                "កម្រិតកសិដ្ឋានមធ្យម (Medium Farm)",
                "កម្រិតគ្រួសារស្តង់ដា (Standard Household)"
            ],
            key="animal_scale"
        )

    animal_notes = st.text_input(
        "📝 បញ្ជាក់បន្ថែម (បើមាន)៖",
        placeholder="ឧទាហរណ៍៖ ចង់ផ្តោតលើការបង្កាត់ពូជ, ការការពារជំងឺរដូវភ្លៀង, ឬរូបមន្តលាយចំណីកាត់បន្ថយថ្លៃដើម...",
        key="animal_notes"
    )

    if st.button("🚀 បង្កើតក្បួនចិញ្ចឹមសត្វស្តង់ដាអន្តរជាតិ (៩ ផ្នែកពេញលេញ)", key="btn_animal"):
        if not api_key:
            st.error("⚠️ សូមបញ្ចូល Gemini API Key នៅរបារខាងឆ្វេងជាមុនសិន!")
        elif not animal_input.strip():
            st.warning("⚠️ សូមសរសេរឈ្មោះសត្វជាមុនសិន!")
        else:
            with st.spinner(f"កំពុងចងក្រងឯកសារបច្ចេកទេស និងយុទ្ធសាស្ត្រទីផ្សារសម្រាប់ការចិញ្ចឹម «{animal_input}»..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    current_date = datetime.now().strftime("%d-%m-%Y")
                    
                    prompt = f"""
                    អ្នកគឺជាអ្នកជំនាញបសុពេទ្យ វារីវប្បកម្ម ក្សេត្រសាស្ត្រ និងយុទ្ធសាស្ត្រទីផ្សារកសិ-ពាណិជ្ជកម្មកម្រិតអន្តរជាតិ ប្រចាំស្ថាប័ន «ដើមកសិកម្ម» នៅប្រទេសកម្ពុជា។
                    កាលបរិច្ឆេទចេញផ្សាយឯកសារ៖ {current_date}
                    
                    សូមសរសេរឯកសារនីតិវិធីប្រតិបត្តិស្តង់ដា (SOP - Standard Operating Procedure) កម្រិតអាជីព និងអន្តរជាតិ ជាភាសាខ្មែរផ្លូវការ ច្បាស់លាស់ ត្រឹមត្រូវតាមវេយ្យាករណ៍ និងបច្ចេកទេសកសិកម្មកម្ពុជា (ហាមបកប្រែឆ្គងពីអង់គ្លេស) អំពីរបៀបចិញ្ចឹម៖
                    - ប្រភេទសត្វ៖ {animal_input} (ត្រូវបញ្ជាក់ឈ្មោះវិទ្យាសាស្ត្រឱ្យត្រឹមត្រូវតាមប្រភេទសត្វនេះ)
                    - ប្រព័ន្ធចិញ្ចឹម៖ {animal_system}
                    - កម្រិតអាជីវកម្ម៖ {animal_scale}
                    - ចំណុចផ្តោតបន្ថែម៖ {animal_notes if animal_notes else "គ្រប់ដណ្តប់គ្រប់ជ្រុងជ្រោយ"}

                    សូមរៀបចំខ្លឹមសារតាមរចនាសម្ព័ន្ធស្តង់ដាអន្តរជាតិ ៩ ផ្នែកដូចខាងក្រោម (ប្រើតារាង និងចំណុចលម្អិតជាមួយតួលេខជាក់លាក់)៖
                    1. **ស្តង់ដាហេដ្ឋារចនាសម្ព័ន្ធ ទីតាំង និងការរៀបចំអាង/ទ្រុង (Housing & Pond/Pen Design):** ទំហំ, ជម្រៅ, សម្ភារៈ, ប្រព័ន្ធខ្យល់, ប្រព័ន្ធបង្ហូរទឹក និងការសម្លាប់មេរោគមុនដាក់សត្វ (Biosecurity)។
                    2. **ការជ្រើសរើសពូជ និងដង់ស៊ីតេចិញ្ចឹម (Breed Selection & Stocking Density):** លក្ខណៈពូជសុទ្ធ/កូនល្អ, ដង់ស៊ីតេសមស្របតាមម៉ែត្រការ៉េ ឬម៉ែត្រគូប និងវិធីបន្សាំមុនព្រលែង។
                    3. **ការគ្រប់គ្រងបរិស្ថាន និងគុណភាពទឹក/អាកាសធាតុ (Environmental & Microclimate Control):** 
                       *(ចំណាំសំខាន់៖ ប្រសិនបើជាសត្វទឹក ត្រូវបង្ហាញតារាងប៉ារ៉ាម៉ែត្រទឹកមាន សីតុណ្ហភាព, pH, DO, អាម៉ូញាក់ NH3, នីទ្រីត NO2 និងការប្រើប្រាស់មេជីវិត Probiotics។ ប្រសិនបើជាសត្វគោក ឬសត្វល្អិត ត្រូវបង្ហាញតែតារាងប៉ារ៉ាម៉ែត្រខ្យល់ និងអាកាសធាតុមាន សីតុណ្ហភាព °C, សំណើម RH%, អត្រាប្តូរខ្យល់ ACH, NH3, CO2 ដោយមិនបាច់ដាក់ជួរឈរ DO និង pH ទឹកទេ)*។
                    4. **កម្មវិធីផ្តល់ចំណី និងអាហារូបត្ថម្ភតាមដំណាក់កាល (Precision Nutrition & Feeding Schedule):** កម្រិតប្រូតេអ៊ីន (%) តាមអាយុ, អត្រាផ្តល់ចំណី (% នៃទម្ងន់ខ្លួន), ចំនួនដង/ថ្ងៃ, គោលដៅមេគុណបំប្លែងចំណី (FCR) និងការបន្ថែមវីតាមីន/រ៉ែ (ADE B-Complex, Calcium, E.lac)។
                    5. **ប្រព័ន្ធជីវសុវត្ថិភាព និងកម្មវិធីវ៉ាក់សាំង/ការពារជំងឺ (Biosecurity & Disease Prevention Program):** កាលវិភាគផ្តល់វ៉ាក់សាំង (បើមានសម្រាប់ប្រភេទសត្វនោះ) ការគ្រប់គ្រងសត្វចង្រៃ និងការការពារតាមរដូវកាល។
                    6. **ការវិភាគ និងព្យាបាលជំងឺសំខាន់ៗ (Common Diseases & Veterinary Protocols):** រោគសញ្ញា មូលហេតុ ក្រុមថ្នាំព្យាបាលស្តង់ដាអន្តរជាតិ កម្រិតប្រើប្រាស់ និងរយៈពេលឈប់ប្រើថ្នាំមុនចាប់លក់ (Withdrawal Period)។
                    7. **ការគ្រប់គ្រងគុណភាពសាច់ និងការប្រមូលផល (Pre-Harvest Conditioning & Harvesting):** វិធីធ្វើឱ្យសាច់ហាប់ណែន គ្មានក្លិនឆ្អាប/ភក់ និងបច្ចេកទេសប្រមូលផលកុំឱ្យសត្វស្ត្រេស។
                    8. **ការវិភាគសេដ្ឋកិច្ច និងផែនការហិរញ្ញវត្ថុប៉ាន់ស្មាន (Economic & ROI Estimation):** រយៈពេលចិញ្ចឹម, អត្រារស់រានមានជីវិតស្តង់ដា (%), ទម្ងន់ចាប់លក់ និងតារាងវិភាគថ្លៃដើមដើម្បីចំណេញខ្ពស់។
                    9. **យុទ្ធសាស្ត្រទីផ្សារ ការកសាងម៉ាកយីហោ និងការលក់កម្រិតអាជីព (Marketing, Branding & Sales Strategy):**
                       - **ការបែងចែកច្រកទីផ្សារ (Market Channels):** លក់បោះដុំ (ឈ្មួញកណ្តាល ផ្សារដើមគរ/ផ្សារខេត្ត), កុងត្រា B2B (ភោជនីយដ្ឋាន សណ្ឋាគារ ផ្សារទំនើប) និងលក់រាយផ្ទាល់ B2C។
                       - **យុទ្ធសាស្ត្រវដ្តផលិតកម្មតាមរដូវកាល (Seasonal & Counter-Seasonal Timing):** របៀបរៀបចំកាលវិភាគដាក់ពូជ និងចាប់លក់ឱ្យចំរដូវកាលខ្វះខាត ឬពិធីបុណ្យធំៗនៅកម្ពុជា (ចូលឆ្នាំខ្មែរ ភ្ជុំបិណ្ឌ ចូលឆ្នាំចិន)។
                       - **ការបន្ថែមតម្លៃ និងការវេចខ្ចប់ (Value-Added Processing & Packaging):** ការលាងសម្អាត វេចខ្ចប់បូមខ្យល់ (Vacuum Pack) បង្កក ឬកែច្នៃបន្ថែមតម្លៃ។
                       - **ទីផ្សារឌីជីថល និងការកសាងទំនុកចិត្ត (Digital Marketing & Trust Building):** ការប្រើប្រាស់ Facebook Page, TikTok និង Telegram ថតវីដេអូបង្ហាញពីស្តង់ដាចិញ្ចឹមស្អាត គ្មានសារធាតុគីមី/ថ្នាំផ្សះសល់ក្នុងសាច់។
                    """
                    
                    response = model.generate_content(prompt)
                    guide_text = response.text
                    
                    st.session_state['current_guide'] = guide_text
                    st.session_state['current_title'] = f"{animal_input} ({animal_system})"
                    st.session_state['current_category'] = "ចិញ្ចឹមសត្វ"
                    save_guide("ចិញ្ចឹមសត្វ", animal_input, animal_system, animal_scale, guide_text)
                    st.success("✅ បង្កើតក្បួនចិញ្ចឹមសត្វ និងរក្សាទុកក្នុងបណ្ណាល័យរួចរាល់!")
                    
                except Exception as e:
                    st.error(f"❌ មានបញ្ហាបច្ចេកទេស៖ {str(e)}")

# ==============================================================================
# TAB 2: ក្បួនដាំដំណាំបន្លែ និងដំណាំផ្សេងៗ
# ==============================================================================
with tab_crop:
    c_col1, c_col2, c_col3 = st.columns([2, 1.5, 1.5])

    with c_col1:
        crop_input = st.text_input(
            "✍️ សរសេរឈ្មោះបន្លែ ឬដំណាំដែលចង់ដាំ (អាចសរសេរដំណាំអ្វីក៏បាន)៖",
            placeholder="ឧទាហរណ៍៖ ស្ពៃក្តោប, ប៉េងប៉ោះ, ត្រសក់ផ្អែម, ម្ទេស, ធុរេន, ម្រេច, ស្រូវសែនក្រអូប, ផ្សិតអំបោះ...",
            key="crop_input"
        )

    with c_col2:
        crop_system = st.selectbox(
            "🚜 ប្រព័ន្ធដាំដុះ (Cultivation System)៖",
            [
                "ដាំលើដីស្តង់ដាទំនើប / CamGAP (Open Field & Drip Irrigation)",
                "ដាំក្នុងផ្ទះសំណាញ់ / ផ្ទះកញ្ចក់ (Greenhouse / Net House)",
                "ដាំដោយមិនប្រើដី / ប្រព័ន្ធទឹកជី (Hydroponics / Cocopeat Substrate)",
                "ដាំបែបសរីរាង្គធម្មជាតិ ១០០% (Organic Farming)"
            ],
            key="crop_system"
        )

    with c_col3:
        crop_scale = st.selectbox(
            "📊 ទំហំផលិតកម្ម (Scale)៖",
            [
                "កម្រិតអាជីព ពាណិជ្ជកម្ម និងនាំចេញ (GlobalG.A.P. / Export Standard)",
                "កម្រិតកសិដ្ឋានមធ្យម (Medium Commercial Farm)",
                "កម្រិតគ្រួសារស្តង់ដា (Standard Household Garden)"
            ],
            key="crop_scale"
        )

    crop_notes = st.text_input(
        "📝 បញ្ជាក់បន្ថែម (បើមាន)៖",
        placeholder="ឧទាហរណ៍៖ ចង់ដាំនៅរដូវភ្លៀង, ផ្តោតលើរូបមន្តបំប៉នផ្លែឱ្យផ្អែម, កាត់បន្ថយជំងឺផ្សិតរលួយគល់, ឬដាំខុសរដូវ...",
        key="crop_notes"
    )

    if st.button("🌿 បង្កើតក្បួនដាំដំណាំស្តង់ដាអន្តរជាតិ (៩ ផ្នែកពេញលេញ)", key="btn_crop"):
        if not api_key:
            st.error("⚠️ សូមបញ្ចូល Gemini API Key នៅរបារខាងឆ្វេងជាមុនសិន!")
        elif not crop_input.strip():
            st.warning("⚠️ សូមសរសេរឈ្មោះបន្លែ ឬដំណាំជាមុនសិន!")
        else:
            with st.spinner(f"កំពុងចងក្រងឯកសារបច្ចេកទេសដាំដុះស្តង់ដាអន្តរជាតិ (GAP) សម្រាប់ «{crop_input}»..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    current_date = datetime.now().strftime("%d-%m-%Y")
                    
                    crop_prompt = f"""
                    អ្នកគឺជាអ្នកជំនាញក្សេត្រសាស្ត្រ បច្ចេកទេសដាំដុះស្តង់ដាអន្តរជាតិ (GlobalG.A.P. / CamGAP) ការការពារដំណាំ និងយុទ្ធសាស្ត្រទីផ្សារកសិផល ប្រចាំស្ថាប័ន «ដើមកសិកម្ម» នៅប្រទេសកម្ពុជា។
                    កាលបរិច្ឆេទចេញផ្សាយឯកសារ៖ {current_date}
                    
                    សូមសរសេរឯកសារនីតិវិធីប្រតិបត្តិស្តង់ដា (SOP - Standard Operating Procedure) កម្រិតអាជីព និងអន្តរជាតិ ជាភាសាខ្មែរផ្លូវការ ច្បាស់លាស់ ត្រឹមត្រូវតាមវេយ្យាករណ៍ និងបច្ចេកទេសកសិកម្មកម្ពុជា (ហាមបកប្រែឆ្គងពីអង់គ្លេស) អំពីរបៀបដាំដុះ៖
                    - ប្រភេទដំណាំ/បន្លែ៖ {crop_input} (ត្រូវបញ្ជាក់ឈ្មោះវិទ្យាសាស្ត្រ និងអំបូររុក្ខជាតិឱ្យត្រឹមត្រូវ)
                    - ប្រព័ន្ធដាំដុះ៖ {crop_system}
                    - កម្រិតផលិតកម្ម៖ {crop_scale}
                    - ចំណុចផ្តោតបន្ថែម៖ {crop_notes if crop_notes else "គ្រប់ដណ្តប់គ្រប់ជ្រុងជ្រោយ"}

                    សូមរៀបចំខ្លឹមសារតាមរចនាសម្ព័ន្ធស្តង់ដាអន្តរជាតិ ៩ ផ្នែកដូចខាងក្រោម (ប្រើតារាង និងចំណុចលម្អិតជាមួយតួលេខជាក់លាក់)៖
                    1. **ការជ្រើសរើសទីតាំង ការរៀបចំដី និងហេដ្ឋារចនាសម្ព័ន្ធ (Site Selection, Soil/Substrate Preparation & Infrastructure):** ប្រភេទដីសមស្រប ឬល្បាយដីដាំ (Cocopeat/Perlite បើជា Hydroponics/ផ្ទះសំណាញ់), ការភ្ជួររាស់ហាលដី, ការលើករង (ទទឹង កម្ពស់ ចន្លោះរង), ការកែលម្អ pH ដីដោយកំបោរស/ដូឡូម៉ាយ (Dolomite), ការដាក់ជីទ្រាប់បាត និងការប្រើមេផ្សិតទ្រីកូដឺម៉ា (Trichoderma) ការពារជំងឺក្នុងដី។
                    2. **ការជ្រើសរើសពូជ ការបណ្តុះកូន និងចន្លោះដាំ (Variety Selection, Nursery & Planting Density):** លក្ខណៈពូជ F1 ឬពូជធន់ជំងឺ, បច្ចេកទេសសម្លាប់មេរោគគ្រាប់ពូជ, ការបណ្តុះកូនក្នុងថាសបណ្តុះ (អាយុដកស្ទូង/ដាំ), ចន្លោះគុម្ព x ចន្លោះជួរ (សង់ទីម៉ែត្រ/ម៉ែត្រ) និងចំនួនដើមស្តង់ដាក្នុង ១ ហិកតា ឬ ១,០០០ ម៉ែត្រការ៉េ។
                    3. **ការគ្រប់គ្រងបរិស្ថាន មីក្រូអាកាសធាតុ និងប្រព័ន្ធស្រោចស្រព (Microclimate & Precision Irrigation):** 
                       បង្ហាញតារាងប៉ារ៉ាម៉ែត្រស្តង់ដាជាក់លាក់រួមមាន៖ សីតុណ្ហភាពសមស្រប (°C), សំណើមខ្យល់ (RH%), កម្រិត pH ដី/ទឹក, កម្រិតជាតិអំបិល/ជី EC (mS/cm), តម្រូវការពន្លឺ, បរិមាណទឹក និងប្រព័ន្ធស្រោចស្រពស្តង់ដា (តំណក់ទឹក Drip Irrigation ឬបាញ់សាច Sprinkler) តាមដំណាក់កាលលូតលាស់។
                    4. **កម្មវិធីផ្តល់ជី និងអាហារូបត្ថម្ភរុក្ខជាតិតាមដំណាក់កាល (Precision Fertilization & Nutrition Schedule):** 
                       បង្ហាញតារាងដាក់ជីតាមអាយុដំណាំ (ដំណាក់កាលលូតលាស់ដើម-ស្លឹក, ចេញផ្កា, ក្តិប/បង្កើតផ្លែ និងមុនប្រមូលផល) ដោយបញ្ជាក់រូបមន្តជី N-P-K, កាល់ស្យូម-បូរ៉ុង (Ca-B), ម៉ាញេស្យូម, មីក្រូសារធាតុ, ជីសរីរាង្គ/អាស៊ីតអាមីណូ និងបច្ចេកទេសបង្ហូរជីតាមទឹក (Fertigation)។
                    5. **ការថែទាំដំណាំ ការតាក់តែងមែក និងការគ្រប់គ្រងស្មៅ (Canopy Management, Mulching & Weed Control):** ការគ្របប្លាស្ទិកប្រាក់-ខ្មៅ ឬចំបើង (Mulching), ការធ្វើទ្រើង/ចងខ្សែ, បច្ចេកទេសតាក់តែងមែក/បេះខ្នែង/ជ្រើសផ្លែ (Pruning & Thinning), ការជួយបង្កាត់លំអង (បើចាំបាច់) និងការកម្ចាត់ស្មៅប្រកបដោយសុវត្ថិភាព។
                    6. **ការគ្រប់គ្រងសត្វល្អិតចង្រៃ និងជំងឺតាមគោលការណ៍ IPM & GAP (Integrated Pest & Disease Management):** 
                       បង្ហាញតារាងជំងឺ (ផ្សិត បាក់តេរី វីរុស) និងសត្វល្អិតសំខាន់ៗ ដោយបញ្ជាក់ពី៖ រោគសញ្ញា, មូលហេតុ, វិធីការពារជីវសាស្ត្រ/អន្ទាក់, ក្រុមសារធាតុសកម្មព្យាបាលស្តង់ដាអន្តរជាតិ (Active Ingredients ឧ. Azoxystrobin, Emamectin benzoate, Copper hydroxide, Bacillus thuringiensis ។ល។), គោលការណ៍ប្តូរក្រុមថ្នាំកុំឱ្យស៊ាំ និង **រយៈពេលឈប់បាញ់ថ្នាំមុនប្រមូលផល (PHI - Pre-Harvest Interval)** ដើម្បីធានាគ្មានសារធាតុគីមីសេសសល់។
                    7. **បច្ចេកទេសប្រមូលផល និងការថែរក្សាក្រោយប្រមូលផល (Harvesting & Post-Harvest Handling):** សញ្ញាសម្គាល់ភាពទុំ/អាយុប្រមូលផល, ពេលវេលាល្អបំផុតក្នុងថ្ងៃសម្រាប់កាត់/បេះ, វិធីបន្ថយកម្ដៅភ្លាមៗ (Pre-cooling), ការលាងសម្អាត ការបែងចែកខ្នាត/គុណភាព (Sorting & Grading) និងសីតុណ្ហភាពស្តុកទុកដើម្បីរក្សាភាពស្រស់បានយូរ។
                    8. **ការវិភាគសេដ្ឋកិច្ច ទិន្នផល និងផែនការហិរញ្ញវត្ថុប៉ាន់ស្មាន (Yield, Cost & ROI Estimation):** រយៈពេលដាំដុះដល់ប្រមូលផល, ទិន្នផលមធ្យមស្តង់ដា (គីឡូក្រាម ឬតោន/ហិកតា ឬក្នុង ១,០០០ ម៉ែត្រការ៉េ), តារាងវិភាគថ្លៃដើមផលិតកម្ម និងចំណុចគន្លឹះកាត់បន្ថយថ្លៃដើមដើម្បីចំណេញខ្ពស់។
                    9. **យុទ្ធសាស្ត្រទីផ្សារ ការកសាងម៉ាកយីហោ និងការលក់កម្រិតអាជីព (Marketing, Branding & Sales Strategy):**
                       - **ការបែងចែកច្រកទីផ្សារ (Market Channels):** លក់បោះដុំ (ផ្សារដើមគរ/ផ្សារខេត្ត), កុងត្រាផ្គត់ផ្គង់ផ្ទាល់ B2B (ផ្សារទំនើប សណ្ឋាគារ ភោជនីយដ្ឋាន ហាងបន្លែសរីរាង្គ) និងលក់រាយផ្ទាល់ដល់អតិថិជន B2C។
                       - **យុទ្ធសាស្ត្រដាំដុះខុសរដូវ និងរដូវកាលកម្ពុជា (Counter-Seasonal Timing):** ការកំណត់ថ្ងៃសាបព្រោះឱ្យចំរដូវខ្វះខាតបន្លែ/ផ្លែឈើ ឬចំថ្ងៃបុណ្យធំៗ (ចូលឆ្នាំខ្មែរ ភ្ជុំបិណ្ឌ ចូលឆ្នាំចិន) ដើម្បីគេចពីការជន់លិចទីផ្សារ និងបានតម្លៃថ្លៃ។
                       - **ការបន្ថែមតម្លៃ ការវេចខ្ចប់ និងវិញ្ញាបនបត្រ (Value-Added & CamGAP Branding):** ការវេចខ្ចប់ស្អាតមានបិទផ្លាកសញ្ញា និង QR Code តាមដានប្រភពដើម (Traceability) ឬការកែច្នៃជាផលិតផលសម្ងួត/បង្កក/ដប។
                       - **ទីផ្សារឌីជីថល និងការកសាងទំនុកចិត្ត (Digital Marketing):** ការប្រើប្រាស់ Facebook Page, TikTok និង Telegram ថតវីដេអូបង្ហាញពីចម្ការស្អាត ការដាំដុះតាមស្តង់ដាគ្មានជាតិគីមីពុល និងការចងម៉ូយប្រចាំសប្តាហ៍។
                    """
                    
                    response = model.generate_content(crop_prompt)
                    guide_text = response.text
                    
                    st.session_state['current_guide'] = guide_text
                    st.session_state['current_title'] = f"{crop_input} ({crop_system})"
                    st.session_state['current_category'] = "ដាំដំណាំ"
                    save_guide("ដាំដំណាំ", crop_input, crop_system, crop_scale, guide_text)
                    st.success("✅ បង្កើតក្បួនដាំដំណាំ និងរក្សាទុកក្នុងបណ្ណាល័យរួចរាល់!")
                    
                except Exception as e:
                    st.error(f"❌ មានបញ្ហាបច្ចេកទេស៖ {str(e)}")

# ==============================================================================
# បង្ហាញលទ្ធផល និងមុខងារ Export / Copy (ប្រើរួមគ្នាទាំងសត្វ និងដំណាំ)
# ==============================================================================
if 'current_guide' in st.session_state:
    st.markdown("---")
    cat_icon = "🥬" if st.session_state.get('current_category') == "ដាំដំណាំ" else "🐾"
    st.subheader(f"{cat_icon} ឯកសារស្តង់ដាអន្តរជាតិ៖ {st.session_state['current_title']}")
    
    safe_filename = re.sub(r'[\\/*?:"<>|\s]+', '_', st.session_state['current_title'])
    
    # ប៊ូតុងទាញយកជាឯកសារ Text/Markdown
    st.download_button(
        label="📥 ទាញយកឯកសារនេះទុក (Download .txt)",
        data=st.session_state['current_guide'],
        file_name=f"DaemKasikamm_{safe_filename}.txt",
        mime="text/plain"
    )
    
    # បង្ហាញខ្លឹមសារពេញលេញ
    st.markdown(st.session_state['current_guide'])
    
    # ប្រអប់សម្រាប់ Copy ងាយស្រួលយកទៅផុស ឬដាក់ក្នុងសៀវភៅ
    with st.expander("📋 ចុចទីនេះដើម្បី Copy អត្ថបទដើមទាំងស្រុង (Raw Text)"):
        st.code(st.session_state['current_guide'], language="markdown")
