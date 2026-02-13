import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ============================================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# ============================================================
st.set_page_config(
    page_title="Обработка на файлове Nike",
    page_icon="👟",
    layout="wide",
)

# ============================================================
# РЕЧНИЦИ
# ============================================================

# Division -> Категория BG
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

# Категория_1 -> префикс за Категория_2
CATEGORY2_PREFIX = {
    'Мъже': 'Мъжки',
    'Жени': 'Дамски',
    'Деца': 'Детски',
    'Унисекс': 'Унисекс',
    'Момчета': 'Детски',
    'Момичета': 'Детски',
}

# TIPO (Silhouette EN) -> TIPO.BG (вграден речник от SOFIA Traduzioni)
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

# Търговски ценови точки
PRICE_POINTS = [
    5, 9, 15, 19, 25, 29, 35, 39, 45, 49,
    55, 59, 65, 69, 75, 79, 85, 89, 95, 99,
    105, 109, 115, 119, 125, 129, 135, 139, 145, 149,
    155, 159, 165, 169, 175, 179, 185, 189, 195, 199,
    209, 219, 229, 239, 249, 259, 269, 279, 289, 299,
]

# Граматически правила за български за Категория_3
#   - Мъжки род (м.р.): Мъжки/Дамски/Детски (суитшърт, панталон, клин, екип, елек, потник)
#   - Женски род (ж.р.): Мъжка/Дамска/Детска (тениска, риза, чанта, раница, жилетка, шапка)
#   - Среден род (ср.р.): Мъжко/Дамско/Детско (яке, бюстие, боди)
#   - Множествено число (мн.ч.): Мъжки/Дамски/Детски (маратонки, кецове, чорапи, боксерки, сандали)

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
# ФУНКЦИИ
# ============================================================

def load_tipo_dictionary(uploaded_file):
    """Зарежда речник TIPO от Excel файл с лист Traduzioni.
    Поддържа два формата:
    - Опростен формат: 3 колони (Inglese, Bulgaro intermedio, Bulgaro)
    - SOFIA формат: 13+ колони (ARTICOLI, ..., колона 12 = опростен български)
    """
    try:
        df_trad = pd.read_excel(uploaded_file, sheet_name='Traduzioni')
        mapping = {}
        num_cols = len(df_trad.columns)

        for _, row in df_trad.iterrows():
            eng = row.iloc[0]  # Първа колона = английски

            if num_cols >= 13:
                # SOFIA формат: използва колона 12 (опростен български)
                bg = row.iloc[12]
            elif num_cols >= 3:
                # Опростен формат: използва последната колона (Bulgaro)
                bg = row.iloc[num_cols - 1]
            else:
                continue

            if pd.notna(eng) and pd.notna(bg) and str(eng).strip() and str(bg).strip():
                eng_str = str(eng).strip()
                bg_str = str(bg).strip()
                if eng_str not in ('INGLESE', 'ARTICOLI', 'Inglese') and bg_str != '0':
                    mapping[eng_str] = bg_str

        return mapping if mapping else None
    except Exception:
        return None


def round_to_price_point(value):
    """Закръгля до най-близката търговска ценова точка. При равенство -> нагоре."""
    best = None
    best_diff = float('inf')
    for pp in PRICE_POINTS:
        diff = abs(pp - value)
        if diff < best_diff or (diff == best_diff and pp > best):
            best = pp
            best_diff = diff
    return best


def get_cat3_value(cat1, tipo_bg):
    """Генерира Категория_3 с правилна граматическа форма."""
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
        prefix = prefixes['m']  # по подразбиране мъжки род

    return f'{prefix} {tipo_bg.lower()}'


def process_file(df, price_multiplier=1.8, tipo_map=None, brand="NIKE"):
    """Обработва DataFrame с всички 23 трансформации."""

    if tipo_map is None:
        tipo_map = TIPO_MAP

    result = pd.DataFrame()

    # 1-10: Основни колони
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

    # 14-16: Оригинални колони преименувани
    result['CATEGORIA'] = df['Division']
    result['GENERE'] = df['Gender']
    result['TIPO'] = df['Silhouette']

    # 17: CATEG.BG
    result['CATEG.BG'] = df['Division'].map(DIVISION_MAP)

    # NEW: Група = BRAND + CATEG.BG (Uppercase)
    result['Група'] = (
        result['BRAND'].fillna('').astype(str) + ' ' +
        result['CATEG.BG'].fillna('').astype(str)
    ).str.upper().str.strip()

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

    # 23: Site Description = Категория_3 + Brand + DESCRIZIONE
    result['Site Description'] = (
        result['Категория_3'].fillna('').astype(str) + ' ' +
        result['BRAND'].fillna('').astype(str) + ' ' +
        result['DESCRIZIONE'].fillna('').astype(str)
    ).str.strip()

    return result


