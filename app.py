import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ============================================================
# CONFIGURAZIONE PAGINA
# ============================================================
st.set_page_config(
    page_title="Elaborazione File Nike",
    page_icon="👟",
    layout="wide",
)

# ============================================================
# DIZIONARI
# ============================================================

# Division -> Categoria BG
DIVISION_MAP = {
    'APP': 'Дрехи',
    'FTW': 'Обувки',
    'EQU': 'Аксесоари',
}

# Gender -> GEN.BG
GENDER_MAP = {
    'MENS': 'Мъже',
    'WOMENS': 'Жени',
    'GIRLS': 'Момичета',
    'BOYS': 'Момчета',
    'YOUTH UNISEX': 'Юноши Унисекс',
    'INFANT UNISEX': 'Бебета Унисекс',
    'ADULT UNISEX': 'Възрастни Унисекс',
    'CHILD UNISEX': 'Деца унисекс',
    'UNISEX': 'Унисекс',
    'Youth unisex': 'Младежи унисекс',
    'Boys pre school': 'Момчета пред училищна',
    'Boys toddler': 'Момчета малки деца',
    'Boys grade schl': 'Момчета начално учулище',
    'KIDS BOYS': 'Момчета',
    'KIDS GIRLS': 'Момичета',
    'KIDS-LITTLE KIDS': 'Малки деца',
    'Youth': 'Младежи',
    'GRD SCHOOL UNSX': 'Унисекс',
    'GRD SCHOOL UNS': 'Деца унисекс',
    'PRE SCHOOL UNSX': 'Деца унисекс',
    'TODDLER UNISEX': 'Унисекс',
}

# GEN.BG -> Категория_1
SESSO_MAP = {
    'Мъже': 'Мъже',
    'Жени': 'Жени',
    'Момичета': 'Деца',
    'Момчета': 'Деца',
    'Юноши Унисекс': 'Деца',
    'Бебета Унисекс': 'Деца',
    'Възрастни Унисекс': 'Унисекс',
    'Деца унисекс': 'Деца',
    'Унисекс': 'Унисекс',
    'Младежи унисекс': 'Деца',
    'Момчета пред училищна': 'Деца',
    'Момчета малки деца': 'Деца',
    'Момчета начално учулище': 'Деца',
    'Малки деца': 'Деца',
    'Младежи': 'Деца',
}

# Категория_1 -> prefisso per Категория_2
CATEGORY2_PREFIX = {
    'Мъже': 'Мъжки',
    'Жени': 'Дамски',
    'Деца': 'Детски',
    'Унисекс': 'Унисекс',
    'Момчета': 'Детски',
    'Момичета': 'Детски',
}

