import streamlit as st
import pandas as pd
import io
import json
import os
from datetime import datetime

# ============================================================
# КОНФИГУРАЦИЯ НА ПРОФИЛИ
# ============================================================
PROFILES = {
    "Nike Ballistic": {
        "columns": {
            "art_num": "Art.num",
            "code": "Code",
            "size": "SizeConverted",
            "description": "Description",
            "season": "Season",
            "barcode": "Barcode",
            "qta": "Dlv.qty",
            "price_eur": "FPC Price w/o VAT in EUR",
            "division": "Division",
            "gender": "Gender",
            "silhouette": "Silhouette",
        },
        "defaults": {
            "brand": "NIKE",
            "price_multiplier": 1.8
        }
    },
    "New Balance Ballistic": {
        "columns": {
            "art_num": "STOCKNO+COLORNAME",
            "code": "STOCKNO",
            "color": "COLORNAME",
            "size": "SIZENAME",
            "description": "NAME",
            "season": "season",
            "barcode": "BARCODE",
            "qta": "QTY",
            "price_eur": "WPRICE",
            "division": "CATEGORY",
            "gender": "SEX",
            "silhouette": "GROUP",
            "cod_color": "COLORNAME",
        },
        "defaults": {
            "brand": "NEW BALANCE",
            "price_multiplier": 1.8
        }
    },
    "On Ballistic": {
        "columns": {
            "art_num": "Article Number",
            "size": "Size",
            "description": "Item Name",
            "season": "Season",
            "barcode": "GTIN",
            "qta": "Qty",
            "price_eur": "Cost EUR",
            "division": "Product Group",
            "gender": "Sex",
            "silhouette": "Silouette",
            "cod_nike": "Vendor Item No.",
            "cod_color": "Color",
        },
        "defaults": {
            "brand": "ON",
            "price_multiplier": 1.8
        }
    },
    "ASICS Ballistic": {
        "columns": {
            "art_num": "Code+color",
            "code": "Стока",
            "size": "Сер.№/Партида",
            "description": "Код",
            "season": "Season",
            "barcode": "Баркод",
            "qta": "Количество",
            "price_eur": "Ед.цена",
            "division": "Категория",
            "gender": "Пол",
            "silhouette": "Тип",
            "cod_color": "Цвят",
            "rrp": "RRP",
        },
        "defaults": {
            "brand": "ASICS",
            "price_multiplier": 1.8
        }
    },
    "SPRAYGROUND Ballistic": {
        "columns": {
            "art_num": "CODE",
            "code": "CODE",
            "size": "Size",
            "description": "ARTICLE",
            "season": "season",
            "barcode": "UPC NUMBER",
            "qta": "Qty",
            "price_eur": "SELL IN",
            "division": "Categoria",
            "gender": "Genere",
            "silhouette": "Tipo",
            "cod_color": "Color",
        },
        "defaults": {
            "brand": "SPRAYGROUND",
            "price_multiplier": 2.0
        }
    },
    "General Ballistic": {
        "columns": {
            "art_num": "Model",
            "code": "Factory Code",
            "size": "Size",
            "description": "Item Name",
            "season": "Season",
            "barcode": "EAN",
            "qta": "Qty",
            "price_eur": "Price EUR",
            "division": "Category",
            "gender": "Gender",
            "silhouette": "Tipo",
        },
        "defaults": {
            "brand": "GENERAL",
            "price_multiplier": 2.0
        }
    }
}

CONFIG_FILE = "profile_mappings.json"

def load_persistent_configurations():
    """Зарежда персонализирани мапинги от JSON файл."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Грешка при зареждане на конфигурация: {e}")
    return {}

def save_persistent_configurations(configs):
    """Записва персонализирани мапинги в JSON файл."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(configs, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Грешка при запис на конфигурация: {e}")

# Инициализация на сесийното състояние с мапингите
if 'profile_configs' not in st.session_state:
    st.session_state['profile_configs'] = load_persistent_configurations()

# Гарантираме, че всички нови дефолтни ключове съществуват (пачване на стари сесии)
for p_name, p_data in PROFILES.items():
    if p_name not in st.session_state['profile_configs']:
        st.session_state['profile_configs'][p_name] = p_data['columns'].copy()
    else:
        # Добавяме липсващи ключове от новата версия на PROFILES
        for col_key, col_default in p_data['columns'].items():
            if col_key not in st.session_state['profile_configs'][p_name]:
                st.session_state['profile_configs'][p_name][col_key] = col_default
    # Гарантираме, че __price_multiplier__ съществува (добавяме ако липсва)
    if '__price_multiplier__' not in st.session_state['profile_configs'][p_name]:
        st.session_state['profile_configs'][p_name]['__price_multiplier__'] = p_data['defaults']['price_multiplier']
    # Per On Ballistic, rimuoviamo la chiave 'code' se presente (non usata)
    if p_name == "On Ballistic" and 'code' in st.session_state['profile_configs'][p_name]:
        del st.session_state['profile_configs'][p_name]['code']

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
    'APPAREL': 'Дрехи',
    'CLOTHES': 'Дрехи',
    'FTW': 'Обувки',
    'FOOTWEAR': 'Обувки',
    'SHOES': 'Обувки',
    'EQU': 'Аксесоари',
    'EQUIPMENT': 'Аксесоари',
    'ACCESSORIES': 'Аксесоари',
}

