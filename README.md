# **IPK PROJEKT 1**

## HTTP resolver doménových mien

Projekt implementovaný v jazyku **_Python3_**.
Použité knižnice sú:<br/>
_socket_ na vytvorenie serveru, komunikáciu s klientom a overovanie IP adries _(IPv4, IPv6)_ <br/>
_sys_ pre správu triviálnych funkcií ako sys.exit alebo spracovanie argumentu<br/>
_signal_ pre zachytávanie signáu SIGINT _(keyboard interruptions)_ <br/>
_urllib_ konkrétne urlparse - na validáciu url adries.<br/>
_re_ pre kontrolu regular expressions. <br/>
<br/>
Server po spustení na localhost a zadanom porte beží v nekonečnom cykle pričom čaká na pripojenie klienta, po pripojení vypíše na stdout bližšie informácie o klientovi a začne spĺňať požiadavky klienta, v prípade chýb v požiadavku alebo iných nepriaznivých situacií server posiela klientovi návratový kód  _400 Bad Request, 404 Not Found, 405 Method Not Allowed_ a v prípade úspechu pošle žiadanú odpoveď s návratovou hodnotou _200 OK_.<br/>
<br/>
Server podporuje povinné **GET** a **POST** requesty.<br/>
Program sa spúšta pomocou _Makefile_ príkazom:<br/>
**_$ make run PORT='číslo portu'_**<br/>
Pre ukončenie je nutné zastaviť server kombináciou _CONTROL + C_ <br/>
<br/>
K testovaniu poslúži program _Curl_  <br/>
pre GET: **_$ curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A_** <br/>
pre POST: **_$ curl --data-binary @queries.txt -X POST http://localhost:5353/dns-query_** <br/>
kde queries.txt obsahuje napríklad:  <br/>
www.fit.vutbr.cz:A <br/>
www.google.com:A <br/>
www.seznam.cz:A <br/>
147.229.14.131:PTR <br/>
ihned.cz:A <br/>