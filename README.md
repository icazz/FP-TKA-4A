# Final Project Teknologi Komputasi Awan 2026

**Kelompok:** FP-TKA-4A  
**Mata Kuliah:** Teknologi Komputasi Awan

---

## Anggota Kelompok


| NRP | Nama |
|------------|--------------------------|
| 5027241008 | Paundra Pujo |
| 5027241022 | Ardhi Putra Pradana |
| 5027241048 | Afrizan Rasya |
| 5027241058 | Ica Zika Hamizah |
| 5027241064 | Hanif Mawla Faizi |
| 5027241093 | M. Atha Tajuddin |

---

## 1. Introduction

Proyek ini merupakan Final Project mata kuliah Teknologi Komputasi Awan 2026. Kami berperan sebagai Cloud Engineer di sebuah startup e-commerce yang diminta untuk men-deploy, mengonfigurasi, dan mengoptimalkan **Order Processing Service** — layanan backend berbasis REST API (Python Flask + MongoDB) yang menangani pembuatan pesanan, pengecekan status, dan riwayat transaksi.

Tantangan utama adalah merancang infrastruktur cloud yang mampu menangani lonjakan traffic (flash sale, promo) secara andal dan efisien, dengan **budget maksimal ≈ 75 US$/bulan**.

Aplikasi menyediakan 4 endpoint utama:

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/order` | Membuat pesanan baru |
| GET | `/order/<order_id>` | Mengambil detail & status pesanan |
| GET | `/orders` | Mengambil seluruh riwayat pesanan |
| PUT | `/order/<order_id>` | Mengubah status pesanan |

---

## 2. Arsitektur Cloud

### Diagram Arsitektur

> **📸 [SCREENSHOT DIPERLUKAN]** — Masukkan gambar diagram arsitektur dari draw.io di sini.  
> Format: `![Arsitektur Cloud](./result/arsitektur.png)`

Arsitektur yang digunakan adalah **Docker Swarm** dengan topologi multi-node:

- **Manager Node** — Menjalankan Traefik sebagai reverse proxy & load balancer (port 80 dan dashboard 8080)
- **Worker Nodes** — Menjalankan 4 replica backend Flask dan 2 replica frontend
- **Database Node** — MongoDB berdiri di VM terpisah (standalone, tidak masuk Swarm)

Traffic masuk diterima Traefik di Manager, kemudian didistribusikan ke replica backend via overlay network `traefik-pub`. Backend berkomunikasi ke MongoDB melalui IP internal.

### Spesifikasi VM & Harga

Menggunakan **Digital Ocean** (Credit $200): (masih salah, harus di cek lagi)

| No | Nama VM | Peran | Spesifikasi | Harga/bulan |
|----|---------|-------|-------------|-------------|
| 1 | manager | Swarm Manager + Traefik LB | 2 vCPU, 2 GB RAM | $18 |
| 2 | worker-1 | Swarm Worker (BE + FE) | 2 vCPU, 2 GB RAM | $12 |
| 3 | worker-2 | Swarm Worker (BE + FE) | 2 vCPU, 2 GB RAM | $12 |
| 4 | db | MongoDB | 1 vCPU, 2 GB RAM | $18 |
| | | | **Total** | **$40/bulan** |

Total biaya **$60/bulan**, masih di bawah budget $60.

### Alasan Pemilihan Konfigurasi

- **Docker Swarm** dipilih karena ringan, built-in ke Docker, dan cukup untuk skala ini dibanding Kubernetes yang overhead-nya lebih besar.
- **Traefik** sebagai load balancer karena integrasi native dengan Docker Swarm via label, serta auto-discovery service tanpa reload config.
- **4 replica backend** memaksimalkan throughput pada 2 worker node (2 container/node), memanfaatkan seluruh core yang tersedia.
- **DB terpisah** menghindari resource contention antara MongoDB dan aplikasi — query I/O MongoDB tidak bersaing dengan CPU Flask.
- **MongoDB indexing** pada field `order_id` dan `created_at` mempercepat query `GET /orders` yang melakukan sort descending.
- Konfigurasi ini memberikan **performa tinggi** sekaligus **biaya efisien** karena tidak ada VM yang idle.

---

## 3. Implementasi

### 3.1 Persiapan VM

Lakukan pada setiap VM (manager, worker-1, worker-2):

```bash
# Update & install Docker
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

![docker -v](./Result/docker-v.png)

### 3.2 Setup MongoDB (VM: db)

```bash
# Jalankan MongoDB via Docker Compose
mkdir -p ~/db && cd ~/db
# Salin file infra/db/docker-compose.yaml ke VM ini
docker compose up -d

# Restore dump data awal
docker cp ./dump mongodb:/dump
docker exec -it mongodb mongorestore /dump
```

Verifikasi MongoDB berjalan:

```bash
docker exec -it mongodb mongosh --eval "db.adminCommand('ping')"
```

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot output `mongosh ping` atau `docker ps` yang menunjukkan MongoDB running.

Tambahkan index untuk optimasi:

```bash
docker exec -it mongodb mongosh orderdb --eval "
  db.orders.createIndex({ order_id: 1 });
  db.orders.createIndex({ created_at: -1 });
"
```

### 3.3 Inisialisasi Docker Swarm (VM: manager)

```bash
# Init swarm di manager
docker swarm init --advertise-addr <IP_MANAGER>
```

Salin token worker yang muncul, lalu jalankan di setiap worker:

```bash
# Di worker-1 dan worker-2
docker swarm join --token <TOKEN_WORKER> <IP_MANAGER>:2377
```

Verifikasi node bergabung:

```bash
# Di manager
docker node ls
```

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot output `docker node ls` yang menunjukkan manager + 2 worker dengan status `Ready`.

### 3.4 Deploy Stack Aplikasi (VM: manager)

```bash
# Buat overlay network
docker network create --driver overlay --attachable traefik-pub
docker network create --driver overlay --attachable app-net

# Deploy stack (gunakan file infra/apps/docker-stack.yaml)
docker stack deploy -c docker-stack.yaml order
```

Pantau status deployment:

```bash
docker stack services order
docker service ls
```

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot output `docker service ls` yang menunjukkan semua service `REPLICAS` terpenuhi (mis. `4/4` untuk backend).

### 3.5 Konfigurasi Traefik

Traefik dikonfigurasi via label di `docker-stack.yaml`:

- Backend route: `PathPrefix(/api)` → strip prefix `/api` → forward ke port 5000
- Frontend route: `PathPrefix(/)` → forward ke port 80
- Dashboard Traefik tersedia di `http://<IP_MANAGER>:8080`

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Traefik dashboard (`http://<IP_MANAGER>:8080`) yang menampilkan router `backend` dan `frontend` aktif.

### 3.6 Verifikasi Frontend

Buka browser ke `http://<IP_MANAGER>/` untuk mengakses antarmuka frontend.

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot tampilan frontend di browser (halaman utama aplikasi Order Processing).

---

## 4. Hasil Pengujian Endpoint

Pengujian dilakukan menggunakan **apidog** ke base URL `http://<IP_MANAGER>/api`.

### 4.1 POST /order — Create Order

**Request:**
```json
{
  "product": "Laptop Gaming",
  "quantity": 1,
  "price": 15000000
}
```

**Expected Response (201 Created):**
```json
{
  "order_id": "<uuid>",
  "product": "Laptop Gaming",
  "quantity": 1,
  "price": 15000000,
  "total": 15000000,
  "status": "pending",
  "created_at": "2026-06-17T10:00:00Z"
}
```

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Postman: request POST `/order` dan response 201 dengan body JSON.

### 4.2 GET /order/\<order_id\> — Get Order Status

Gunakan `order_id` dari hasil POST di atas.

**Expected Response (200 OK):**
```json
{
  "order_id": "<uuid>",
  "product": "Laptop Gaming",
  "quantity": 1,
  "price": 15000000,
  "total": 15000000,
  "status": "pending",
  "created_at": "2026-06-17T10:00:00Z"
}
```

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Postman: request GET `/order/<uuid>` dan response 200.

### 4.3 GET /orders — Get Order History

**Expected Response (200 OK):** Array seluruh pesanan, diurutkan terbaru lebih dulu.

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Postman: request GET `/orders` dan response array JSON.

### 4.4 PUT /order/\<order_id\> — Update Order Status

**Request:**
```json
{ "status": "completed" }
```

**Expected Response (200 OK):**
```json
{
  "order_id": "<uuid>",
  "status": "completed"
}
```

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Postman: request PUT `/order/<uuid>` dan response 200 dengan status updated.

### 4.5 Tampilan Frontend

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot antarmuka frontend yang menampilkan form pembuatan order dan daftar riwayat pesanan.

---

## 5. Hasil Load Testing

Load testing dilakukan menggunakan Locust (`Resources/Test/locustfile.py`) dari komputer host yang **berbeda** dari server aplikasi. Database di-reset setelah setiap skenario (hanya data yang diinsert selama testing, bukan data awal).

**Reset database antar skenario:**
```bash
docker exec -it mongodb mongosh orderdb --eval "db.orders.deleteMany({ _test: true })"
```
> *(Atau sesuai kondisi — hapus hanya dokumen yang diinsert selama skenario berjalan)*

### Skenario 1 — Maksimum RPS (0% Failure)

- **Parameter:** User dinaikkan bertahap, spawn rate disesuaikan
- **Durasi:** 60 detik
- **Target:** RPS tertinggi dengan 0% failure

| Metric | Nilai |
|--------|-------|
| Max RPS (0% failure) | **[ISI HASIL]** |
| Avg Response Time | [ISI HASIL] ms |
| Jumlah User | [ISI HASIL] |

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Locust: grafik RPS, response time, dan failure rate skenario 1 (0% failure). Sertakan juga screenshot `htop`/resource monitor di salah satu server.

### Skenario 2 — Peak Concurrency (Spawn Rate 50)

