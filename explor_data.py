import numpy as np
import pandas as pd
import requests
resp_jabar = requests.get('https://data.covid19.go.id/public/api/prov_detail_JAWA_BARAT.json')
cov_jabar_raw = resp_jabar.json()

cov_jabar = pd.DataFrame(cov_jabar_raw['list_perkembangan'])
print('Info cov_jabar:\n', cov_jabar.info())
print('\nLima data teratas cov_jabar:\n', cov_jabar.head())


#cleaning data
cov_jabar_tidy = (cov_jabar.drop(columns=[item for item in cov_jabar.columns 
                                               if item.startswith('AKUMULASI') 
                                                  or item.startswith('DIRAWAT')])
                           .rename(columns=str.lower)
                           .rename(columns={'kasus': 'kasus_baru'})
                  )
cov_jabar_tidy['tanggal'] = pd.to_datetime(cov_jabar_tidy['tanggal']*1e6, unit='ns')
print('Lima data teratas:\n', cov_jabar_tidy.head())


# #visualisasi data
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# plt.clf()
# fig, ax = plt.subplots(figsize=(10,5))
# ax.bar(data=cov_jabar_tidy, x='tanggal', height='kasus_baru', color='salmon')
# fig.suptitle('Kasus Harian Positif COVID-19 di Jawa Barat', 
#              y=1.00, fontsize=16, fontweight='bold', ha='center')
# ax.set_title('Terjadi pelonjakan kasus di awal bulan juli akibat klaster Secapa AD Bandung',
#              fontsize=10)
# ax.set_xlabel('')
# ax.set_ylabel('Jumlah kasus')
# ax.text(1, -0.3, 'Sumber data:covid.19.go.id', color='blue',
#         ha='right', transform=ax.transAxes)
# ax.set_xticklabels(ax.get_xticks(), rotation=90)

# ax.xaxis.set_major_locator(mdates.MonthLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# plt.grid(axis='y')
# plt.tight_layout()
# plt.show()

# Perkembangan tiap pekan
cov_jabar_pekanan = (cov_jabar_tidy.set_index('tanggal')['kasus_baru'] #jadikan kolom tanggal menjadi index dengan set_index
                                   .resample('W') #penerapan pandas timeseries dengan melakukan resampling per pekan atau week
                                   .sum() #melakukan penjumlahan
                                   .reset_index() #reset index
                                   .rename(columns={'kasus_baru': 'jumlah'})
                    )
cov_jabar_pekanan['tahun'] = cov_jabar_pekanan['tanggal'].apply(lambda x: x.year) #mendapatkan nilai tahun untuk kolom tahun
cov_jabar_pekanan['pekan_ke'] =cov_jabar_pekanan['tanggal'].apply(lambda x: x.weekofyear) #mendapatkan nilai "minggu ke-" untuk kolom pekan_ke 
cov_jabar_pekanan = cov_jabar_pekanan[['tahun', 'pekan_ke', 'jumlah']] #memasukkan kolom ke dalam dataframe dan menghapus kolom tanggal

print('Info cov_jabar_pekanan:')
print(cov_jabar_pekanan.info())
print('\nLima data teratas cov_jabar_pekanan:\n', cov_jabar_pekanan.head())

#membuat kolom baru untuk tahu apakah lebih baik atau tidak
cov_jabar_pekanan['jumlah_pekanlalu'] = cov_jabar_pekanan['jumlah'].shift().replace(np.nan, 0).astype(np.int)
cov_jabar_pekanan['lebih_baik'] = cov_jabar_pekanan['jumlah'] < cov_jabar_pekanan['jumlah_pekanlalu']

print('Sepuluh data teratas:\n', cov_jabar_pekanan.head(10))

# import matplotlib.pyplot as plt

# plt.clf()
# jml_tahun_terjadi_covid19 = cov_jabar_pekanan['tahun'].nunique()
# tahun_terjadi_covid19 = cov_jabar_pekanan['tahun'].unique()
# fig, axes = plt.subplots(nrows=jml_tahun_terjadi_covid19,
# 						 figsize=(10,3*jml_tahun_terjadi_covid19))

