## note

#### 使用

* `nohup socket_ssh_server.py &` 开启socket服务器，等待接收密码。（没有nohup的话，关闭退出当前shell，如关闭terminal当前标签，就会被kill。详见[这个](https://www.maketecheasier.com/run-bash-commands-background-linux/)，还没细看）
* `send_command.py --start` 发送密码给socket服务器，socket服务器收到密码就开始登录ssh。（这么做仅仅是因为服务器文件后台运行，没法让我输入密码）
* `send_command.py --stop` 在发送密码前，或者建立ssh连接后，都可以杀死`socket_ssh_server.py`。
* `socket_command.py --send [any command that will be sent to ssh server]`  执行代码，打印结果。
* 目前的alias，我把`sss`对应后台启动socket服务器，`ss`对应`send_command.py`，`s`对应`send_command.py —send`。程序都没有映射到`/usr/local/bin/`下。

#### To do

* 考虑怎么改进`socket_ssh_server.py`，响应传入请求的代码放在一块，我现在是发送密码前和发送密码后的响应分开写，有点啰嗦。
* 好像socket不能简单地实现单个connection发送多次信息。所以`send_command.py`中我是每次发送一个命令都重新建立一个连接。
* 对于南大集群以外的服务器，不需要用`pexpect`模块，用`paramiko`之类的肯定性能上更好。（`pxssh` is a screen-scraping wrapper around the SSH command on your system，是pexpect的一个子模块。可以适用南大集群。我是通过搜索"python ssh print login message"来实现的，因为我猜测这个message可能要以与屏幕交互的形式获取，如果那个方法能获取到这个message，那说不定就能适用于该集群的交互，搜到了这个回答。）
* socket服务器接收的是json格式（两个key），发送的最好也改成类似格式，目前是简单地返回纯文本，因为暂时也没对socket服务器的返回值做什么判断，可以做一些判断（`send_comamnd.py`），更漂亮地做出反应。