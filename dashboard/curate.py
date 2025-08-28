import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import plotly.io as pio
pio.renderers.default = "browser"
import re


# mengecilkan huruf header dan mengganti space jadi underscore
def measure_df_clean_header(df):
    headers  = df.columns
    cheaders = [] 
    for name in headers:
        cname = re.sub(r"\s+", "_", name)
        cname = re.sub(r"\,", "", cname)
        cname = re.sub(r"\.", "_", cname)
        cname = cname.lower()
        cheaders.append(cname)
    df.columns = cheaders
    return df


# mengubah tipe data beberapa kolom menjadi float dan int
def measure_df_update_dtype(df):
    # replace comma to dot
    float_names = [
        "depth_(m)",
        "area_(m2)",
        "size_(cm)",
        "ind_weight_(kg)",
        "density_(n/ha)",
        "biomass_(kg/ha)"
    ]

    for name in float_names:
        df[name] = df[name].apply(lambda x: float(x.replace(',', '.')))
    
    dtype_dict = {
        'year'                  : int, 
        'month'                 : int, 
        'transect'              : int,
        'size_(cm)'             : int,
        'number_individu_(n)'   : int,
    }

    df = df.astype(dtype_dict)

    return df


path_measure    = "dataset/mpa_fish.xlsx"
measure_df      = pd.read_excel(path_measure, dtype=str).fillna("n/a")

observe_fish    = (measure_df
    .pipe(measure_df_clean_header)
    .pipe(measure_df_update_dtype)
)


# ------ - - --- - - -- - - -- - -- -- -- - - - --- - -  - - - -- - - -- - - - - - - --  -- - - - - - - - - - -
# mengubah data koordinat ke format desimal
def latlon_to_decimal(latlon_str):
    latlon_str = latlon_str.lower()
    nreg = r"(\d+[,\.]*\d*)"
    sreg = r"[nsew]"

    if not latlon_str:
        return None
    
    if latlon_str.lower() == "n/a":
        return None
    
    if latlon_str.lower() == "nan":
        return None 
    
    n_matches = re.findall(nreg, latlon_str)
    s_match   = re.findall(sreg, latlon_str)

    if len(n_matches) == 1:
        return float(latlon_str)

    if len(n_matches) == 3:
        degree, minute, seconds = n_matches
        if s_match:
            direction = s_match[0]
    else:
        return None
    
    degrees = int(degree)
    minutes = int(minute)
    
    seconds = seconds.replace(",", ".")
    seconds = float(seconds)

    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)

    if direction == 'n':
        return decimal_degrees
    
    if direction == 's':
        decimal_degrees = -decimal_degrees
        return decimal_degrees
    
    if direction == 'e':
        return decimal_degrees
    
    if direction == 'w':
        decimal_degrees = -decimal_degrees
        return decimal_degrees
    

# potong baris di excel, tapi kayaknya udah ga perlu dipake
def site_df_onetime_truncate_columns(df):
    df = df.iloc[:, :-2]
    return df


# sama fungsinya dengan clean header buat fish_df
def site_df_clean_header(df):
    headers  = df.columns
    cheaders = [] 
    for name in headers:
        cname = re.sub(r"\s+", "_", name)
        cname = re.sub(r"\,", "", cname)
        cname = re.sub(r"\.", "", cname)
        cname = cname.lower()
        cheaders.append(cname)
    df.columns = cheaders
    return df


# replace string n/a jadi numeric np.nan
def site_df_replace_na(df):
    target_columns = {
        "dive_no"       : {"n/a": np.nan},
        "slope_angle"   : {"n/a": np.nan},
        "visibility"    : {"n/a": np.nan},
    }

    for col, pair in target_columns.items():
        pair    = target_columns[col]
        for key, val in pair.items():
           df[col] = df[col].apply(lambda s: s.replace(key, val))

    return df


# replace comma to dot
def site_df_replace_comma(df):
    float_names = [
        "latitude",   
        "longitude", 
        "slope_angle",
        "visibility"
    ]

    for name in float_names:
        df.loc[:, name] = df[name].str.replace(',', '.')

    return df


# ini implement fungsi latlon_to_decimal
def site_df_cleanse_coordinate(df):
    coords = [
        "latitude",   
        "longitude", 
    ]

    for name in coords:
        df.loc[:, name] = df[name].apply(latlon_to_decimal)
    
    return df


# konversi data type ke float dan integer 
def site_df_update_dtype(df):
    # fix lat lon string
    
    integer_list = {
        'rec_id', 
        'dive_no'
    }

    float_list = {
        "latitude",   
        "longitude", 
        'slope_angle',
        'visibility'
    }

    for col in integer_list:
        df.loc[:, col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    for col in float_list:
        df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')

    return df


# mengubah string tanggal menjadi date object
def site_df_handle_date(df):
    date_columns = [
        "date_of_survey"
    ]

    for col in date_columns:
        df.loc[:, col] = pd.to_datetime(df[col], errors="coerce", format="%Y-%m-%d %H:%M:%S").dt.date

    return df

# mengubah time string menjadi time object
def site_df_handle_time(df):
    def convert(time_str):
        needles = time_str.split(".")
        if len(needles) == 2:
            hour    = int(needles[0])
            minute  = int(needles[1])
            result = f"{hour:02d}:{minute:02d}"
            return result
        else:
            return time_str

    time_columns = [
        "time"
    ]

    for col in time_columns:
        df.loc[:, col] = df[col].apply(convert)
        # df.loc[:, col] = pd.to_datetime(df[col].apply(convert), errors="coerce", format="%H:%M").dt.time

    return df


path_site       = "dataset/mpa_site.xlsx"
site_df         = pd.read_excel(path_site, dtype=str).fillna("n/a")

site_fish = (site_df
    .pipe(site_df_onetime_truncate_columns)
    .pipe(site_df_clean_header)
    .pipe(site_df_replace_comma)
    # .pipe(site_df_replace_na)
    .pipe(site_df_cleanse_coordinate)
    .pipe(site_df_update_dtype)
    .pipe(site_df_handle_date)
    # .pipe(site_df_handle_time)
)


def randomly_swap_rows(df, inplace=False):
    """
    Randomly swaps the values of rows for each column in a DataFrame.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame to shuffle
    inplace : bool, default False
        If True, modify the DataFrame in place. If False, return a new DataFrame.
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with randomly shuffled row values for each column
    """
    if not inplace:
        df = df.copy()
    
    # Shuffle each column independently
    for col in df.columns:
        df.loc[:, col] = np.random.permutation(df[col].values)
    
    return df


if __name__ == "__main__":
    # randomly_swap_rows(observe_fish, inplace=True)
    # randomly_swap_rows(site_fish, inplace=True)
    observe_fish.to_json('observe_fish.json', orient='records', indent=3)
    site_fish.to_json('site_fish.json', orient='records', indent=3)