# Gender -> GEN.BG
GENDER_MAP = {
    'MENS': 'Мъже',
    'MEN': 'Мъже',
    'Men': 'Мъже',
    'men': 'Мъже',
    'MALE': 'Мъже',
    'Male': 'Мъже',
    'male': 'Мъже',
    'WOMENS': 'Жени',
    'WOMEN': 'Жени',
    'Women': 'Жени',
    'women': 'Жени',
    'FEMALE': 'Жени',
    'Female': 'Жени',
    'female': 'Жени',
    'GIRLS': 'Момичета',
    'BOYS': 'Момчета',
    'YOUTH UNISEX': 'Юноши Унисекс',
    'INFANT UNISEX': 'Бебета Унисекс',
    'ADULT UNISEX': 'Възрастни Унисекс',
    'CHILD UNISEX': 'Деца унисекс',
    'UNISEX': 'Унисекс',
    'Unisex': 'Унисекс',
    'unisex': 'Унисекс',
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
    'KIDS BOY': 'Деца',
    'KIDS GIRL': 'Деца',
    'KIDS UNISEX': 'Деца',
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
    'Деца': 'Деца',
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
    'CLASSIC RUNNING': 'Маратонки',
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

# Punti di prezzo commerciali
PRICE_POINTS = [
    5, 9, 15, 19, 25, 29, 35, 39, 45, 49,
    55, 59, 65, 69, 75, 79, 85, 89, 95, 99,
    105, 109, 115, 119, 125, 129, 135, 139, 145, 149,
    155, 159, 165, 169, 175, 179, 185, 189, 195, 199,
    209, 219, 229, 239, 249, 259, 269, 279, 289, 299,
]

# Regole grammaticali per la lingua bulgara
FEMININE_WORDS = {'тениска', 'риза', 'чанта', 'раница', 'жилетка', 'шапка'}
NEUTER_WORDS = {'яке', 'бюстие', 'боди'}
PLURAL_WORDS = {'маратонки', 'кецове', 'чорапи', 'боксерки', 'сандали', 'предпазни кори'}

# Prefissi di genere per il bulgaro
GENDER_PREFIXES = {
    'Мъже': {'m': 'Мъжки', 'f': 'Мъжка', 'n': 'Мъжко', 'pl': 'Мъжки'},
    'Жени': {'m': 'Дамски', 'f': 'Дамска', 'n': 'Дамско', 'pl': 'Дамски'},
    'Деца': {'m': 'Детски', 'f': 'Детска', 'n': 'Детско', 'pl': 'Детски'},
    'Унисекс': {'m': 'Унисекс', 'f': 'Унисекс', 'n': 'Унисекс', 'pl': 'Унисекс'},
    'Момчета': {'m': 'Детски', 'f': 'Детска', 'n': 'Детско', 'pl': 'Детски'},
    'Момичета': {'m': 'Детски', 'f': 'Детска', 'n': 'Детско', 'pl': 'Детски'},
}


def scrivi_log(messaggio):
    """Scrive un messaggio di errore nel file di log 'output/log.txt'.
    Crea la cartella 'output' se non esiste già.
    """
    try:
        # Crea la cartella 'output' se non esiste nel percorso corrente
        os.makedirs("output", exist_ok=True)
        # Ottiene la data e l'ora corrente nel formato standard
        ora_corrente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Apre il file log.txt in modalità 'append' per aggiungere testo in coda
        with open("output/log.txt", "a", encoding="utf-8") as file_log:
            # Scrive l'errore registrando il momento esatto in cui è avvenuto
            file_log.write(f"[{ora_corrente}] {messaggio}\n")
    except Exception as errore:
        # In caso di errore nella scrittura del log, lo stampa sulla console di Streamlit
        print(f"Impossibile scrivere il log: {errore}")


def load_tipo_dictionary(uploaded_file):
    """Зарежда речник TIPO от Excel файл с лист Traduzioni.
    Поддържа два формата:
    - Опростен формат: 3 колони (Inglese, Bulgaro intermedio, Bulgaro)
    - SOFIA формат: 13+ колони (ARTICOLI, ..., колона 12 = опростен български)
    """
    try:
        # Carica il file Excel usando la libreria pandas
        df_trad = pd.read_excel(uploaded_file, sheet_name='Traduzioni')
        # Inizializza un dizionario vuoto per salvare le traduzioni trovate
        mapping = {}
        # Salva il numero totale delle colonne nel foglio di calcolo
        num_cols = len(df_trad.columns)

        # Itera su ogni riga della tabella caricata
        for _, row in df_trad.iterrows():
            # Legge il valore della prima colonna come termine inglese
            eng = row.iloc[0]

            # Controlla se le colonne sono 13 o più (formato SOFIA)
            if num_cols >= 13:
                # Estrae il termine in bulgaro semplificato dalla colonna indice 12
                bg = row.iloc[12]
            # Se le colonne sono meno di 13 ma almeno 3 (formato semplificato)
            elif num_cols >= 3:
                # Prende il valore dall'ultima colonna della riga corrente
                bg = row.iloc[num_cols - 1]
            # In tutti gli altri casi passa direttamente al ciclo successivo
            else:
                continue

            # Verifica che entrambi i valori non siano vuoti o nulli
            if pd.notna(eng) and pd.notna(bg) and str(eng).strip() and str(bg).strip():
                # Rimuove eventuali spazi vuoti all'inizio o alla fine del termine inglese
                eng_str = str(eng).strip()
                # Rimuove eventuali spazi vuoti all'inizio o alla fine del termine bulgaro
                bg_str = str(bg).strip()
                # Esclude le righe di intestazione standard o i valori non validi (pari a '0')
                if eng_str not in ('INGLESE', 'ARTICOLI', 'Inglese') and bg_str != '0':
                    # Aggiunge la traduzione corretta al dizionario di corrispondenza
                    mapping[eng_str] = bg_str

        # Restituisce il dizionario se contiene elementi, altrimenti ritorna None
        return mapping if mapping else None
    except Exception as errore:
        # Registra l'errore avvenuto nel file di log per il tracciamento delle anomalie
        scrivi_log(f"Errore nel caricamento del dizionario dei tipi: {errore}")
        # Ritorna None in caso di eccezione per non bloccare il caricamento dell'app
        return None


def load_size_table(uploaded_file):
    """Зарежда таблица за размери (Size Table) от Excel файл.
    Пробва първо лист 'Size_table', ако не съществува - първия наличен.
    Очаквани колони: 'brand', 'div', 'style', 'size_table'.
    """
    try:
        # Inizializza l'oggetto ExcelFile per esplorare le caratteristiche del documento Excel
        excel_file = pd.ExcelFile(uploaded_file)
        # Sceglie il foglio specifico 'Size_table' se esiste, altrimenti usa il primo foglio utile
        sheet_name = 'Size_table' if 'Size_table' in excel_file.sheet_names else excel_file.sheet_names[0]
        
        # Estrae i dati dal foglio selezionato senza consumare lo stream del file caricato
        df_size = excel_file.parse(sheet_name)
        # Prepara un dizionario vuoto per memorizzare le relazioni delle taglie
        mapping = {}
        
        # Trasforma i nomi di tutte le colonne in lettere minuscole e ne rimuove gli spazi
        cols_lower = {str(c).lower().strip(): c for c in df_size.columns}
        
        # Cerca la colonna del brand (supportando anche le versioni scritte in caratteri cirillici)
        brand_col = cols_lower.get('brand') or cols_lower.get('бранд')
        # Cerca la colonna della divisione commerciale (es: APP, FTW, Categoria, ecc.)
        div_col = cols_lower.get('categoria') or cols_lower.get('div') or cols_lower.get('дивизия') or cols_lower.get('divisiya')
        # Identifica la colonna con lo stile (corrispondente al Genere/Gender originale del prodotto)
        style_col = cols_lower.get('genere') or cols_lower.get('style') or cols_lower.get('стил') or cols_lower.get('stil')
        # Identifica la colonna del codice finale della tabella delle taglie
        code_col = cols_lower.get('size_table') or cols_lower.get('код') or cols_lower.get('size code')
        
        # Se non si trovano le intestazioni corrette per le colonne necessarie, usa la posizione
        if not (brand_col and style_col and code_col):
            # Procede solo se sono presenti almeno 3 colonne totali nella tabella
            if len(df_size.columns) >= 3:
                # Imposta la prima colonna (indice 0) per il Brand del prodotto
                brand_col = df_size.columns[0]
                # Se sono presenti 4 colonne, assegna le posizioni per tutte le variabili
                if len(df_size.columns) >= 4:
                    div_col = df_size.columns[1]
                    style_col = df_size.columns[2]
                    code_col = df_size.columns[3]
                # Se ci sono solo 3 colonne, esclude la colonna della divisione (impostandola a None)
                else:
                    div_col = None
                    style_col = df_size.columns[1]
                    code_col = df_size.columns[2]
            # Se la tabella ha una struttura non idonea con meno di 3 colonne, ritorna None
            else:
                return None
        
        # Cicla riga per riga su tutti gli elementi del DataFrame caricato
        for _, row in df_size.iterrows():
            # Estrae la marca normalizzandola (spazi rimossi e lettere tutte maiuscole)
            b_val = str(row[brand_col]).strip().upper() if pd.notna(row[brand_col]) else ""
            # Estrae la divisione commerciale (es. APP o FTW) normalizzandola in maiuscolo
            d_val = str(row[div_col]).strip().upper() if div_col and pd.notna(row[div_col]) else ""
            # Estrae lo stile del genere del prodotto in maiuscolo (es. WOMENS, MENS, ecc.)
            s_val = str(row[style_col]).strip().upper() if pd.notna(row[style_col]) else ""
            # Estrae il codice corrispondente della tabella taglie (es. WANIKE, USNIKE)
            c_val = str(row[code_col]).strip() if pd.notna(row[code_col]) else ""
            
            # Filtra ed elimina le stringhe nule derivanti da celle vuote rappresentate come 'NAN'
            if b_val == "NAN": b_val = ""
            if d_val == "NAN": d_val = ""
            if s_val == "NAN": s_val = ""
            if c_val == "NAN": c_val = ""
            
            # Se i campi marca, stile e codice sono popolati correttamente, registra la taglia
            if b_val and s_val and c_val and b_val != 'BRAND':
                # Registra la chiave principale che comprende la divisione commerciale
                mapping[(b_val, d_val, s_val)] = c_val
                # Se esiste una divisione, registra una chiave di fallback con divisione vuota
                if d_val:
                    mapping[(b_val, "", s_val)] = c_val
                    
        # Restituisce il dizionario creato solo se contiene dati, altrimenti ritorna None
        return mapping if mapping else None
    except Exception as errore:
        # Invia l'errore rilevato al file di log centralizzato dell'applicazione
        scrivi_log(f"Errore nel caricamento della tabella delle taglie: {errore}")
        # Restituisce None per far proseguire l'esecuzione dell'app senza crash improvvisi
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


# Tabella conversione taglie US → EUR (scarpe ASICS)
US_TO_EUR_SIZE = {
    '3':    '35.5',
    '3.5':  '35.5',
    '4':    '36',
    '4.5':  '37',
    '5':    '37.5',
    '5.5':  '38',
    '6':    '38.5',
    '6.5':  '39.5',
    '7':    '40',
    '7.5':  '40.5',
    '8':    '41.5',
    '8.5':  '42',
    '9':    '42.5',
    '9.5':  '43.5',
    '10':   '44',
    '10.5': '44.5',
    '11':   '45',
    '11.5': '46',
    '12':   '46.5',
    '12.5': '47',
    '13':   '47.5',
    '13.5': '48',
    '14':   '48.5',
    '15':   '49.5',
    '16':   '51',
}

def convert_us_to_eur_size(val):
    """Converte taglia US in EUR. Ignora il suffisso di larghezza (es. M, W, D)."""
    s = str(val).strip()
    # Rimuove suffissi di larghezza: lettere alla fine (es. "10M" → "10", "8.5W" → "8.5")
    numeric = s.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz').strip()
    return US_TO_EUR_SIZE.get(numeric, s)


def converti_in_stringhe(serie):
    """Converte una serie di pandas in stringhe pulite.
    Gestisce i valori mancanti (NaN, None, pd.NA) convertendoli in stringhe vuote.
    
    Parametri:
    serie (pd.Series): La serie di input da convertire.
    
    Restituisce:
    pd.Series: La serie convertita in stringhe senza valori nulli o 'nan'/'<NA>'.
    """
    # Sostituisce i valori nulli con una stringa vuota ed esegue il cast a stringa
    serie_pulita = serie.fillna('').astype(str)
    # Rimuove le rappresentazioni testuali di valori nulli
    return serie_pulita.replace({'<NA>': '', 'nan': '', 'None': ''})



def get_cat3_value(cat1, tipo_bg):
    """Генерира Категория_3 с правилна граматическа форма."""
    if pd.isna(cat1) or pd.isna(tipo_bg):
        return ''

    tipo_lower = str(tipo_bg).lower().strip()
    prefixes = GENDER_PREFIXES.get(cat1)
    if not prefixes:
        return f'{cat1} {str(tipo_bg).strip().capitalize()}'

    if tipo_lower in FEMININE_WORDS:
        prefix = prefixes['f']
    elif tipo_lower in NEUTER_WORDS:
        prefix = prefixes['n']
    elif tipo_lower in PLURAL_WORDS:
        prefix = prefixes['pl']
    else:
        prefix = prefixes['m']  # по подразбиране мъжки род

    return f'{prefix} {str(tipo_bg).strip().capitalize()}'


def get_multi_col_data(df, col_spec, sep=" "):
    """Извлича данни от една или няколко колони (съединени с '+')."""
    if not col_spec:
        return pd.Series([""] * len(df))
    
    # Se il nome della colonna esiste direttamente nel DataFrame (es: "Code+color"),
    # lo utilizziamo direttamente senza dividere per il carattere '+'
    col_str = str(col_spec)
    if col_str in df.columns:
        return df[col_str]
    
    parts = [p.strip() for p in col_str.split('+')]
    valid_parts = [p for p in parts if p in df.columns]
    
    if not valid_parts:
        return pd.Series([""] * len(df))
    
    # Режим за една колона - запазваме оригиналния тип ако е възможно
    if len(valid_parts) == 1:
        return df[valid_parts[0]]
    
    # Режим за няколко колони - конкатенираме като низове
    combined = df[valid_parts[0]].astype(str)
    for p in valid_parts[1:]:
        combined = combined + sep + df[p].astype(str)
    
    return combined


def process_file(df, col_map, price_multiplier=1.8, tipo_map=None, brand="NIKE", profile_name="", size_map=None, season_override=""):
    """Обработва DataFrame с всички 24 трансформации."""

    if tipo_map is None:
        tipo_map = TIPO_MAP
    
    # Нормализираме речника на типовете към главни букви за по-добро съвпадение
    tipo_map_upper = {str(k).upper(): v for k, v in tipo_map.items()}

    result = pd.DataFrame()

    # Извличане на имена на колони от мапинга
    c_art = col_map.get('art_num', 'Art.num')
    c_code = col_map.get('code', 'Code')
    c_size = col_map.get('size', 'SizeConverted')
    c_desc = col_map.get('description', 'Description')
    c_stag = col_map.get('season', 'Season')
    c_bar = col_map.get('barcode', 'Barcode')
    c_qta = col_map.get('qta', 'Dlv.qty')
    c_price = col_map.get('price_eur', 'FPC Price w/o VAT in EUR')
    c_div = col_map.get('division', 'Division')
    c_gen = col_map.get('gender', 'Gender')
    c_tipo = col_map.get('silhouette', 'Silhouette')
    c_cod_color = col_map.get('cod_color', '')
    c_color = col_map.get('color', '')
    c_cod_nike = col_map.get('cod_nike', '')
    c_rrp = col_map.get('rrp', '')

    # Proверка за наличие на колони (включително мулти-колони)
    all_specified_cols = []
    # Per On Ballistic, c_code non viene usato (si usano c_cod_color e c_cod_nike al suo posto)
    # Per ASICS Ballistic, code e cod_color derivano dalla stessa colonna di art_num - non vanno validati separatamente
    if profile_name == "On Ballistic":
        check_list = [c_art, c_size, c_desc, c_stag, c_bar, c_qta, c_price, c_div, c_gen, c_tipo]
    else:
        # c_stag è opzionale: incluso solo se la colonna esiste nel file (può essere inserita manualmente)
        base = [c_art, c_code, c_size, c_desc, c_bar, c_qta, c_price, c_div, c_gen, c_tipo]
        check_list = base + ([c_stag] if c_stag and c_stag in df.columns else [])
    if c_cod_color:
        check_list.append(c_cod_color)
    if c_color:
        check_list.append(c_color)
    if c_cod_nike:
        check_list.append(c_cod_nike)
    if c_rrp:
        check_list.append(c_rrp)

    for spec in check_list:
        if spec:
            spec_str = str(spec)
            if spec_str in df.columns:
                all_specified_cols.append(spec_str)
            else:
                all_specified_cols.extend([p.strip() for p in spec_str.split('+')])

    missing_cols = [c for c in all_specified_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Липсващи колони в оригиналния (качения) файл: {', '.join(set(missing_cols))}")

    # 1-10: Основни колони
    if profile_name == "New Balance Ballistic":
        # Специална логика за New Balance
        result['Cod+Color'] = get_multi_col_data(df, c_art, sep="-")

        # Cod Color: priorità a 'color', poi 'cod_color', poi fallback a 'code'
        nb_color_source = c_color if c_color else (c_cod_color if c_cod_color else c_code)
        result['Cod Color'] = get_multi_col_data(df, nb_color_source)
    elif profile_name == "On Ballistic":
        # Cod Color взима данни от колоната мапната към cod_color (по подразбиране 'Color')
        result['Cod Color'] = get_multi_col_data(df, c_cod_color if c_cod_color else c_code)
        # Cod+Color = Vendor Item No. (c_cod_nike) + '-' + Color (c_cod_color)
        result['Cod+Color'] = get_multi_col_data(df, c_cod_nike).astype(str) + '-' + result['Cod Color'].astype(str)
    elif profile_name == "ASICS Ballistic":
        # Cod+Color = Code+color colonna letta direttamente
        result['Cod+Color'] = converti_in_stringhe(get_multi_col_data(df, c_art))
        # Cod Color = colonna Цвят letta direttamente
        cod_color_src = c_cod_color if c_cod_color else c_art
        result['Cod Color'] = converti_in_stringhe(get_multi_col_data(df, cod_color_src))
    elif profile_name == "SPRAYGROUND Ballistic":
        # Cod+Color = colonna "Code+Color" letta direttamente (il + è parte del nome colonna)
        if 'Code+Color' in df.columns:
            result['Cod+Color'] = df['Code+Color'].astype(str)
        else:
            result['Cod+Color'] = get_multi_col_data(df, c_art).astype(str)
        # Cod Color = colonna Color
        result['Cod Color'] = get_multi_col_data(df, c_cod_color).astype(str) if c_cod_color else pd.Series([''] * len(df))
    else:
        # Стандартна логика за Nike и други
        result['Cod+Color'] = get_multi_col_data(df, c_art, sep=" ")
        # Екстракция на цвят от артикулен номер (допускаме '-' като разделител в оригиналния Nike формат)
        art_data_raw = get_multi_col_data(df, c_art, sep="-")
        result['Cod Color'] = art_data_raw.astype(str).str.split('-', n=1).str[1]

    if profile_name == "On Ballistic":
        result['Cod.Nike'] = get_multi_col_data(df, c_cod_nike if c_cod_nike else 'Vendor Item No.')
    elif profile_name == "ASICS Ballistic":
        # Cod.Nike = Стока colonna letta direttamente
        result['Cod.Nike'] = converti_in_stringhe(get_multi_col_data(df, c_code))
    else:
        result['Cod.Nike'] = get_multi_col_data(df, c_code)
    taglia_raw = get_multi_col_data(df, c_size)
    if profile_name == "ASICS Ballistic":
        result['TAGLIA'] = converti_in_stringhe(taglia_raw).apply(convert_us_to_eur_size)
    else:
        result['TAGLIA'] = taglia_raw

    if profile_name in ["New Balance Ballistic", "On Ballistic", "ASICS Ballistic", "SPRAYGROUND Ballistic"]:
        result['SKU Completo'] = converti_in_stringhe(result['Cod+Color']) + '-' + converti_in_stringhe(result['TAGLIA'])
    else:
        # За Nike използваме оригиналния арт. номер без промяна на сепаратора за SKU
        art_orig = get_multi_col_data(df, c_art, sep="") 
        result['SKU Completo'] = converti_in_stringhe(art_orig) + '-' + converti_in_stringhe(result['TAGLIA'])
    result['DESCRIZIONE'] = get_multi_col_data(df, c_desc)
    if c_stag and c_stag in df.columns:
        result['STAG.'] = get_multi_col_data(df, c_stag)
    else:
        result['STAG.'] = season_override
    # Гарантираме, че BARCODE се чете като чист низ (без .0 ако е число)
    bar_raw = get_multi_col_data(df, c_bar)
    result['BARCODE'] = bar_raw.astype(str).str.replace(r'\.0$', '', regex=True)
    
    # Гарантираме, че QTA е число, за да работи сумирането
    qta_raw = get_multi_col_data(df, c_qta)
    result['QTA'] = pd.to_numeric(qta_raw, errors='coerce').fillna(0).astype(int)
    
    # За цената не поддържаме конкатенация, взимаме първата посочена колона
    price_col = [p.strip() for p in str(c_price).split('+')][0]
    price_raw = df[price_col]
    # Normalizza: sostituisce virgola con punto e converte in float (es. "61,5" → 61.5)
    if price_raw.dtype == object:
        price_raw = pd.to_numeric(
            price_raw.astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        ).fillna(0.0)
    result['FPC Price w/o VAT in EUR'] = price_raw.round(2)

    # 11: PRZ DETT
    result['PRZ DETT'] = (price_raw * price_multiplier).round(2)

    # 12: PREZZO NEGOZIO
    if profile_name == "SPRAYGROUND Ballistic" and 'SUGGESTED SELL OUT' in df.columns:
        sell_out_raw = df['SUGGESTED SELL OUT']
        if sell_out_raw.dtype == object:
            sell_out_raw = pd.to_numeric(
                sell_out_raw.astype(str).str.replace(',', '.', regex=False),
                errors='coerce'
            ).fillna(0.0)
        result['PREZZO NEGOZIO'] = sell_out_raw.round(2)
    elif profile_name == "ASICS Ballistic" and c_rrp and c_rrp in df.columns:
        rrp_raw = df[c_rrp]
        if rrp_raw.dtype == object:
            rrp_raw = pd.to_numeric(
                rrp_raw.astype(str).str.replace(',', '.', regex=False),
                errors='coerce'
            ).fillna(0.0)
        result['PREZZO NEGOZIO'] = rrp_raw.round(2)
    else:
        result['PREZZO NEGOZIO'] = result['PRZ DETT'].apply(round_to_price_point)

    # 13: BRAND
    result['BRAND'] = brand

    # 14-16: Оригинални колони преименувани
    result['CATEGORIA'] = get_multi_col_data(df, c_div)
    result['GENERE'] = get_multi_col_data(df, c_gen)
    result['TIPO'] = get_multi_col_data(df, c_tipo)

    # 17: CATEG.BG
    div_data = get_multi_col_data(df, c_div).astype(str).str.upper().str.strip()
    result['CATEG.BG'] = div_data.map(DIVISION_MAP)

    # NEW: Група = BRAND + CATEG.BG (Uppercase)
    result['Група'] = (
        result['BRAND'].fillna('').astype(str) + ' ' +
        result['CATEG.BG'].fillna('').astype(str)
    ).str.upper().str.strip()

    # 18: GEN.BG
    gen_data = get_multi_col_data(df, c_gen)
    if profile_name == "On Ballistic":
        on_map = GENDER_MAP.copy()
        on_map.update({'w': 'Жени', 'W': 'Жени', 'm': 'Мъже', 'M': 'Мъже'})
        result['GEN.BG'] = gen_data.map(on_map)
    else:
        result['GEN.BG'] = gen_data.map(GENDER_MAP)

    # 19: TIPO.BG
    tipo_orig_data = get_multi_col_data(df, c_tipo).astype(str).str.upper().str.strip()
    result['TIPO.BG'] = tipo_orig_data.map(tipo_map_upper)

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

    # 24: Код таблицаразмери
    if size_map:
        # Използваме Brand, Категория (Division) и Категория_2 за мапинг към таблицата с размери
        # CATEGORIA е оригиналната дивизия (напр. 'APP', 'FTW')
        # Категория_2 съответства на 'Style' в Size_table (напр. 'Мъжки Обувки')
        current_brand_upper = str(brand).strip().upper()
        
        def get_size_code(row):
            # Il 'Style' della Size_table corrisponde alla colonna originale Gender (es: WOMENS, MENS)
            style_val = str(row['GENERE']).strip().upper() if pd.notna(row['GENERE']) else ""
            cat_orig = str(row['CATEGORIA']).strip().upper() if pd.notna(row['CATEGORIA']) else ""
            
            if not style_val:
                return ""
            
            # 1. Пробваме мач с Brand + DIV + Style
            current_brand_upper = str(brand).strip().upper()
            key_full = (current_brand_upper, cat_orig, style_val)
            if key_full in size_map:
                return size_map[key_full]
            
            # 2. Fallback: Пробваме без DIV (Brand + "" + Style)
            key_fallback = (current_brand_upper, "", style_val)
            return size_map.get(key_fallback, "")

        result['Код таблицаразмери'] = result.apply(get_size_code, axis=1)
    else:
        result['Код таблицаразмери'] = ""

    return result


def to_excel_bytes(df, sheet_name='Sheet1'):
    """Конвертира DataFrame в bytes за изтегляне.
    Специална обработка за MultiIndex хедъри при index=False.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if isinstance(df.columns, pd.MultiIndex):
            # Запис на MultiIndex хедърите ръчно
            # Ред 1: Titles (numeric IDs) - level 0
            # Ред 2: Subtitles (Bulgarian names) - level 1
            header_df = pd.DataFrame(df.columns.tolist()).T
            header_df.to_excel(writer, index=False, header=False, sheet_name=sheet_name, startrow=0)
            
            # Запис на данните от РЕД 3 (индекс 2)
            # Премахваме MultiIndex преди запис на данните, за да избегнем NotImplementedError
            df_temp = df.copy()
            df_temp.columns = range(len(df.columns))
            df_temp.to_excel(writer, index=False, header=False, sheet_name=sheet_name, startrow=2)
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

    profile_name = st.selectbox(
        "Профил на обработка",
        list(PROFILES.keys()),
        help="Изберете профил за трансформация на данни"
    )
    
    selected_profile = PROFILES[profile_name]
    
    # Редактор на мапинг на колони
    with st.expander("🛠️ Мапинг на колони", expanded=False):
        st.markdown("##### Изберете колоните от оригиналния файл, които да попълнят полетата в изходния файл (Еlaborato).")
        st.info("💡 Можете да съедините няколко колони, като използвате знака **+** (напр. `Марка + Модел`).")
        st.info("Структурата на изходния файл е фиксирана. Тук определяте откъде идват данните.")
        
        current_mappings = st.session_state['profile_configs'][profile_name]
        updated_mappings = {}
        
        # Списък с етикети за интерфейса
        labels_dict = {
            "art_num": "→ Cod+Color (Артикулен номер)",
            "code": "→ Cod.Nike (Код)",
            "color": "→ Cod Color - Color (Цвят / Nome colore)",
            "size": "→ TAGLIA (Размер)",
            "description": "→ DESCRIZIONE (Описание)",
            "season": "→ STAG. (Сезон)",
            "barcode": "→ BARCODE (Баркод)",
            "qta": "→ QTA (Количество)",
            "price_eur": "→ FPC Price EUR (Цена без ДДС)",
            "division": "→ CATEGORIA (Дивизия)",
            "gender": "→ GENERE (Пол)",
            "silhouette": "→ TIPO (Силует)",
            "cod_color": "→ Cod Color - Color Code (Код цвят)",
            "cod_nike": "→ Cod.Nike (Специфичен код)"
        }

        for key, val in current_mappings.items():
            # Saltiamo le chiavi speciali interne (come __price_multiplier__)
            if key.startswith('__'):
                continue
            label = labels_dict.get(key, key)
            updated_mappings[key] = st.text_input(label, value=val, key=f"inp_{profile_name}_{key}")
        
        # Обновяваме сесийното състояние (само ключовете di mapping, senza __price_multiplier__)
        st.session_state['profile_configs'][profile_name].update(updated_mappings)
        
        if st.button("💾 Запази мапинга за този профил", use_container_width=True):
            # Salviamo anche il moltiplicatore corrente dalla session_state
            st.session_state['profile_configs'][profile_name]['__price_multiplier__'] = \
                st.session_state.get(f'pm_{profile_name}', selected_profile['defaults']['price_multiplier'])
            save_persistent_configurations(st.session_state['profile_configs'])
            st.success(f"Конфигурацията за **{profile_name}** е запазена!")
    
    # Filtriamo le chiavi speciali (come __price_multiplier__) che non sono mapping di colonne
    col_map = {k: v for k, v in st.session_state['profile_configs'][profile_name].items()
               if not k.startswith('__')}

    st.divider()

    price_multiplier = st.number_input(
        "Множител на цена (PRZ DETT)",
        min_value=1.0,
        max_value=5.0,
        # Използваме запазената стойност за профила (или фабричния default ако няма)
        value=float(st.session_state['profile_configs'][profile_name].get(
            '__price_multiplier__', selected_profile['defaults']['price_multiplier']
        )),
        step=0.1,
        help="Цената FPC се умножава по тази стойност",
        key=f'pm_{profile_name}'
    )

    brand_name = st.text_input(
        "Марка",
        value=selected_profile['defaults']['brand'],
        help="Име на марката за колона BRAND"
    )

    season_manual = st.text_input(
        "Сезон (ако няма колона в файла)",
        value="",
        placeholder="Напр. SS25, FW24...",
        help="Използва се за колона STAG. ако файлът не съдържа колона за сезон"
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

    st.subheader("Таблица с размери")
    # Crea l'uploader per il file delle taglie nella barra laterale
    size_file = st.file_uploader(
        "Качете Size Table (по избор)",
        type=['xlsx'],
        help="Excel файл с лист 'Size_table' за мапинг на Код таблицаразмери. Ако не е качен, се използва файлът по подразбиране 'File sorgenti/Size_table.xlsx'."
    )

    # Inizializza la mappa delle taglie come None
    size_table_map = None
    # Controlla se l'utente ha inserito un file personalizzato
    if size_file is not None:
        # Carica il file inserito dall'utente usando la funzione load_size_table
        size_table_map = load_size_table(size_file)
        # Se il caricamento ha successo, mostra il messaggio di conferma
        if size_table_map:
            st.success(f"Таблицата за размери е заредена: {len(size_table_map)} записа")
            # Mostra una finestra espandibile di debug per verificare le chiavi trovate
            with st.sidebar.expander("🔍 Дебъг: Преглед на Size Table", expanded=False):
                st.write("Първите 10 записа (Brand, Div, Style) -> Code:")
                for k, v in list(size_table_map.items())[:10]:
                    st.code(f"{k} -> {v}")
        # In caso di errore nel caricamento, mostra un avviso a video
        else:
            st.warning("Не може да се прочете таблицата за размери.")
    # Se non è stato inserito alcun file personalizzato
    else:
        # Percorso predefinito del file Excel con le taglie all'interno del progetto
        percorso_default = "File sorgenti/Size_table.xlsx"
        # Controlla se il file di default esiste nel percorso indicato
        if os.path.exists(percorso_default):
            # Carica la tabella taglie dal percorso predefinito
            size_table_map = load_size_table(percorso_default)
            # Se la tabella viene letta correttamente
            if size_table_map:
                # Mostra un messaggio informativo indicando che è stata caricata automaticamente
                st.info(f"💡 Автоматично заредена таблица за размери по подразбиране ({len(size_table_map)} записа)")
                # Aggiunge il box espandibile di debug anche per la tabella predefinita
                with st.sidebar.expander("🔍 Дебъг: Преглед на Size Table (по подразбиране)", expanded=False):
                    st.write("Първите 10 записа (Brand, Div, Style) -> Code:")
                    for k, v in list(size_table_map.items())[:10]:
                        st.code(f"{k} -> {v}")

    st.divider()
    st.caption(f"v1.1 - Профил: {profile_name}")

# --- ОСНОВНА ОБЛАСТ ---

uploaded_file = st.file_uploader(
    "Качете Excel файл за обработка",
    type=['xlsx', 'xls'],
    help=f"Файл за обработка с профил {profile_name}. Очаквани колони: {', '.join(col_map.values())}"
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

    # Проверка на необходимите колони (включително конкатенирани с +)
    all_mapped_cols = []
    # Chiavi da escludere dalla validazione per profili specifici
    excluded_keys = set()
    if profile_name == "On Ballistic":
        excluded_keys = {'code'}  # 'code' non usato in On Ballistic
    for k, val in col_map.items():
        if k in excluded_keys:
            continue
        # 'season' è sempre opzionale: se non esiste nel file si usa il valore manuale
        if k == 'season':
            continue
        if val:
            val_str = str(val)
            if val_str in df_input.columns:
                all_mapped_cols.append(val_str)
            else:
                all_mapped_cols.extend([p.strip() for p in val_str.split('+')])
    missing_cols = [c for c in set(all_mapped_cols) if c not in df_input.columns]

    if missing_cols:
        st.error(f"⚠️ **Липсващи колони** във файла за профил **{profile_name}**")
        st.write(f"Следните колони не бяха намерени в качения файл: `{', '.join(missing_cols)}`")
        st.info(f"💡 Проверете мапинга в секция **🛠️ Мапинг на колони** или качете друг файл.")
        with st.expander("Виж всички налични колони в качения файл"):
            st.write(df_input.columns.tolist())
        st.stop()

    st.divider()

    # Бутон за обработка
    if st.button("Обработи файла", type="primary", use_container_width=True):
        with st.spinner("Обработка в ход..."):
            tipo_map_to_use = custom_tipo_map if custom_tipo_map else TIPO_MAP

            try:
                df_output = process_file(
                    df_input,
                    col_map=col_map,
                    price_multiplier=price_multiplier,
                    tipo_map=tipo_map_to_use,
                    brand=brand_name,
                    profile_name=profile_name,
                    size_map=size_table_map,
                    season_override=season_manual,
                )
                st.session_state['df_output'] = df_output
                st.session_state['elaborated'] = True
            except ValueError as ve:
                st.error(f"Грешка при обработка: {ve}")
            except Exception as e:
                st.error(f"Неочаквана грешка: {e}")

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

        try:
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
        except Exception as e:
            st.error(f"Грешка при генериране на основния Excel файл: {e}")
            excel_bytes = None

        # --- ОПАКОВЪЧЕН ЛИСТ ---
        # Дефанзивна проверка: Гарантираме, че QTA е число преди групирането
        if 'QTA' in df_output.columns:
            df_output['QTA'] = pd.to_numeric(df_output['QTA'], errors='coerce').fillna(0).astype(int)

        if profile_name == "New Balance Ballistic":
            df_packing = df_output.groupby(['Cod+Color', 'DESCRIZIONE'], sort=False).agg(
                CATEG_BG=('CATEG.BG', 'first'),
                QTA=('QTA', 'sum'),
                PREZZO_NEGOZIO=('PREZZO NEGOZIO', 'first'),
            ).reset_index()
        else:
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
        # Гарантираме числови стойности и тук
        if 'QTA' in df_output.columns:
            df_output['QTA'] = pd.to_numeric(df_output['QTA'], errors='coerce').fillna(0).astype(int)
        
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
            ("Склад", ""): [warehouse_name] * len(df_output),
            ("Главна група", ""): df_output['BRAND'],
            ("Група", ""): df_output['Група'],
            ("Стока", ""): df_output['Cod.Nike'],
            ("Сер./парт. номер", ""): df_output['BARCODE'],
            ("Код на стока", ""): df_output['Site Description'],
            ("Баркод на стока", ""): "",
            ("Мярка", ""): "бр.",
            ("Количество", ""): df_output['QTA'],
            ("Доставна цена", ""): df_output['FPC Price w/o VAT in EUR'],
            ("Доставна валута", ""): "eur",
            ("Цена на дребно", ""): df_output['PREZZO NEGOZIO'],
            ("Валута на дребно", ""): "eur",
            ("Доставчик", ""): [supplier_name] * len(df_output),
            ("К-во за поръчване", ""): df_output['QTA'],
            ("Цена", ""): df_output['FPC Price w/o VAT in EUR'],
            ("Валута", ""): "eur",
            ("Бележка", ""): df_output['Cod+Color'],
            ("Активна", ""): "Y",
            ("Активна за Web", ""): "Y",
            ("Ограничения в сметки", ""): "без ограничения",
            ("Процент ДДС", ""): "",
            # Нови колони с ID-та
            ("14", "Размер сайт"): df_output['TAGLIA'],
            ("107", "Цвят сайт"): df_output['Cod Color'],
            ("13", "SKU"): df_output['SKU Completo'],
            ("109", "Категория 1"): df_output['Категория_1'],
            ("110", "Категория 2"): df_output['Категория_2'],
            ("111", "Категория 3"): df_output['Категория_3'],
            ("15", "Бранд"): df_output['BRAND'],
            ("2", "Пол"): df_output['Категория_1'],
            ("5", "Категория"): df_output['CATEG.BG'],
            ("6", "Сезон"): df_output['STAG.'],
            ("108", "Цена срв. сайт"): df_output['PREZZO NEGOZIO'],
            ("113", "Код таблица за размери"): df_output['Код таблицаразмери'],
            ("103", "Доствчик"): [supplier_name] * len(df_output),
        }

        df_gensoft = pd.DataFrame(gensoft_data)
        # Настройка на MultiIndex колони
        df_gensoft.columns = pd.MultiIndex.from_tuples(df_gensoft.columns)

        gensoft_bytes = to_excel_bytes(df_gensoft, sheet_name='Import_Gensoft')
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

        # --- ИМПОРТ ГЕНСОФТ БАРКОД (tutti i profili) ---
        barcode_txt = "\n".join(
            f"{row['BARCODE']},{row['QTA']}"
            for _, row in df_output.iterrows()
        )
        barcode_txt_filename = f"Import_Gensoft_Barcode_({data}).txt"
        col_nb1, col_nb2 = st.columns(2)
        with col_nb1:
            st.download_button(
                label="Импорт Генсофт Баркод",
                data=barcode_txt.encode("utf-8"),
                file_name=barcode_txt_filename,
                mime="text/plain",
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