# TIPO (Silhouette EN) -> TIPO.BG  (dizionario integrato da SOFIA Traduzioni)
TIPO_MAP = {
    'Sneakers': 'Маратонки',
    'T-shirt': 'Тениска',
    'Shirt': 'Риза',
    'Sweatshirt': 'Суитшърт',
    'Hat': 'Шапка',
    'Jacket': 'Яке',
    'Pants': 'Панталон',
    'Shorts': 'Къс панталон',
    'Socks': 'Чорапи',
    'Body': 'Боди',
    'Sandals': 'Сандали',
    'SHORT SLEEVE TOP': 'Тениска',
    'LOW TOP': 'Маратонки',
    'UPPER THIGH LENGTH SHORT': 'Къс панталон',
    'MID THIGH LENGTH SHORT': 'Къс панталон',
    'SHORT SLEEVE T-SHIRT': 'Тениска',
    'KNEE LENGTH SHORT': 'Къс панталон',
    'HOODED FULL ZIP LS TOP': 'Суитшърт',
    'FULL LENGTH PANT': 'Панталон',
    'CREW SOCK': 'Чорапи',
    'THREE QUARTER HIGH': 'Кецове',
    'FULL LENGTH TIGHT': 'Клин',
    'HIGH TOP': 'Кецове',
    'LONG SLEEVE TOP': 'Суитшърт',
    'SLEEVELESS TOP': 'Топ',
    'HIP LENGTH HOODED JKT': 'Яке',
    'HOODED LONG SLEEVE TOP': 'Суитшърт',
    'DUFFEL GRIP DRUM': 'Чанта',
    'FOOTIE SOCK': 'Чорапи',
    'WAIST LENGTH JKT': 'Яке',
    'ANKLE LENGTH TIGHT': 'Клин',
    'HIP LENGTH HOODED VEST': 'Елек',
    'SMALL ITEMS WAISTPACKS': 'Чанта',
    'BAG - WAISTPACK': 'Чанта',
    'HIP LENGTH VEST': 'Елек',
    'ANKLE LENGTH PANT': 'Панталон',
    'THIGH LENGTH HOODED JKT': 'Яке',
    'HIP LENGTH JKT': 'Яке',
    'NO SHOW SOCK': 'Чорапи',
    'BACKPACK': 'Раница',
    'SHORT SLEEVE POLO': 'Тенска поло',
    'CLUB BAG': 'Чанта',
    'ONE QUARTER SOCK': 'Чорапи',
    'BRA': 'Бюстие',
    'SHORT': 'Къс панталон',
    'TANK TOP/SINGLET': 'Бюстие',
    'ADJUSTABLE CAP': 'Шапка',
    'WARM UP': 'Екип',
    'SHINGUARD': 'Предпазни кори',
    'MID THIGH LENGTH TIGHT': 'Къс панталон',
    'BUCKET HAT': 'Шапка',
    'MID SHORT W MID TGH TGT': 'Къс панталон',
    'UPPER SHORT W UPP TGH TGT': 'Къс панталон',
    'UPPER THIGH LENGTH TIGHT': 'Тениска',
    'UNITARD/LEOTARD': 'Боди',
    'WAIST LENGTH HOODED JKT': 'Яке',
    'BEANIE': 'Шапка',
    'KNIT TOP': 'Жилетка',
    'ONE-QUARTER SOCK': 'Чорапи',
    'TWO PIECE SET': 'Комплект',
    'S/S TEE': 'Тениска',
    'BOXER/BRIEF': 'Боксерки',
    'FRENCH TERRY SET': 'Комплект',
    'LEGGING SET': 'Комплект',
    '3PK CREW SOCK': 'Чорапи',
    'TRICOT SET': 'Комплект',
    'DRI-FIT SHORT': 'Къс панталон',
    'TANK TOP': 'Потник',
    'KNIT SHORT SET': 'Спортен екип',
    'ONE PIECE': 'Къс гащеризон',
    'MID SHORT W KNEE TGT': 'Къс панталон',
    'UPPER SHORT W MID TGH TGT': 'Къс панталон',
    'G NP DF TANK': 'Потник',
}

# Price points commerciali
PRICE_POINTS = [
    5, 9, 15, 19, 25, 29, 35, 39, 45, 49,
    55, 59, 65, 69, 75, 79, 85, 89, 95, 99,
    105, 109, 115, 119, 125, 129, 135, 139, 145, 149,
    155, 159, 165, 169, 175, 179, 185, 189, 195, 199,
    209, 219, 229, 239, 249, 259, 269, 279, 289, 299,
]

# Regole grammaticali bulgare per Категория_3
# (Категория_1, TIPO.BG) -> forma corretta
# Le regole dipendono dal genere grammaticale della parola bulgara:
#   - Maschile (м.р.): Мъжки/Дамски/Детски (суитшърт, панталон, клин, екип, елек, потник)
#   - Femminile (ж.р.): Мъжка/Дамска/Детска (тениска, риза, чанта, раница, жилетка, шапка)
#   - Neutro (ср.р.): Мъжко/Дамско/Детско (яке, бюстие, боди)
#   - Plurale (мн.ч.): Мъжки/Дамски/Детски (маратонки, кецове, чорапи, боксерки, сандали)

FEMININE_WORDS = {'тениска', 'риза', 'чанта', 'раница', 'жилетка', 'шапка'}
NEUTER_WORDS = {'яке', 'бюстие', 'боди'}
PLURAL_WORDS = {'маратонки', 'кецове', 'чорапи', 'боксерки', 'сандали', 'предпазни кори'}

GENDER_PREFIXES = {
    'Мъже': {'m': 'Мъжки', 'f': 'Мъжка', 'n': 'Мъжко', 'pl': 'Мъжки'},
    'Жени': {'m': 'Дамски', 'f': 'Дамска', 'n': 'Дамско', 'pl': 'Дамски'},
    'Деца': {'m': 'Детски', 'f': 'Детска', 'n': 'Детско', 'pl': 'Детски'},
    'Унисекс': {'m': 'Унисекс', 'f': 'Унисекс', 'n': 'Унисекс', 'pl': 'Унисекс'},
    'Момчета': {'m': 'Детски', 'f': 'Детска', 'n': 'Детско', 'pl': 'Детски'},
    'Момичета': {'m': 'Детски', 'f': 'Детска', 'n': 'Детско', 'pl': 'Детски'},
}


