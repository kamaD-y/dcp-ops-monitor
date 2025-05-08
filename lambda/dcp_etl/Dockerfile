# uvからrequirements.txtを生成する為、builderステージを使用
FROM public.ecr.aws/lambda/python:3.13 as builder

WORKDIR /app
RUN python3.13 -m pip install uv

COPY . ./
RUN uv export -o requirements.txt --no-hashes

FROM public.ecr.aws/lambda/python:3.13

# Chromeの依存関係をインストール
# 参考: https://qiita.com/hideki/items/d1ff83e7e82afc0c0502
RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
        libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
        libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
        xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm \
        libgbm libxkbcommon libdrm

# 日本語フォントインストール
RUN dnf install -y google-noto-sans-cjk-jp-fonts

# 依存関係のインストール
COPY --from=builder /app/requirements.txt ./
RUN python3.13 -m pip install -r requirements.txt -t .

# selenium-managerを使ってChromeとChromeDriverをダウンロード
RUN /var/task/selenium/webdriver/common/linux/selenium-manager --browser chrome --cache-path /opt

# 実行用ファイルをコピー
COPY ./src ./

# Command can be overwritten by providing a different command in the template directly.
CMD ["handler.handler"]
