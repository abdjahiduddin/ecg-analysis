# ECG Analisis
Repository ini terdiri dari 3 aplikasi

ECG Clasify berisi kode program untuk melakukan analisis data ECG yang bertujuan untuk melakukan Klasifikasi penyakit Arrhytmia dengan menggunakan algoritma CNN (Deep Learning). Hasil analisis akan disimpan di database mongodb. Data yang tersimpan di mongodb akan diakses oleh ECG Web melalui ECG Storage

ECG Storage berisi kode program REST API yang digunakan untuk mengambil data hasil analisis yang tersimpan di database mongodb

ECG Web berisi website yang bertujuan untuk menampilkan daftar pasien, melakukan request ke ECG clasify untuk melakukan analisis data, dan melakukan request hasil analisis ke REST API kemudian ditampilkan ke website

Didalam 3 folder tersebut terdapat folder docker yang berisi Dockerfile dan requirements yang dapat digunakan untuk membuat docker image 