# ============================================================
# FUNZIONI
# ============================================================

def load_tipo_dictionary(uploaded_file):
    """Carica dizionario TIPO da un file Excel con foglio Traduzioni."""
    try:
        df_trad = pd.read_excel(uploaded_file, sheet_name='Traduzioni')
        # Colonna 0 = ARTICOLI (inglese), Colonna 12 = Unnamed:12 (bulgaro semplificato)
        mapping = {}
        for _, row in df_trad.iterrows():
            eng = row.iloc[0]  # ARTICOLI / INGLESE
            bg = row.iloc[12]  # Unnamed:12 / bulgaro semplificato
            if pd.notna(eng) and pd.notna(bg) and str(eng).strip() and str(bg).strip():
                eng_str = str(eng).strip()
                bg_str = str(bg).strip()
                if eng_str not in ('INGLESE', 'ARTICOLI') and bg_str != '0':
                    mapping[eng_str] = bg_str
        return mapping if mapping else None
    except Exception:
        return None


def round_to_price_point(value):
    """Arrotonda al price point commerciale piu vicino. Parita -> eccesso."""
    best = None
    best_diff = float('inf')
    for pp in PRICE_POINTS:
        diff = abs(pp - value)
        if diff < best_diff or (diff == best_diff and pp > best):
            best = pp
            best_diff = diff
    return best


def get_cat3_value(cat1, tipo_bg):
    """Genera Категория_3 con forma grammaticale corretta."""
    if pd.isna(cat1) or pd.isna(tipo_bg):
        return ''

    tipo_lower = str(tipo_bg).lower().strip()
    prefixes = GENDER_PREFIXES.get(cat1)
    if not prefixes:
        return f'{cat1} {tipo_bg}'

    if tipo_lower in FEMININE_WORDS:
        prefix = prefixes['f']
    elif tipo_lower in NEUTER_WORDS:
        prefix = prefixes['n']
    elif tipo_lower in PLURAL_WORDS:
        prefix = prefixes['pl']
    else:
        prefix = prefixes['m']  # default maschile

    return f'{prefix} {tipo_bg.lower()}'


def process_file(df, price_multiplier=1.8, tipo_map=None, brand="NIKE"):
    """Elabora il DataFrame con tutte le 22 trasformazioni."""

    if tipo_map is None:
        tipo_map = TIPO_MAP

    result = pd.DataFrame()

    # 1-10: Colonne base
    result['Cod+Color'] = df['Art.num']
    result['Cod.Nike'] = df['Code']
    result['Cod Color'] = df['Art.num'].astype(str).str.split('-', n=1).str[1]
    result['TAGLIA'] = df['SizeConverted']
    result['SKU Completo'] = df['Art.num'].astype(str) + '-' + df['SizeConverted'].astype(str)
    result['DESCRIZIONE'] = df['Description']
    result['STAG.'] = df['Season']
    result['BARCODE'] = df['Barcode']
    result['QTA'] = df['Dlv.qty']
    result['FPC Price w/o VAT in EUR'] = df['FPC Price w/o VAT in EUR'].round(2)

    # 11: PRZ DETT
    result['PRZ DETT'] = (df['FPC Price w/o VAT in EUR'] * price_multiplier).round(2)

    # 12: PREZZO NEGOZIO
    result['PREZZO NEGOZIO'] = result['PRZ DETT'].apply(round_to_price_point)

    # 13: BRAND
    result['BRAND'] = brand

    # 14-16: Colonne originali rinominate
    result['CATEGORIA'] = df['Division']
    result['GENERE'] = df['Gender']
    result['TIPO'] = df['Silhouette']

    # 17: CATEG.BG
    result['CATEG.BG'] = df['Division'].map(DIVISION_MAP)

    # 18: GEN.BG
    result['GEN.BG'] = df['Gender'].map(GENDER_MAP)

    # 19: TIPO.BG
    result['TIPO.BG'] = df['Silhouette'].map(tipo_map)

    # 20: Категория_1
    result['Категория_1'] = result['GEN.BG'].map(SESSO_MAP)

    # 21: Категория_2
    result['Категория_2'] = result.apply(
        lambda row: f"{CATEGORY2_PREFIX.get(row['Категория_1'], '')} {row['CATEG.BG']}"
        if pd.notna(row['Категория_1']) and pd.notna(row['CATEG.BG']) else '',
        axis=1
    )

    # 22: Категория_3
    result['Категория_3'] = result.apply(
        lambda row: get_cat3_value(row['Категория_1'], row['TIPO.BG']),
        axis=1
    )

    return result