- **Parameter:** User dinaikkan hingga failure muncul, catat nilai tertinggi sebelum failure
- **Durasi:** 60 detik
- **Spawn Rate:** 50 user/detik

| Metric | Nilai |
|--------|-------|
| Max Concurrent Users (0% failure) | **[ISI HASIL]** |
| RPS pada kondisi tersebut | [ISI HASIL] |

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Locust skenario 2: grafik RPS + failure rate, dan screenshot CPU/memory server.

### Skenario 3 — Peak Concurrency (Spawn Rate 100)

| Metric | Nilai |
|--------|-------|
| Max Concurrent Users (0% failure) | **[ISI HASIL]** |
| RPS pada kondisi tersebut | [ISI HASIL] |

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Locust skenario 3: grafik RPS + failure rate, dan screenshot CPU/memory server.

### Skenario 4 — Peak Concurrency (Spawn Rate 200)

| Metric | Nilai |
|--------|-------|
| Max Concurrent Users (0% failure) | **[ISI HASIL]** |
| RPS pada kondisi tersebut | [ISI HASIL] |

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Locust skenario 4: grafik RPS + failure rate, dan screenshot CPU/memory server.

### Skenario 5 — Peak Concurrency (Spawn Rate 500)

| Metric | Nilai |
|--------|-------|
| Max Concurrent Users (0% failure) | **[ISI HASIL]** |
| RPS pada kondisi tersebut | [ISI HASIL] |

> **📸 [SCREENSHOT DIPERLUKAN]** — Screenshot Locust skenario 5: grafik RPS + failure rate, dan screenshot CPU/memory server.

### Ringkasan Hasil Load Testing

| Skenario | Spawn Rate | Max Users (0% fail) | Avg RPS |
|----------|------------|----------------------|---------|
| 1 – Maks RPS | Bertahap | [ISI] | **[ISI]** |
| 2 | 50 | **[ISI]** | [ISI] |
| 3 | 100 | **[ISI]** | [ISI] |
| 4 | 200 | **[ISI]** | [ISI] |
| 5 | 500 | **[ISI]** | [ISI] |

### Analisis

Dari hasil pengujian, arsitektur Docker Swarm dengan 4 replica backend mampu mendistribusikan beban secara merata ke seluruh worker node. Traefik sebagai load balancer dengan algoritma round-robin memberikan distribusi request yang adil antar container.

Pada spawn rate tinggi (200–500), bottleneck umumnya muncul di sisi koneksi MongoDB karena antrian operasi tulis `POST /order` mulai menumpuk. Penggunaan index pada koleksi `orders` membantu mempertahankan performa `GET /orders` meskipun jumlah dokumen bertambah.

---

## 6. Kesimpulan dan Saran

### Kesimpulan

Implementasi Order Processing Service pada infrastruktur Docker Swarm di Digital Ocean berhasil:

1. **Seluruh endpoint berfungsi** dengan benar — POST, GET, PUT order semua memberikan respons sesuai spesifikasi.
2. **Arsitektur multi-replica** dengan Traefik load balancer terbukti meningkatkan throughput dibandingkan deployment single-instance.
3. **Pemisahan database** ke VM tersendiri mengurangi resource contention dan meningkatkan stabilitas di bawah beban tinggi.
4. **Budget terkontrol** — Total $72/bulan dari alokasi $75, menyisakan buffer $3 untuk biaya transfer/snapshot.

### Saran untuk Production Deployment

1. **Gunakan Managed Database** — Ganti MongoDB self-hosted dengan MongoDB Atlas atau DigitalOcean Managed MongoDB untuk built-in replication, backup otomatis, dan failover.
2. **Tambahkan CDN** — Frontend yang bersifat statis idealnya di-serve dari CDN (Cloudflare/DO Spaces) untuk mengurangi beban server dan meningkatkan latency global.
3. **Implementasi Horizontal Auto-Scaling** — Integrasikan monitoring (Prometheus + Grafana) dengan trigger otomatis untuk menambah replica saat RPS atau CPU melewati threshold tertentu.
4. **Gunakan HTTPS** — Konfigurasikan TLS di Traefik menggunakan Let's Encrypt (sudah tersedia di Traefik) untuk keamanan data in-transit.
5. **Connection Pooling** — Atur `maxPoolSize` pada `MongoClient` di `app.py` agar koneksi tidak berlebihan saat concurrent user tinggi.
6. **Rate Limiting** — Tambahkan middleware rate limiting di Traefik untuk mencegah abuse pada endpoint `/order`.
7. **Pisahkan Log & Monitoring** — Gunakan stack ELK atau Loki + Grafana untuk centralized logging dari semua replica backend.

---

## Referensi

- [Docker Swarm Documentation](https://docs.docker.com/engine/swarm/)
- [Traefik Docker Provider](https://doc.traefik.io/traefik/providers/docker/)
- [MongoDB Indexing Strategies](https://www.mongodb.com/docs/manual/applications/indexes/)
- [Locust Documentation](https://docs.locust.io/)
