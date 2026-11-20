import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime

# ការកំណត់ទំព័រ (Page Config)
st.set_page_config(
    page_title="ដើមកសិកម្ម AI - ក្បួនចិញ្ចឹមសត្វស្តង់ដាអន្តរជាតិ",
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
        font-size: 2.2rem;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        width: 100%;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        color: #ffeb3b;
    }
    </style>
""", unsafe_allow_html=True)

# តភ្ជាប់ Database SQLite ដើម្បីរក្សាទុកប្រវត្តិឯកសារដែលបានបង្កើត
def init_db():
    conn = sqlite3.connect('daem_kasikamm_guides.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS animal_guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_name TEXT,
            farming_system TEXT,
            scale TEXT,
            content TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_guide(animal_name, farming_system, scale, content):
    conn = sqlite3.connect('daem_kasikamm_guides.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO animal_guides (animal_name, farming_system, scale, content, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (animal_name, farming_system, scale, content, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def get_all_guides():
    conn = sqlite3.connect('daem_kasikamm_guides.db')
    c = conn.cursor()
    c.execute('SELECT id, animal_name, farming_system, scale, content, created_at FROM animal_guides ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# ការកំណត់ API Key (ទាញពី Streamlit Secrets ដោយសុវត្ថិភាព ឬបញ្ចូលក្នុង Sidebar)
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
    saved_records = get_all_guides()
    if saved_records:
        selected_record = st.selectbox(
            "ជ្រើសរើសមើលឯកសារចាស់ៗ:",
            options=saved_records,
            format_func=lambda x: f"🐾 {x[1]} ({x[2]}) - {x[5]}"
        )
        if st.button("📖 បើកមើលឯកសារនេះ"):
            st.session_state['current_guide'] = selected_record[4]
            st.session_state['current_title'] = f"{selected_record[1]} - {selected_record[2]}"
    else:
        st.info("មិនទាន់មានឯកសាររក្សាទុកនៅឡើយទេ។")

# ក្បាលទំព័រ (Header)
st.markdown("""
    <div class="main-header">
        <h1>🌱 ប្រព័ន្ធបង្កើតក្បួនចិញ្ចឹមសត្វស្តង់ដាអាជីព និងអន្តរជាតិ</h1>
        <p>ដោយ ដើមកសិកម្ម • ប្រឹក្សាបច្ចេកទេស និងឱសថសត្វស្តង់ដា (096 841 3424 / 085 696 350 / 097 923 3833)</p>
    </div>
