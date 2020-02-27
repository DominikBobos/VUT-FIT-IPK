# **IPK PROJEKT 1**

## HTTP resolver doménových mien

Projekt implementovaný v jazyku **_Python3_**.
Použité knižnice sú:
_socket_ na vytvorenie serveru, komunikáciu s klientom a overovanie IP adries
_sys_ pre správu triviálnych funkcií ako sys.exit alebo spracovanie argumentu
_urllib_ konkrétne urlparse - na validáciu url adries.

Server podporuje povinné **GET** a **POST** requesty.
Program sa spúšta pomocou _Makefile_ príkazom:
**_$ make run PORT='číslo portu'_** 

K testovaniu poslúži program _Curl_  
pre GET: **_$ curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A_**
pre POST: **_$ curl --data-binary @queries.txt -X POST http://localhost:5353/dns-query_**
kde queries.txt obsahuje napríklad: 
www.fit.vutbr.cz:A
www.google.com:A
www.seznam.cz:A
147.229.14.131:PTR
ihned.cz:A
