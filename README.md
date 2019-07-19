# analysis-infrastructure
Repository ini berisi 3 aplikasi

ECG Clasify berisi kode program untuk melakukan analisis data ecg yang bertujuan untuk melakukan klasifikasi penyakit Arrhytmia dengan menggunakan algoritma CNN (Deep Learning). Hasil anlysis akan disimpan di database mongodb yang nantinya akan di akses oleh egc web melalui ecgstorage

ECG Storage berisi kode program REST API yang digunakan untuk mengambil data hasil analisis yang tersimpan di database mongodb

ECG Web merupakan website yang bertujuan untuk menampilkan daftar pasien, malakukan request ke ECG clasify untuk melakukan anlysis data, dan melakukan request hasil analisi ke REST API kemudian ditampilkan ke website
