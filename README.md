# stream-basler-usb-video-by-x11
## 概要
stream-basler-usb-video-by-x11は、basler製のSDKであるpypylonをラップした、basler製品のカメラを使用するためのマイクロサービスです。   
接続されたbasler製品のカメラを認識し、画像を撮影します。   
撮影データはX11 Bitmap及びX11 Pixmap形式に変換されたあと、jpgに変換され、メモリ内に保存されます。
他マイクロサービスへの提供時には、メモリ内の画像データをbase64に変換して送信します。

## 動作環境
stream-basler-usb-video-by-x11は、aion-coreのプラットフォーム上での動作を前提としています。   
使用する際は、事前に下記の通りAIONの動作環境を用意してください。   
* ARM CPU搭載のデバイス(NVIDIA Jetson シリーズ等)   
* OS: Linux Ubuntu OS   
* CPU: ARM64   
* Kubernetes   
* [AION](https://github.com/latonaio/aion-core)のリソース    

### basler製品のカメラ対応機種：
- acA1920-40gc
- acA1920-40uc
- acA1300-30gm
- acA2040-55uc

## セットアップ

1. ベースイメージをビルドします
```
bash docker-build-base.sh
```

2. イメージをビルドする
```
bash docker-build.sh
```

## 起動方法
### デプロイ on AION
project.ymlのmicroservicesに、以下のように記載してください。
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

### デプロイ方法
1. ターミナルを開き、以下のコマンドを実行してください。
```
$ export DISPLAY=:1
$ xhost +
```

2. aion-coreを起動します。

3. 映像が出力されます。

## grpcサーバー

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

