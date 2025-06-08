# uvからrequirements.txtを生成する為、builderステージを使用
FROM public.ecr.aws/lambda/python:3.13 as builder

# ChromeとChromeDriverのバージョンを明示的に指定してダウンロード
# バージョンに差異があるとエラーを起こす為、バージョンを揃える必要がある
# 参考: https://github.com/umihico/docker-selenium-lambda/blob/main/Dockerfile
RUN dnf install -y unzip && \
    curl -Lo "/tmp/chromedriver-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.68/linux64/chromedriver-linux64.zip" && \
    curl -Lo "/tmp/chrome-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.68/linux64/chrome-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/

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
# RUN /var/task/selenium/webdriver/common/linux/selenium-manager --browser chrome --cache-path /opt

# ChromeとChromeDriverを配置
COPY --from=builder /opt/chrome-linux64 /opt/chrome
COPY --from=builder /opt/chromedriver-linux64 /opt/

# 実行用ファイルをコピー
COPY ./src ./

# Command can be overwritten by providing a different command in the template directly.
CMD ["handler.handler"]
