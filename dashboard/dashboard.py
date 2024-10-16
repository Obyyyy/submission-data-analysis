import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

sns.set(style='dark')

def create_cnt_df(df):
  cnt_df = df.groupby(by=['season', 'weekday'])['cnt'].mean().reset_index()

  weekday_mapping = {
    0: 'Minggu',
    1: 'Senin',
    2: 'Selasa',
    3: 'Rabu',
    4: 'Kamis',
    5: 'Jumat',
    6: 'Sabtu'
  }
  season_mapping = {
      1: 'Semi',
      2: 'Panas',
      3: 'Gugur',
      4: 'Dingin'
  }
  cnt_df['day_name'] = cnt_df['weekday'].map(weekday_mapping)
  cnt_df['season_name'] = cnt_df['season'].map(season_mapping)
  return cnt_df

def create_month_season_df(df):
  month_season_df = df.groupby('mnth')['cnt'].sum().reset_index()

  month_mapping = {
    1: 'Januari',
    2: 'Februari',
    3: 'Maret',
    4: 'April',
    5: 'Mei',
    6: 'Juni',
    7: 'Juli',
    8: 'Agustus',
    9: 'September',
    10: 'Oktober',
    11: 'November',
    12: 'Desember'
  }
  month_season_df['month_name'] = month_season_df['mnth'].map(month_mapping)

  return month_season_df

def create_avg_rentals(df):
  df_workingday = df[df['workingday'] == 1]
  avg_rentals = df_workingday.groupby('yr').agg({
    'casual': 'mean',
    'registered': 'mean'
  }).reset_index()

  avg_rentals_melted = avg_rentals.melt(id_vars='yr', value_vars=['casual', 'registered'], var_name='User Type', value_name='Average Rentals')

  return avg_rentals_melted

def create_bytemp_df(df):
  bins = [0, 20/41, 30/41, 0.9]
  labels = ['Dingin', 'Normal', 'Panas']

  df['suhu_kategori'] = pd.cut(df['temp'], bins=bins, labels=labels, right=False)
  temp_analysis = df.groupby(['suhu_kategori'])['cnt'].sum().reset_index()

  return temp_analysis

# Load dataset
day_df = pd.read_csv('./data/day.csv')

# Convert dteday to datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Convert year code to actual year
year_mapping = {
    0: 2011,
    1: 2012
  }
day_df['yr'] = day_df['yr'].map(year_mapping)

# Sidebar untuk pemilihan tahun
with st.sidebar:
  year = st.multiselect(
    label='Select Year', 
    options=(2011, 2012),
    default=(2011, 2012)
  )

# Main content

# Filter data berdasarkan tahun yang dipilih
main_df = day_df[day_df['yr'].isin(year)]

# Header
st.header('Bike Sharing Dashboard Analysis 🚲')

# Pertanyaan 1
st.subheader('Pola Penggunaan Sepeda per Hari dalam Seminggu di Tiap Musim')
cnt_df = create_cnt_df(main_df)

fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(data=cnt_df, x="day_name", y="cnt", hue="season_name", marker="o")
plt.title(f"Pola Penggunaan Sepeda per Hari dalam Seminggu di Tiap Musim {year}")
plt.xlabel("Hari dalam Seminggu")
plt.ylabel("Jumlah Pengguna Sepeda")
plt.legend(title="Musim")
st.pyplot(fig)

# Pertanyaan 2
st.subheader('Tren Penggunaan Sepeda Selama Musim')

season_mapping = {
    'Semi': 1,
    'Panas': 2,
    'Gugur': 3,
    'Dingin': 4
}
season_label = st.radio(
  label="Pilih Musim",
  options=('Semi', 'Panas', 'Gugur', 'Dingin'),
  horizontal=True
)
season_value = season_mapping[season_label]

# Filter data berdasarkan musim yang dipilih
season_df = main_df[main_df['season'] == season_value]

month_season_df = create_month_season_df(season_df)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=month_season_df, x='month_name', y='cnt', palette='viridis')
plt.title(f"Tren Penggunaan Sepeda Selama Musim {season_label} {year}")
plt.xlabel("Bulan")
plt.ylabel("Jumlah Pengguna Sepeda")
st.pyplot(fig)

# Pertanyaan 3
st.subheader('Rata-rata Penyewaan Sepeda pada Hari Kerja')
avg_rentals = create_avg_rentals(main_df)

colors = ['#198bff', '#ff681f']
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=avg_rentals, x="yr", y="Average Rentals", hue="User Type", palette=colors)
plt.title(f"Rata-rata Penyewaan Sepeda pada Hari Kerja {year}")
plt.xlabel('Tahun')
plt.ylabel('Rata-rata jumlah penyewaan')
st.pyplot(fig)

col1, col2 = st.columns(2)
with col1:
    total_casual = avg_rentals[avg_rentals['User Type'] == 'casual']['Average Rentals'].sum()
    st.metric("Penyewa Kasual", value=total_casual)
with col2:
    total_registered = avg_rentals[avg_rentals['User Type'] == 'registered']['Average Rentals'].sum()
    st.metric("Penyewa Terdaftar", value=total_registered)

# Pertanyaan lanjutan
st.subheader('Total Penyewaan Sepeda Berdasarkan Kategori Suhu')
season_selected = st.radio(
  label="Pilih Musim",
  options=('Semi', 'Panas', 'Gugur', 'Dingin'),
  horizontal=True,
  key="season_radio"
)
season = season_mapping[season_selected]

# Filter data berdasarkan musim yang dipilih
season_temp_df = main_df[main_df['season'] == season]
temp_analysis = create_bytemp_df(season_temp_df)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=temp_analysis, y='suhu_kategori', x='cnt', palette='viridis')
plt.title(f'Total Penyewaan Sepeda Berdasarkan Kategori Suhu di Musim {season_selected} {year}')
plt.ylabel('Kategori Suhu')
plt.xlabel('Total Penyewaan')
st.pyplot(fig)

col1, col2, col3 = st.columns(3)
with col1:
    total_cold = temp_analysis[temp_analysis['suhu_kategori'] == 'Dingin']['cnt'].sum()
    st.metric("Dingin", value=total_cold)
with col2:
    total_normal = temp_analysis[temp_analysis['suhu_kategori'] == 'Normal']['cnt'].sum()
    st.metric("Normal", value=total_normal)
with col3:
    total_hot = temp_analysis[temp_analysis['suhu_kategori'] == 'Panas']['cnt'].sum()
    st.metric("Panas", value=total_hot)