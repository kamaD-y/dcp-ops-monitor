# uvからrequirements.txtを生成する為、builderステージを使用
FROM public.ecr.aws/lambda/python:3.13 as builder

# NOTE: 2025/06/08時点で、137.x.x.xのバージョンでは対象サイトのスクレイピングにてエラーが発生した為、バージョン126で固定化している
# 参考: https://github.com/umihico/docker-selenium-lambda/blob/main/Dockerfile
RUN dnf install -y unzip && \
    curl -Lo "/tmp/chromedriver-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip" && \
    curl -Lo "/tmp/chrome-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chrome-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/

WORKDIR /app
RUN python3.13 -m pip install uv

# workspace root と shared をコピー
COPY pyproject.toml ./
COPY uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY web-scraping/pyproject.toml ./web-scraping/
RUN cd web-scraping && uv export -o /tmp/requirements.txt --no-hashes --no-dev --no-emit-workspace

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
COPY --from=builder /tmp/requirements.txt ./
RUN python3.13 -m pip install -r requirements.txt -t .

# selenium-managerを使ってChromeとChromeDriverをダウンロード
# RUN /var/task/selenium/webdriver/common/linux/selenium-manager --browser chrome --cache-path /opt

# ChromeとChromeDriverを配置
COPY --from=builder /opt/chrome-linux64 /opt/chrome
COPY --from=builder /opt/chromedriver-linux64 /opt/

# shared と src をコピー
COPY shared/src/shared ./shared
COPY web-scraping/src ./src

# Command can be overwritten by providing a different command in the template directly.
CMD ["src.handler.handler"]
