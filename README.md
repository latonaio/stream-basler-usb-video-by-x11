# stream-basler-usb-video-by-x11
stream-basler-usb-video-by-x11は、basler製のSDKであるpypylonをラップした、主にエッジコンピューティング環境においてbasler製品のカメラを使用するためのマイクロサービスです。  
stream-basler-usb-video-by-x11は、接続されたbasler製品のカメラを認識し、画像を撮影します。  
撮影データはX11 Bitmap及びX11 Pixmap形式に変換されたあと、jpgに変換され、メモリ内に保存されます。  
他マイクロサービスへの提供時には、メモリ内の画像データをbase64に変換して送信します。  

# 動作環境
stream-basler-usb-video-by-x11は、aion-coreのプラットフォーム上での動作を前提としています。  
使用する際は、事前に下記の通りAIONの動作環境を用意してください。  

OS: Linux OS  
CPU: ARM/AMD/Intel  
Kubernetes  
AIONのリソース  

# basler製品のカメラ対応機種

・acA1920-40gc  
・acA1920-40uc  
・acA1300-30gm  
・acA2040-55uc  

# 使用方法

①ベースイメージをビルドします
```
bash docker-build-base.sh
```

②イメージをビルドします
```
bash docker-build.sh
```

③project.ymlのmicroservicesに以下を追加します
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

④ターミナルを開き、以下のコマンドを実行します
```
export DISPLAY=:1
xhost +
```

⑤aion-coreを起動します

⑥映像が出力されます

# grpcサーバー

### サービス定義
```
service MainServer{
	rpc getImage (ImageRequest) returns (stream ImageReply) {}
}
```

### メッセージ定義
```
message ImageReply{
	string image = 1;
	string date = 2;
}
```

image: base64にエンコードされた画像データ
date: 撮影日時