def to_excel_bytes(df):
    """Converte DataFrame in bytes per il download."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Elaborato')
    return output.getvalue()


# ============================================================
# INTERFACCIA STREAMLIT
# ============================================================

st.title("Elaborazione File Nike")
st.markdown("Carica un file Excel di consegna, elaboralo e scarica il risultato.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configurazione")

    profile = st.selectbox(
        "Profilo elaborazione",
        ["Nike Ballistic"],
        help="Seleziona il profilo di trasformazione dati"
    )

    st.divider()

    price_multiplier = st.number_input(
        "Moltiplicatore prezzo (PRZ DETT)",
        min_value=1.0,
        max_value=5.0,
        value=1.8,
        step=0.1,
        help="Il prezzo FPC viene moltiplicato per questo valore"
    )

    brand_name = st.text_input(
        "Brand",
        value="NIKE",
        help="Nome del brand da inserire nella colonna BRAND"
    )

    st.divider()

    st.subheader("Dizionario traduzioni")
    dict_file = st.file_uploader(
        "Carica dizionario (opzionale)",
        type=['xlsx'],
        help="File Excel con foglio 'Traduzioni' per mappatura TIPO. Se non caricato, usa il dizionario integrato."
    )

    custom_tipo_map = None
    if dict_file is not None:
        custom_tipo_map = load_tipo_dictionary(dict_file)
        if custom_tipo_map:
            st.success(f"Dizionario caricato: {len(custom_tipo_map)} voci")
        else:
            st.warning("Impossibile leggere il dizionario. Uso dizionario integrato.")

    st.divider()
    st.caption("v1.0 - Elaborazione File Gensoft")

# --- AREA PRINCIPALE ---

uploaded_file = st.file_uploader(
    "Carica il file Excel da elaborare",
    type=['xlsx', 'xls'],
    help="File di consegna Nike/Ballistic con colonne: Art.num, Code, SizeConverted, ecc."
)

if uploaded_file is not None:
    # Leggi il file
    try:
        df_input = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
        st.stop()

    st.subheader("Anteprima file originale")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Righe", len(df_input))
    with col2:
        st.metric("Colonne", len(df_input.columns))

    with st.expander("Mostra anteprima dati originali", expanded=False):
        st.dataframe(df_input.head(10), use_container_width=True)

    # Verifica colonne necessarie
    required_cols = ['Art.num', 'Code', 'SizeConverted', 'Description', 'Season',
                     'Barcode', 'Dlv.qty', 'FPC Price w/o VAT in EUR',
                     'Division', 'Gender', 'Silhouette']
    missing_cols = [c for c in required_cols if c not in df_input.columns]

    if missing_cols:
        st.error(f"Colonne mancanti nel file: **{', '.join(missing_cols)}**")
        st.info(f"Colonne trovate: {', '.join(df_input.columns.tolist())}")
        st.stop()

    st.divider()

    # Pulsante elabora
    if st.button("Elabora File", type="primary", use_container_width=True):
        with st.spinner("Elaborazione in corso..."):
            tipo_map_to_use = custom_tipo_map if custom_tipo_map else TIPO_MAP

            df_output = process_file(
                df_input,
                price_multiplier=price_multiplier,
                tipo_map=tipo_map_to_use,
                brand=brand_name,
            )

            st.session_state['df_output'] = df_output
            st.session_state['elaborated'] = True

    # Mostra risultato
    if st.session_state.get('elaborated', False):
        df_output = st.session_state['df_output']

        st.subheader("Risultato elaborazione")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Righe", len(df_output))
        with col2:
            st.metric("Colonne", len(df_output.columns))
        with col3:
            # Conta valori mancanti
            missing_count = df_output.isna().sum().sum()
            unmapped_tipo = df_output['TIPO.BG'].isna().sum()
            unmapped_gen = df_output['GEN.BG'].isna().sum()
            if unmapped_tipo > 0 or unmapped_gen > 0:
                st.metric("Valori non mappati", f"TIPO: {unmapped_tipo}, GEN: {unmapped_gen}")
            else:
                st.metric("Stato", "Tutto mappato!")

        # Mostra valori non mappati se presenti
        if df_output['TIPO.BG'].isna().any():
            unmapped = df_output[df_output['TIPO.BG'].isna()]['TIPO'].unique()
            st.warning(f"TIPO non tradotti: **{', '.join(str(x) for x in unmapped)}**")

        if df_output['GEN.BG'].isna().any():
            unmapped = df_output[df_output['GEN.BG'].isna()]['GENERE'].unique()
            st.warning(f"GENERE non tradotti: **{', '.join(str(x) for x in unmapped)}**")

        with st.expander("Mostra anteprima risultato", expanded=True):
            st.dataframe(df_output.head(20), use_container_width=True)

        # Statistiche
        with st.expander("Statistiche"):
            tab1, tab2, tab3 = st.tabs(["Categorie", "Prezzi", "Genere"])
            with tab1:
                st.write("**CATEG.BG**")
                st.dataframe(df_output['CATEG.BG'].value_counts().reset_index())
                st.write("**Категория_1**")
                st.dataframe(df_output['Категория_1'].value_counts().reset_index())
            with tab2:
                st.write("**PREZZO NEGOZIO - distribuzione**")
                st.dataframe(df_output['PREZZO NEGOZIO'].value_counts().sort_index().reset_index())
            with tab3:
                st.write("**GEN.BG**")
                st.dataframe(df_output['GEN.BG'].value_counts().reset_index())

        st.divider()

        # Download
        timestamp = datetime.now().strftime("%d%m%Y_%H%M")
        filename = f"ELABORATO_{timestamp}.xlsx"

        excel_bytes = to_excel_bytes(df_output)

        st.download_button(
            label="Scarica File Elaborato",
            data=excel_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

else:
    st.info("Carica un file Excel per iniziare l'elaborazione.")

    # Mostra le colonne attese
    with st.expander("Colonne richieste nel file sorgente"):
        st.markdown("""
        Il file Excel deve contenere queste colonne:
        - **Art.num** - Codice articolo + colore (es: DA1028-502)
        - **Code** - Codice Nike (es: DA1028)
        - **SizeConverted** - Taglia convertita (es: S, M, L, XL)
        - **Description** - Descrizione prodotto
        - **Season** - Stagione
        - **Barcode** - Codice a barre
        - **Dlv.qty** - Quantita consegnata
        - **FPC Price w/o VAT in EUR** - Prezzo senza IVA
        - **Division** - Divisione (APP, FTW, EQU)
        - **Gender** - Genere
        - **Silhouette** - Tipo prodotto
        """)

    with st.expander("Colonne generate"):
        st.markdown("""
        L'elaborazione genera **22 colonne**:

        | # | Colonna | Origine |
        |---|---------|---------|
        | 1 | Cod+Color | Art.num |
        | 2 | Cod.Nike | Code |
        | 3 | Cod Color | parte dopo "-" di Art.num |
        | 4 | TAGLIA | SizeConverted |
        | 5 | SKU Completo | Art.num + "-" + SizeConverted |
        | 6 | DESCRIZIONE | Description |
        | 7 | STAG. | Season |
        | 8 | BARCODE | Barcode |
        | 9 | QTA | Dlv.qty |
        | 10 | FPC Price w/o VAT in EUR | stessa |
        | 11 | PRZ DETT | FPC Price x moltiplicatore |
        | 12 | PREZZO NEGOZIO | arrotondamento commerciale |
        | 13 | BRAND | Nike |
        | 14 | CATEGORIA | Division |
        | 15 | GENERE | Gender |
        | 16 | TIPO | Silhouette |
        | 17 | CATEG.BG | Division tradotto BG |
        | 18 | GEN.BG | Gender tradotto BG |
        | 19 | TIPO.BG | Silhouette tradotto BG |
        | 20 | Категория_1 | Raggruppamento genere |
        | 21 | Категория_2 | Prefisso genere + Categoria |
        | 22 | Категория_3 | Prefisso grammaticale + Tipo |
        """)
