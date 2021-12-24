<p align="center">
  <a href="" rel="noopener">
 <img width=100% height=400px src="https://supraoracles.com/wp-content/uploads/2021/11/blockchain-domains.jpg" alt="Project logo"></a>
</p>

<h1 align="center"><b>DNS BLOCKCHAIN</b></h1>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](https://github.com/kylelobo/The-Documentation-Compendium/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](https://github.com/kylelobo/The-Documentation-Compendium/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center">This is my exams to end my university journey. Takes 2.5 months. The day report is 24/12/2021 ( Chrismas in COVID and Ormicron 😥 ). Lots of memorible moment 😁. 
<br>
<a href="" rel="noopener">
<img width=450px height=250px src="https://scontent.fsgn5-6.fna.fbcdn.net/v/t1.15752-9/264329563_623215088925900_5231524545818107820_n.jpg?_nc_cat=106&ccb=1-5&_nc_sid=ae9488&_nc_ohc=P6I4aaQ25T4AX9Yu8W0&_nc_ht=scontent.fsgn5-6.fna&oh=03_AVIWddUf-4NBS0t94Zuyh1WDnaKUZlJi6Sw_1iI1ZC4rJA&oe=61EAA151" alt="Memorible Moment">
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

### <b> Installing </b>
All the setup process is in the setup.sh, you can just easily run batch and the database included a number of table data. 
```
setup.sh
```
Another need in this program is DNS Server config, go to dns/Server.py and rewrite bellow option

```
# Global variables
IP = '192.168.43.7' # wifi Ipv4 address
PORT = 53
```

And lanch these lines to generate restartNIC.bat based on above 'Global variables' ( -rw means rewriting file batch, find more with -h )
```
cd dns
python Server.py -p -rw 
```

The result with like restartNIC.sample.bat with Ipv4 is 192.168.43.7

## 🎈 Usage <a name="usage"></a>

Add notes about how to use the system.
Take screen shot 

## ✍️ Authors <a name = "authors"></a>

- [@PerryPhan aka Phan Dai](https://github.com/PerryPhan) - All operations director. 

Thank to :<br> 
⭐[@almighty-ken](https://github.com/almighty-ken) with his [DNS Blockchain repository](https://github.com/almighty-ken/DNS_BlockChain) .<br>
⭐[@akapila011](https://github.com/akapila011) with his [DNS Server](https://github.com/akapila011/DNS-Server)

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Knowledge of Blockchain and DNS 
- Ways to resolve DNS request
- Progress of making block 
