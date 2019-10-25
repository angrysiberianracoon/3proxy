# Proxy Server from Docker image based on 3Proxy server by 3APA3A
## Description
With this project, you can deploy your own HTTP/Socks proxy server with support for client management and localization through a convenient console menu.

## Features
* Easy installation via Docker
* Configuration via a convenient console menu
* Adding/remove clients, set traffic limit, view traffic count statistic
* Localization support

## Restrictions
* Only the IP address is supported as the server address

## Prerequisites
* Server with Docker installed and Internet access
* External IP address for this server
* Access the Server via ssh

## Installation
Run the Docker image deployment command on the server:

```Bash
docker run -d --net=host --restart=always --name=3proxy angrysiberianracoon/3proxy
```

## Server configuration
To configure, run the command:

```Bash
docker exec -it 3proxy python /data/bin/proxy.py
```
The command opens the console server setup menu, through which you can perform the initial configuration, add, remove, view stat for users.

### Console menu example:
![Console menu example](https://github.com/angrysiberianracoon/3proxy/blob/master/docs/screen_sample.png?raw=true)


## Localization
If you want to add your localization to the project, send a .po file to my email or make a pull request.

## Author
Angry Siberian Racoon
e-mail: angrysiberianracoon@gmail.com

## License
Copyright (c) 2019 Angry Siberian Racoon, this software is licensed under [MIT License](https://github.com/angrysiberianracoon/3proxy/blob/master/LICENSE).