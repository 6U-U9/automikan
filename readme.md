<div align="center">
  <a href="https://github.com/6U-U9/automikan/readme.md">
    <img src="documents/images/logo.png" alt="Logo" height="80">
  </a>
  <h4 align="center">Auto anime downloader based on Mikan</h4>
  <h4 align="center">基于 Mikan 的自动追番工具</h4>
</div>

# How To Use 如何使用
## Docker Compose All In One
#### 1. 将下面的配置保存为 [docker-compose.yml](documents/docker-compose-all-in-one.yml)
```yml
services:
  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent-automikan
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - WEBUI_PORT=8080
      - TORRENTING_PORT=6881
    volumes:
      - /path/to/qbittorrent/appdata:/config            # qbittorrent 配置保存路径
      - /path/to/bangumi/downloads:/bangumi/downloads   # 下载路径
    ports:
      - 8080:8080
      - 6881:6881/tcp
      - 6881:6881/udp
    networks:
      - automikan
    restart: unless-stopped

  automikan-server:
    image: 6uau9/automikan:latest
    container_name: automikan-server
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - /path/to/bangumi:/bangumi                       # 番剧保存路径
      - /path/to/torrents:/torrents                     # 种子保存路径
      - /path/to/automikan:/automikan                   # 配置及数据保存路径
    ports:
      - 8236:8236
    networks:
      - automikan
    restart: unless-stopped

  automikan-web:
    image: 6uau9/automikan-web:latest
    container_name: automikan-web
    environment:
      - API_BASE_URL="http://automikan-server:8236"
    ports:
      - 8237:8237
    networks:
      - automikan
    restart: unless-stopped

networks:
  automikan:
    name: automikan
    driver: bridge
```
#### 2. 调整配置  
调整 volume 下路径到合适的位置，路径填写在冒号左侧  
qbittorrent:  
    /config 为 qbittorrent 保存设置以及元数据的路径  
    /bangumi/downloads 为下载文件保存的路径  
automikan-server:  
    /bangumi 为保存整理过的文件的路径  
    /torrents 为种子文件保存路径  
    /automikan 为设置文件保存路径  

**注意: 文件整理功能通过硬链接实现，所以 qbittorrent 的下载路径需要在 automikan-server /bangumi 对应路径下，否则文件整理功能无法正常运行**

#### 3. 运行容器
```sh
docker-compose up -d
```

#### 4. 初始化 qbittorrent  
1. 从日志中获取 qbittorrent 初始密码
```sh
docker logs qbittorrent-automikan  
```  
2. 使用浏览器访问 [http://localhost:8080](http://localhost:8080)； 使用 admin 以及初始密码登录

3. 进入设置界面：  
    1. 修改密码  
    2. 修改默认下载路径为 /bangumi/downloads

#### 5. 设置 automikan  
1. 使用浏览器访问 [http://localhost:8237](http://localhost:8237)；第一次登陆可以使用任意用户名和密码，automikan 将创建该用户
2. 进入设置界面：
    1. 修改 qbittorrent 部分的用户名和密码
    2. 点击下方 save 按钮保存
3. 其他的设置请参考 [wiki]()

#### 6. 添加 mikan 订阅链接 
使用浏览器访问 [mikan](https://mikanime.tv/)
##### 1. 聚合 RSS
1. 注册账号，订阅想看的番剧
2. 进入订阅选项卡，复制右下角 RSS 图标的链接
3. 在 [http://localhost:8237](http://localhost:8237) Subscription 选项卡中新建订阅
4. 粘贴刚才的链接并保存
##### 2. 番剧 RSS
1. 进入任一番剧页面
2. 选择喜欢的字幕组
3. 右键点击右侧的橙色 RSS 图标，复制链接
4. 在 [http://localhost:8237](http://localhost:8237) Subscription 选项卡中新建订阅 
5. 粘贴链接，取消勾选 aggregate，保存  

#### 7. 等待下载完成  
可以看番啦 ☆⌒☆！

# Report a Bug
1. 请详细描述问题
2. 请上传 /automikan 路径下 automikan.log, config.json, automikan.db 以获取更好的支持

# Special Thanks
感谢 Mikan 提供新番发布以及 RSS

# License
BSD 3-Clause License