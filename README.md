# 使用方法

①ベースをビルドする（時間がかかる）
```
bash docker-build-base.sh
```

②イメージをビルドする
```
bash docker-build.sh
```

③project.ymlのmicroservicesに以下を追加
```
  stream-basler-usb-video-by-x11:
    startup: yes
    privileged: yes
    always: yes
    network: ClusterIP
    dnsPolicy: ClusterFirstWithHostNet
    ports:
      - name: camera
        protocol: TCP
        port: 8555
    env:
      DISPLAY: ":1"
    volumeMountPathList:
      - /tmp/.X11-unix/:/tmp/.X11-unix/
```

④ターミナルを開き、以下のコマンドを実行
```
export DISPLAY=:1
xhost +
```

⑤aion-coreを動かす

⑥映像が出力される
