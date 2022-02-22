<p align="center">
  <a href="" rel="noopener">
 <img width=600px height=400px src="https://supraoracles.com/wp-content/uploads/2021/11/blockchain-domains.jpg" alt="Project logo"></a>
</p>

<h1 align="center"><b>DNS BLOCKCHAIN</b></h1>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](https://github.com/kylelobo/The-Documentation-Compendium/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](https://github.com/kylelobo/The-Documentation-Compendium/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center">This is my exams to end my university journey. Takes 2.5 months. The day report is 24/12/2021 ( Chrismas in COVID and Ormicron 😥 ). Lots of memorible moment 😁. <br> I'm the last one on the left 
<br>
<a href="" rel="noopener">
<img width=550px height=300px src="./screenshot/our_class_final_photo.jpg" alt="Memorible Moment">
</a>

</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Built Using](#built_using)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

At the beginning, suppose this program to be small one, which has only terminal and some web servers to test on. But it took me like 3 weeks to find out this is going massive. <br>
It can resolve any request <b> resolving domain from any where ( using 'ping', 'nslookup', 'dig', even in the browser ) </b>. The Data structure is Blockchain, decentralized network, start by CMD NODE to init. 

## ⛏️ Built Using <a name = "built_using"></a>

- [PostgreSQL](https://www.postgresql.org/) - Database
- [Python Flask](https://flask.palletsprojects.com/en/2.0.x/) - Server Framework
- [Python Socket](https://vuejs.org/) - Request and Response Flatform
- [Jinja](https://jinja.palletsprojects.com/en/3.0.x/) - Web Template

## 🏁 Getting Started <a name = "getting_started"></a>
### <b> Prerequisites </b>
You must have Python in your PC to start program, my version is 
```
Python 3.9.5
```
Try with upper or equal version only. Because I had bug when hashing SHA 256 from database in hashlib in version 3.6.5

Also your apdater setting for DNS very important. 

#1: The Ipv4 setting and Ipv6 off

![Adapter setting](/screenshot/20211225_adapter_setting.png?raw=true "Adapter setting")

### <b> Installing </b>
All the setup process is in the setup.sh, you can just easily run batch and the database included a number of table data. 
```
setup.sh
```
Another need in this program is DNS Server config, go to dns/Server.py and rewrite bellow option

```
# Global variables
IP = '192.168.1.7' # wifi Ipv4 address
PORT = 53
```

And lanch these lines to generate restartNIC.bat based on above 'Global variables' ( -rw means rewriting file batch, find more with -h )
```
cd dns
python Server.py -p -rw 
```

The result with like restartNIC.sample.bat with Ipv4 is 192.168.43.7

## 🎈 Usage <a name="usage"></a>

<b> ABOUT BLOCKCHAIN </b>

To run every nodes in the network, just run command 
```
python manage.py -p 
```
![Run node](/screenshot/20211225_run_node_1.png?raw=true "Run node" )
'-p \<port>' : which port you open with ( defualt 5000 ), used again will access random one in your node list. <br>
The other option can be found out more by command help ' -h ' 

# 
When you have 2 nodes open in the Command line, then go to website and login with administrator or registry with hoster right.

#1 : Registry with hoster or login with admin.

<br> 📍 Login

![Login with admin](/screenshot/20211225_login_with_admin.png?raw=true "Login with admin")

<br> 📍 Registry

![Registry hoster](/screenshot/20211225_registry_with_hoster.png?raw=true "Registry hoster")

#2 : Go to operation page and insert data with two ways ( by file, only .zone and .txt file, you can find it in /sample ).

<br>

![Do operation insert](/screenshot/20211225_do_operation.png?raw=true "Do operation insert")

#3 : Show transactions and domains, may be blocks.

<br> 📍 Transactions

![Show transactions](/screenshot/20211225_show_transactions.png?raw=true "show transactions")

<br> 📍 Domains

![Show domains](/screenshot/20211225_show_domains.png?raw=true "show domains")

<b> ABOUT SERVER </b>

To run dns 
```
cd dns
python Server.py -p
```
![Show dns](/screenshot/20211225_run_dns.png?raw=true "show dns")

'-p \<port>' : which port you get data by ( defualt 5000 )<br>
Especially, you need one '-ip' option but default it will be local ip

The other option can be found out more by command help ' -h ' 

#
That it, now you can resolve your own default by your browser or 'ping' or 'nslookup' <br>
Make sure web cache and dns cache is clear

<br> 📍 Ping and Nslookup

![Ping and Nslookup](/screenshot/20211225_ping_with_nslookup.png?raw=true "ping nslookup")

<br> 📍 Browser

![Browser](/screenshot/20211225_browser.png?raw=true "browser")




## ✍️ Authors <a name = "authors"></a>
- [Mr. Huynh Thanh Tam]() - Guided Teacher  
- [@PerryPhan aka Phan Dai](https://github.com/PerryPhan) - Creator. 

Thank to :<br> 
⭐[@almighty-ken](https://github.com/almighty-ken) with his basic skeleton [DNS Blockchain repository](https://github.com/almighty-ken/DNS_BlockChain) .<br>
⭐[@akapila011](https://github.com/akapila011) with his [DNS Server](https://github.com/akapila011/DNS-Server)

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Knowledge of Blockchain and DNS 
- Ways to resolve DNS request
- Progress of mining block based on Proof of Work  

<h2 align="center"> <b> Have fun 😉 </b> </h2>