
# Zabbix Apache HTTPD Status

> Template to Show Apache HTTPD Statistics Using mod_status, Python and UserParameter
> 
> There is a mechanism to store the result in a cache file, this avoid frequent requests to the web server

## Installation

Instructions based on Ubuntu/Debian

### Agent machine

Download and copy the files

If you copy the Python to a differente place, you have to change the path inside the `userparameter_httpd.conf`

```sh
git clone https://github.com/rodrigoluissilva/Zabbix-Template-Apache-HTTPD-Status.git
cd Zabbix-Template-Apache-HTTPD-Status
cp ApacheHttpdStatus.py /etc/zabbix
chmod +x /etc/zabbix/ApacheHttpdStatus.py
cp userparameter_httpd.conf /etc/zabbix/zabbix_agentd.d
service zabbix-agent restart
```

### Apache HTTPD Server

Enable the Status module

```sh
a2enmod status
```

Usually the default configuration is fine.

If you need access from different server, change the file `/etc/apache2/mods-available/status.conf`

```
<IfModule mod_status.c>
  <Location /server-status>
    SetHandler server-status
    Require local
    Require ip 127.0.0.1 ::1 10.10.10.10
  </Location>
  ExtendedStatus On
</IfModule>
```

## Troubleshooting

You can run the script manually

```
./ApacheHttpdStatus Uptime "http://10.10.10.10/server-status"
1042
```

Or using `zabbix_get`

```
zabbix_get -s 10.10.10.10 -k "httpd[Uptime, http://localhost:80/server-status]"
1390
```

Sample error message

```
# zabbix_get -s 10.200.200.201 -k "httpd[Uptime, http://localhost:80/server-status]"
ZBX_NOTSUPPORTED
<urlopen error [Errno 111] Connection refused>
```

Check the Zabbix Server log `/var/log/zabbix/zabbix_server.log`


## Templates

This script will try to collect information from the localhost

This is fine, since the script is local to each web server, but you can change it using Macros

### Macros

You can change the URL to be queried by changing the Macro `{$STATUS_URL}`

The default value for this Macro is `http://localhost:80/server-status`

#### URL protected with password

Not supported

### Metrics

All available metrics will be collected.

If you need some new metrics, just add a new item and using the key `httpd[MetricName, {$STATUS_URL}]`

Change the `MetricName` to the correct metric name, some examples

```
httpd[Total Accesses, {$STATUS_URL}]
httpd[CPULoad, {$STATUS_URL}]
```

## Screenshots


Zabbix Apache Workers Overview Graph
![Zabbix Apache Workers Overview Graph](https://image.prntscr.com/image/DPdJMyXGQHaF_9AM7v7dWw.png)

Zabbix Apache Workers Busy Graph
![Zabbix Apache Workers Busy Graph](https://image.prntscr.com/image/uIvOkTVeSWukjilAuRIN1Q.png)

Zabbix Apache Requests Graph
![Zabbix Apache Requests Graph](https://image.prntscr.com/image/9qFhS-CWQqeNuFFAjGvvmQ.png)

Zabbix Apache CPU Utilization Graph
![Zabbix Apache CPU Utilization Graph](https://image.prntscr.com/image/EJADiiaKR5WG-EP8dDtHjA.png)

Zabbix Apache CPU Load Graph
![Zabbix Apache CPU Load Graph](https://image.prntscr.com/image/WLE-k4gqTAaHoLAHKER4Rg.png)

Zabbix Apache Access Graph
![Zabbix Apache Access Graph](https://image.prntscr.com/image/VqEG71F_TemH8HutlYxhVQ.png)