# fig.suptitle('Kasus Pekanan Positif COVID-19 di Jawa Barat',
# y=1.00, fontsize=16, fontweight='bold', ha='center')
# for i, ax in enumerate(axes):
#    ax.bar(data=cov_jabar_pekanan.loc[cov_jabar_pekanan['tahun']==tahun_terjadi_covid19[i]],
#    x='pekan_ke',height='jumlah',
#    color=['mediumseagreen' if x is True else 'salmon'
#    for x in cov_jabar_pekanan['lebih_baik']])
#    if i == 0:
#       ax.set_title('Kolom hijau menunjukkan penambahan kasus baru lebih sedikit dibandingkan satu pekan sebelumnya',
#       fontsize=10)
#    elif i == jml_tahun_terjadi_covid19-1:
#       ax.text(1,-0.2, 'Sumber data: covid.19.go.id', color='blue',
#       ha='right', transform=ax.transAxes)

#    ax.set_xlim([0, 52.5])
#    ax.set_ylim([0, max(cov_jabar_pekanan['jumlah'])])
#    ax.set_xlabel('')
#    ax.set_ylabel('Jumlah kasus %d'%(tahun_terjadi_covid19[i],))
#    ax.grid(axis='y')

# plt.tight_layout()
# plt.show()


#menghitung akumulasi kasus aktif, akumulasi sembuh, dan akumulasi meninggal tanpa melihat data
cov_jabar_akumulasi = cov_jabar_tidy[['tanggal']].copy()
cov_jabar_akumulasi['akumulasi_aktif'] = (cov_jabar_tidy['kasus_baru'] - cov_jabar_tidy['sembuh'] - cov_jabar_tidy['meninggal']).cumsum()
cov_jabar_akumulasi['akumulasi_sembuh'] = cov_jabar_tidy['sembuh'].cumsum()
cov_jabar_akumulasi['akumulasi_meninggal'] = cov_jabar_tidy['meninggal'].cumsum()
print(cov_jabar_akumulasi.tail())

#visualiasi akumulasi aktif
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# plt.clf()
# fig, ax = plt.subplots(figsize=(10,5))
# ax.plot('tanggal', 'akumulasi_aktif', data=cov_jabar_akumulasi, lw=2)

# ax.set_title('Akumulasi aktif COVID-19 di Jawa Barat',
#              fontsize=22)
# ax.set_xlabel('')
# ax.set_ylabel('Akumulasi aktif')
# ax.text(1, -0.3, 'Sumber data: covid.19.go.id', color='blue',
#         ha='right', transform=ax.transAxes)
# ax.set_xticklabels(ax.get_xticks(), rotation=90)

# ax.xaxis.set_major_locator(mdates.MonthLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# plt.grid()
# plt.tight_layout()
# plt.show()

# visualisasi linechart
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# plt.clf()
# fig, ax = plt.subplots(figsize=(10,5))
# ax.plot('tanggal', 'akumulasi_aktif', data=cov_jabar_akumulasi, lw=2)

# ax.set_title('Akumulasi aktif COVID-19 di Jawa Barat',
#              fontsize=22)
# ax.set_xlabel('')
# ax.set_ylabel('Akumulasi aktif')
# ax.text(1, -0.3, 'Sumber data: covid.19.go.id', color='blue',
#         ha='right', transform=ax.transAxes)
# ax.set_xticklabels(ax.get_xticks(), rotation=90)

# ax.xaxis.set_major_locator(mdates.MonthLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# plt.grid()
# plt.tight_layout()
# plt.show()

#Visualisasi perbandingan
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.clf()
fig, ax = plt.subplots(figsize=(10,5))
cov_jabar_akumulasi_ts = cov_jabar_akumulasi.set_index('tanggal')
cov_jabar_akumulasi_ts.plot(kind='line', ax=ax, lw=3,
							color=['salmon', 'slategrey', 'olivedrab'])

ax.set_title('Dinamika Kasus COVID-19 di Jawa Barat',
			 fontsize=22)
ax.set_xlabel('')
ax.set_ylabel('Akumulasi aktif')
ax.text(1, -0.3, 'Sumber data: covid.19.go.id', color='blue',
		ha='right', transform=ax.transAxes)

plt.grid()
plt.tight_layout()
plt.show()