""", unsafe_allow_html=True)

# ផ្នែកបញ្ចូលទិន្នន័យដោយសរសេរដៃ
col1, col2, col3 = st.columns([2, 1.5, 1.5])

with col1:
    animal_input = st.text_input(
        "✍️ សរសេរឈ្មោះសត្វដែលចង់ចិញ្ចឹម (អាចសរសេរសត្វអ្វីក៏បាន)៖",
        placeholder="ឧទាហរណ៍៖ កង្កែប, ត្រីទីឡាព្យ៉ា, ជ្រូកសាច់, មាន់ស្រែ, ក្តាមថ្ម, បង្កងអូស្ត្រាលី..."
    )

with col2:
    system_input = st.selectbox(
        "🏗️ ប្រព័ន្ធចិញ្ចឹម (Farming System)៖",
        [
            "ស្តង់ដាទំនើប / អេកូឡូស៊ី (Semi-Intensive / Bio-System)",
            "បែបឧស្សាហកម្មខ្នាតធំ (Intensive Commercial)",
            "បែបធម្មជាតិ / សរីរាង្គ (Organic / Free-Range)",
            "បែបសន្សំសំចៃទីធ្លា / ទឹករាក់ / បណ្តែតទឹក"
        ]
    )

with col3:
    scale_input = st.selectbox(
        "📊 ទំហំអាជីវកម្ម (Scale)៖",
        [
            "កម្រិតអាជីព និងពាណិជ្ជកម្ម (Commercial Standard)",
            "កម្រិតកសិដ្ឋានមធ្យម (Medium Farm)",
            "កម្រិតគ្រួសារស្តង់ដា (Standard Household)"
        ]
    )

extra_notes = st.text_input(
    "📝 បញ្ជាក់បន្ថែម (បើមាន)៖",
    placeholder="ឧទាហរណ៍៖ ចង់ផ្តោតលើការបង្កាត់ពូជ, ការការពារជំងឺរដូវភ្លៀង, ឬរូបមន្តលាយចំណីកាត់បន្ថយថ្លៃដើម..."
)

# ប៊ូតុងដំណើរការបង្កើតឯកសារ
if st.button("🚀 បង្កើតក្បួនខ្នាតបច្ចេកទេសស្តង់ដាអន្តរជាតិ (៩ ផ្នែកពេញលេញ)"):
    if not api_key:
        st.error("⚠️ សូមបញ្ចូល Gemini API Key នៅរបារខាងឆ្វេងជាមុនសិន!")
    elif not animal_input.strip():
        st.warning("⚠️ សូមសរសេរឈ្មោះសត្វជាមុនសិន!")
    else:
        with st.spinner(f"កំពុងចងក្រងឯកសារបច្ចេកទេស និងយុទ្ធសាស្ត្រទីផ្សារសម្រាប់ «{animal_input}»..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                current_date = datetime.now().strftime("%d-%m-%Y")
                
                prompt = f"""
                អ្នកគឺជាអ្នកជំនាញបសុពេទ្យ វារីវប្បកម្ម ក្សេត្រសាស្ត្រ និងយុទ្ធសាស្ត្រទីផ្សារកសិ-ពាណិជ្ជកម្មកម្រិតអន្តរជាតិ ប្រចាំស្ថាប័ន «ដើមកសិកម្ម» នៅប្រទេសកម្ពុជា។
                កាលបរិច្ឆេទចេញផ្សាយឯកសារ៖ {current_date}
                
                សូមសរសេរឯកសារនីតិវិធីប្រតិបត្តិស្តង់ដា (SOP - Standard Operating Procedure) កម្រិតអាជីព និងអន្តរជាតិ ជាភាសាខ្មែរផ្លូវការ ច្បាស់លាស់ ត្រឹមត្រូវតាមវេយ្យាករណ៍ និងបច្ចេកទេសកសិកម្មកម្ពុជា (ហាមបកប្រែឆ្គងពីអង់គ្លេស) អំពីរបៀបចិញ្ចឹម៖
                - ប្រភេទសត្វ៖ {animal_input} (ត្រូវបញ្ជាក់ឈ្មោះវិទ្យាសាស្ត្រឱ្យត្រឹមត្រូវតាមប្រភេទសត្វនេះ)
                - ប្រព័ន្ធចិញ្ចឹម៖ {system_input}
                - កម្រិតអាជីវកម្ម៖ {scale_input}
                - ចំណុចផ្តោតបន្ថែម៖ {extra_notes if extra_notes else "គ្រប់ដណ្តប់គ្រប់ជ្រុងជ្រោយ"}

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
                   - **ការបែងចែកច្រកទីផ្សារ (Market Channels):** យុទ្ធសាស្ត្រលក់បោះដុំ (ឈ្មួញកណ្តាល ផ្សារដើមគរ/ផ្សារខេត្ត) ការចុះកុងត្រាផ្គត់ផ្គង់ផ្ទាល់ (B2B ទៅកាន់ភោជនីយដ្ឋាន សណ្ឋាគារ ផ្សារទំនើប) និងការលក់រាយផ្ទាល់ទៅអ្នកប្រើប្រាស់ (B2C) ដើម្បីគេចពីការទម្លាក់តម្លៃ។
                   - **យុទ្ធសាស្ត្រវដ្តផលិតកម្មតាមរដូវកាល (Seasonal & Counter-Seasonal Timing):** របៀបរៀបចំកាលវិភាគដាក់ពូជ និងចាប់លក់ឱ្យចំរដូវកាលខ្វះខាត ឬពិធីបុណ្យធំៗនៅកម្ពុជា (ចូលឆ្នាំខ្មែរ ភ្ជុំបិណ្ឌ ចូលឆ្នាំចិន) ដើម្បីបានតម្លៃខ្ពស់បំផុត។
                   - **ការបន្ថែមតម្លៃ និងការវេចខ្ចប់ (Value-Added Processing & Packaging):** វិធីកែច្នៃ (លាងសម្អាត វេចខ្ចប់បូមខ្យល់ Vacuum Pack បង្កក ឬផលិតជាផលិតផលសម្រេច/ពាក់កណ្តាលសម្រេច) ការបង្កើតម៉ាកយីហោ និងស្តង់ដាគុណភាព/អនាម័យ។
                   - **ទីផ្សារឌីជីថល និងការកសាងទំនុកចិត្ត (Digital Marketing & Trust Building):** វិធីប្រើប្រាស់ Facebook Page, TikTok និង Telegram ថតវីដេអូបង្ហាញពីដំណើរការចិញ្ចឹមស្អាត គ្មានសារធាតុគីមី/គ្មានថ្នាំផ្សះសល់ក្នុងសាច់ និងវិធីចងម៉ូយអចិន្ត្រៃយ៍ (Customer Retention)។
                """
                
                response = model.generate_content(prompt)
                guide_text = response.text
                
                # រក្សាទុកក្នុង Session និង Database
                st.session_state['current_guide'] = guide_text
                st.session_state['current_title'] = f"{animal_input} ({system_input})"
                save_guide(animal_input, system_input, scale_input, guide_text)
                st.success("✅ បង្កើត និងរក្សាទុកក្នុងបណ្ណាល័យរួចរាល់!")
                
            except Exception as e:
                st.error(f"❌ មានបញ្ហាបច្ចេកទេស៖ {str(e)}")

# បង្ហាញលទ្ធផល និងមុខងារ Export / Copy
if 'current_guide' in st.session_state:
    st.markdown("---")
    st.subheader(f"📘 ឯកសារស្តង់ដាអន្តរជាតិ៖ {st.session_state['current_title']}")
    
    safe_filename = st.session_state['current_title'].replace('/', '_').replace('\\', '_').replace(' ', '_')
    
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