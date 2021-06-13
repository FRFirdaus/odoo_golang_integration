# efishery_test
Test Recruitment Efishery

- create docker image golang service dengan command "docker build -t efishery-odoo-sale ."
![image](https://user-images.githubusercontent.com/40462921/121804472-c9dc6600-cc70-11eb-8dd5-6258089a5cc0.png)
![image](https://user-images.githubusercontent.com/40462921/121804484-d791eb80-cc70-11eb-9492-425cd48a4259.png)

- execute docker-compose "docker-compose up" untuk container odoo dan db
![image](https://user-images.githubusercontent.com/40462921/121787713-f8672c00-cbf1-11eb-8a60-758f3fc80365.png)

- setelah selesai dan terbuat container db dan odoo14, cek config file pada directory "config_odoo_14" file "odoo.conf"
![image](https://user-images.githubusercontent.com/40462921/121787478-6b6fa300-cbf0-11eb-9109-556e6f55dfe5.png)

- untuk awal "db_name" pada "config_odoo_14" dikosongkan terlebih dahulu untuk membuat database baru
![image](https://user-images.githubusercontent.com/40462921/121787497-83472700-cbf0-11eb-942f-f4fbcede6a68.png)

- masuk ke dalam ui odoo http://localhost:8091
![image](https://user-images.githubusercontent.com/40462921/121787509-9ce86e80-cbf0-11eb-9e96-e2528de61b9f.png)

- buat database baru dengan nama "efishery" dengan email: "admin" dan password: "admin", centang demo data lalu klik "continue"
![image](https://user-images.githubusercontent.com/40462921/121787523-b5f11f80-cbf0-11eb-97d8-40a0bd5c56c1.png)

- jika terdapat lebih dari 1 database odoo pada database postgre, rubah "db_name" pada file "config_odoo_14" menjadi efishery, := db_name = efishery, hal tersebut ditujukan agar endpoint/API odoo tidak bingung untuk menggunakan database yang mana
![image](https://user-images.githubusercontent.com/40462921/121787560-e8028180-cbf0-11eb-9036-f77708865880.png) ![image](https://user-images.githubusercontent.com/40462921/121787570-ff416f00-cbf0-11eb-9804-7bf0a4855fb6.png)

- jika database telah terbuat, login ke dalam odoo lalu masuk ke menu apps, dan search module name dengan keyword "efishery" jangan lupa di silang default search "Apps" pada kolom search
![image](https://user-images.githubusercontent.com/40462921/121787581-15e7c600-cbf1-11eb-857d-ce60320f2890.png)![image](https://user-images.githubusercontent.com/40462921/121787603-3021a400-cbf1-11eb-8d47-347f45e9a137.png)
![image](https://user-images.githubusercontent.com/40462921/121787612-44fe3780-cbf1-11eb-83b0-928543c7c0ca.png)

- install module Efishery Sale(efishery_sale)
![image](https://user-images.githubusercontent.com/40462921/121787644-6ced9b00-cbf1-11eb-811d-133cfd032a7b.png)

- untuk menset statik token, masuk ke dalam menu settings pada pojok kiri atas, lalu pilih menu efishery, secara default kolom akan terisi dengan value "the_token" kita perlu action save untuk menyimpan static token untuk pertama kalinya
![image](https://user-images.githubusercontent.com/40462921/121787662-8c84c380-cbf1-11eb-8df7-26c4b134062d.png)

- cek apakah service golang dapat berjalan atau tidak, buka http://localhost:8081/test
![image](https://user-images.githubusercontent.com/40462921/121804535-0c9e3e00-cc71-11eb-952f-7d292dd44f0f.png)

- kita bisa memakai REST API pada golang yang sudah dibuat untuk integrasi dengan odoo
![image](https://user-images.githubusercontent.com/40462921/121787699-cfdf3200-cbf1-11eb-9312-ad3b3e38fea5.png)
![image](https://user-images.githubusercontent.com/40462921/121787750-3cf2c780-cbf2-11eb-963f-13f539e08936.png)

- berikut documentasi postmannya https://documenter.getpostman.com/view/4527508/TzeTHU9T