def to_excel_bytes(df, sheet_name='Sheet1'):
    """Конвертира DataFrame в bytes за изтегляне.
    Специална обработка за MultiIndex хедъри при index=False.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if isinstance(df.columns, pd.MultiIndex):
            # Запис на MultiIndex хедърите ръчно, тъй като pandas има бъг с index=False
            # Ред 1: Titles (numeric IDs)
            # Ред 2: Subtitles (Bulgarian names)
            header_df = pd.DataFrame(df.columns.tolist()).T
            header_df.to_excel(writer, index=False, header=False, sheet_name=sheet_name)
            # Запис на данните от ред 3
            df.to_excel(writer, index=False, header=False, sheet_name=sheet_name, startrow=2)
        else:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


# ============================================================
# ИНТЕРФЕЙС STREAMLIT
# ============================================================

st.title("Обработка на файлове Nike")
st.markdown("Качете Excel файл за доставка, обработете го и изтеглете резултата.")

# --- СТРАНИЧНА ЛЕНТА ---
with st.sidebar:
    st.header("Настройки")

    profile = st.selectbox(
        "Профил на обработка",
        ["Nike Ballistic"],
        help="Изберете профил за трансформация на данни"
    )

    st.divider()

    price_multiplier = st.number_input(
        "Множител на цена (PRZ DETT)",
        min_value=1.0,
        max_value=5.0,
        value=1.8,
        step=0.1,
        help="Цената FPC се умножава по тази стойност"
    )

    brand_name = st.text_input(
        "Марка",
        value="NIKE",
        help="Име на марката за колона BRAND"
    )

    warehouse_name = st.text_input(
        "Склад (за Import Gensoft)",
        value="",
        placeholder="Въведете склад..."
    )

    supplier_name = st.text_input(
        "Доставчик (за Import Gensoft)",
        value="",
        placeholder="Въведете доставчик..."
    )

    st.divider()

    st.subheader("Речник за преводи")
    dict_file = st.file_uploader(
        "Качете речник (по избор)",
        type=['xlsx'],
        help="Excel файл с лист 'Traduzioni' за съпоставяне на TIPO. Ако не е качен, се използва вграденият речник."
    )

    custom_tipo_map = None
    if dict_file is not None:
        custom_tipo_map = load_tipo_dictionary(dict_file)
        if custom_tipo_map:
            st.success(f"Речникът е зареден: {len(custom_tipo_map)} записа")
        else:
            st.warning("Не може да се прочете речникът. Използва се вграденият речник.")

    st.divider()
    st.caption("v1.0 - Обработка на файлове Gensoft")

# --- ОСНОВНА ОБЛАСТ ---

uploaded_file = st.file_uploader(
    "Качете Excel файл за обработка",
    type=['xlsx', 'xls'],
    help="Файл за доставка Nike/Ballistic с колони: Art.num, Code, SizeConverted и др."
)

if uploaded_file is not None:
    # Четене на файла
    try:
        df_input = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Грешка при четене на файла: {e}")
        st.stop()

    st.subheader("Преглед на оригиналния файл")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Редове", len(df_input))
    with col2:
        st.metric("Колони", len(df_input.columns))

    with st.expander("Покажи преглед на оригиналните данни", expanded=False):
        st.dataframe(df_input.head(10), use_container_width=True)

    # Проверка на необходимите колони
    required_cols = ['Art.num', 'Code', 'SizeConverted', 'Description', 'Season',
                     'Barcode', 'Dlv.qty', 'FPC Price w/o VAT in EUR',
                     'Division', 'Gender', 'Silhouette']
    missing_cols = [c for c in required_cols if c not in df_input.columns]

    if missing_cols:
        st.error(f"Липсващи колони във файла: **{', '.join(missing_cols)}**")
        st.info(f"Намерени колони: {', '.join(df_input.columns.tolist())}")
        st.stop()

    st.divider()

    # Бутон за обработка
    if st.button("Обработи файла", type="primary", use_container_width=True):
        with st.spinner("Обработка в ход..."):
            tipo_map_to_use = custom_tipo_map if custom_tipo_map else TIPO_MAP

            df_output = process_file(
                df_input,
                price_multiplier=price_multiplier,
                tipo_map=tipo_map_to_use,
                brand=brand_name,
            )

            st.session_state['df_output'] = df_output
            st.session_state['elaborated'] = True

    # Показване на резултата
    if st.session_state.get('elaborated', False):
        df_output = st.session_state['df_output']

        st.subheader("Резултат от обработката")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Редове", len(df_output))
        with col2:
            st.metric("Колони", len(df_output.columns))
        with col3:
            # Брой липсващи стойности
            missing_count = df_output.isna().sum().sum()
            unmapped_tipo = df_output['TIPO.BG'].isna().sum()
            unmapped_gen = df_output['GEN.BG'].isna().sum()
            if unmapped_tipo > 0 or unmapped_gen > 0:
                st.metric("Несъпоставени стойности", f"TIPO: {unmapped_tipo}, GEN: {unmapped_gen}")
            else:
                st.metric("Статус", "Всичко е съпоставено!")

        # Показване на несъпоставени стойности
        if df_output['TIPO.BG'].isna().any():
            unmapped = df_output[df_output['TIPO.BG'].isna()]['TIPO'].unique()
            st.warning(f"Непреведени TIPO: **{', '.join(str(x) for x in unmapped)}**")

        if df_output['GEN.BG'].isna().any():
            unmapped = df_output[df_output['GEN.BG'].isna()]['GENERE'].unique()
            st.warning(f"Непреведени GENERE: **{', '.join(str(x) for x in unmapped)}**")

        with st.expander("Покажи преглед на резултата", expanded=True):
            st.dataframe(df_output.head(20), use_container_width=True)

        # Статистики
        with st.expander("Статистики"):
            tab1, tab2, tab3 = st.tabs(["Категории", "Цени", "Пол"])
            with tab1:
                st.write("**CATEG.BG**")
                st.dataframe(df_output['CATEG.BG'].value_counts().reset_index())
                st.write("**Категория_1**")
                st.dataframe(df_output['Категория_1'].value_counts().reset_index())
            with tab2:
                st.write("**PREZZO NEGOZIO - разпределение**")
                st.dataframe(df_output['PREZZO NEGOZIO'].value_counts().sort_index().reset_index())
            with tab3:
                st.write("**GEN.BG**")
                st.dataframe(df_output['GEN.BG'].value_counts().reset_index())

        st.divider()

        # Изтегляне
        data = datetime.now().strftime("%d%m%Y")
        filename = f"Elaborato_({data}).xlsx"

        excel_bytes = to_excel_bytes(df_output)

        col_dl1, col_dl2 = st.columns(2)
        col_dl3, col_dl4 = st.columns(2)

        with col_dl1:
            st.download_button(
                label="Изтегли обработен файл",
                data=excel_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )

        # --- ОПАКОВЪЧЕН ЛИСТ ---
        df_packing = df_output.groupby('Cod+Color', sort=False).agg(
            DESCRIZIONE=('DESCRIZIONE', 'first'),
            CATEG_BG=('CATEG.BG', 'first'),
            QTA=('QTA', 'sum'),
            PREZZO_NEGOZIO=('PREZZO NEGOZIO', 'first'),
        ).reset_index()

        # Добави ред с тотал в края
        packing_total_row = pd.DataFrame({
            'Cod+Color': ['TOTALE'],
            'DESCRIZIONE': [''],
            'CATEG_BG': [''],
            'QTA': [df_packing['QTA'].sum()],
            'PREZZO_NEGOZIO': ['']
        })
        df_packing = pd.concat([df_packing, packing_total_row], ignore_index=True)

        # Преименуване на колони на български
        df_packing = df_packing.rename(columns={
            'Cod+Color': 'Код',
            'DESCRIZIONE': 'Описание',
            'CATEG_BG': 'Категория',
            'QTA': 'Колич.',
            'PREZZO_NEGOZIO': 'Цена',
        })

        packing_bytes = to_excel_bytes(df_packing)
        packing_filename = f"Packing_list_({data}).xlsx"

        with col_dl2:
            st.download_button(
                label="Изтегли Packing List",
                data=packing_bytes,
                file_name=packing_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="secondary",
                use_container_width=True,
            )

        # --- ОПАКОВЪЧЕН ЛИСТ ДЕТАЙЛЕН ---
        df_packing_dett = df_output.groupby(['Cod.Nike', 'Cod Color', 'TAGLIA'], sort=False).agg(
            DESCRIZIONE=('DESCRIZIONE', 'first'),
            CATEG_BG=('CATEG.BG', 'first'),
            QTA=('QTA', 'sum'),
            PREZZO_NEGOZIO=('PREZZO NEGOZIO', 'first'),
        ).reset_index()

        # Добави ред с тотал в края
        total_row = pd.DataFrame({
            'Cod.Nike': ['TOTALE'],
            'Cod Color': [''],
            'TAGLIA': [''],
            'DESCRIZIONE': [''],
            'CATEG_BG': [''],
            'QTA': [df_packing_dett['QTA'].sum()],
            'PREZZO_NEGOZIO': ['']
        })
        df_packing_dett = pd.concat([df_packing_dett, total_row], ignore_index=True)

        # Преименуване на колони на български за детайлния списък
        df_packing_dett = df_packing_dett.rename(columns={
            'Cod.Nike': 'КОД',
            'Cod Color': 'Цвят',
            'TAGLIA': 'Размер',
            'DESCRIZIONE': 'Описание',
            'CATEG_BG': 'Категория',
            'QTA': 'Колич.',
            'PREZZO_NEGOZIO': 'Цена'
        })

        packing_dett_bytes = to_excel_bytes(df_packing_dett)
        packing_dett_filename = f"Packing_list_dett_({data}).xlsx"

        with col_dl3:
            st.download_button(
                label="Изтегли Packing List Детайлен",
                data=packing_dett_bytes,
                file_name=packing_dett_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="secondary",
                use_container_width=True,
            )

        # --- IMPORT GENSOFT ---
        # Дефиниране на данни за новата структура с два реда хедър (ID и Име)
        gensoft_data = {
            ("", "Склад"): [warehouse_name] * len(df_output),
            ("", "Главна група"): df_output['BRAND'],
            ("", "Група"): df_output['Група'],
            ("", "Стока"): df_output['Cod.Nike'],
            ("", "Сер./парт. номер"): df_output['BARCODE'],
            ("", "Код на стока"): df_output['Site Description'],
            ("", "Баркод на стока"): "",
            ("", "Мярка"): "бр.",
            ("", "Количество"): df_output['QTA'],
            ("", "Доставна цена"): df_output['FPC Price w/o VAT in EUR'],
            ("", "Доставна валута"): "eur",
            ("", "Цена на дребно"): df_output['PREZZO NEGOZIO'],
            ("", "Валута на дребно"): "eur",
            ("", "Доставчик"): [supplier_name] * len(df_output),
            ("", "К-во за поръчване"): df_output['QTA'],
            ("", "Цена"): df_output['FPC Price w/o VAT in EUR'],
            ("", "Валута"): "eur",
            ("", "Бележка"): df_output['Cod+Color'],
            ("", "Активна"): "Y",
            ("", "Активна за Web"): "Y",
            ("", "Ограничения в сметки"): "без ограничения",
            ("", "Процент ДДС"): "",
            # Нови колони с ID-та
            ("14", "Размер сайт"): df_output['TAGLIA'],
            ("107", "Цвят сайт"): df_output['Cod Color'],
            ("13", "SKU"): df_output['SKU Completo'],
            ("109", "Категория 1"): df_output['Категория_1'],
            ("110", "Категория 2"): df_output['Категория_2'],
            ("111", "Категория 3"): df_output['Категория_3'],
            ("15", "Бранд"): df_output['BRAND'],
            ("2", "Пол"): df_output['GEN.BG'],
            ("5", "Категория"): df_output['CATEG.BG'],
            ("6", "Сезон"): df_output['STAG.'],
            ("108", "Цена срв. сайт"): df_output['PREZZO NEGOZIO'],
            ("113", "Код таблица за размери"): "",
            ("103", "Доствчик"): [supplier_name] * len(df_output),
        }

        df_gensoft = pd.DataFrame(gensoft_data)
        # Настройка на MultiIndex колони
        df_gensoft.columns = pd.MultiIndex.from_tuples(df_gensoft.columns)

        gensoft_bytes = to_excel_bytes(df_gensoft)
        gensoft_filename = f"Import_Gensoft_({data}).xlsx"

        with col_dl4:
            st.download_button(
                label="Изтегли Import Gensoft",
                data=gensoft_bytes,
                file_name=gensoft_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="secondary",
                use_container_width=True,
            )

        # Преглед на Packing List
        with st.expander("Преглед на Packing List"):
            st.dataframe(df_packing, use_container_width=True)

        # Преглед на Packing List Детайлен
        with st.expander("Преглед на Packing List Детайлен"):
            st.dataframe(df_packing_dett, use_container_width=True)

        # Преглед на Import Gensoft
        with st.expander("Преглед на Import Gensoft"):
            # Флатване на MultiIndex за преглед в Streamlit (за избягване на грешки в дисплея)
            df_gensoft_preview = df_gensoft.copy()
            if isinstance(df_gensoft_preview.columns, pd.MultiIndex):
                df_gensoft_preview.columns = [
                    f"{col[0]} {col[1]}".strip() if col[0] else col[1] 
                    for col in df_gensoft_preview.columns
                ]
            st.dataframe(df_gensoft_preview, use_container_width=True)

else:
    st.info("Качете Excel файл, за да започнете обработката.")

    # ============================================================
    # ДОКУМЕНТАЦИЯ / ПОМОЩ
    # ============================================================
    st.divider()
    col_help1, col_help2 = st.columns(2)

    with col_help1:
        with st.expander("Необходими колони в оригиналния файл"):
            st.markdown("""
            Файлът трябва да съдържа следните колони (имена от оригиналния Ballistic файл):
            - `Art.num`
            - `Code`
            - `SizeConverted`
            - `Description`
            - `Season`
            - `Barcode`
            - `Dlv.qty`
            - `FPC Price w/o VAT in EUR`
            - `Division`
            - `Gender`
            - `Silhouette`
            """)

    with col_help2:
        with st.expander("Генерирани колони (Elaborato)"):
            st.markdown("""
            Обработката генерира **24 колони**:

            | # | Колона | Източник |
            |---|--------|----------|
            | 1 | Cod+Color | Art.num |
            | 2 | Cod.Nike | Code |
            | 3 | Cod Color | частта след "-" от Art.num |
            | 4 | TAGLIA | SizeConverted |
            | 5 | SKU Completo | Art.num + "-" + SizeConverted |
            | 6 | DESCRIZIONE | Description |
            | 7 | STAG. | Season |
            | 8 | BARCODE | Barcode |
            | 9 | QTA | Dlv.qty |
            | 10 | FPC Price w/o VAT in EUR | същата |
            | 11 | PRZ DETT | FPC Price x множител |
            | 12 | PREZZO NEGOZIO | търговско закръгляне |
            | 13 | BRAND | Nike |
            | 14 | CATEGORIA | Division |
            | 15 | GENERE | Gender |
            | 16 | TIPO | Silhouette |
            | 17 | CATEG.BG | Division преведено на БГ |
            | 18 | Група | Brand + CATEG.BG (главни букви) |
            | 19 | GEN.BG | Gender преведено на БГ |
            | 20 | TIPO.BG | Silhouette преведено на БГ |
            | 21 | Категория_1 | Групиране по пол |
            | 22 | Категория_2 | Префикс пол + Категория |
            | 23 | Категория_3 | Граматически префикс + Тип |
            | 24 | Site Description | Категория_3 + Brand + Описание |
            """)

    with st.expander("Описание на файловете за изтегляне"):
        st.markdown("""
        1. **Обработен файл (Elaborato)**: Пълният списък с всички 24 трансформации.
        2. **Packing List**: Обобщен по артикул и цвят.
        3. **Packing List Детайлен**: Обобщен по артикул, цвят и размер, с преведени колони.
        4. **Import Gensoft**: Специален формат за директен импорт в Gensoft, използващ мануалните полета от настройките.
        """)
